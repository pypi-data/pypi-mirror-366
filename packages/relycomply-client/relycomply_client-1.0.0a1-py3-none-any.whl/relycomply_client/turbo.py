from dataclasses import dataclass
from textwrap import dedent
from relycomply_client.integration_client import RelyComplyIntegrationClient
from relycomply_client.gql_client import RelyComplyGQLClient
from relycomply_client.types import (
    IngestLookupTablesStep,
    StepBaseModel,
    SyncStep,
    SetupDemoPermissionsStep,
    IngestDataSourcesStep,
    RunMonitorStep,
    ShellStep,
)
import requests
from .sync import RelySync
from .configuration_sources import StandardConfiguration
import typer
import tomli_w

from pathlib import Path
import os
import sh


@dataclass
class DataSourceSpec:
    data_set_name: str
    data_source_name: str
    semantic_date: str
    parquet_file_name: str


class Turbo:
    def __init__(self, root, configuration: StandardConfiguration, *, cli=None):
        self.root = Path(root)
        self.configuration = configuration
        self.gql = RelyComplyGQLClient(self.configuration)
        self.rc_client = RelyComplyIntegrationClient(self.gql)

    def run_steps(self, tags):
        for step in self.configuration.values.steps:
            if tags and not (set(tags) & set(step.tags)):
                continue

            typer.secho("\nRunning step", fg="green")
            typer.secho(tomli_w.dumps(step.model_dump()))

            match step.type:
                case "sync":
                    self.run_sync_step(step)
                case "ingest_lookup_tables":
                    self.run_ingest_lookup_tables_step(step)
                case "setup_demo_permissions":
                    self.run_setup_demo_permissions_step(step)
                case "ingest_data_sources":
                    self.run_ingest_data_sources_step(step)
                case "run_monitor":
                    self.run_monitor_step(step)
                case "shell":
                    self.run_shell(step)

    def run_setup_demo_permissions_step(self, step_config: SetupDemoPermissionsStep):
        self.gql.setDemoPermissions()  # type: ignore

    def run_sync_step(self, step_config: SyncStep):
        sync_folders = step_config.folders

        for folder in sync_folders:
            folder_path = self.root / folder

            rs = RelySync(
                folder_path,
                recursive=True,
                interactive=False,
                configuration=self.configuration,
                gql_client=self.gql,
            )
            rs.run_cli()

    def run_ingest_lookup_tables_step(self, step_config: IngestLookupTablesStep):
        sync_folders = step_config.folders

        for folder in sync_folders:
            folder_path = self.root / folder
            for file in folder_path.glob("*.parquet"):
                lookup_table_name = file.stem
                lookup_file = self.gql.createDataFile(  # type: ignore
                    name="lookup_table/" + lookup_table_name + ".parquet"
                )
                print(f"Uploading {file.name}...", end="", flush=True)
                with open(file, "rb") as fp:
                    requests.put(lookup_file["putUrl"], data=fp).raise_for_status()

                self.rc_client.ingest_parquet_lookup_table(
                    lookup_table_name,
                    lookup_file,
                    version_tag=step_config.version_tag,
                    replace_tag=True,
                )
                print(" COMPLETE")

    def run_ingest_data_sources_step(self, step_config: IngestDataSourcesStep):
        for data_source in step_config.data_sources:
            data_spec = DataSourceSpec(**data_source.model_dump())
            print(f"Upserting data source: {data_spec.data_source_name}")
            if not (
                datasource := self.rc_client.gql.dataSources(  # type: ignore
                    name=data_spec.data_source_name, _only=True
                )
            ):
                datasource = self.rc_client.gql.createDataSource(  # type: ignore
                    name=data_spec.data_source_name,
                    label=data_spec.data_source_name,
                    dataset=data_spec.data_set_name,
                    semanticDate=data_spec.semantic_date,
                )
            print(f"Creating datafile {data_spec.parquet_file_name}...", end="")
            datafile = self.rc_client.gql.createDataFile(  # type: ignore
                name=data_spec.parquet_file_name
            )
            print(" COMPLETE")

            with open(data_spec.parquet_file_name, "rb") as fp:
                print(f"Uploading {data_spec.parquet_file_name}...", end="")
                requests.put(datafile["putUrl"], data=fp).raise_for_status()
                print(" COMPLETE")

            print("Ingesting datasource...", end="")
            self.rc_client.ingest_datasource(datasource, datafile)
            print(" COMPLETE\n")

    def run_shell(self, step_config: ShellStep):
        command = step_config.command
        print(f"Running shell command: {command}")
        try:
            result = sh.bash(c=command)  # type: ignore
            print(result)
        except sh.ErrorReturnCode as e:
            typer.secho(f"Error: {e}", fg="red")
            typer.secho(f"Exit code: {e.exit_code}", fg="red")

    def run_monitor_step(self, step_config: RunMonitorStep):
        print("Runnning monitor...", end="")
        self.rc_client.gql.runMonitor(  # type: ignore
            id=step_config.monitor,
            runConfig=step_config.run_config,
            engine="athena",
        )
        print(" COMPLETE\n")


def turbo_help_text():
    def field_help(prop_name, prop_info, schema):
        prop_desc = prop_info.get("description", "No description")
        prop_type = prop_info.get("type", "unknown")
        required = prop_name in schema.get("required", [])
        req_str = " (required)" if required else " (optional)"
        return f"   * {prop_name}: {prop_type}{req_str} - {prop_desc}"

    def step_help(name, StepModel):
        schema = StepModel.model_json_schema()
        return (
            f"\n\n{name}:\n\n"
            + f"\n\n {schema.get('description', 'No description available')}\n\n\n\n"
            + "\n\n".join(
                [
                    field_help(prop_name, prop_info, schema)
                    for prop_name, prop_info in schema["properties"].items()
                    if prop_name != "type"
                ]
            )
        )

    return dedent("""
                Rely turbo allows us to define a series of steps that we commonly need to perform to 
                either setup or update an environment. You can think of it as 
                akin to a simple build system. Steps are defined in your configuration. Each step has a type, and potentially various parameters. 
                These essentially leverage the client capabilities.\n\n
                """) + "\n\n".join(
        [
            step_help(name, StepModel)
            for name, StepModel in StepBaseModel.get_step_types().items()
        ]
    )


def turbo(tag: list[str] = typer.Option([], help="Only run steps with these tags")):
    """
    An experimental deployment system for relycomply environments
    """
    typer.secho("Going TURBO!!!!", fg="green")
    root = os.getcwd()
    typer.echo(f"Root directory: {root}")
    configuration = StandardConfiguration()
    configuration.validate()

    my_turbo = Turbo(root, configuration)
    my_turbo.run_steps(tags=tag)

    return 0
