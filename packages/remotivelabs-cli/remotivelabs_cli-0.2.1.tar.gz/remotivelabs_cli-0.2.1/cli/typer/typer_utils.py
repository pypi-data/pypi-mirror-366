from typing import Any

import typer
from click import Context
from rich.console import Console
from typer.core import TyperGroup


class OrderCommands(TyperGroup):
    def list_commands(self, _ctx: Context):  # type: ignore
        return list(self.commands)


console = Console()


def create_typer(**kwargs: Any) -> typer.Typer:
    """Create a Typer instance with default settings."""
    # return typer.Typer(no_args_is_help=True, **kwargs)
    return typer.Typer(cls=OrderCommands, no_args_is_help=True, **kwargs)


def print_padded(label: str, right_text: str, length: int = 30) -> None:
    padded_label = label.ljust(length)  # pad to 30 characters
    console.print(f"{padded_label} {right_text}")
