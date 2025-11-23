import os
import pandas as pd
import time
import requests
import json
from datetime import datetime

try:
    import FinanceDataReader as fdr
except Exception:
    fdr = None

try:
    from pykrx import stock as pystock
except Exception:
    pystock = None

from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

# .env 로드 (현재 작업 디렉토리 기준)
load_dotenv()


class HantuStock:
    def __init__(
        self,
        api_key: str | None = None,
        secret_key: str | None = None,
        account_id: str | None = None,
        *,
        env: str | None = None,
    ):
        """
        env: "prod"(실전) | "vps"(모의)
        - 인자를 생략하면 .env 값을 사용함
          KIS_APP_KEY, KIS_APP_SECRET, KIS_ACCOUNT_ID, KIS_ACCOUNT_SUFFIX(optional), KIS_ENV(optional)
        """
        self._api_key = api_key or os.getenv("KIS_APP_KEY", "").strip()
        self._secret_key = secret_key or os.getenv("KIS_APP_SECRET", "").strip()
        self._account_id = account_id or os.getenv("KIS_ACCOUNT_ID", "").strip()
        self._account_suffix = os.getenv("KIS_ACCOUNT_SUFFIX", "01").s1trip() or "01"

        _env = (env or os.getenv("KIS_ENV", "prod")).strip().lower()
        if _env not in {"prod", "vps", "paper", "demo", "sandbox", "vts"}:
            raise ValueError("env must be one of {'prod','vps'}; alias {'paper','demo','sandbox'} allowed")
        # alias 처리
        self._env = "vps" if _env in {"vps", "paper", "demo", "sandbox", "vts"} else "prod"

        # 필수값 검증
        missing = [k for k, v in {
            "KIS_APP_KEY": self._api_key,
            "KIS_APP_SECRET": self._secret_key,
            "KIS_ACCOUNT_ID": self._account_id,
        }.items() if not v]
        if missing:
            raise ValueError(
                "Missing credentials: " + ", ".join(missing) +
                ". Set them in .env or pass them to HantuStock(...)."
            )

        self._base_url = (
            "https://openapi.koreainvestment.com:9443"
            if self._env == "prod"
            else "https://openapivts.koreainvestment.com:29443"
        )
        self._access_token = self._get_access_token()

    # -------------------- 내부 공통 --------------------
    def _tr(self, key: str) -> str:
        prefix = "TTTC" if self._env == "prod" else "VTTC"
        codes = {
            "inquire-balance": "8434R",
            "order-buy": "0012U",
            "order-sell": "0011U",
        }
        return prefix + codes[key]

    def _get_access_token(self) -> str:
        token_path = "/oauth2/token" if self._env == "prod" else "/oauth2/tokenP"
        url = self._base_url + token_path
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self._api_key,
            "appsecret": self._secret_key,
        }
        backoff = 0.5
        for attempt in range(6):
            try:
                res = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
                data = res.json()
                if "access_token" in data:
                    return data["access_token"]
                # error message
                print(f"[WARN] token error: {data}")
            except Exception as e:
                print(f"[ERROR] get_access_token: {e}")
            time.sleep(backoff)
            backoff = min(backoff * 2, 5.0)
        raise RuntimeError("Failed to get access token after retries")

    def _header(self, tr_id: str) -> dict:
        return {
            "content-type": "application/json",
            "appkey": self._api_key,
            "appsecret": self._secret_key,
            "authorization": f"Bearer {self._access_token}",
            "tr_id": tr_id,
        }


    def _request(self, url: str, headers: dict, params: dict, *, method: str = "get"):
        backoff = 0.5
        for attempt in range(6):
            try:
                if method == "get":
                    resp = requests.get(url, headers=headers, params=params, timeout=30)
                else:
                    resp = requests.post(url, headers=headers, data=json.dumps(params), timeout=30)
                r_headers = resp.headers
                data = resp.json()
                if data.get("rt_cd") != "0":
                    # 과호출 제한 등 재시도 케이스
                    if data.get("msg_cd") in {"EGW00201", "EGW00123"}:  # throttling 등
                        time.sleep(backoff)
                        backoff = min(backoff * 2, 5.0)
                        continue
                return r_headers, data
            except requests.exceptions.ConnectTimeout:
                print(f"[WARN] connect timeout, retry {attempt+1}")
            except requests.exceptions.ReadTimeout:
                print(f"[WARN] read timeout, retry {attempt+1}")
            except Exception as e:
                print(f"[WARN] request error: {e}, retry {attempt+1}")
            time.sleep(backoff)
            backoff = min(backoff * 2, 5.0)
        return {}, {"rt_cd": "1", "msg1": "request failed after retries"}

    # -------------------- 시세 --------------------
    @staticmethod
    def get_past_data(ticker: str, days: int = 100):
        if fdr is None:
            raise ImportError("FinanceDataReader not installed")
        df = fdr.DataReader(ticker)
        df.columns = [c.lower() for c in df.columns]
        df.index.name = "timestamp"
        df = df.reset_index()
        return df.iloc[-1] if days == 1 else df.tail(days)

    @staticmethod
    def get_past_data_total(days: int = 10):
        if pystock is None:
            raise ImportError("pykrx not installed")
        total = None
        got = 0
        passed = 0
        today = datetime.now()
        while (got < days) and passed < max(10, days * 2):
            d = str(today - relativedelta(days=passed)).split(" ")[0]
            k1 = pystock.get_market_ohlcv(d, market="KOSPI")
            k2 = pystock.get_market_ohlcv(d, market="KOSDAQ")
            data = pd.concat([k1, k2])
            passed += 1
            if data["거래대금"].sum() == 0:
                continue
            got += 1
            data.columns = ["open", "high", "low", "close", "volume", "trade_amount", "diff"]
            data.index.name = "ticker"
            data["timestamp"] = d
            total = data.copy() if total is None else pd.concat([total, data])
        total = total.sort_values("timestamp").reset_index()
        for col in ["open", "high", "low"]:
            total[col] = total[col].where(total[col] > 0, other=total["close"])
        return total

    # -------------------- 계좌 --------------------
    def _inquire_balance_raw(self, *, account_info=False):
        headers = self._header(self._tr("inquire-balance"))
        out = []
        cont = True
        fk100 = ""
        nk100 = ""
        while cont:
            params = {
                "CANO": self._account_id,
                "ACNT_PRDT_CD": self._account_suffix,
                "AFHR_FLPR_YN": "N",
                "OFL_YN": "N",
                "INQR_DVSN": "01",
                "UNPR_DVSN": "01",
                "FUND_STTL_ICLD_YN": "N",
                "FNCG_AMT_AUTO_RDPT_YN": "N",
                "PRCS_DVSN": "01",
                "CTX_AREA_FK100": fk100,
                "CTX_AREA_NK100": nk100,
            }
            url = self._base_url + "/uapi/domestic-stock/v1/trading/inquire-balance"
            hd, res = self._request(url, headers, params)
            if account_info:
                return res.get("output2", [{}])[0]
            cont = hd.get("tr_cont") in {"F", "M"}
            headers["tr_cont"] = "N"
            fk100 = res.get("ctx_area_fk100", "")
            nk100 = res.get("ctx_area_nk100", "")
            out += res.get("output1", [])
        return out

    def get_holding_stock(self, ticker: str | None = None, *, remove_stock_warrant: bool = True):
        """보유 종목 조회 (간단한 dict 반환)"""
        rows = self._inquire_balance_raw(account_info=False)
        if ticker is not None:
            for r in rows:
                if r.get("pdno") == ticker:
                    return int(r.get("hldg_qty", 0))
            return 0
        res = {}
        for r in rows:
            tkr = r.get("pdno", "")
            if remove_stock_warrant and tkr.startswith("J"):
                continue
            res[tkr] = int(r.get("hldg_qty", 0))
        return res

    def get_holding_stock_detail(self, *, remove_stock_warrant: bool = True):
        """보유 종목 상세 정보 조회 (평가액, 매입가, 손익 포함)

        Returns:
            list[dict]: 보유 종목 상세 정보 리스트
                - pdno: 종목코드
                - prdt_name: 종목명
                - hldg_qty: 보유수량
                - pchs_avg_prc: 매입평균가
                - prpr: 현재가
                - evlu_amt: 평가금액
                - evlu_pfls_amt: 평가손익금액
                - evlu_pfls_rt: 평가손익률
        """
        rows = self._inquire_balance_raw(account_info=False)
        result = []
        for r in rows:
            tkr = r.get("pdno", "")
            if remove_stock_warrant and tkr.startswith("J"):
                continue

            # 수량이 0인 종목 제외
            qty = int(r.get("hldg_qty", 0))
            if qty == 0:
                continue

            result.append({
                "pdno": tkr,
                "prdt_name": r.get("prdt_name", ""),
                "hldg_qty": qty,
                "pchs_avg_prc": float(r.get("pchs_avg_prc", 0)),
                "prpr": float(r.get("prpr", 0)),
                "evlu_amt": float(r.get("evlu_amt", 0)),
                "evlu_pfls_amt": float(r.get("evlu_pfls_amt", 0)),
                "evlu_pfls_rt": float(r.get("evlu_pfls_rt", 0)),
            })
        return result

    def get_holding_cash(self) -> float:
        info = self._inquire_balance_raw(account_info=True)
        try:
            return float(info.get("prvs_rcdl_excc_amt", 0))
        except Exception:
            return 0.0

    # -------------------- 주문 --------------------
    def bid(self, ticker: str, price, quantity, quantity_scale: str):
        if price in {"market", "", 0}:
            ord_unpr = "0"  # 시장가
            ord_dvsn = "01"
            if str(quantity_scale).upper() == "CASH":
                if fdr is None:
                    raise ImportError("FinanceDataReader not installed")
                px = self.get_past_data(ticker).iloc[-1]["close"]
        else:
            px = price
            ord_unpr = str(price)
            ord_dvsn = "00"
        scale = str(quantity_scale).upper()
        if scale == "CASH":
            qty = int(float(quantity) / float(px))
        elif scale == "STOCK":
            qty = int(quantity)
        else:
            print("[ERROR] quantity_scale should be CASH or STOCK")
            return None, 0
        headers = self._header(self._tr("order-buy"))
        params = {
            "CANO": self._account_id,
            "ACNT_PRDT_CD": self._account_suffix,
            "PDNO": ticker,
            "ORD_DVSN": ord_dvsn,
            "ORD_QTY": str(qty),
            "ORD_UNPR": ord_unpr,
        }
        url = self._base_url + "/uapi/domestic-stock/v1/trading/order-cash"
        _, data = self._request(url, headers, params, method="post")
        if data.get("rt_cd") == "0":
            return data.get("output", {}).get("ODNO"), qty
        print(data.get("msg1"))
        return None, 0

    def ask(self, ticker: str, price, quantity, quantity_scale: str):
        if price in {"market", "", 0}:
            ord_unpr = "0"
            ord_dvsn = "01"
            if str(quantity_scale).upper() == "CASH":
                if fdr is None:
                    raise ImportError("FinanceDataReader not installed")
                px = self.get_past_data(ticker).iloc[-1]["close"]
        else:
            px = price
            ord_unpr = str(price)
            ord_dvsn = "00"
        scale = str(quantity_scale).upper()
        if scale == "CASH":
            qty = int(float(quantity) / float(px))
        elif scale == "STOCK":
            qty = int(quantity)
        else:
            print("[ERROR] quantity_scale should be CASH or STOCK")
            return None, 0
        headers = self._header(self._tr("order-sell"))
        params = {
            "CANO": self._account_id,
            "ACNT_PRDT_CD": self._account_suffix,
            "PDNO": ticker,
            "ORD_DVSN": ord_dvsn,
            "ORD_QTY": str(qty),
            "ORD_UNPR": ord_unpr,
        }
        url = self._base_url + "/uapi/domestic-stock/v1/trading/order-cash"
        _, data = self._request(url, headers, params, method="post")
        if data.get("rt_cd") == "0":
            od = data.get("output", {}).get("ODNO")
            if od is None:
                print("[ERROR] ask: ", data.get("msg1"))
                return None, 0
            return od, qty
        print(data.get("msg1"))
        return None, 0


if __name__ == "__main__":
    # .env 기반 기본 실행 (모의: KIS_ENV=vps, 실전: KIS_ENV=prod)
    try:
        h = HantuStock()
        print("현금:", h.get_holding_cash())
        print("보유종목:", h.get_holding_stock())
        # 간단 주문 테스트 (시장가, 1주)
        # od_buy, q1 = h.bid("005930", "market", 1, "STOCK")
        # print("매수주문:", od_buy, q1)
        # od_sell, q2 = h.ask("005930", "market", 1, "STOCK")
        # print("매도주문:", od_sell, q2)
    except Exception as e:
        print("[MAIN]", e)
