from decimal import Decimal

import mm_print

from mm_okx.api.account import AccountClient
from mm_okx.cli.commands.account_commands import BaseAccountParams
from mm_okx.cli.utils import print_debug_or_error


async def run(*, params: BaseAccountParams, ccy: str, amt: Decimal, fee: Decimal, to_addr: str, chain: str | None) -> None:
    client = AccountClient(params.account)
    res = await client.withdraw(ccy=ccy, amt=amt, fee=fee, to_addr=to_addr, chain=chain)
    print_debug_or_error(res, params.debug)

    headers = ["ccy", "chain", "amt", "wd_id"]
    rows = [
        [
            t.ccy,
            t.chain,
            t.amt,
            t.wd_id,
        ]
        for t in res.unwrap()
    ]
    mm_print.table("Withdrawal", headers, rows)
