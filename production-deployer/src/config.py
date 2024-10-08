from pathlib import Path

from pydantic import BaseModel

from config_loader import load_config
from definitions import project_root_dir

class DeployerConfig(BaseModel):
    webhook_secret_token: str

untrusted_config = load_config(Path(project_root_dir, "config"))
config = DeployerConfig.model_validate(untrusted_config)
