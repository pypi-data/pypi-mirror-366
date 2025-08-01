from __future__ import annotations

import os
import sys
from typing import Optional

import grpc
from rich.console import Console

err_console = Console(stderr=True)


# This should be renamed to Printer since print_generic_message is not an error message.
# Then we can also add more things here
class ErrorPrinter:
    @staticmethod
    def print_grpc_error(error: grpc.RpcError) -> None:
        if error.code() == grpc.StatusCode.UNAUTHENTICATED:
            is_access_token = os.environ["ACCESS_TOKEN"]
            if is_access_token is not None and is_access_token == "true":
                err_console.print(f":boom: [bold red]Authentication failed[/bold red]: {error.details()}")
                err_console.print("Please login again")
            else:
                err_console.print(":boom: [bold red]Authentication failed[/bold red]")
                err_console.print("Failed to verify api-key")
        else:
            # print(f"Unexpected error: {error.code()}")
            err_console.print(f":boom: [bold red]Unexpected error, status code[/bold red]: {error.code()}")
            err_console.print(error.details())
        sys.exit(1)

    @staticmethod
    def print_hint(message: str) -> None:
        err_console.print(f":point_right: [bold]{message}[/bold]")

    @staticmethod
    def print_generic_error(message: str, exit_code: Optional[int] = None) -> None:
        err_console.print(f":boom: [bold red]Failed[/bold red]: {message}")
        if exit_code is not None:
            sys.exit(exit_code)

    @staticmethod
    def print_generic_message(message: str) -> None:
        err_console.print(f"[bold]{message}[/bold]")
