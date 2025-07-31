from .BaseClient import OkxBaseClient
from ..constants import *


class GridTradingClient(OkxBaseClient):
    def __init__(
        self,
        apikey: str = "",
        apisecret: str = "",
        passphrase: str = "",
        use_server_time: bool = False,
        simulation: bool = False,
        domain: str = API_URL,
        debug: bool = False,
        proxy: dict | None = None,
    ):
        OkxBaseClient.__init__(
            self,
            apikey,
            apisecret,
            passphrase,
            use_server_time,
            simulation,
            domain,
            debug,
            proxy,
        )

    def place_order(
        self,
        instId: str,
        algoOrdType: str,
        maxPx: float,
        minPx: float,
        gridNum: int,
        runType: str = "",
        tpTriggerPx: str = "",
        slTriggerPx: str = "",
        tag: str = BROKER_ID,
        profitSharingRatio: float | None = None,
        triggerParams: dict | None = None,
        quoteSz: str = "",
        baseSz: str = "",
        sz: str = "",
        direction: str = "",
        lever: str = "",
        basePos: str = "",
        tpRatio: str = "",
        slRatio: str = "",
    ) -> dict:
        params = {
            "instId": instId,
            "algoOrdType": algoOrdType,
            "maxPx": maxPx,
            "minPx": minPx,
            "gridNum": gridNum,
            "runType": runType,
            "tpTriggerPx": tpTriggerPx,
            "slTriggerPx": slTriggerPx,
            "tag": tag,
            "profitSharingRatio": profitSharingRatio,
            "triggerParams": triggerParams,
            "quoteSz": quoteSz,
            "baseSz": baseSz,
            "sz": sz,
            "direction": direction,
            "lever": lever,
            "basePos": basePos,
            "tpRatio": tpRatio,
            "slRatio": slRatio,
        }
        return self._request(POST, GRID_ORDER_ALGO, params)

    def amend_order(
        self, algoId: str, instId: str, slTriggerPx: str = "", tpTriggerPx: str = ""
    ) -> dict:
        params = {
            "algoId": algoId,
            "instId": instId,
            "slTriggerPx": slTriggerPx,
            "tpTriggerPx": tpTriggerPx,
        }
        return self._request(POST, GRID_AMEND_ORDER_ALGO, params)

    def stop_order(
        self, algoId: str, instId: str, algoOrdType: str, stopType: str
    ) -> dict:
        params = [
            {
                "algoId": algoId,
                "instId": instId,
                "algoOrdType": algoOrdType,
                "stopType": stopType,
            }
        ]
        return self._request(POST, GRID_STOP_ORDER_ALGO, params)

    def close_position(
        self, algoId: str, mktClose: bool, sz: str = "", px: str = ""
    ) -> dict:
        params = [{"algoId": algoId, "mktClose": mktClose, "sz": sz, "px": px}]
        return self._request(POST, GRID_CLOSE_POSITION, params)

    def cancel_close_position_order(self, algoId: str, ordId: str) -> dict:
        params = [{"algoId": algoId, "ordId": ordId}]
        return self._request(POST, GRID_CANCEL_CLOSE_ORDER, params)

    def get_pending_orders(
        self,
        algoOrdType: str = "",
        algoId: str = "",
        instId: str = "",
        instType: str = "",
        after: str = "",
        before: str = "",
        limit: str = "",
        instFamily: str = "",
    ) -> dict:
        params = {
            "algoOrdType": algoOrdType,
            "algoId": algoId,
            "instId": instId,
            "instType": instType,
            "after": after,
            "before": before,
            "limit": limit,
            "instFamily": instFamily,
        }
        return self._request(GET, GRID_ORDERS_ALGO_PENDING, params)

    def get_orders_history(
        self,
        algoOrdType: str = "",
        algoId: str = "",
        instId: str = "",
        instType: str = "",
        after: str = "",
        before: str = "",
        limit: str = "",
        instFamily: str = "",
    ) -> dict:
        params = {
            "algoOrdType": algoOrdType,
            "algoId": algoId,
            "instId": instId,
            "instType": instType,
            "after": after,
            "before": before,
            "limit": limit,
            "instFamily": instFamily,
        }
        return self._request(GET, GRID_ORDERS_ALGO_HISTORY, params)

    def get_orders_details(self, algoOrdType: str = "", algoId: str = "") -> dict:
        params = {"algoOrdType": algoOrdType, "algoId": algoId}
        return self._request(GET, GRID_ORDERS_ALGO_DETAILS, params)

    def get_sub_orders(
        self,
        algoId: str = "",
        algoOrdType: str = "",
        type: str = "",
        groupId: str = "",
        after: str = "",
        before: str = "",
        limit: str = "",
    ) -> dict:
        params = {
            "algoId": algoId,
            "algoOrdType": algoOrdType,
            "type": type,
            "groupId": groupId,
            "after": after,
            "before": before,
            "limit": limit,
        }
        return self._request(GET, GRID_SUB_ORDERS, params)

    def get_positions(self, algoOrdType: str = "", algoId: str = "") -> dict:
        params = {"algoOrdType": algoOrdType, "algoId": algoId}
        return self._request(GET, GRID_POSITIONS, params)

    def withdraw_income(self, algoId: str = "") -> dict:
        params = {"algoId": algoId}
        return self._request(POST, GRID_WITHDRAW_INCOME, params)

    def compute_margin_balance(
        self, algoId: str = "", type: str = "", amt: str = ""
    ) -> dict:
        params = {"algoId": algoId, "type": type, "amt": amt}
        return self._request(POST, GRID_COMPUTE_MARGIN_BALANCE, params)

    def adjust_margin_balance(
        self, algoId: str = "", type: str = "", amt: str = "", percent: str = ""
    ) -> dict:
        params = {"algoId": algoId, "type": type, "amt": amt, "percent": percent}
        return self._request(POST, GRID_MARGIN_BALANCE, params)

    def get_ai_param(
        self,
        algoOrdType: str = "",
        instId: str = "",
        direction: str = "",
        duration: str = "",
    ) -> dict:
        params = {
            "algoOrdType": algoOrdType,
            "instId": instId,
            "direction": direction,
            "duration": duration,
        }
        return self._request(GET, GRID_AI_PARAM, params)

    def compute_min_investment(
        self,
        instId: str,
        algoOrdType: str,
        maxPx: float,
        minPx: float,
        gridNum: int,
        runType: str,
        direction: str = "",
        lever: str = "",
        basePos: str = "",
        investmentData: list = [],
    ) -> dict:
        params = {
            "instId": instId,
            "algoOrdType": algoOrdType,
            "maxPx": maxPx,
            "minPx": minPx,
            "gridNum": gridNum,
            "runType": runType,
            "direction": direction,
            "lever": lever,
            "basePos": basePos,
            "investmentData": investmentData,
        }
        return self._request(POST, GRID_MIN_INVESTMENT, params)

    def get_rsi_back_testing(
        self,
        instId: str,
        timeframe: str,
        thold: float,
        timePeriod: int,
        triggerCond: str = "",
        duration: str = "",
    ) -> dict:
        params = {
            "instId": instId,
            "timeframe": timeframe,
            "thold": thold,
            "timePeriod": timePeriod,
            "triggerCond": triggerCond,
            "duration": duration,
        }
        return self._request(GET, GRID_AI_PARAM, params)
