import asyncio
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel
from typer import BadParameter, Context, Option, Typer

from mm_okx.api.account import AccountConfig
from mm_okx.cli import commands


def decimal_parser(value: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation:
        raise BadParameter(f"Invalid decimal: {value}") from None


app = Typer(no_args_is_help=True, help="Account API commands")
InstIdOption = Annotated[str, Option()]
SzOption = Annotated[Decimal, Option(parser=decimal_parser)]
AmtOption = Annotated[Decimal, Option(parser=decimal_parser)]
CcyOption = Annotated[str, Option()]
CcyOptionalOption = Annotated[str | None, Option()]


class BaseAccountParams(BaseModel):
    account: AccountConfig
    debug: bool

    @staticmethod
    def from_ctx(ctx: Context) -> "BaseAccountParams":
        debug = ctx.obj.get("debug", False)
        account = ctx.obj.get("account", False)
        return BaseAccountParams(account=AccountConfig.from_toml_file(account), debug=debug)


@app.command(name="buy-market")
def buy_market_command(ctx: Context, inst_id: InstIdOption, sz: SzOption) -> None:
    asyncio.run(commands.account.buy_market.run(BaseAccountParams.from_ctx(ctx), inst_id, sz))


@app.command(name="currencies")
def currencies_command(ctx: Context, ccy: CcyOptionalOption = None) -> None:
    asyncio.run(commands.account.currencies.run(BaseAccountParams.from_ctx(ctx), ccy))


@app.command(name="deposit-address")
def deposit_address_command(ctx: Context, ccy: CcyOption) -> None:
    asyncio.run(commands.account.deposit_address.run(BaseAccountParams.from_ctx(ctx), ccy))


@app.command(name="deposit-history")
def deposit_history_command(ctx: Context, ccy: CcyOptionalOption = None) -> None:
    asyncio.run(commands.account.deposit_history.run(BaseAccountParams.from_ctx(ctx), ccy))


@app.command(name="balances")
def balances_command(ctx: Context, ccy: CcyOptionalOption = None) -> None:
    asyncio.run(commands.account.balances.run(BaseAccountParams.from_ctx(ctx), ccy))


@app.command(name="funding-balances")
def funding_balances_command(ctx: Context, ccy: CcyOptionalOption = None) -> None:
    asyncio.run(commands.account.funding_balances.run(BaseAccountParams.from_ctx(ctx), ccy))


@app.command(name="order-history")
def order_history_command(ctx: Context, inst_id: Annotated[str | None, Option()] = None) -> None:
    asyncio.run(commands.account.order_history.run(BaseAccountParams.from_ctx(ctx), inst_id))


@app.command(name="sell-market")
def sell_market_command(ctx: Context, inst_id: InstIdOption, sz: SzOption) -> None:
    asyncio.run(commands.account.sell_market.run(BaseAccountParams.from_ctx(ctx), inst_id, sz))


@app.command(name="trading-balances")
def trading_balances_command(ctx: Context, ccy: CcyOptionalOption = None) -> None:
    asyncio.run(commands.account.trading_balances.run(BaseAccountParams.from_ctx(ctx), ccy))


@app.command(name="transfer-to-funding")
def transfer_to_funding_command(ctx: Context, ccy: CcyOption, amt: AmtOption) -> None:
    asyncio.run(commands.account.transfer_to_funding.run(BaseAccountParams.from_ctx(ctx), ccy, amt))


@app.command(name="transfer-to-trading")
def transfer_to_trading_command(ctx: Context, ccy: CcyOption, amt: AmtOption) -> None:
    asyncio.run(commands.account.transfer_to_trading.run(BaseAccountParams.from_ctx(ctx), ccy, amt))


@app.command(name="withdraw")
def withdraw_command(
    ctx: Context,
    ccy: CcyOption,
    amt: AmtOption,
    fee: Annotated[Decimal, Option(parser=decimal_parser)],
    to_addr: Annotated[str, Option()],
    chain: Annotated[str | None, Option()] = None,
) -> None:
    asyncio.run(
        commands.account.withdraw.run(
            params=BaseAccountParams.from_ctx(ctx), ccy=ccy, amt=amt, fee=fee, to_addr=to_addr, chain=chain
        )
    )


@app.command(name="withdraw-history")
def withdrawal_history_command(
    ctx: Context, ccy: CcyOptionalOption = None, wd_id: Annotated[str | None, Option()] = None
) -> None:
    asyncio.run(commands.account.withdrawal_history.run(BaseAccountParams.from_ctx(ctx), ccy, wd_id))


@app.callback()
def account_callback(ctx: Context, account: Annotated[Path, Option("--account", "-a", envvar="MM_OKX_ACCOUNT")]) -> None:
    ctx.obj["account"] = account
