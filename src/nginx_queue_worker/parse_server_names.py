from pathlib import Path

import crossplane

from util.crossplane_types import CrossplaneParseResult, CrossplaneDirectiveParseResult


def parse_server_names(site_file_path: Path) -> list[str]:
    """Retrieve the arguments given to the ``server_name`` directive from an nginx configuration file."""

    parse_result: CrossplaneParseResult = crossplane.parse(str(site_file_path), check_ctx=False, single=True)
    assert parse_result.get("status") == "ok"
    assert len(parse_result.get("config")) == 1
    directives = parse_result["config"][0]["parsed"]
    server_directive: CrossplaneDirectiveParseResult | None = next(
        (directive for directive in directives if directive["directive"] == "server"),
        None,
    )
    assert server_directive is not None
    assert server_directive.get("block") is not None
    server_name_directive: CrossplaneDirectiveParseResult | None = next(
        (directive for directive in server_directive["block"] if directive["directive"] == "server_name"),
        None,
    )
    assert server_name_directive is not None
    server_names = server_name_directive["args"]
    return server_names
