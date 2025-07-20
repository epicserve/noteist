from enum import Enum
from pathlib import Path
from typing import Annotated

import toml
import typer
from rich import box, print
from rich.console import Console
from rich.table import Table

config_app = typer.Typer()


class ConfigOptions(str, Enum):
    project = "project"
    token = "token"  # noqa: S105


def get_config_path() -> Path:
    config_dir = Path.home() / ".config" / "noteist"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.toml"


def load_config():
    config_path = get_config_path()
    if config_path.exists():
        return toml.loads(config_path.read_text())
    return {}


def save_config(token: str = None, project: str = None):
    config_path = get_config_path()
    config = {}
    if token:
        config["token"] = token
    if project:
        config["project"] = project
    config_path.write_text(toml.dumps(config))


@config_app.callback(invoke_without_command=True)
def user_callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        ctx.get_help()  # Display help for the 'user' subcommand group


@config_app.command("list", help="List all the default options and values set.")
def list_config():
    data = load_config()
    print_config(data)


@config_app.command("set", help="Set a default value or an option.")
def set_value(
    option: Annotated[ConfigOptions, typer.Argument(help="The option to set.")],
    value: Annotated[
        str,
        typer.Argument(help="Set a default value or an option (e.g., Work)."),
    ],
):
    data = load_config()
    data[option.value] = value
    save_config(**data)
    print(f'\n[green]"{value}" was set for the {option.value} option.[/green]')


@config_app.command(help="Unset a default value or an option.")
def unset(
    option: Annotated[
        ConfigOptions,
        typer.Argument(help="Unset a default value or an option (e.g., project)."),
    ],
):
    data = load_config()
    if option.value not in data:
        print(f"\n[red]Error: The option '{option.value}' is not set.[/red]\n")
        raise typer.Exit(1)
    del data[option.value]
    save_config(**data)
    print(f'\n[green]The "{option.value}" option was unset.[/green]')
    print_config(data)


def print_config(config_data):
    if not config_data:
        print("\n[red]No default values or options are set.[/red]\n")
        return
    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("option", justify="left", style="cyan", no_wrap=True)
    table.add_column("value", justify="left")
    for key, val in config_data.items():
        table.add_row(key, val)
    console = Console()
    console.print(table)
