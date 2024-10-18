from tomllib import load as load_toml
from pathlib import Path
from typing import Optional, TypedDict, Iterable
from os import getenv

from .types import Record
from .utils import deep_merge


type LoadConfigOptions = TypedDict("LoadConfigOptions", {
    "deployment_name": Optional[str]
}, total=False)


def find_potential_config_files(from_directory: Path) -> list[Path]:
    return list(from_directory.glob("*.toml"))


def get_allowed_filenames(deployment_name: str) -> list[str]:
    return [
        "default",
        deployment_name,
        "local",
        f"local-{deployment_name}",
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
        options = {
            "deployment_name": getenv("PYTHON_ENV") or "development"
        }
        
    potential_config_files = find_potential_config_files(from_directory)
    allowed_filenames = get_allowed_filenames(options["deployment_name"])
    config_files = filter_config_files(potential_config_files, allowed_filenames)
    config_files = sorted_config_files(config_files, allowed_filenames)
    
    return deep_merge(map(load_config_file, config_files))
