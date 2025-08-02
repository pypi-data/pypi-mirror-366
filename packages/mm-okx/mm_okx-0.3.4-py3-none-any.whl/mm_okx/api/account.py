import base64
import hmac
import json
import logging
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Self, cast
from urllib.parse import urlencode

from mm_http import http_request
from mm_result import Result
from mm_std import replace_empty_dict_entries
from pydantic import BaseModel, Field

from mm_okx.utils import toml_loads

type JsonType = dict[str, Any]


logger = logging.getLogger(__name__)


class Currency(BaseModel):
    ccy: str
    chain: str
    can_dep: bool = Field(..., alias="canDep")
    can_wd: bool = Field(..., alias="canWd")
    max_fee: Decimal = Field(..., alias="maxFee")
    min_fee: Decimal = Field(..., alias="minFee")
    max_wd: Decimal = Field(..., alias="maxWd")
    min_wd: Decimal = Field(..., alias="minWd")


class Balance(BaseModel):
    ccy: str
    avail: Decimal
    frozen: Decimal


class DepositAddress(BaseModel):
    ccy: str
    chain: str
    addr: str


class Withdrawal(BaseModel):
    ccy: str
    chain: str
    amt: Decimal
    wd_id: str = Field(..., alias="wdId")


class WithdrawalHistory(BaseModel):
    wd_id: str = Field(..., alias="wdId")
    chain: str
    ccy: str
    amt: Decimal
    fee: Decimal
    state: int
    tx_id: str = Field(..., alias="txId")
    to: str
    ts: int


class DepositHistory(BaseModel):
    dep_id: str = Field(..., alias="depId")
    ccy: str
    chain: str
    to: str
    amt: Decimal
    ts: int
    tx_id: str = Field(..., alias="txId")
    state: int
    actual_dep_blk_confirm: int = Field(..., alias="actualDepBlkConfirm")


class Transfer(BaseModel):
    trans_id: str = Field(..., alias="transId")
    ccy: str
    client_id: str = Field(..., alias="clientId")
    from_: str = Field(..., alias="from")
    amt: str
    to: str


class AccountConfig(BaseModel):
    name: str
    api_key: str
    secret_key: str
    passphrase: str
    proxy: str | None = None

    @classmethod
    def from_toml_file(cls, path: Path) -> Self:
        """
        Load the configuration from a TOML file.
        """

        config = toml_loads(path.read_text())
        return cls(**config)


