import typer

from cli.cloud import auth, brokers, configs, organisations, projects, recordings, sample_recordings, service_accounts, storage
from cli.typer import typer_utils
from cli.utils.rest_helper import RestHelper

app = typer_utils.create_typer()


@app.command(help="List licenses for an organization")
def licenses(
    organization: str = typer.Option(..., help="Organization ID", envvar="REMOTIVE_CLOUD_ORGANIZATION"),
    filter_option: str = typer.Option("all", help="all, valid, expired"),
) -> None:
    RestHelper.handle_get(f"/api/bu/{organization}/licenses", {"filter": filter_option})


app.add_typer(organisations.app, name="organizations", help="Manage organizations")
app.add_typer(projects.app, name="projects", help="Manage projects")
app.add_typer(auth.app, name="auth")
app.add_typer(brokers.app, name="brokers", help="Manage cloud broker lifecycle")
app.add_typer(recordings.app, name="recordings", help="Manage recordings")
app.add_typer(configs.app, name="signal-databases", help="Manage signal databases")
app.add_typer(storage.app, name="storage")
app.add_typer(service_accounts.app, name="service-accounts", help="Manage project service account keys")
app.add_typer(sample_recordings.app, name="samples", help="Manage sample recordings")

if __name__ == "__main__":
    app()
