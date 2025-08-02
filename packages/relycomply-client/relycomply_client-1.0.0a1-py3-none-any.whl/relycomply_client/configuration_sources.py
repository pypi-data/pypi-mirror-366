import os
from typing import Any
from pydantic import ValidationError
from relycomply_client.types import ConfigurationModel
import toml
from pathlib import Path
import logging
import git
import os
import boto3
import base64
from botocore.exceptions import ClientError
import typer


from .exceptions import RelyComplyClientException

log = logging.getLogger(__name__)
keys = ["token", "url", "impersonate", "variables"]


def dict_merge(dct, merge_dct):
    """Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k in merge_dct.keys():
        if k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], dict):  # noqa
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def merge_credentials(layers):
    credentials = {}
    for layer_credentials in layers:
        dict_merge(credentials, layer_credentials)
    return credentials


class ConfigurationLoader:
    def __str__(self):
        return type(self).__name__ + "()"

    def items(self) -> dict[str, Any]: ...

    def variables(self) -> dict[str, Any]:
        return self.get("variables", {})  # type: ignore

    def get(self, key, default=None):
        return self.items().get(key, default)

    def require(self, key):
        value = self.get(key)
        if not value:
            raise RelyComplyClientException(
                f"Configuration '{key}' is required but not present"
            )
        return value


class Default(ConfigurationLoader):
    def items(self):
        return {"url": "https://app.relycomply.com"}


class Environment(ConfigurationLoader):
    def items(self):
        return {
            key: os.environ[f"RELYCOMPLY_{key.upper()}"]
            for key in keys
            if f"RELYCOMPLY_{key.upper()}" in os.environ
        }


class ConfigFolder(ConfigurationLoader):
    def __init__(self, folder: Path, filename=".rely.toml"):
        self.filename = filename
        self.folder = folder

    def items(self):
        config_path = self.folder / self.filename
        if not config_path.exists():
            return {}
        else:
            with open(config_path) as f:
                config_values = toml.load(f)
                return config_values

    def __str__(self):
        return type(self).__name__ + f"({self.folder}/{self.filename})"


class SecretsManager(ConfigurationLoader):
    def load_secret(self, key):
        session = boto3.session.Session()  # type: ignore
        client = session.client(
            service_name="secretsmanager",
        )
        secret_name = key

        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            raise RelyComplyClientException(
                f"Could not retrieve secret {key}: str(e)"
            ) from e
        else:
            # Decrypts secret using the associated KMS CMK.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
            if "SecretString" in get_secret_value_response:
                return get_secret_value_response["SecretString"]
            else:
                return base64.b64decode(get_secret_value_response["SecretBinary"])

    def items(self):
        secret_keys = {
            key: os.environ[f"RELYCOMPLY_{key.upper()}_AWS_SECRET"]
            for key in keys
            if f"RELYCOMPLY_{key.upper()}_AWS_SECRET" in os.environ
        }
        return {key: self.load_secret(value) for key, value in secret_keys.items()}


class Arguments(ConfigurationLoader):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def items(self):
        return {key: self.kwargs[key] for key in keys if self.kwargs.get(key)}


class StandardConfiguration(ConfigurationLoader):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._values = None

        environment = self.environment
        self.loaders = [
            Default(),
            *self.folder_loaders(environment),
            SecretsManager(),
            Environment(),
            Arguments(**self.kwargs),
        ]
        log.info("Loading Credentials")
        self.layers = [loader.items() for loader in self.loaders]
        self.results = merge_credentials(self.layers)

        for loader, layer in zip(self.loaders, self.layers):
            log.info(f"{loader}: {layer}")

        log.info(f"Merged Credentials: {self.results}")

        # TODO: Branch protection

        log.info(f"Final Credentials: {self.results}")

    def directory_ladder(self):
        root = Path(".").resolve()
        yield root
        yield from root.parents

    def folder_loaders(self, environment: str | None):
        folder_credentials = []

        file_patterns = (
            [
                ".rely.toml",
                f".rely-configuration-{environment}.toml",
                ".rely-configuration.toml",
                f"rely-configuration-{environment}.toml",
                "rely-configuration.toml",
            ]
            if environment
            else [
                ".rely.toml",
                ".rely-configuration.toml",
                "rely-configuration.toml",
            ]
        )
        for root in self.directory_ladder():
            for filename in file_patterns:
                if (root / filename).exists():
                    folder_credentials.append(ConfigFolder(root, filename))

        return reversed(folder_credentials)

    @property
    def environment(self):
        if not hasattr(self, "_environment"):
            self._environment = self.find_environment()
        return self._environment

    def find_environment(self):
        if environment := os.environ.get("RELY_ENVIRONMENT"):
            return environment

        for root in self.directory_ladder():
            if (root / ".rely-environment").exists():
                with open(root / ".rely-environment") as f:
                    environment = f.read()
                    return environment

    def known_environments(self):
        environments = set()
        for root in self.directory_ladder():
            for x in root.glob(
                "*rely-configuration-*.toml",
            ):
                environment = x.stem.split("-")[-1]
                environments.add(environment)
        return environments

    def items(self):
        return self.results

    @property
    def values(self):
        if not self._values:
            self._values = ConfigurationModel.model_validate(self.results)

        return self._values

    def validate(self):
        try:
            ConfigurationModel.model_validate(self.results)
        except ValidationError as e:
            typer.secho(
                f"The provided configuration contains {e.error_count()} validation errros",
                fg="red",
            )

            for error in e.errors():
                path = ".".join([str(i) for i in error["loc"]])
                typer.secho(f"  * {path}: {error['msg']}", fg="red")
            print()
            typer.secho(
                "Please run `rely environment configuration` for more information and diagnostics.",
                fg="red",
            )
            exit()
