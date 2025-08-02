from __future__ import annotations

from typing import List, Literal, Optional

import typer
from rich.console import Console
from rich.table import Table

from cli.api.cloud import tokens
from cli.cloud.organisations import do_select_default_org
from cli.errors import ErrorPrinter
from cli.settings import TokenNotFoundError, settings
from cli.settings.token_file import TokenFile
from cli.typer import typer_utils
from cli.utils.rest_helper import RestHelper as Rest

console = Console(stderr=False)
err_console = Console(stderr=True)

app = typer_utils.create_typer()

PromptType = Literal["activate", "login"]


def _prompt_choice(  # noqa: C901, PLR0912
    choices: List[TokenFile],
    skip_prompt: bool = False,
    info_message: Optional[str] = None,
) -> Optional[TokenFile]:
    accounts = settings.get_cli_config().accounts

    table = Table("#", "Active", "Type", "Token", "Account", "Created", "Expires")

    included_tokens: list[TokenFile] = []
    excluded_tokens: list[TokenFile] = []

    for token in choices:
        account = accounts.get(token.account.email)
        if account and account.credentials_file:
            try:
                token_file = settings.get_token_file(account.credentials_file)
                if token_file.name in (token.name or ""):
                    included_tokens.append(token)
            except TokenNotFoundError:
                excluded_tokens.append(token)
        else:
            excluded_tokens.append(token)

    if len(included_tokens) == 0:
        return None

    included_tokens.sort(key=lambda token: token.created, reverse=True)

    def get_active_token_or_none() -> Optional[TokenFile]:
        try:
            return settings.get_active_token_file()
        except TokenNotFoundError:
            return None

    active_token = get_active_token_or_none()
    active_token_index = None
    for idx, choice in enumerate(included_tokens, start=1):
        is_active = active_token is not None and active_token.name == choice.name
        active_token_index = idx if is_active else active_token_index

        table.add_row(
            f"[yellow]{idx}",
            ":white_check_mark:" if is_active else "",
            "user" if choice.type == "authorized_user" else "sa",
            choice.name,
            f"[bold]{choice.account.email if choice.account else 'unknown'}[/bold]",
            str(choice.created),
            str(choice.expires),
        )
    console.print(table)

    if skip_prompt:
        return None

    typer.echo("")
    if info_message is not None:
        console.print(info_message)

    selection = typer.prompt(
        f"Enter the number(# 1-{len(included_tokens)}) of the account to select (q to quit)",
        default=f"{active_token_index}" if active_token_index is not None else None,
    )

    if selection == "q":
        return None
    try:
        index = int(selection) - 1
        if 0 <= index < len(included_tokens):
            return included_tokens[index]
        raise ValueError
    except ValueError:
        typer.echo("Invalid choice, please try again")
        return _prompt_choice(included_tokens, skip_prompt, info_message)


# @app.command(name="create")
def create(
    activate: bool = typer.Option(False, help="Activate the token for use after download"),
) -> None:
    """
    Create a new personal access token in [bold]cloud[/bold] and download locally
    """
    response = tokens.create()
    pat = settings.add_personal_token(response.text())
    print(f"Personal access token added: {pat.name}")

    if not activate:
        print(f"Use 'remotive cloud auth tokens activate {pat.name}' to use this access token from cli")
    else:
        settings.activate_token(pat)
        print("Token file activated and ready for use")
    print("\033[93m This file contains secrets and must be kept safe")


# @app.command(name="list", help="List personal credentials in [bold]cloud[/bold]")
def list_tokens() -> None:
    Rest.handle_get("/api/me/keys")


# @app.command(name="revoke")
def revoke(
    name: str = typer.Argument(help="Access token name"),
    delete: bool = typer.Option(True, help="Also delete token"),
) -> None:
    """
    Revoke personal credentials in cloud and removes the file from filesystem

    If cloud token is not found but token is found on file system it will delete it and
    vice versa.
    """
    _revoke_and_delete_personal_token(name, delete)


# @app.command(name="activate")
def activate(
    token_name: str = typer.Argument(..., help="Token path, filename or name to activate"),
) -> None:
    """
    Activate a credential file to be used for authentication using filename, path or name.

    This will be used as the current access token in all requests.
    """
    try:
        token_file = settings.get_token_file(token_name)
        settings.activate_token(token_file)
    except TokenNotFoundError:
        err_console.print(f":boom: [bold red] Error: [/bold red] Token with filename or name {token_name} could not be found")


def prompt_to_set_org() -> None:
    active_account = settings.get_cli_config().get_active_account()
    if active_account and not active_account.default_organization:
        set_default_organisation = typer.confirm(
            "You have not set a default organization\nWould you like to choose one now?",
            abort=False,
            default=True,
        )
        if set_default_organisation:
            do_select_default_org(get=False)


@app.command("activate")
def select_personal_token(
    token_name: str = typer.Argument(None, help="Name, filename or path to a credentials file"),
) -> None:
    """
    Activates is setting the current active credentials to use by the CLI, this can be done by specifying a name
    of the token or getting prompted and choosing from existing.
    """
    do_activate(token_name)


