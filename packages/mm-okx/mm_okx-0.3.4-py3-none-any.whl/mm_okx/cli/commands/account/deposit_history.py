import mm_print

from mm_okx.api.account import AccountClient
from mm_okx.cli.commands.account_commands import BaseAccountParams
from mm_okx.cli.utils import format_ts, print_debug_or_error


async def run(params: BaseAccountParams, ccy: str | None) -> None:
    client = AccountClient(params.account)
    res = await client.get_deposit_history(ccy)
    print_debug_or_error(res, params.debug)

    headers = ["dep_id", "ccy", "chain", "to", "amt", "ts", "tx_id", "state", "blk_confirm"]
    rows = [
        [
            a.dep_id,
            a.ccy,
            a.chain,
            a.to,
            a.amt,
            format_ts(a.ts),
            a.tx_id,
            a.state,
            a.actual_dep_blk_confirm,
        ]
        for a in res.unwrap()
    ]
    mm_print.table("Deposit History", headers, rows)
