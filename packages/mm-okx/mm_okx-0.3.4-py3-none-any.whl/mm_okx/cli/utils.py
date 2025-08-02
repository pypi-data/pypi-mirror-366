from datetime import UTC, datetime
from typing import Any

import mm_print
from click.exceptions import Exit
from mm_result import Result


def print_debug_or_error(res: Result[Any], debug: bool) -> None:
    if debug:
        mm_print.json(res)
        raise Exit

    if res.is_err():
        mm_print.fatal(res.unwrap_err())


def format_ts(ts: int) -> str:
    return datetime.fromtimestamp(ts / 1000, tz=UTC).strftime("%Y-%m-%d %H:%M:%S")
