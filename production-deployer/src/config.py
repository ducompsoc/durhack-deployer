from pathlib import Path

from pydantic import BaseModel, HttpUrl, PositiveInt, NonNegativeInt

from config_loader import load_config
from definitions import project_root_dir


class ProxyFixConfig(BaseModel):
    x_for: NonNegativeInt
    x_proto: NonNegativeInt


class ListenConfig(BaseModel):
    host: str
    port: PositiveInt


class DeployerConfig(BaseModel):
    listen: ListenConfig
    proxy_fix: ProxyFixConfig
    origin: HttpUrl
    webhook_secret_token: str


untrusted_config = load_config(Path(project_root_dir, "config"))
config = DeployerConfig.model_validate(untrusted_config)
