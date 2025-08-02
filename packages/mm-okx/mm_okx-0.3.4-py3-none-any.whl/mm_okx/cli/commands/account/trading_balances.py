import mm_print

from mm_okx.api.account import AccountClient
from mm_okx.cli.commands.account_commands import BaseAccountParams
from mm_okx.cli.utils import print_debug_or_error


async def run(params: BaseAccountParams, ccy: str | None) -> None:
    client = AccountClient(params.account)
    res = await client.get_trading_balances(ccy)
    print_debug_or_error(res, params.debug)

    headers = ["ccy", "avail", "frozen"]
    rows = [[b.ccy, b.avail, b.frozen] for b in res.unwrap()]
    mm_print.table("Trading Balances", headers, rows)
