# main.py — Orchestrator: KIS + DART + FDR
from datetime import datetime
from pathlib import Path
import os, pandas as pd

from HantuStock import HantuStock
from dart_client import DartClient
from collectors import (
    collect_prices_daily, collect_index_daily,
    collect_dart_financials, collect_dart_filings_list
)

DIR_PROC = Path("./processed"); DIR_PROC.mkdir(exist_ok=True)

def _ensure_outdir(outdir="processed"):
    Path(outdir).mkdir(exist_ok=True); return outdir

def save_cash_csv(api: HantuStock, outdir="processed"):
    _ensure_outdir(outdir)
    try:
        cash = api.get_holding_cash()
        df = pd.DataFrame([{
            "asof": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cash": pd.to_numeric(cash, errors="ignore")
        }])
        fp = Path(outdir)/f"cash_{datetime.now():%Y%m%d}.csv"
        df.to_csv(fp, index=False, encoding="utf-8")
        print("[OK] cash saved ->", fp)
    except Exception as e:
        print("[WARN] cash save failed:", e)

def _rows_from_holdings(holdings):
    """
    holdings가
      - 리스트(원본 TR rows)면 그대로 표준화
      - dict(티커->수량)면 최소 컬럼으로 변환
    """
    if isinstance(holdings, list):
        # KIS 잔고조회 output1 포맷 가정
        rows = []
        for r in holdings:
            rows.append({
                "pdno": r.get("pdno"),
                "prdt_name": r.get("prdt_name"),
                "hldg_qty": r.get("hldg_qty"),
                "pchs_avg_prc": r.get("pchs_avg_prc"),
                "evlu_amt": r.get("evlu_amt"),
                "evlu_pfls_amt": r.get("evlu_pfls_amt"),
            })
        return rows
    elif isinstance(holdings, dict):
        # { "005930": 10, ... } → 최소 컬럼으로 변환
        return [{"pdno": k, "hldg_qty": v} for k, v in holdings.items()]
    else:
        return []

def save_holdings_csv(api: HantuStock, outdir="processed"):
    """보유 종목 상세 정보 저장 (평가액, 매입가, 손익 포함)"""
    _ensure_outdir(outdir)
    try:
        # 상세 정보 조회로 변경
        holdings_detail = api.get_holding_stock_detail()

        if not holdings_detail:
            # 보유 종목 없을 때
            df = pd.DataFrame(columns=[
                "pdno", "prdt_name", "hldg_qty", "pchs_avg_prc",
                "prpr", "evlu_amt", "evlu_pfls_amt", "evlu_pfls_rt"
            ])
        else:
            df = pd.DataFrame(holdings_detail)

        # 타임스탬프 추가
        df.insert(0, "asof", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        fp = Path(outdir)/f"holdings_{datetime.now():%Y%m%d}.csv"
        df.to_csv(fp, index=False, encoding="utf-8")
        print("[OK] holdings (detailed) saved ->", fp)
    except Exception as e:
        print("[WARN] holdings save failed:", e)

def main():
    # ---- ENV 로딩 (KIS는 HantuStock 내부에서 .env 자동 사용) ----
    DART_API_KEY = os.getenv("DART_API_KEY")
    TICKERS = [t.strip() for t in os.getenv("TICKERS","005930,000660,035420").split(",") if t.strip()]
    DAYS = int(os.getenv("DAYS","120"))

    # ---- KIS: 현금/보유 저장 ----
    try:
        api = HantuStock()  # 인자 없이 .env에서 KIS_APP_KEY/SECRET/ACCOUNT_ID/KIS_ENV 사용
        save_cash_csv(api, "processed")
        save_holdings_csv(api, "processed")
    except Exception as e:
        print("[WARN] KIS 초기화/저장 실패:", e)

    # ---- 시세/지수 ----
    try:
        collect_prices_daily(TICKERS, DAYS)
        print(f"[OK] prices saved for {TICKERS} (days={DAYS})")
        collect_index_daily(DAYS)
        print("[OK] index daily saved")
    except Exception as e:
        print("[WARN] FDR/pykrx collect 실패:", e)

    # ---- DART ----
    if DART_API_KEY:
        try:
            # 보유 종목 모두 재무제표 수집
            current_year = datetime.now().year
            # 11011: 사업보고서(연간), 11012: 반기, 11013: 1분기, 11014: 3분기
            report_types = os.getenv("DART_REPORT_TYPES", "11011").split(",")
            report_types = [r.strip() for r in report_types if r.strip()]

            for ticker in TICKERS:
                print(f"[DART] Collecting financials for {ticker}...")
                for reprt_code in report_types:
                    try:
                        collect_dart_financials(DART_API_KEY, ticker, current_year - 1, reprt_code, "CFS")
                    except Exception as e:
                        print(f"[WARN] DART financials failed for {ticker} ({reprt_code}): {e}")

                # 공시 목록 수집
                try:
                    collect_dart_filings_list(DART_API_KEY, ticker, 30)
                except Exception as e:
                    print(f"[WARN] DART filings failed for {ticker}: {e}")

            print("[OK] DART collection completed for all tickers")
        except Exception as e:
            print("[WARN] DART collect 실패:", e)
    else:
        print("[INFO] DART_API_KEY 미설정: DART 수집 스킵")

    print("[DONE] all tasks")

if __name__ == "__main__":
    main()
