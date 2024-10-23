import abc
from pathlib import Path
from typing import Annotated, Literal, Never

from pydantic import (
    BaseModel,
    HttpUrl,
    PositiveInt,
    NonNegativeInt,
    Discriminator,
)

from config_loader import load_config
from definitions import project_root_dir


class ProxyFixConfig(BaseModel):
    x_for: NonNegativeInt
    x_proto: NonNegativeInt


class ListenConfig(BaseModel):
    host: str
    port: PositiveInt


class BaseDeploymentConfig(BaseModel, abc.ABC):
    repository: str
    enabled: bool
    branch: str
    path: Path


class NginxDeploymentConfig(BaseDeploymentConfig):
    repository: Literal["ducompsoc/durhack-nginx"]


class DurHackDeploymentConfig(BaseDeploymentConfig):
    repository: Literal["ducompsoc/durhack"]


class GuildsDeploymentConfig(BaseDeploymentConfig):
    repository: Literal["ducompsoc/durhack-guilds"]


class LiveDeploymentConfig(BaseDeploymentConfig):
    repository: Literal["ducompsoc/durhack-live"]


class JuryDeploymentConfig(BaseDeploymentConfig):
    repository: Literal["ducompsoc/durhack-jury"]


type DeploymentConfig = Annotated[
    NginxDeploymentConfig
    | DurHackDeploymentConfig
    | GuildsDeploymentConfig
    | LiveDeploymentConfig
    | JuryDeploymentConfig,
    Discriminator("repository"),
]


class DeployerConfig(BaseModel):
    listen: ListenConfig
    proxy_fix: ProxyFixConfig
    origin: HttpUrl
    webhook_secret_token: str
    deployments: dict[str, DeploymentConfig]


untrusted_config = load_config(Path(project_root_dir, "config"))
config = DeployerConfig.model_validate(untrusted_config)

if __name__ == "__main__":
    print(config.model_dump_json(indent=2))
