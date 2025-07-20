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

    def _request(self, method: str, endpoint: str, params=None) -> list[dict] | dict:
        url = f"{self.base_url}/{endpoint}"
        params = params or {}
        response = requests.request(method, url, headers=self.headers, params=params, timeout=30)
        logger.debug(f"Request: {method} {url} - {response.status_code} - {response.reason} - {response.text}")
        response.raise_for_status()
        return response.json()

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
        """Get completed tasks for a specific project since a given date."""
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
        return data["items"]
