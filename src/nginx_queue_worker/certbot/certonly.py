from logging import Logger, getLogger

from util import async_subprocess


async def certonly(
    site_name: str,
    domains: list[str],
    logger: Logger | None = None,
) -> None:
    logger = logger if logger is not None else getLogger(__name__)

    domain_args = " ".join(f"-d '{domain}'" for domain in domains)

    result = await async_subprocess.run(
        f"sudo certbot --non-interactive --nginx --cert-name '{site_name}' {domain_args} --renew-with-new-domains certonly"
    )

    if result.exit_code == 0:
        return

    raise Exception(f"`certbot --cert-name '{site_name}' certonly` exited with status {result.exit_code}; {result.stderr}")
