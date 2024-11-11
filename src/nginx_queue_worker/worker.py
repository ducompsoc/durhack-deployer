import asyncio
import re
import shutil
from itertools import chain
from pathlib import Path
from typing import override, ClassVar

from config import NginxDeploymentConfig
from data_types import GitHubEvent
from deployments import Deployment
import git
from filters import Filter
from github_payload_types import PushEvent
from json_serialization import durhack_deployer_json_load
from nginx_queue_worker.parse_server_names import parse_server_names
from github_repository_queue_worker import GitHubRepositoryQueueWorker
from storage import persisted_event_exists, persist_handled_event

from . import certbot
from . import systemctl


class NginxQueueWorker(GitHubRepositoryQueueWorker):
    def __init__(self, deployment: Deployment[NginxDeploymentConfig], *args, **kwargs):
        super().__init__(deployment.queue, deployment.config.repository, *args, **kwargs)
        self.deploy_lock = asyncio.Lock()
        self.config = deployment.config
        self.site_filter = Filter(self.config.sites)

    @staticmethod
    def has_production_changes(diff: git.FileTreeDiff) -> bool:
        for path in chain(diff.added, diff.removed, diff.modified):
            if path.startswith("production/"):
                return True

        return False

    site_file_name_pattern: ClassVar[re.Pattern] = re.compile("^\\[(?P<site_name>.*)\\]\\.conf(?:\\.disabled)?$")

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
    async def process_github_event(self, event: GitHubEvent) -> None:
        assert event.type == "push"
        payload: PushEvent = event.payload

        async with self.deploy_lock:
            if await persisted_event_exists(event):
                # log a message saying we are ignoring an event as it was previously processed
                return

            await git.fetch(self.config.path, self._logger)
            file_tree_diff = await git.diff(self.config.path, "HEAD", payload["head_commit"]["id"])
            await git.checkout(self.config.path, payload["head_commit"]["id"])
            await self.link_added_snippets(file_tree_diff)
            if not self.has_production_changes(file_tree_diff):
                await self.unlink_removed_snippets(file_tree_diff)
                await systemctl.reload("nginx")
                await persist_handled_event(event)
                return

            await self.acquire_or_renew_certificates(file_tree_diff)
            await self.deploy_added_and_modified_files(file_tree_diff)
            await self.unlink_removed_snippets(file_tree_diff)
            await self.deploy_removed_files(file_tree_diff)
            await systemctl.reload("nginx")

            await persist_handled_event(event)

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
