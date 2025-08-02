import mm_print

from mm_okx.api.account import AccountClient
from mm_okx.cli.commands.account_commands import BaseAccountParams
from mm_okx.cli.utils import print_debug_or_error


async def run(params: BaseAccountParams, inst_id: str | None) -> None:
    client = AccountClient(params.account)
    res = await client.get_order_history(inst_id)
    print_debug_or_error(res, params.debug)

    mm_print.json(res)