class AccountClient:
    def __init__(self, config: AccountConfig) -> None:
        self.name = config.name
        self.api_key = config.api_key
        self.passphrase = config.passphrase
        self.secret_key = config.secret_key
        self.proxy = config.proxy
        self.base_url = "https://www.okx.com"

    async def get_currencies(self, ccy: str | None = None) -> Result[list[Currency]]:
        res = None
        try:
            params = {"ccy": ccy} if ccy else None
            res = await self._send_get("/api/v5/asset/currencies", params)
            if res.is_err():
                return Result.err(res.unwrap_err(), res.extra)
            return Result.ok([Currency(**c) for c in res.unwrap()["data"]], {"response": res.to_dict()})
        except Exception as e:
            return Result.err(e, {"response": res.to_dict() if res else None})

    async def get_funding_balances(self, ccy: str | None = None) -> Result[list[Balance]]:
        res = None
        try:
            params = {"ccy": ccy} if ccy else None
            res = await self._send_get("/api/v5/asset/balances", params)
            if res.is_err():
                return Result.err(res.unwrap_err(), res.extra)
            balances = [
                Balance(ccy=item["ccy"], avail=item["availBal"], frozen=item["frozenBal"]) for item in res.unwrap()["data"]
            ]
            return Result.ok(balances, {"response": res.to_dict()})
        except Exception as e:
            return Result.err(e, {"response": res.to_dict() if res else None})

    async def get_trading_balances(self, ccy: str | None = None) -> Result[list[Balance]]:
        res = None
        try:
            params = {"ccy": ccy} if ccy else None
            res = await self._send_get("/api/v5/account/balance", params)
            if res.is_err():
                return Result.err(res.unwrap_err(), res.extra)
            balances = [
                Balance(ccy=i["ccy"], avail=i["availBal"], frozen=i["frozenBal"]) for i in res.unwrap()["data"][0]["details"]
            ]
            return Result.ok(balances, {"response": res.to_dict()})
        except Exception as e:
            return Result.err(e, {"response": res.to_dict() if res else None})

    async def get_deposit_address(self, ccy: str) -> Result[list[DepositAddress]]:
        res = None
        try:
            res = await self._send_get("/api/v5/asset/deposit-address", {"ccy": ccy})
            if res.is_err():
                return Result.err(res.unwrap_err(), res.extra)
            return Result.ok([DepositAddress(**a) for a in res.unwrap()["data"]], {"response": res.to_dict()})
        except Exception as e:
            return Result.err(e, {"response": res.to_dict() if res else None})

    async def get_deposit_history(self, ccy: str | None = None) -> Result[list[DepositHistory]]:
        res = None
        try:
            params = replace_empty_dict_entries({"ccy": ccy})
            res = await self._send_get("/api/v5/asset/deposit-history", params)
            if res.is_err():
                return Result.err(res.unwrap_err(), res.extra)
            return Result.ok([DepositHistory(**d) for d in res.unwrap()["data"]], {"response": res.to_dict()})
        except Exception as e:
            return Result.err(e, {"response": res.to_dict() if res else None})

    async def get_withdrawal_history(self, ccy: str | None = None, wd_id: str | None = None) -> Result[list[WithdrawalHistory]]:
        res = None
        try:
            params = replace_empty_dict_entries({"ccy": ccy, "wdId": wd_id})
            res = await self._send_get("/api/v5/asset/withdrawal-history", params)
            if res.is_err():
                return Result.err(res.unwrap_err(), res.extra)
            return Result.ok([WithdrawalHistory(**h) for h in res.unwrap()["data"]], {"response": res.to_dict()})
        except Exception as e:
            return Result.err(e, {"response": res.to_dict() if res else None})

    async def withdraw(
        self, *, ccy: str, amt: Decimal, fee: Decimal, to_addr: str, chain: str | None = None
    ) -> Result[list[Withdrawal]]:
        res = None
        params = {"ccy": ccy, "amt": str(amt), "dest": "4", "toAddr": to_addr, "fee": str(fee), "chain": chain}
        try:
            res = await self._send_post("/api/v5/asset/withdrawal", params)
            if res.is_err():
                return Result.err(res.unwrap_err(), res.extra)
            result = [Withdrawal(**w) for w in res.unwrap()["data"]]
            if result:
                return Result.ok(result, {"response": res.to_dict()})
            # if res.get("code") == "58207":
            #     return Result.err("withdrawal_address_not_whitelisted", {"response": res})
            return Result.err("error", {"response": res.to_dict()})
        except Exception as e:
            return Result.err(e, {"response": res.to_dict() if res else None})

    async def transfer_to_funding(self, ccy: str, amt: Decimal) -> Result[list[Transfer]]:
        res = None
        try:
            res = await self._send_post(
                "/api/v5/asset/transfer", {"ccy": ccy, "amt": str(amt), "from": "18", "to": "6", "type": "0"}
            )
            if res.is_err():
                return Result.err(res.unwrap_err(), res.extra)
            return Result.ok([Transfer(**t) for t in res.unwrap()["data"]], {"response": res.to_dict()})
        except Exception as e:
            return Result.err(e, {"response": res.to_dict() if res else None})

    async def transfer_to_trading(self, ccy: str, amt: Decimal) -> Result[list[Transfer]]:
        res = None
        try:
            res = await self._send_post(
                "/api/v5/asset/transfer", {"ccy": ccy, "amt": str(amt), "from": "6", "to": "18", "type": "0"}
            )
            if res.is_err():
                return Result.err(res.unwrap_err(), res.extra)
            return Result.ok([Transfer(**t) for t in res.unwrap()["data"]], {"response": res.to_dict()})
        except Exception as e:
            return Result.err(e, {"response": res.to_dict() if res else None})

    async def transfer_to_parent(self, ccy: str, amount: Decimal) -> Result[list[Transfer]]:
        # type = 3: sub-account to master account (Only applicable to APIKey from sub-account)
        res = None
        try:
            res = await self._send_post(
                "/api/v5/asset/transfer", {"ccy": ccy, "amt": str(amount), "from": "6", "to": "6", "type": "3"}
            )
            if res.is_err():
                return Result.err(res.unwrap_err(), res.extra)
            return Result.ok([Transfer(**t) for t in res.unwrap()["data"]], {"response": res.to_dict()})
        except Exception as e:
            return Result.err(e, {"response": res.to_dict() if res else None})

    async def buy_market(self, inst_id: str, sz: Decimal) -> Result[str]:
        """
        Place a market order, side=buy
        :param inst_id: for example, ETH-USDT
        :param sz: for example, Decimal("100.0"), buy 100 USDT worth of ETH
        """
        res = None
        params = {"instId": inst_id, "tdMode": "cash", "side": "buy", "ordType": "market", "sz": str(sz)}
        try:
            res = await self._send_post("/api/v5/trade/order", params)
            if res.is_err():
                return Result.err(res.unwrap_err(), res.extra)
            return Result.ok(res.unwrap()["data"][0]["ordId"], {"response": res.to_dict()})
        except Exception as e:
            return Result.err(e, {"response": res.to_dict() if res else None})

    async def sell_market(self, inst_id: str, sz: Decimal) -> Result[str]:
        """
        Place a market order, side=sell
        :param inst_id: for example, BTC-ETH
        :param sz: for example, Decimal("0.123")
        """
        res = None
        params = {"instId": inst_id, "tdMode": "cash", "side": "sell", "ordType": "market", "sz": str(sz)}
        try:
            res = await self._send_post("/api/v5/trade/order", params)
            if res.is_err():
                return Result.err(res.unwrap_err(), res.extra)
            return Result.ok(res.unwrap()["data"][0]["ordId"], {"response": res.to_dict()})
        except Exception as e:
            return Result.err(e, {"response": res.to_dict() if res else None})

    async def get_order_history(self, inst_id: str | None = None) -> Result[JsonType]:
        url = "/api/v5/trade/orders-history-archive?instType=SPOT"
        if inst_id:
            url += f"&instId={inst_id}"
        return await self._request("GET", url)

    async def _send_get(self, request_path: str, query_params: dict[str, Any] | None = None) -> Result[JsonType]:
        return await self._request("GET", request_path, query_params=query_params)

    async def _send_post(self, request_path: str, body: dict[str, Any] | str = "") -> Result[JsonType]:
        return await self._request("POST", request_path, body=body)

    async def _request(
        self, method: str, request_path: str, *, body: dict[str, Any] | str = "", query_params: dict[str, object] | None = None
    ) -> Result[JsonType]:
        logger.debug(
            "request", extra={"method": method, "request_path": request_path, "body": body, "query_params": query_params}
        )
        method = method.upper()
        if method == "GET" and query_params:
            request_path = add_query_params_to_url(request_path, query_params)
        timestamp = get_timestamp()
        message = pre_hash(timestamp, method, request_path, body)
        signature = sign(message, self.secret_key)
        headers = {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature.decode(),
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
        }
        params = None
        if isinstance(body, dict):
            params = body
        res = await http_request(self.base_url + request_path, method=method, json=params, headers=headers, proxy=self.proxy)
        if res.is_err():
            return res.to_result_err()

        json_body = res.parse_json_body()
        if json_body.get("code") != "0":
            error_msg = f"{json_body.get('msg')}, code: {json_body.get('code')}"
            return Result.err(error_msg, {"response": res.to_dict()})

        return res.to_result_ok(cast(JsonType, json_body))


def pre_hash(timestamp: str, method: str, request_path: str, body: JsonType | str) -> str:
    if isinstance(body, dict):
        body = json.dumps(body)
    return timestamp + method.upper() + request_path + body


def sign(message: str, secret_key: str) -> bytes:
    mac = hmac.new(bytes(secret_key, encoding="utf8"), bytes(message, encoding="utf-8"), digestmod="sha256")
    d = mac.digest()
    return base64.b64encode(d)


def get_timestamp() -> str:
    return datetime.now(tz=UTC).isoformat(sep="T", timespec="milliseconds").removesuffix("+00:00") + "Z"


def add_query_params_to_url(url: str, params: dict[str, object]) -> str:
    return f"{url}?{urlencode(params)}" if params else url
