import re
import shutil
from itertools import chain
from pathlib import Path
from typing import override, ClassVar

from shell import certbot, git, systemctl
from shell.git import FileTreeDiff
from config import NginxDeploymentConfig
from deployments import Deployment
from filters import Filter
from github_payload_types import PushEvent
from github_repository_queue_worker import GitHubRepositoryQueueWorker

from .parse_server_names import parse_server_names


class NginxQueueWorker(GitHubRepositoryQueueWorker):
    def __init__(self, deployment: Deployment[NginxDeploymentConfig], *args, **kwargs):
        super().__init__(deployment, *args, **kwargs)
        self.site_filter = Filter(self.config.sites)

    @staticmethod
    def has_production_changes(diff: git.FileTreeDiff) -> bool:
        for path in chain(diff.added, diff.removed, diff.modified):
            if path.startswith("production/"):
                return True

        return False

    site_file_name_pattern: ClassVar[re.Pattern] = re.compile("^\\[(?P<site_name>.*)\\]\\.(?:nginx)?conf(?:\\.disabled)?$")

    @classmethod
    def is_site_file(cls, path: Path) -> bool:
        name = path.name
        return cls.site_file_name_pattern.match(name) is not None

    @classmethod
    def get_site_file_site_name(cls, path: Path) -> str | None:
        name = path.name
        match = cls.site_file_name_pattern.match(name)
        if match is None:
            return None
        return match.group("site_name")

    @override
    async def on_push(self, payload: PushEvent) -> None:
        diff = await self.checkout(payload["head_commit"]["id"])
        await self.deploy(diff)

    async def on_init(self) -> None:
        empty_tree_ref = await git.hash_object(self.config.path, Path("/dev/null"), object_type="tree", logger=self._logger)
        diff = await git.diff(self.config.path, empty_tree_ref, "HEAD", logger=self._logger)
        await self.deploy(diff)

    async def deploy(self, diff: FileTreeDiff) -> None:
        await self.link_added_snippets(diff)
        if not self.has_production_changes(diff):
            await self.unlink_removed_snippets(diff)
            await systemctl.reload("nginx")
            return

        await self.acquire_or_renew_certificates(diff)
        await self.deploy_added_and_modified_files(diff)
        await self.unlink_removed_snippets(diff)
        await self.deploy_removed_files(diff)
        await systemctl.reload("nginx")

    async def link_added_snippets(self, diff: git.FileTreeDiff) -> None:
        for path in diff.added:
            if not path.startswith("snippets/"):
                continue
            target = Path(self.config.path, path)
            link_name = Path("/", "etc", "nginx", "snippets", target.relative_to(Path(self.config.path, "snippets")))
            if link_name.exists(follow_symlinks=False):
                assert link_name.readlink() == target
                return
            link_name.symlink_to(target)

    async def unlink_removed_snippets(self, diff: git.FileTreeDiff) -> None:
        for path in diff.removed:
            if not path.startswith("snippets/"):
                continue
            target = Path(self.config.path, path)
            link_name = Path("/", "etc", "nginx", "snippets", target.relative_to(Path(self.config.path, "snippets")))
            if not link_name.is_symlink():
                return
            if not link_name.readlink() == target:
                return
            link_name.unlink()

    async def acquire_or_renew_certificate(self, site_file_path: Path) -> None:
        site_name = self.get_site_file_site_name(site_file_path)
        domain_names = parse_server_names(site_file_path)
        await certbot.certonly(site_name, domain_names, logger=self._logger)

    async def acquire_or_renew_certificates(self, diff: git.FileTreeDiff) -> None:
        for path in chain(diff.added, diff.modified):
            if not path.startswith("production/"):
                continue
            if path.endswith(".disabled"):
                continue
            source = Path(self.config.path, path)
            site_name = self.get_site_file_site_name(source)
            if site_name is None:
                continue
            if not self.site_filter.matches(site_name):
                continue
            await self.acquire_or_renew_certificate(source)

    async def deploy_added_and_modified_files(self, diff: git.FileTreeDiff) -> None:
        for path in chain(diff.added, diff.modified):
            if not path.startswith("production/"):
                continue

            source = Path(self.config.path, path)
            site_name = self.get_site_file_site_name(source)
            if site_name is not None and not self.site_filter.matches(site_name):
                continue

            destination = Path(self.config.path, "local-live", source.relative_to(Path(self.config.path, "production")))
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)

            target = destination
            link_name = Path("/", "etc", "nginx", "conf.d", target.relative_to(Path(self.config.path, "local-live")))
            if link_name.exists(follow_symlinks=False):
                assert link_name.readlink() == target
                continue
            link_name.symlink_to(target)

    async def deploy_removed_files(self, diff: git.FileTreeDiff) -> None:
        for path in diff.removed:
            if not path.startswith("production/"):
                continue
            source = Path(self.config.path, path)
            destination = Path(self.config.path, "local-live", source.relative_to(Path(self.config.path, "production")))
            if not destination.exists():
                continue

            destination.unlink()

            target = destination
            link_name = Path("/", "etc", "nginx", "conf.d", target.relative_to(Path(self.config.path, "local-live")))
            if not link_name.is_symlink():
                return
            if not link_name.readlink() == target:
                return
            link_name.unlink()
