import mm_print

from mm_okx.api.account import AccountClient
from mm_okx.cli.commands.account_commands import BaseAccountParams
from mm_okx.cli.utils import format_ts, print_debug_or_error


async def run(params: BaseAccountParams, ccy: str | None, wd_id: str | None) -> None:
    client = AccountClient(params.account)
    res = await client.get_withdrawal_history(ccy=ccy, wd_id=wd_id)
    print_debug_or_error(res, params.debug)

    headers = ["wd_id", "chain", "ccy", "amt", "fee", "state", "tx_id", "to", "ts"]
    rows = [
        [
            t.wd_id,
            t.chain,
            t.ccy,
            t.amt,
            t.fee,
            t.state,
            t.tx_id,
            t.to,
            format_ts(t.ts),
        ]
        for t in res.unwrap()
    ]
    mm_print.table("Withdrawal History", headers, rows)
