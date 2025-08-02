import mm_print

from mm_okx.api.account import AccountClient
from mm_okx.cli.commands.account_commands import BaseAccountParams
from mm_okx.cli.utils import print_debug_or_error


async def run(params: BaseAccountParams, ccy: str) -> None:
    client = AccountClient(params.account)
    res = await client.get_deposit_address(ccy)
    print_debug_or_error(res, params.debug)

    headers = ["ccy", "chain", "address"]

    rows = [[a.ccy, a.chain, a.addr] for a in res.unwrap()]

    mm_print.table(title="Deposit Address", columns=headers, rows=rows)
