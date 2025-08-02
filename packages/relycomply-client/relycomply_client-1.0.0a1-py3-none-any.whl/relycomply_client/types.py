from typing import Any, Literal, Union
from typing_extensions import Annotated
from pydantic import BaseModel, Field


class StepBaseModel(BaseModel):
    """Base model for all configuration steps in the RelyComply automation workflow.

    All step types inherit from this base class and share common functionality
    like tagging for conditional execution.
    """

    def __init_subclass__(cls, **kwargs):
        """Register step types when subclasses are created."""
        super().__init_subclass__(**kwargs)

        # Get the step type from the type field annotation if it exists
        if hasattr(cls, "__annotations__") and "type" in cls.__annotations__:
            type_annotation = cls.__annotations__["type"]
            # Extract the literal value from Annotated[Literal["step_name"], ...]
            if hasattr(type_annotation, "__args__"):
                for arg in type_annotation.__args__:
                    if hasattr(arg, "__args__") and len(arg.__args__) > 0:
                        step_type = arg.__args__[0]
                        # Store in module-level registry
                        _STEP_TYPES_REGISTRY[step_type] = cls
                        break

    @classmethod
    def get_step_types(cls) -> dict[str, type["StepBaseModel"]]:
        """Get all registered step types."""
        return _STEP_TYPES_REGISTRY.copy()

    @classmethod
    def get_step_type_names(cls) -> list[str]:
        """Get all registered step type names."""
        return list(_STEP_TYPES_REGISTRY.keys())

    tags: Annotated[
        list[str],
        Field(
            description="Optional tags for conditional step execution. Steps with matching tags will be run when specified.",
        ),
    ] = []


# Module-level registry for step types
_STEP_TYPES_REGISTRY: dict[str, type[StepBaseModel]] = {}


class SyncStep(StepBaseModel):
    """Synchronizes configuration files from specified folders to the RelyComply platform.

    This step recursively uploads configuration files (assessments, workflows, etc.)
    from local folders to the RelyComply system, enabling configuration management.
    """

    type: Annotated[
        Literal["sync"], Field(description="Step type identifier for sync operations")
    ]
    folders: Annotated[
        list[str],
        Field(
            description="List of folder paths to synchronize. Paths are relative to the configuration root."
        ),
    ]


class SetupDemoPermissionsStep(StepBaseModel):
    """Sets up demo permissions in the RelyComply system.

    This step configures the necessary permissions for demo environments,
    typically used during initial setup or demonstration scenarios.
    """

    type: Annotated[
        Literal["setup_demo_permissions"],
        Field(description="Step type identifier for demo permission setup"),
    ]


class IngestLookupTablesStep(StepBaseModel):
    """Ingests lookup tables from Parquet files into the RelyComply system.

    This step uploads and processes lookup table data stored in Parquet format,
    making the data available for use in risk ratings.
    """

    type: Annotated[
        Literal["ingest_lookup_tables"],
        Field(description="Step type identifier for lookup table ingestion"),
    ]
    folders: Annotated[
        list[str],
        Field(
            description="List of folder paths containing Parquet files to ingest as lookup tables"
        ),
    ]
    version_tag: Annotated[
        str,
        Field(
            description="Version tag to apply to the ingested lookup tables for versioning and rollback purposes"
        ),
    ]


class DataSource(BaseModel):
    """Represents a data source configuration for ingestion into RelyComply.

    Defines the metadata and file location for a data source that will be
    uploaded and made available for compliance monitoring and analysis.
    """

    data_set_name: Annotated[
        str, Field(description="Name of the dataset this data source belongs to")
    ]
    data_source_name: Annotated[
        str, Field(description="Unique name for this data source within the dataset")
    ]
    semantic_date: Annotated[
        str,
        Field(
            description="Semantic date for the data source, in ISO format (YYYY-MM-DD)"
        ),
    ]
    parquet_file_name: Annotated[
        str,
        Field(description="Path to the Parquet file containing the data source data"),
    ]


class IngestDataSourcesStep(StepBaseModel):
    """Ingests multiple data sources into the RelyComply platform.

    This step creates and uploads data sources from Parquet files,
    making the data available for data flows.
    """

    type: Annotated[
        Literal["ingest_data_sources"],
        Field(description="Step type identifier for data source ingestion"),
    ]
    data_sources: Annotated[
        list[DataSource],
        Field(
            description="List of data sources to ingest, each with its own configuration and data file"
        ),
    ]


class RunMonitorStep(StepBaseModel):
    """Executes a compliance monitor with specified configuration.

    This step triggers the execution of a compliance monitoring job
     with custom run-time configuration.
    """

    type: Annotated[
        Literal["run_monitor"],
        Field(description="Step type identifier for monitor execution"),
    ]
    monitor: Annotated[str, Field(description="ID or name of the monitor to execute")]
    run_config: Annotated[
        str, Field(description="Runtime configuration for the monitor execution")
    ]


class ShellStep(StepBaseModel):
    """Executes a shell command as part of the automation workflow.

    This step allows for running arbitrary shell commands, enabling
    custom operations like file processing, external tool execution, or system setup.
    """

    type: Annotated[
        Literal["shell"],
        Field(description="Step type identifier for shell command execution"),
    ]
    command: Annotated[
        str, Field(description="Shell command to execute. Will be run using bash.")
    ]


Step = Annotated[
    Union[
        SyncStep,
        SetupDemoPermissionsStep,
        IngestLookupTablesStep,
        IngestDataSourcesStep,
        RunMonitorStep,
        ShellStep,
    ],
    Field(discriminator="type"),
]
"""Union type for all possible step configurations in the RelyComply automation workflow.

The discriminator field 'type' is used to determine which specific step type to instantiate
when parsing configuration files. This enables type-safe step execution with proper
validation of step-specific fields.
"""


class ConfigurationModel(BaseModel):
    """Main configuration model for RelyComply automation workflows.

    This model defines the complete configuration for a RelyComply automation session,
    including connection details, authentication, and the sequence of steps to execute.
    """

    url: Annotated[str, Field(description="Base URL of the RelyComply API endpoint")]
    token: Annotated[str, Field(description="Authentication token for API access")]
    impersonate: Annotated[
        str | None,
        Field(
            description="Optional user ID to impersonate for the session. Useful for testing or admin operations.",
        ),
    ] = None

    variables: Annotated[
        dict[str, Any],
        Field(
            description="Key-value pairs for template variables that can be used throughout the configuration",
        ),
    ] = {}
    steps: Annotated[
        list[Step],
        Field(
            description="Ordered list of steps to execute in the automation workflow",
        ),
    ] = []
