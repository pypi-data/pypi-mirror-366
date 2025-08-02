from __future__ import annotations

import dataclasses
import datetime
from typing import Any

import typer
from rich.console import Console

from cli.errors import ErrorPrinter
from cli.settings import TokenNotFoundError, settings
from cli.typer import typer_utils
from cli.utils.rest_helper import RestHelper

HELP = """
RemotiveTopology commands
"""
console = Console()
app = typer_utils.create_typer(help=HELP)


@dataclasses.dataclass
class Subscription:
    type: str
    display_name: str
    feature: str
    start_date: str  # TODO: add datetime
    end_date: str  # TODO: add datetime


def _print_current_subscription(subscription_info: dict[str, Any]) -> None:
    subscription_type = subscription_info.get("subscriptionType")
    end_date_str = subscription_info.get("endDate")
    now = datetime.datetime.now()

    def parse_date(date_str: str | None) -> datetime.datetime | None:
        return datetime.datetime.fromisoformat(date_str) if date_str else None

    expires = parse_date(end_date_str)

    if subscription_type == "trial":
        if expires and expires < now:
            console.print(f"Your Topology trial expired {end_date_str}, please contact support@remotivelabs.com")
        else:
            console.print(f"You already have an active topology trial, it expires {end_date_str}")

    elif subscription_type == "paid":
        if expires and expires < now:
            console.print(f"Topology subscription has ended, expired {end_date_str}")
        else:
            console.print(f"You already have an active topology subscription, it expires {end_date_str or 'Never'}")

    else:
        ErrorPrinter.print_generic_error("Unexpected exception, please contact support@remotivelabs.com")
        raise typer.Exit(1)


@app.command("start-trial")
def start_trial(
    organization: str = typer.Option(None, help="Organization to start trial for", envvar="REMOTIVE_CLOUD_ORGANIZATION"),
) -> None:
    """
    Allows you ta start a 30 day trial subscription for running RemotiveTopology, you can read more at https://docs.remotivelabs.com/docs/remotive-topology.

    """
    RestHelper.use_progress("Checking access tokens...", transient=True)
    try:
        _ = settings.get_active_token_file()
    except TokenNotFoundError:
        if len(settings.list_personal_token_files()) == 0:
            console.print(
                "You must first sign in to RemotiveCloud, please use [bold]remotive cloud auth login[/bold] to sign-in"
                "This requires a RemotiveCloud account, if you do not have an account you can sign-up at https://cloud.remotivelabs.com"
            )
        else:
            console.print(
                "You have not active account, please run [bold]remotive cloud auth activate[/bold] to choose an account"
                "or [bold]remotive cloud auth login[/bold] to sign-in"
            )
        return

    has_access = RestHelper.has_access("/api/whoami")
    if not has_access:
        ErrorPrinter.print_generic_message("Your current active credentials are not valid")
        raise typer.Exit(1)

    active_account = settings.get_cli_config().get_active_account()
    if active_account and not organization and not active_account.default_organization:
        ErrorPrinter.print_hint("You have not specified any organization and no default organization is set")
        raise typer.Exit(1)

    sub = RestHelper.handle_get(f"/api/bu/{organization}/features/topology", return_response=True, allow_status_codes=[404, 403])
    if sub.status_code == 404:
        created = RestHelper.handle_post(f"/api/bu/{organization}/features/topology", return_response=True)
        console.print(f"Topology trial started, it expires {created.json()['endDate']}")
    elif sub.status_code == 403:
        ErrorPrinter.print_generic_error(f"You are not allowed to start-trial topology in organization {organization}")
        raise typer.Exit(1)
    else:
        subscription_info = sub.json()
        _print_current_subscription(subscription_info)
    return
