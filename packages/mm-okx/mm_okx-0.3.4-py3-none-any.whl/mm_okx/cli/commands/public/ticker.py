import mm_print

from mm_okx.api.public import PublicClient


async def run(inst_id: str, proxy: str | None) -> None:
    client = PublicClient(proxy=proxy)
    res = await client.get_ticker_raw(inst_id)
    mm_print.json(res)
