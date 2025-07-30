import logging
from datetime import datetime

import requests

logger = logging.getLogger(__name__)


class TodoistClient:
    def __init__(self, api_token: str):
        """Todoist API client for making requests."""
        self.api_token = api_token
        self.base_url = "https://api.todoist.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def _merge_dicts(self, parent_data: dict, child_data: dict):
        result = parent_data.copy()
        for key, value in child_data.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._merge_dicts(result[key], value)
                elif isinstance(result[key], list) and isinstance(value, list):
                    result[key] += value
                else:
                    result[key] = value
            else:
                result[key] = value
        return result

    def _request(self, method: str, endpoint: str, params=None, data=None) -> list[dict] | dict:
        url = f"{self.base_url}/{endpoint}"
        params = params or {}
        response = requests.request(method, url, headers=self.headers, params=params, timeout=30)
        logger.debug(f"Request: {method} {url} - {response.status_code} - {response.reason} - {response.text}")
        response.raise_for_status()
        response_data = response.json()
        next_cursor = response_data.get("next_cursor")
        data = self._merge_dicts(data, response_data) if data is not None else response_data
        if next_cursor:
            params["cursor"] = next_cursor
            return self._request(method, endpoint, params=params, data=data)
        return data

    def get_projects(self) -> list[dict]:
        """Get all projects."""
        return self._request("GET", "projects")

    def find_project_by_name(self, project_name: str) -> dict | None:
        """Find a project by name."""
        projects = self.get_projects()
        if not projects or "results" not in projects:
            return None
        else:
            projects = projects["results"]

        for project in projects:
            if project["name"].lower() == project_name.lower():
                logger.info(f"Found project: {project['name']} (ID: {project['id']})")
                return project
        return None

    def get_completed_tasks(self, project_id: str, since: datetime, until: datetime) -> list[dict]:
        """Get completed tasks for a specific project since a given date, nested by parent-child relationships."""
        iso_8601_format = "%Y-%m-%dT%H:%M:%SZ"

        data = self._request(
            "GET",
            "tasks/completed/by_completion_date",
            params={
                "project_id": project_id,
                "since": since.strftime(iso_8601_format),
                "until": until.strftime(iso_8601_format),
            },
        )
        items = data["items"]
        # Build id -> item mapping
        id_map = {item["id"]: {**item, "children": []} for item in items}
        # Nest children under parents
        roots = []
        for item in items:
            parent_id = item.get("parent_id")
            if parent_id is None:
                roots.append(id_map[item["id"]])
            elif parent_id in id_map:
                id_map[parent_id]["children"].append(id_map[item["id"]])

        # Sort children by child_order
        def sort_children(task):
            task["children"].sort(key=lambda x: x.get("child_order", 0))
            for child in task["children"]:
                sort_children(child)

        for root in roots:
            sort_children(root)
        return roots
