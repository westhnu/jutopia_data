# collectors.py
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import FinanceDataReader as fdr
from pykrx import stock as pystock
import requests
from dart_client import DartClient

OUT = Path("./processed"); OUT.mkdir(exist_ok=True)

def _save_csv(df: pd.DataFrame, name: str):
    p = OUT / name
    df.to_csv(p, index=False, encoding="utf-8")
    print("[CSV] saved:", p)
    return p

def collect_prices_daily(tickers: list[str], days: int = 120):
    for t in tickers:
        df = fdr.DataReader(t).reset_index().rename(columns={"Date":"timestamp"}).rename(columns=str.lower)
        cols = ["timestamp","open","high","low","close","volume","change"]
        df = df[[c for c in cols if c in df.columns]].tail(days).reset_index(drop=True)
        _save_csv(df, f"prices_{t}_{datetime.now():%Y%m%d}.csv")

def _yyyymmdd(d: datetime) -> str: return d.strftime("%Y%m%d")

def collect_index_daily(days: int = 180):
    for t in ["KS11","KQ11"]:
        df = fdr.DataReader(t).reset_index().rename(columns={"Date":"timestamp"}).rename(columns=str.lower)
        _save_csv(df.tail(days), f"index_{t}_{datetime.now():%Y%m%d}.csv")

def collect_dart_financials(dart_key: str, stock_code: str, year: int, reprt_code: str = "11011", fs_div: str = "CFS"):
    dart = DartClient(dart_key)
    corp = dart.get_corp_code(stock_code)
    if not corp:
        print("[DART] corp_code not found:", stock_code); return
    fin = dart.get_financials(corp, year, reprt_code, fs_div=fs_div)
    if fin is None or len(fin) == 0:
        print("[DART] empty financials"); return
    keep = ["bsns_year","reprt_code","sj_div","sj_nm","account_nm","thstrm_amount","frmtrm_amount"]
    fin = fin[[c for c in keep if c in fin.columns]]
    _save_csv(fin, f"financials_{stock_code}_{year}_{reprt_code}_{fs_div}.csv")

def collect_dart_filings_list(dart_key: str, stock_code: str, days: int = 30, page_count: int = 100):
    dart = DartClient(dart_key)
    corp = dart.get_corp_code(stock_code)
    if not corp:
        print("[DART] corp_code not found:", stock_code); return
    ed = datetime.today(); bd = ed - timedelta(days=days)
    url = "https://opendart.fss.or.kr/api/list.json"
    params = {
        "crtfc_key": dart_key, "corp_code": corp,
        "bgn_de": bd.strftime("%Y%m%d"), "end_de": ed.strftime("%Y%m%d"),
        "page_no": 1, "page_count": page_count,
    }
    res = requests.get(url, params=params, timeout=20).json()
    df = pd.DataFrame(res.get("list") or [])
    if df.empty:
        print("[DART] no filings"); return
    keep = ["rcp_no","rpt_nm","rcp_dt","corp_name","corp_code"]
    df = df[[c for c in keep if c in df.columns]]
    _save_csv(df, f"filings_{stock_code}_{bd:%Y%m%d}_{ed:%Y%m%d}.csv")
