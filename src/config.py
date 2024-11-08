import abc
from pathlib import Path
from typing import Annotated, ClassVar, Literal, List

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


class IncludeRule(BaseModel):
    rule: Literal["include"]
    select: list[str]


class ExcludeRule(BaseModel):
    rule: Literal["exclude"]
    select: list[str]


type FilterRule = Annotated[
    IncludeRule | ExcludeRule,
    Discriminator("rule"),
]


class NginxDeploymentConfig(BaseDeploymentConfig):
    worker_module: ClassVar[str] = "nginx_queue_worker"
    repository: Literal["ducompsoc/durhack-nginx"]
    sites: List[FilterRule]
    """Filter rules for configuration files from the ``production`` directory."""


class DurHackDeploymentConfig(BaseDeploymentConfig):
    worker_module: ClassVar[str] = "durhack_queue_worker"
    repository: Literal["ducompsoc/durhack"]


class GuildsDeploymentConfig(BaseDeploymentConfig):
    worker_module: ClassVar[str] = "guilds_queue_worker"
    repository: Literal["ducompsoc/durhack-guilds"]


class LiveDeploymentConfig(BaseDeploymentConfig):
    worker_module: ClassVar[str] = "live_queue_worker"
    repository: Literal["ducompsoc/durhack-live"]


class JuryDeploymentConfig(BaseDeploymentConfig):
    worker_module: ClassVar[str] = "jury_queue_worker"
    repository: Literal["ducompsoc/durhack-jury"]


class DeployerDeploymentConfig(BaseDeploymentConfig):
    worker_module: ClassVar[str] = "deployer_queue_worker"
    repository: Literal["ducompsoc/durhack-deployer"]


type DeploymentConfig = Annotated[
    NginxDeploymentConfig
    | DurHackDeploymentConfig
    | GuildsDeploymentConfig
    | LiveDeploymentConfig
    | JuryDeploymentConfig
    | DeployerDeploymentConfig,
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
