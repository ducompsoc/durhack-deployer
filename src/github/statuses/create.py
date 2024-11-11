from dataclasses import dataclass
from logging import Logger, getLogger
from pathlib import Path
from typing import Literal, Optional

from util import async_subprocess


@dataclass
class CommitStatus:
    context: str
    state: Literal["error", "failure", "pending", "success"]
    target_url: Optional[str] = None
    description: Optional[str] = None

    def build_gh_cli_args(self) -> str:
        args = [
            f'-f "state={self.state}"',
            f'-f "context={self.context}"',
        ]

        if self.target_url is not None:
            args.append(f'-f "target_url={self.target_url}"')

        if self.description is not None:
            args.append(f'-f "description={self.description}"')

        return " ".join(args)


async def create(
    repository_full_name: Path,
    commit_hash: str,
    status: CommitStatus,
    logger: Logger | None = None,
) -> None:
    logger = logger if logger is not None else getLogger(__name__)

    result = await async_subprocess.run(
        f"""gh api \
        --method POST \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        /repos/{repository_full_name}/statuses/{commit_hash} \
        {status.build_gh_cli_args()}
        """
    )

    if result.exit_code == 0:
        return

    raise Exception(f"`gh api --method POST /repos/{repository_full_name}/statuses/{commit_hash} ...` exited with status {result.exit_code}; {result.stderr}")
