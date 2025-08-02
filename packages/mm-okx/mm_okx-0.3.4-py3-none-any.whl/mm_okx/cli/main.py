import importlib.metadata
from typing import Annotated

from click import get_current_context
from typer import Exit, Option, Typer, echo

from mm_okx.cli.commands import account_commands, public_commands
from mm_okx.logger import configure_debug_logging

app = Typer(no_args_is_help=True, pretty_exceptions_enable=False)


app.add_typer(public_commands.app, name="public")
app.add_typer(public_commands.app, name="p", hidden=True)


app.add_typer(account_commands.app, name="account")


app.add_typer(account_commands.app, name="a", hidden=True)


def version_callback(value: bool) -> None:
    if value:
        echo(f"mm-okx: {importlib.metadata.version('mm-okx')}")
        raise Exit


@app.callback()
def main(
    debug: Annotated[bool, Option("--debug", "-d", help="Debug mode")] = False,
    _version: Annotated[bool, Option("--version", "-v", callback=version_callback, is_eager=True)] = False,
) -> None:
    if debug:
        configure_debug_logging()

    ctx = get_current_context()
    ctx.obj = {"debug": debug}
