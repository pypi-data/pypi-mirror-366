from pathlib import Path

import toml

from .gql_client import RelyComplyGQLClient

from .configuration_sources import StandardConfiguration
from .sync import RelySync
import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from typing_extensions import Annotated


def render(
    location: Path = typer.Argument(
        help="The location to look for configuration template file"
    ),
    highlight: Annotated[bool, typer.Option(help="Say hi formally.")] = True,
):
    """
    Renders jinja templates of configuration files for the purposes of debugging
    """
    # Check if location exists and is a file
    if not location.exists():
        raise typer.BadParameter(f"Location {location} does not exist")
    if not location.is_file():
        raise typer.BadParameter(f"Location {location} is not a file")
    configuration = StandardConfiguration()
    configuration.validate()
    gql_client = RelyComplyGQLClient(configuration=configuration)
    rely_sync = RelySync(
        location=location,
        recursive=False,
        interactive=False,
        configuration=configuration,
        gql_client=gql_client,
    )
    rendered_results = rely_sync.load_and_render_template(location)

    console = Console()

    try:
        toml.loads(rendered_results)
    except toml.TomlDecodeError as e:
        message = "TOML Decode Error" + str(e)
        if highlight:
            console.print(Panel(message, style="on red"))
        else:
            print(message)
    if highlight:
        console = Console()
        syntax = Syntax(rendered_results, "toml", line_numbers=True)

        console.print(syntax)
    else:
        print(rendered_results)
