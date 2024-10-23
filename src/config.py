import abc
from pathlib import Path
from typing import Annotated, Literal

from pydantic import (
    AnyUrl,
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


type DeploymentConfig = Annotated[
    NginxDeploymentConfig | DurHackDeploymentConfig,
    Discriminator("repository"),
]


class DeployerConfig(BaseModel):
    listen: ListenConfig
    proxy_fix: ProxyFixConfig
    origin: HttpUrl
    webhook_secret_token: str
    celery_task_broker_uri: AnyUrl
    deployments: dict[str, DeploymentConfig]


untrusted_config = load_config(Path(project_root_dir, "config"))
config = DeployerConfig.model_validate(untrusted_config)
