from relycomply_client.configuration_sources import StandardConfiguration
from relycomply_client.gql_client import RelyComplyGQLClient
from .sync import sync
from .render import render
from .watch import watch_sync
from .cli import RelyComplyCLI
from .environment import environment_app
import typer
from .turbo import turbo, turbo_help_text


app = typer.Typer(rich_markup_mode="markdown")

app.command()(sync)
app.command("watch")(watch_sync)
app.command()(render)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def cli(
    ctx: typer.Context,
):
    """
    A convinient CLI for interacting with the RelyComply GraphQL API
    """
    configuration = StandardConfiguration()
    configuration.validate()
    gql_client = RelyComplyGQLClient(configuration=configuration)
    cli = RelyComplyCLI(gql_client=gql_client)
    cli.run_command(ctx.args)


app.add_typer(environment_app, name="environment")

app.command(help=turbo_help_text())(turbo)


def main():
    app()
