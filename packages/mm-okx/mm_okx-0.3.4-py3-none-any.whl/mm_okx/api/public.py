from mm_http import http_request


class PublicClient:
    """
    Public data client, no auth required
    """

    def __init__(self, proxy: str | None = None) -> None:
        self.base_url = "https://www.okx.com"
        self.proxy = proxy

    async def get_instruments_raw(self, inst_type: str = "SPOT") -> object:
        url = f"{self.base_url}/api/v5/public/instruments?instType={inst_type}"
        return (await http_request(url, timeout=5, proxy=self.proxy)).parse_json_body()

    async def get_instrument_raw(self, inst_id: str, inst_type: str = "SPOT") -> object:
        url = f"{self.base_url}/api/v5/public/instruments?instId={inst_id}&instType={inst_type}"
        return (await http_request(url, timeout=5, proxy=self.proxy)).parse_json_body()

    async def get_tickers_raw(self, inst_type: str = "SPOT") -> object:
        url = f"{self.base_url}/api/v5/market/tickers?instType={inst_type}"
        return (await http_request(url, timeout=5, proxy=self.proxy)).parse_json_body()

    async def get_ticker_raw(self, inst_id: str) -> object:
        url = f"{self.base_url}/api/v5/market/ticker?instId={inst_id}"
        return (await http_request(url, timeout=5, proxy=self.proxy)).parse_json_body()
