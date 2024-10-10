from ipaddress import IPv4Network, IPv6Network, ip_network, IPv4Address, IPv6Address
from typing import TypedDict

from aiohttp import ClientResponse
from aiohttp_client_cache import CachedSession, CacheBackend
from werkzeug.exceptions import Forbidden

from config import config

cache = CacheBackend(cache_control=True)

type Network = list[IPv4Network | IPv6Network]

type GitHubMetaResponseBody = TypedDict("GitHubMetaResponse", {
    'hooks': list[str]
})


async def fetch_github_meta() -> ClientResponse:
    async with CachedSession(cache=cache) as session:
        async with session.get(
            "https://api.github.com/meta", 
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
        ) as response:
            return response


github_hooks_network: Network | None = None
github_meta_etag: str | None = None


async def get_github_hooks_network() -> Network:
    global github_hooks_network
    global github_meta_etag

    response = await fetch_github_meta()
    if github_meta_etag == response.headers.get("ETag"):
        return github_hooks_network

    body: GitHubMetaResponseBody = await response.json()
    github_hooks_network = [ip_network(address) for address in body["hooks"]]
    github_meta_etag = response.headers.get("ETag")
    return github_hooks_network


async def ensure_ip_is_github_hooks_ip(ip: IPv4Address | IPv6Address) -> None:
    network = await get_github_hooks_network()
    if any(map(lambda x: ip in x, network)):
        return
    raise Forbidden()
