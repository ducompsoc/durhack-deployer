def ensure_cwd_is_none(cwd: str | None) -> None:
    if cwd is None: return
    raise ValueError("cwd must be None for pnpm commands: https://github.com/ducompsoc/durhack-deployer/issues/12")


def get_filter_options(filter_selector: str | None = None) -> str:
    return "" if filter_selector is None else f"--filter '{filter_selector}' --fail-if-no-match"
