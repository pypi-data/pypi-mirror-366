from typing import Any

import tomlkit


def toml_loads(string: str | bytes) -> dict[str, Any]:
    return tomlkit.loads(string)
