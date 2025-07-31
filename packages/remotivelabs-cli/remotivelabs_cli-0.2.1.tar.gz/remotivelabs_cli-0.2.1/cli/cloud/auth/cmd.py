from __future__ import annotations

import sys

import typer

from cli.cloud.auth.login import login as do_login
from cli.errors import ErrorPrinter
from cli.settings import TokenNotFoundError, settings
from cli.typer import typer_utils
from cli.utils.rest_helper import RestHelper as Rest

from .. import auth_tokens

HELP = """
Manage how you authenticate with our cloud platform
"""
app = typer_utils.create_typer(help=HELP)
# app.add_typer(auth_tokens.app, name="credentials", help="Manage account credentials")


@app.command(name="login")
def login(browser: bool = typer.Option(default=True, help="Does not automatically open browser, instead shows a link")) -> None:
    """
    Login to the cli using browser

    If not able to open a browser it will show fallback to headless login and show a link that
    users can copy into any browser when this is unsupported where running the cli - such as in docker,
    virtual machine or ssh sessions.
    """
    do_login(headless=not browser)


@app.command()
def whoami() -> None:
    """
    Validates authentication and fetches your account information
    """
    try:
        Rest.handle_get("/api/whoami")
    except TokenNotFoundError as e:
        ErrorPrinter.print_hint(str(e))
        sys.exit(1)


@app.command()
def print_access_token(
    account: str = typer.Option(None, help="Email of the account you want to print access token for, defaults to active"),
) -> None:
    """
    Print current active access token or the token for the specified account
    """
    if account is None:
        try:
            print(settings.get_active_token())
        except TokenNotFoundError:
            ErrorPrinter.print_generic_error("You have no active account", exit_code=1)
    else:
        config = settings.get_cli_config()
        if account in config.accounts:
            token_file_name = config.accounts[account].credentials_file
            try:
                print(settings.get_token_file(token_file_name).token)
            except TokenNotFoundError:
                ErrorPrinter.print_generic_error(f"Token file for {account} could not be found", exit_code=1)
        else:
            ErrorPrinter.print_generic_error(f"No account for {account} was found", exit_code=1)


def print_access_token_file() -> None:
    """
    Print current active token and its metadata
    """
    try:
        print(settings.get_active_token_file())
    except TokenNotFoundError as e:
        ErrorPrinter.print_hint(str(e))
        sys.exit(1)


# @app.command(help="Clears active credentials")
def logout() -> None:
    settings.clear_active_token()
    print("Access token removed")


app.command("activate")(auth_tokens.select_personal_token)
app.command("list")(auth_tokens.list_pats_files)
