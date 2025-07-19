#!/usr/bin/env python3

import logging
import textwrap
import argparse
import os
import toml

import requests
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class TodoistClient:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.todoist.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, endpoint: str, params=None) -> list[dict] | dict:
        """Generic method to make API requests."""
        url = f"{self.base_url}/{endpoint}"
        params = params or {}
        response = requests.request(method, url, headers=self.headers, params=params)
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

    def get_completed_tasks(
        self, project_id: str, since: datetime, until: datetime
    ) -> list[dict]:
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


def format_task_info(prev_task: dict, task: dict) -> str:
    """Format task information for display."""
    completed_at = datetime.fromisoformat(task["completed_at"].replace("Z", "+00:00"))
    completed_local = completed_at.strftime("%Y-%m-%d %H:%M:%S")

    bullet = "* "
    if task["parent_id"]:
        bullet = "  - "
    rtn_val = f"{bullet}{task['content']} (completed: {completed_local})"
    if prev_task["parent_id"] is not None and task["parent_id"] is None:
        rtn_val = f"\n{rtn_val}"
    if task["description"]:
        rtn_val += textwrap.indent(f"\n{task['description']}\n", " " * len(bullet))

    return rtn_val


def get_config_path():
    config_dir = Path.home() / ".config" / "noteist"
    config_dir.mkdir(parents=True, exist_ok=True)
    return str(config_dir / "config.toml")


def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return toml.load(f)
    return {}


def save_config(token=None, project=None):
    config_path = get_config_path()
    config = load_config()
    if token:
        config["token"] = token
    if project:
        config["project"] = project
    with open(config_path, "w") as f:
        toml.dump(config, f)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="noteist",
        description="Output a Markdown formatted report of completed tasks in Todoist.",
    )
    config = load_config()
    parser.add_argument(
        "--project",
        type=str,
        help="Project name (e.g., Work)",
        required=("project" not in config),
        default=config.get("project"),
    )
    parser.add_argument(
        "--token",
        type=str,
        help="Todoist API token",
        required=("token" not in config),
        default=config.get("token"),
    )
    parser.add_argument(
        "--since",
        type=str,
        default=(datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
        help="Start date (YYYY-MM-DD, default: one week ago)",
    )
    parser.add_argument(
        "--until",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="End date (YYYY-MM-DD, default: today)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--save-project",
        action="store_true",
        help="Save the provided project as default",
    )
    parser.add_argument(
        "--save-token", action="store_true", help="Save the provided token as default"
    )
    return parser.parse_args()


def cli():
    args = parse_args()

    if args.save_project:
        save_config(project=args.project)
    if args.save_token:
        save_config(token=args.token)

    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    client = TodoistClient(args.token)

    project = client.find_project_by_name(args.project)
    if not project:
        # Print error in red and exit with code 1
        print(
            f"\n\033[91mError: Could not find project named '{args.project}'\033[0m\n"
        )
        print("Available projects:")
        projects = client.get_projects()
        for project in projects["results"]:
            print(f"  - {project['name']}")
        exit(1)

    # Calculate date range (last week)
    since = datetime.strptime(args.since, "%Y-%m-%d")
    until = (
        datetime.strptime(args.until, "%Y-%m-%d")
        + timedelta(days=1)
        - timedelta(seconds=1)
    )

    completed_tasks = client.get_completed_tasks(project["id"], since, until)
    time_range_str = f"({since.strftime('%Y-%m-%d')} to {until.strftime('%Y-%m-%d')})"

    if not completed_tasks:
        print(f"\nNo completed tasks found {time_range_str}")
        return

    # Display results
    print(f"\n📋 Completed Tasks in #Canopy {time_range_str}")
    print("=" * 56)
    print(f"Total completed: {len(completed_tasks)}\n")

    prev_task = {
        "parent_id": None,
    }
    for task in completed_tasks:
        print(format_task_info(prev_task, task))
        prev_task = task
