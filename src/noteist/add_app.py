from typing import Annotated

import typer
from rich import print
from typer import Context

from noteist.config_app import load_config
from src.noteist.todoist_client import TodoistClient

add_app = typer.Typer()


@add_app.callback(invoke_without_command=True)
def add(
    ctx: Context,
    content: Annotated[str, typer.Argument(help="My task #work tomorrow")],
):
    config_data = load_config()
    token = config_data.get("token")
    client = TodoistClient(token)
    data = client.add_task(content)
    print(f"\n[green]Your task has been added![/green]\n")
