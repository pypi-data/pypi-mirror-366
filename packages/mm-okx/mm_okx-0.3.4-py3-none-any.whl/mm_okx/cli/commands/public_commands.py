import asyncio
from typing import Annotated

import typer

from mm_okx.cli import commands

# CLI parameter aliases using Annotated.
# Typer does not yet support `type Foo = Annotated[...]`, so assignment is used instead.
ProxyOption = Annotated[str | None, typer.Option("--proxy", "-p", help="Proxy")]
InstTypeOption = Annotated[str, typer.Option("--type", "-t", help="Instrument type")]
InstIdArgument = Annotated[str, typer.Argument(help="Instrument ID")]


app = typer.Typer(no_args_is_help=True, help="Public API commands")


@app.command(name="instruments", help="Get all instruments")
def instruments_command(
    inst_type: InstTypeOption = "SPOT",
    proxy: ProxyOption = None,
) -> None:
    asyncio.run(commands.public.instruments.run(inst_type, proxy))


@app.command(name="instrument", help="Get instrument")
def instrument_command(
    inst_id: InstIdArgument,
    inst_type: InstTypeOption = "SPOT",
    proxy: ProxyOption = None,
) -> None:
    asyncio.run(commands.public.instrument.run(inst_id, inst_type, proxy))


@app.command(name="tickers", help="Get all tickers")
def tickers_command(
    inst_type: InstTypeOption = "SPOT",
    proxy: ProxyOption = None,
) -> None:
    asyncio.run(commands.public.tickers.run(inst_type, proxy))


@app.command(name="ticker", help="Get ticker")
def ticker_command(
    inst_id: InstIdArgument,
    proxy: ProxyOption = None,
) -> None:
    asyncio.run(commands.public.ticker.run(inst_id, proxy))
