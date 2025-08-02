from pathlib import Path
from typing import Optional

from .configuration_sources import StandardConfiguration
from .gql_client import RelyComplyGQLClient
import typer
from watchfiles import Change, DefaultFilter, watch

from relycomply_client.sync import RelySync


class TomlFilter(DefaultFilter):
    def __call__(self, change: Change, path: str) -> bool:
        return (
            super().__call__(change, path)
            and (path.endswith(".toml") or path.endswith(".toml.jinja"))
            and change == Change.modified
        )


def watch_sync(
    location: Optional[Path] = typer.Argument(
        Path("."), help="The location to look for configuration files"
    ),
    recursive: bool = typer.Option(
        False,
        help="If true will search for files recursively from the given location directory",
    ),
    interactive: bool = typer.Option(
        False, help="If true the will ask for confirmation before taking any action"
    ),
    break_on_error: bool = typer.Option(
        True,
        help="If true the sync will stop on the first error. If false it will attempt to continue.",
    ),
):
    """
    Watch for changes in configuration files and sync them with rely-sync
    """
    configuration = StandardConfiguration()
    configuration.validate()
    gql_client = RelyComplyGQLClient(configuration=configuration)

    assert location
    abs_location = location.absolute()
    wait_message = f"Waiting for changes at path: {abs_location} {'(recursive)' if recursive else ''}\n"

    print(wait_message)

    for changes in watch(
        location, recursive=recursive, debounce=1_600, watch_filter=TomlFilter()
    ):
        print("Detected changes in:")
        for change in changes:
            print(change[0])
            print(f"  - {change[1]}")
        print()
        changed_locations = [change[1] for change in changes]
        rely_sync = RelySync(
            changed_locations,
            recursive,
            interactive,
            break_on_error=break_on_error,
            configuration=configuration,
            gql_client=gql_client,
        )
        rely_sync.run_cli()
        print()
        print(wait_message)


def main():
    typer.run(watch_sync)


if __name__ == "__main__":
    main()
