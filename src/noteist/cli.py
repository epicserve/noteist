#!/usr/bin/env python3

import logging
import textwrap
from datetime import datetime, timedelta

import dateparser
import typer
from rich import print
from typer import Context
from typing_extensions import Annotated  # noqa: UP035

from noteist.config_app import config_app, load_config
from noteist.todoist_client import TodoistClient

logger = logging.getLogger(__name__)
DATE_FORMAT = "%Y-%m-%d"


def format_task_info(prev_task: dict, task: dict, child: bool = False) -> str:
    """Format task information for display."""
    completed_at = datetime.fromisoformat(task["completed_at"].replace("Z", "+00:00"))
    completed_local = completed_at.strftime("%Y-%m-%d %H:%M:%S")

    bullet = "* "
    color = "bold green" if child is False else "bold white"
    if child is True:
        bullet = "  - "
    rtn_val = f"{bullet}[{color}]{task['content']}[/{color}] (completed: {completed_local})"
    if prev_task["parent_id"] is not None and task["parent_id"] is None:
        rtn_val = f"\n{rtn_val}"
    if task["description"]:
        rtn_val += textwrap.indent(f"\n[white]{task['description']}[/white]\n", " " * len(bullet))

    return rtn_val


def _version_callback(value: bool):
    if value:
        from noteist import __version__

        print(f"\n[green]noteist[/green] {__version__}")
        raise typer.Exit()


app = typer.Typer()
app.add_typer(config_app, name="config", help="Manage default values and options.")


@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    project: Annotated[str, typer.Option(help="Project name (e.g., Work)")] = "",
    token: Annotated[str, typer.Option(..., help="Todoist API token")] = "",
    since: Annotated[
        str,
        typer.Option(
            ...,
            help="Start date (YYYY-MM-DD, default: two weeks ago)",
        ),
    ] = (datetime.now() - timedelta(days=14)).strftime(DATE_FORMAT),
    until: Annotated[
        str,
        typer.Option(
            ...,
            help="End date (YYYY-MM-DD, default: today)",
        ),
    ] = datetime.now().strftime(DATE_FORMAT),
    version: Annotated[bool, typer.Option("--version", help="Print the current version", is_flag=True)] = False,
    debug: Annotated[bool, typer.Option("--debug", help="Enable debug logging", is_flag=True)] = False,
):
    if ctx.invoked_subcommand is not None:
        return

    if version:
        _version_callback(version)
        return

    config_data = load_config()
    if not project:
        project = config_data.get("project")
    if not token:
        token = config_data.get("token")
    if not project:
        print("\n[bold red]Error: The --project option is required, if you haven't set a default.[/bold red]\n")
        raise typer.Exit(1)
    if not token:
        print("\n[red]Error: The --token option is is required, if you haven't set a default.[/red]\n")
        raise typer.Exit(1)
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    client = TodoistClient(token)
    proj = client.find_project_by_name(project)
    if not proj:
        print(f"\n[red]Error: Could not find project named '{project}'[/red]\n")
        print("Available projects:")
        projects = client.get_projects()
        for p in projects["results"]:
            print(f"  - {p['name']}")
        raise typer.Exit(1)

    if not since:
        since = (datetime.now() - timedelta(days=14)).strftime(DATE_FORMAT)
    if not until:
        until = datetime.now().strftime(DATE_FORMAT)
    since_dt = dateparser.parse(since)
    until_dt = dateparser.parse(until) + timedelta(days=1) - timedelta(seconds=1)
    completed_tasks = client.get_completed_tasks(proj["id"], since_dt, until_dt)
    time_range_str = f"({since_dt.strftime(DATE_FORMAT)} to {until_dt.strftime(DATE_FORMAT)})"
    if not completed_tasks:
        typer.echo(f"\nNo completed tasks found {time_range_str}")
        return
    typer.echo(f"\n📋 Completed Tasks in #Canopy {time_range_str}")
    typer.echo("=" * 56 + "\n")

    main_tasks: int = 0
    sub_tasks: int = 0
    prev_task = {"parent_id": None}
    for task in completed_tasks:
        main_tasks += 1
        print(format_task_info(prev_task, task))
        if task["children"]:
            for child in task["children"]:
                sub_tasks += 1
                print(format_task_info(task, child, True))
        prev_task = task

    typer.echo("\nCompleted Totals")
    total_string = f"Main tasks: {main_tasks}, Sub tasks: {sub_tasks}, Total: {main_tasks + sub_tasks}\n"
    typer.echo("-" * (len(total_string) - 1))
    typer.echo(total_string)


def cli():
    app()
