from dataclasses import dataclass, field
from tomllib import load as load_toml
from pathlib import Path
from typing import Iterable
from os import getenv

from .types import Record
from .utils import deep_merge


def _resolve_deployment_name() -> str:
    return getenv("PYTHON_ENV") or "development"

def _resolve_instance_name() -> str | None:
    return getenv("PYTHON_APP_INSTANCE") or None


@dataclass
class LoadConfigOptions:
    deployment_name: str = field(default_factory=_resolve_deployment_name)
    instance_name: str | None = field(default_factory=_resolve_instance_name)


def find_potential_config_files(from_directory: Path) -> list[Path]:
    return list(from_directory.glob("*.toml"))


def get_allowed_filenames(options: LoadConfigOptions) -> list[str]:
    if options.instance_name is None:
        return [
            "default",
            options.deployment_name,
            "local",
            f"local-{options.deployment_name}",
        ]

    return [
        "default",
        options.deployment_name,
        options.instance_name,
        f"{options.deployment_name}-{options.instance_name}",
        "local",
        f"local-{options.deployment_name}",
        f"local-{options.instance_name}",
        f"local-{options.deployment_name}-{options.instance_name}",
    ]


def filter_config_files(config_files: Iterable[Path], allowed_filenames: list[str]) -> Iterable[Path]:
    def config_file_is_valid(config_file: Path) -> bool:
        return config_file.stem in allowed_filenames

    return filter(config_file_is_valid, config_files)


def sorted_config_files(config_files: Iterable[Path], allowed_filenames: list[str]) -> list[Path]:
    def config_file_preference_key(config_file: Path) -> int:
        return allowed_filenames.index(config_file.stem)

    return sorted(config_files, key=config_file_preference_key)


def load_config_file(from_config_file: Path) -> Record:
    with open(from_config_file, "rb") as from_config_file_handle:
        return load_toml(from_config_file_handle)


def load_config(from_directory: Path, options: LoadConfigOptions = None) -> Record:
    from_directory = from_directory.resolve()
    if not from_directory.exists():
        raise FileNotFoundError
    if not from_directory.is_dir():
        raise NotADirectoryError

    if options is None:
        options = LoadConfigOptions()

    potential_config_files = find_potential_config_files(from_directory)
    allowed_filenames = get_allowed_filenames(options)
    config_files = filter_config_files(potential_config_files, allowed_filenames)
    config_files = sorted_config_files(config_files, allowed_filenames)

    return deep_merge(map(load_config_file, config_files))
