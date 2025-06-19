def get_filter_options(filter_selector: str | None = None) -> str:
    return "" if filter_selector is None else f"--filter '{filter_selector}'"
