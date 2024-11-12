import json
from logging import Logger, getLogger
from pathlib import Path

from pydantic import BaseModel

from config import config
from util import async_subprocess


class PM2App(BaseModel):
    name: str


class PM2Ecosystem(BaseModel):
    apps: list[PM2App]


async def read_config(
    ecosystem_file: Path,
    env: dict[str, str] | None = None,
    logger: Logger | None = None,
) -> PM2Ecosystem:
    logger = logger if logger is not None else getLogger(__name__)

    result = await async_subprocess.run(
        f"node --eval \"import('{ecosystem_file}').then((mod) => console.log(JSON.stringify(mod)))\"",
        env,
    )

    if result.exit_code > 0:
        raise Exception(f"`node ...` exited with status {result.exit_code}; {result.stderr}")

    module = json.loads(result.stdout)
    if not "default" in module:
        raise Exception(f"{ecosystem_file} is missing default export")

    raw_ecosystem = module["default"]
    if not isinstance(raw_ecosystem, dict):
        raise Exception(f"{ecosystem_file}'s default export is not a record-like object")

    ecosystem = PM2Ecosystem.model_validate(raw_ecosystem)
    return ecosystem
