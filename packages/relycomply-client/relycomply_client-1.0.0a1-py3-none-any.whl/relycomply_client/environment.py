from collections import defaultdict
import os
from pathlib import Path

import git
from pydantic import ValidationError
import toml

from .configuration_sources import StandardConfiguration
import typer
import tomli_w

environment_app = typer.Typer(help="Manage and investigate environments")


@environment_app.command()
def configuration():
    """
    Display the credential loading process and final resolved credentials.

    This command shows the sequence of credential loaders that were attempted,
    the configuration layers they produced, and the final merged credentials
    that will be used by the application. The credentials are displayed in
    TOML format with environments shown separately from other credential fields.
    The output includes:

        * Each credential loader attempted and its resulting layers

        * Final merged credentials (excluding environments) in green

        * Environment configurations displayed separately
    """

    configuration = StandardConfiguration()
    typer.secho("Credential Loaders Found:\n")
    for loader, layer in zip(configuration.loaders, configuration.layers):
        if layer:
            typer.secho(str(loader))
            typer.secho("-" * len(str(loader)))

            typer.secho(toml.dumps(layer))
            typer.secho()

    typer.secho("Final configuration")
    typer.secho("=================\n")

    typer.secho(
        tomli_w.dumps(
            {k: v for k, v in configuration.items().items() if k != "environments"}
        ),
        fg="green",
    )

    try:
        configuration.validate()
    except ValidationError as e:
        typer.secho(e, fg="red")
        exit()


@environment_app.command()
def list():
    """
    List all environments.
    """

    configuration = StandardConfiguration()
    current_environment = configuration.environment

    for k in configuration.known_environments():
        if k != current_environment:
            print(f"  {k}")
        else:
            typer.secho(f"* {k}", fg="green")


@environment_app.command()
def select(environment: str):
    """
    Select an environment
    """
    configuration = StandardConfiguration()

    if current_environment := os.environ.get("RELY_ENVIRONMENT"):
        typer.secho(
            f"Environment variable RELY_ENVIRONMENT={current_environment} is set. Changes will have no effect.",
            fg="red",
        )
        exit()
    else:
        typer.secho(f"Current environment: {configuration.environment}")

    known_environments = configuration.known_environments()
    if environment not in known_environments:
        typer.secho(
            f"The selected environment {environment} does not have any known configurations, the known environments are:",
            fg="red",
        )
        for known_env in known_environments:
            typer.secho("  * " + known_env, fg="red")
        if not typer.confirm("Are you sure you wish to continue"):
            exit()

    # Find closest .rely.toml
    environment_file_path = None
    for root in configuration.directory_ladder():
        path = root / ".rely-environment"
        if path.exists():
            typer.secho(f"Found {path}")
            environment_file_path = path
            break

    # Otherwise offer to create one in the git root
    if not environment_file_path:
        repo = git.Repo(os.getcwd(), search_parent_directories=True)
        environment_file_path = Path(repo.working_dir) / ".rely-environment"
        if not typer.confirm(
            f"No .rely-environment found, would you like to create one at the git root ({environment_file_path})"
        ):
            typer.secho("Environment could not be set", fg="red")
            exit()

    with open(environment_file_path, "w") as f:
        f.write(environment)
        typer.secho(f"Environment set to {environment}", fg="green")