def do_activate(token_name: Optional[str]) -> Optional[TokenFile]:
    if token_name is not None:
        try:
            token_file = settings.get_token_file(token_name)
            settings.activate_token(token_file)
            return token_file
        except TokenNotFoundError:
            err_console.print(f":boom: [bold red] Error: [/bold red] Token with filename or name {token_name} could not be found")
            return None
    else:
        token_files = settings.list_personal_tokens()
        token_files.extend(settings.list_service_account_tokens())
        if len(token_files) > 0:
            token_selected = list_and_select_personal_token(include_service_accounts=True)
            if token_selected is not None:
                is_logged_in = Rest.has_access("/api/whoami")
                if not is_logged_in:
                    ErrorPrinter.print_generic_error("Could not access RemotiveCloud with selected token")
                else:
                    console.print("[green]Success![/green] Access to RemotiveCloud granted")
                    # Only select default if activate was done with selection and successful
                    # and not SA since SA cannot list available organizations
                    if token_selected.type == "authorized_user":
                        prompt_to_set_org()
            return token_selected

        ErrorPrinter.print_hint("No credentials available, login to activate credentials")
        return None


def list_and_select_personal_token(
    skip_prompt: bool = False,
    include_service_accounts: bool = False,
    info_message: Optional[str] = None,
) -> Optional[TokenFile]:
    personal_tokens = settings.list_personal_tokens()

    if include_service_accounts:
        sa_tokens = settings.list_service_account_tokens()
        personal_tokens.extend(sa_tokens)

    selected_token = _prompt_choice(personal_tokens, skip_prompt=skip_prompt, info_message=info_message)
    if selected_token is not None:
        settings.activate_token(selected_token)

    return selected_token


# @app.command("select-revoke")
def select_revoke_personal_token() -> None:
    """
    Prompts a user to select one of the credential files to revoke and delete
    """
    personal_tokens = settings.list_personal_tokens()
    sa_tokens = settings.list_service_account_tokens()
    personal_tokens.extend(sa_tokens)

    is_logged_in = Rest.has_access("/api/whoami")
    if not is_logged_in:
        ErrorPrinter.print_hint("You must be logged in")
        raise typer.Exit(0)

    # merged = _merge_local_tokens_with_cloud(personal_tokens)

    selected_token = _prompt_choice(personal_tokens)

    if selected_token is not None:
        _revoke_and_delete_personal_token(selected_token.name, True)
        # Rest.handle_patch(f"/api/me/keys/{selected_token.name}/revoke", quiet=True, access_token=selected_token.token)
        # Rest.handle_delete(f"/api/me/keys/{selected_token.name}", quiet=True, access_token=selected_token.token)
        # settings.remove_token_file(selected_token.name)
        # active_token = settings.get_active_token_file()
        # if active_token.name == selected_token.name:
        #    settings.clear_active_token()
        # select_revoke_personal_token()


# @app.command("test-all")
def test_all_personal_tokens() -> None:
    """
    Tests each credential file to see if it is valid
    """
    personal_tokens = settings.list_personal_tokens()
    personal_tokens.extend(settings.list_service_account_tokens())
    if len(personal_tokens) == 0:
        console.print("No personal tokens found on disk")
        return

    for token in personal_tokens:
        r = Rest.handle_get(
            "/api/whoami",
            allow_status_codes=[401],
            access_token=token.token,
            use_progress_indicator=True,
            return_response=True,
        )
        if r.status_code == 200:
            if token.account is not None:
                console.print(f"{token.account.email} ({token.name}) :white_check_mark:")
            else:
                console.print(f"{token.name} :white_check_mark:")
        elif token.account is not None:
            console.print(f"{token.account.email} ({token.name}) :x: Failed")
        else:
            console.print(f"{token.name} :x: Failed")


# @app.command(name="list-service-account-tokens-files")
def list_sats_files() -> None:
    """
    List service account access token files in remotivelabs config directory
    """
    service_account_files = settings.list_service_account_token_files()
    for file in service_account_files:
        print(file)


@app.command(name="list")
def list_pats_files(
    accounts: bool = typer.Option(True, help="Lists all available accounts"),
    files: bool = typer.Option(False, help="Shows all token files in config directory"),
) -> None:
    """
    Lists available credential files on filesystem
    """

    if accounts:
        list_and_select_personal_token(skip_prompt=True, include_service_accounts=True, info_message="hello")

    if files:
        personal_files = settings.list_personal_token_files()
        service_account_files = settings.list_service_account_token_files()
        personal_files.extend(service_account_files)
        for file in personal_files:
            print(file)


def _revoke_and_delete_personal_token(name: str, delete: bool) -> None:
    token_file = None

    # First we try to find the file and make sure its not the currently active
    try:
        token_file = settings.get_token_file(name)
        active_token = settings.get_active_token_file()
        if token_file.name == active_token.name:
            ErrorPrinter.print_hint("You cannot revoke the current active token")
            return
    except TokenNotFoundError:
        pass

    # The lets try to revoke from cloud
    res_revoke = tokens.revoke(name)
    if delete:
        res_delete = tokens.delete(name)
        if res_delete.is_success:
            ErrorPrinter.print_generic_message("Token successfully revoked and deleted")
        else:
            ErrorPrinter.print_hint(f"Failed to revoke and delete token in cloud: {res_delete.status_code}")
    elif res_revoke.is_success:
        ErrorPrinter.print_generic_message("Token successfully revoked")
    else:
        ErrorPrinter.print_hint("Failed to revoke and delete token in cloud")

    # Finally try to remove the file if exists
    if token_file is not None:
        settings.remove_token_file(token_file.name)
        console.print("Successfully deleted token on filesystem")
    else:
        ErrorPrinter.print_hint("Token not found on filesystem")
