import mm_print

from mm_okx.api.public import PublicClient


async def run(inst_type: str, proxy: str | None) -> None:
    client = PublicClient(proxy=proxy)
    res = await client.get_tickers_raw(inst_type)
    mm_print.json(res)
