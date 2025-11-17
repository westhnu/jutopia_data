# stock_analyzer.py - 주식 분석 엔진 (CSV + 실시간 API)
# -*- coding: utf-8 -*-
"""
CSV 파일 또는 실시간 API에서 데이터를 읽어 분석하는 클래스
- use_realtime=False: CSV 파일 사용 (기본)
- use_realtime=True: FinanceDataReader API로 실시간 데이터 수집
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Union

# 실시간 모드를 위한 import (없어도 CSV 모드는 작동)
try:
    import FinanceDataReader as fdr
    REALTIME_AVAILABLE = True
except ImportError:
    REALTIME_AVAILABLE = False


class StockAnalyzer:
    """주식 데이터 분석 엔진 (CSV + 실시간 API)"""

    def __init__(self, data_dir: str = "./processed", use_realtime: bool = False):
        """
        Args:
            data_dir: CSV 파일들이 저장된 폴더 경로
            use_realtime: True면 API로 실시간 데이터 수집, False면 CSV 사용
        """
        self.data_dir = Path(data_dir)
        self.use_realtime = use_realtime

        # 실시간 모드인데 FDR이 없으면 에러
        if use_realtime and not REALTIME_AVAILABLE:
            raise ImportError("실시간 모드를 사용하려면 FinanceDataReader를 설치하세요: pip install finance-datareader")

        # CSV 모드일 때만 폴더 체크
        if not use_realtime and not self.data_dir.exists():
            raise FileNotFoundError(f"데이터 폴더를 찾을 수 없습니다: {data_dir}")

        # 종목명 매핑 (확장 가능)
        self.stock_names = {
            '005930': '삼성전자',
            '000660': 'SK하이닉스',
            '035420': '네이버',
            '035720': '카카오',
            '051910': 'LG화학',
        }

    # ========================================================================
    # 데이터 로딩 메서드
    # ========================================================================

    def _get_latest_file(self, pattern: str) -> Optional[Path]:
        """패턴에 맞는 가장 최신 파일 반환"""
        files = sorted(self.data_dir.glob(pattern))
        return files[-1] if files else None

    def load_cash_balance(self) -> Dict:
        """최신 현금 잔고 로드"""
        file = self._get_latest_file("cash_*.csv")
        if not file:
            return {"error": "현금 잔고 파일을 찾을 수 없습니다"}

        df = pd.read_csv(file)
        return {
            "asof": df['asof'].iloc[0],
            "cash": float(df['cash'].iloc[0]),
            "file": file.name
        }

    def load_holdings(self) -> pd.DataFrame:
        """최신 보유 종목 로드"""
        file = self._get_latest_file("holdings_*.csv")
        if not file:
            return pd.DataFrame()

        return pd.read_csv(file)

    def load_price_data(self, ticker: str, days: Optional[int] = None) -> pd.DataFrame:
        """특정 종목의 가격 데이터 로드

        Args:
            ticker: 종목코드 (예: '005930')
            days: 최근 N일 데이터만 로드 (None이면 전체)
        """
        # 실시간 모드: API로 데이터 수집
        if self.use_realtime:
            try:
                # 종목명도 함께 조회하여 캐시에 저장
                if ticker not in self.stock_names:
                    self.get_stock_name(ticker)

                end_date = datetime.now()
                start_date = end_date - timedelta(days=days if days else 365)

                df = fdr.DataReader(ticker, start=start_date, end=end_date)
                if df.empty:
                    return pd.DataFrame()

                # 컬럼명 통일
                df = df.reset_index()
                df.columns = [col.lower() for col in df.columns]
                if 'date' in df.columns:
                    df = df.rename(columns={'date': 'timestamp'})

                required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df = df[required_columns]

                return df
            except Exception as e:
                print(f"❌ 실시간 데이터 수집 실패: {e}")
                return pd.DataFrame()

        # CSV 모드: 파일에서 읽기
        file = self._get_latest_file(f"prices_{ticker}_*.csv")
        if not file:
            return pd.DataFrame()

        df = pd.read_csv(file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        if days:
            df = df.tail(days).reset_index(drop=True)

        return df

    def load_index_data(self, index_code: str) -> pd.DataFrame:
        """시장 지수 데이터 로드

        Args:
            index_code: 지수 코드 ('KS11': 코스피, 'KQ11': 코스닥)
        """
        file = self._get_latest_file(f"index_{index_code}_*.csv")
        if not file:
            return pd.DataFrame()

        df = pd.read_csv(file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def load_financials(self, ticker: str, year: Optional[int] = None) -> pd.DataFrame:
        """재무제표 데이터 로드"""
        pattern = f"financials_{ticker}_{year}_*.csv" if year else f"financials_{ticker}_*.csv"
        file = self._get_latest_file(pattern)
        if not file:
            return pd.DataFrame()

        return pd.read_csv(file)

    # ========================================================================
    # 포트폴리오 분석
    # ========================================================================

    def get_portfolio_summary(self) -> Dict:
        """포트폴리오 전체 요약"""
        cash_info = self.load_cash_balance()
        holdings_df = self.load_holdings()

        if "error" in cash_info:
            return cash_info

        cash = cash_info["cash"]
        stock_value = 0
        holdings_detail = []

        for _, row in holdings_df.iterrows():
            ticker = row['pdno']
            qty = row['hldg_qty']

            # 최신 가격 조회
            price_df = self.load_price_data(ticker)
            if not price_df.empty:
                latest_price = price_df['close'].iloc[-1]
                value = latest_price * qty
                stock_value += value

                holdings_detail.append({
                    'ticker': ticker,
                    'name': self.stock_names.get(ticker, ticker),
                    'quantity': qty,
                    'price': latest_price,
                    'value': value
                })

        total_assets = cash + stock_value

        return {
            "asof": cash_info["asof"],
            "cash": cash,
            "stock_value": stock_value,
            "total_assets": total_assets,
            "cash_ratio": cash / total_assets * 100 if total_assets > 0 else 0,
            "stock_ratio": stock_value / total_assets * 100 if total_assets > 0 else 0,
            "holdings": holdings_detail
        }

    def get_portfolio_return(self, period_days: int = 30) -> Dict:
        """포트폴리오 수익률 계산

        Args:
            period_days: 수익률 계산 기간 (일)
        """
        holdings_df = self.load_holdings()
        if holdings_df.empty:
            return {"error": "보유 종목이 없습니다"}

        results = []
        for _, row in holdings_df.iterrows():
            ticker = row['pdno']
            qty = row['hldg_qty']

            price_df = self.load_price_data(ticker, days=period_days + 10)
            if len(price_df) < 2:
                continue

            current_price = price_df['close'].iloc[-1]

            # period_days 전 가격 (없으면 가장 오래된 가격)
            idx = min(len(price_df) - 1, period_days)
            past_price = price_df['close'].iloc[-idx-1] if idx < len(price_df) else price_df['close'].iloc[0]

            return_pct = (current_price - past_price) / past_price * 100
            profit = (current_price - past_price) * qty

            results.append({
                'ticker': ticker,
                'name': self.stock_names.get(ticker, ticker),
                'quantity': qty,
                'past_price': past_price,
                'current_price': current_price,
                'return_pct': return_pct,
                'profit': profit
            })

        total_profit = sum(r['profit'] for r in results)

        return {
            "period_days": period_days,
            "stocks": results,
            "total_profit": total_profit
        }

    # ========================================================================
    # 기술적 분석 지표 계산
    # ========================================================================

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI(상대강도지수) 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_moving_averages(self, prices: pd.Series, windows: List[int] = [5, 20, 60]) -> Dict:
        """이동평균선 계산"""
        mas = {}
        for w in windows:
            mas[f'MA{w}'] = prices.rolling(window=w).mean().iloc[-1]
        return mas

    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, num_std: int = 2) -> Dict:
        """볼린저 밴드 계산"""
        sma = prices.rolling(window=period).mean().iloc[-1]
        std = prices.rolling(window=period).std().iloc[-1]
        upper = sma + (std * num_std)
        lower = sma - (std * num_std)

        current_price = prices.iloc[-1]
        position = (current_price - lower) / (upper - lower) * 100 if upper != lower else 50

        return {
            'upper': upper,
            'middle': sma,
            'lower': lower,
            'position_pct': position
        }

    # ========================================================================
    # 종목별 분석
    # ========================================================================

    def analyze_stock_technical(self, ticker: str, indicators: List[str] = None) -> Dict:
        """특정 종목 기술적 분석

        Args:
            ticker: 종목코드
            indicators: 분석할 지표 리스트 ['RSI', 'MA', 'BB', 'VOLUME', '52WEEK']
                       None이면 전체 분석
        """
        if indicators is None:
            indicators = ['RSI', 'MA', 'BB', 'VOLUME', '52WEEK']

        df = self.load_price_data(ticker)
        if df.empty:
            return {"error": f"종목 {ticker} 데이터를 찾을 수 없습니다"}

        result = {
            "ticker": ticker,
            "name": self.stock_names.get(ticker, ticker),
            "current_price": float(df['close'].iloc[-1]),
            "timestamp": str(df['timestamp'].iloc[-1])
        }

        # RSI
        if 'RSI' in indicators:
            rsi_series = self.calculate_rsi(df['close'])
            rsi = float(rsi_series.iloc[-1])
            result['rsi'] = {
                'value': rsi,
                'signal': '과매수' if rsi > 70 else '과매도' if rsi < 30 else '중립'
            }

        # 이동평균선
        if 'MA' in indicators:
            mas = self.calculate_moving_averages(df['close'])
            result['moving_averages'] = mas

            # 추세 판단
            current = result['current_price']
            ma5 = mas.get('MA5', current)
            ma20 = mas.get('MA20', current)
            ma60 = mas.get('MA60', current)

            if current > ma5 > ma20 > ma60:
                trend = "강한 상승 추세 (정배열)"
            elif current < ma5 < ma20 < ma60:
                trend = "강한 하락 추세 (역배열)"
            elif current > ma20:
                trend = "상승 추세"
            else:
                trend = "하락 추세"

            result['trend'] = trend

        # 볼린저 밴드
        if 'BB' in indicators:
            bb = self.calculate_bollinger_bands(df['close'])
            result['bollinger_bands'] = bb

            if bb['position_pct'] > 80:
                result['bollinger_bands']['signal'] = '상단 근접 (과매수)'
            elif bb['position_pct'] < 20:
                result['bollinger_bands']['signal'] = '하단 근접 (과매도)'
            else:
                result['bollinger_bands']['signal'] = '중간 구간'

        # 거래량 분석
        if 'VOLUME' in indicators:
            recent_vol = df['volume'].iloc[-5:].mean()
            avg_vol = df['volume'].mean()
            vol_change = (recent_vol / avg_vol - 1) * 100

            result['volume'] = {
                'recent_5d_avg': float(recent_vol),
                'overall_avg': float(avg_vol),
                'change_pct': float(vol_change)
            }

        # 52주 고가/저가
        if '52WEEK' in indicators:
            high_52w = df['high'].max()
            low_52w = df['low'].min()
            current_pos = (result['current_price'] - low_52w) / (high_52w - low_52w) * 100

            result['52week'] = {
                'high': float(high_52w),
                'low': float(low_52w),
                'current_position_pct': float(current_pos)
            }

        return result

    def get_price_change(self, ticker: str, days: int = 5) -> Dict:
        """N일간 가격 변화율 조회"""
        df = self.load_price_data(ticker, days=days+5)
        if len(df) < 2:
            return {"error": "데이터 부족"}

        current = df['close'].iloc[-1]
        past = df['close'].iloc[-min(days+1, len(df)-1)]
        change_pct = (current - past) / past * 100

        return {
            "ticker": ticker,
            "name": self.stock_names.get(ticker, ticker),
            "period_days": days,
            "past_price": float(past),
            "current_price": float(current),
            "change_pct": float(change_pct),
            "change_amount": float(current - past)
        }

    # ========================================================================
    # 종목 비교 분석
    # ========================================================================

    def compare_stocks(self, tickers: List[str], metric: str = 'return', period: int = 30) -> Dict:
        """여러 종목 비교

        Args:
            tickers: 비교할 종목 리스트
            metric: 비교 지표 ('return', 'rsi', 'volume')
            period: 비교 기간 (일)
        """
        results = []

        for ticker in tickers:
            df = self.load_price_data(ticker, days=period+10)
            if df.empty:
                continue

            data = {
                'ticker': ticker,
                'name': self.stock_names.get(ticker, ticker),
                'current_price': float(df['close'].iloc[-1])
            }

            if metric == 'return':
                # 수익률 비교
                idx = min(len(df)-1, period)
                past = df['close'].iloc[-idx-1]
                change = (data['current_price'] - past) / past * 100
                data['return_pct'] = float(change)
                data['past_price'] = float(past)

            elif metric == 'rsi':
                # RSI 비교
                rsi = self.calculate_rsi(df['close']).iloc[-1]
                data['rsi'] = float(rsi)

            elif metric == 'volume':
                # 거래량 비교
                recent_vol = df['volume'].iloc[-5:].mean()
                avg_vol = df['volume'].mean()
                data['recent_volume'] = float(recent_vol)
                data['avg_volume'] = float(avg_vol)
                data['volume_change_pct'] = float((recent_vol / avg_vol - 1) * 100)

            results.append(data)

        return {
            "metric": metric,
            "period_days": period,
            "comparison": results
        }

    # ========================================================================
    # 재무 분석
    # ========================================================================

    def get_financial_ratios(self, ticker: str, year: Optional[int] = None) -> Dict:
        """재무비율 계산"""
        df = self.load_financials(ticker, year)
        if df.empty:
            return {"error": f"재무제표 데이터를 찾을 수 없습니다 (종목: {ticker})"}

        def get_value(account_name: str, sj_div: str = 'BS'):
            row = df[(df['account_nm'] == account_name) & (df['sj_div'] == sj_div)]
            if not row.empty:
                return float(row.iloc[0]['thstrm_amount'])
            return 0

        # 재무상태표 (BS)
        total_assets = get_value('자산총계')
        current_assets = get_value('유동자산')
        current_liabilities = get_value('유동부채')
        total_liabilities = get_value('부채총계')
        total_equity = get_value('자본총계')
        cash = get_value('현금및현금성자산')

        # 손익계산서 (IS)
        revenue = get_value('매출액', 'IS')
        operating_profit = get_value('영업이익', 'IS')
        net_income = get_value('당기순이익', 'IS')

        result = {
            "ticker": ticker,
            "name": self.stock_names.get(ticker, ticker),
            "balance_sheet": {
                "total_assets": total_assets,
                "current_assets": current_assets,
                "total_liabilities": total_liabilities,
                "current_liabilities": current_liabilities,
                "total_equity": total_equity,
                "cash": cash
            },
            "income_statement": {
                "revenue": revenue,
                "operating_profit": operating_profit,
                "net_income": net_income
            },
            "ratios": {}
        }

        # 재무비율 계산
        if current_liabilities > 0:
            result['ratios']['current_ratio'] = (current_assets / current_liabilities) * 100
            result['ratios']['cash_ratio'] = (cash / current_liabilities) * 100

        if total_equity > 0:
            result['ratios']['debt_ratio'] = (total_liabilities / total_equity) * 100
            result['ratios']['roe'] = (net_income / total_equity) * 100

        if total_assets > 0:
            result['ratios']['equity_ratio'] = (total_equity / total_assets) * 100

        if revenue > 0:
            result['ratios']['operating_margin'] = (operating_profit / revenue) * 100
            result['ratios']['net_margin'] = (net_income / revenue) * 100

        return result

    # ========================================================================
    # 시장 분석
    # ========================================================================

    def get_market_trend(self, index_code: str = 'KS11', period: int = 60) -> Dict:
        """시장 지수 추세 분석

        Args:
            index_code: 'KS11' (코스피) 또는 'KQ11' (코스닥)
            period: 분석 기간
        """
        df = self.load_index_data(index_code)
        if df.empty:
            return {"error": f"지수 데이터를 찾을 수 없습니다 ({index_code})"}

        df = df.tail(period)
        current = df['close'].iloc[-1]

        # 이동평균
        ma20 = df['close'].rolling(window=20).mean().iloc[-1]
        ma60 = df['close'].rolling(window=60).mean().iloc[-1] if len(df) >= 60 else None

        # 추세 판단
        if ma60 and current > ma20 > ma60:
            trend = "상승 추세"
        elif ma60 and current < ma20 < ma60:
            trend = "하락 추세"
        else:
            trend = "횡보"

        # 기간별 변화율
        changes = {}
        for days in [5, 20, 60]:
            if len(df) > days:
                past = df['close'].iloc[-days-1]
                changes[f'{days}d'] = float((current - past) / past * 100)

        return {
            "index_code": index_code,
            "index_name": "KOSPI" if index_code == "KS11" else "KOSDAQ",
            "current_value": float(current),
            "ma20": float(ma20),
            "ma60": float(ma60) if ma60 else None,
            "trend": trend,
            "changes": changes
        }

    # ========================================================================
    # 유틸리티 메서드
    # ========================================================================

    def get_available_stocks(self) -> List[str]:
        """분석 가능한 종목 리스트 반환"""
        # CSV 모드
        if not self.use_realtime:
            price_files = self.data_dir.glob("prices_*.csv")
            tickers = set()
            for f in price_files:
                # prices_005930_20251031.csv -> 005930 추출
                parts = f.stem.split('_')
                if len(parts) >= 2:
                    tickers.add(parts[1])
            return sorted(list(tickers))

        # 실시간 모드: 캐시된 종목만
        return sorted(list(self.stock_names.keys()))

    def get_stock_name(self, ticker: str) -> str:
        """종목코드 -> 종목명 변환"""
        # 캐시된 이름이 있으면 반환
        if ticker in self.stock_names:
            return self.stock_names[ticker]

        # 실시간 모드: API로 종목명 조회
        if self.use_realtime:
            try:
                stocks = fdr.StockListing('KRX')
                # Code 컬럼이 정확히 일치하는 종목 찾기
                stock = stocks[stocks['Code'] == ticker]

                if not stock.empty:
                    name = stock.iloc[0]['Name']
                    if name and isinstance(name, str) and name.strip():
                        self.stock_names[ticker] = name  # 캐시
                        return name

                # 종목을 찾지 못한 경우 로그 출력
                print(f"⚠️ 종목명을 찾을 수 없음: {ticker}")

            except Exception as e:
                print(f"⚠️ 종목명 조회 오류 ({ticker}): {e}")

        # CSV 모드이거나 API 조회 실패 시: 캐시에서 찾기
        return self.stock_names.get(ticker, ticker)

    def search_stock(self, keyword: str) -> List[Dict]:
        """
        종목 검색 (이름 또는 코드로)

        Args:
            keyword: 검색어 (예: "삼성", "005930")

        Returns:
            list: 검색 결과 [{'ticker': '005930', 'name': '삼성전자', 'market': 'KOSPI'}, ...]
        """
        # 실시간 모드만 지원
        if not self.use_realtime:
            return []

        try:
            # KRX 전체 종목 리스트
            stocks = fdr.StockListing('KRX')

            # 코드 또는 이름으로 검색
            results = stocks[
                (stocks['Code'].str.contains(keyword, na=False)) |
                (stocks['Name'].str.contains(keyword, na=False))
            ]

            # 결과 정리
            search_results = []
            for _, row in results.head(10).iterrows():  # 상위 10개만
                ticker = row['Code']
                name = row['Name']

                # 종목명 캐시에 저장
                if name and isinstance(name, str) and name.strip():
                    self.stock_names[ticker] = name

                search_results.append({
                    'ticker': ticker,
                    'name': name,
                    'market': row['Market']
                })

            return search_results

        except Exception as e:
            print(f"❌ 종목 검색 실패: {e}")
            return []


# ========================================================================
# 사용 예시
# ========================================================================

if __name__ == "__main__":
    analyzer = StockAnalyzer()

    print("=" * 80)
    print("StockAnalyzer 사용 예시")
    print("=" * 80)

    # 1. 포트폴리오 요약
    print("\n[1] 포트폴리오 요약")
    portfolio = analyzer.get_portfolio_summary()
    print(f"총 자산: {portfolio.get('total_assets', 0):,.0f}원")
    print(f"현금 비중: {portfolio.get('cash_ratio', 0):.1f}%")

    # 2. 삼성전자 기술적 분석
    print("\n[2] 삼성전자 기술적 분석")
    samsung = analyzer.analyze_stock_technical("005930", indicators=['RSI', 'MA'])
    print(f"현재가: {samsung.get('current_price', 0):,.0f}원")
    print(f"RSI: {samsung.get('rsi', {}).get('value', 0):.1f} ({samsung.get('rsi', {}).get('signal', '-')})")
    print(f"추세: {samsung.get('trend', '-')}")

    # 3. 종목 비교
    print("\n[3] 보유 종목 수익률 비교 (30일)")
    comparison = analyzer.compare_stocks(['005930', '000660', '035420'], metric='return', period=30)
    for stock in comparison.get('comparison', []):
        print(f"{stock['name']}: {stock.get('return_pct', 0):+.2f}%")

    # 4. 삼성전자 재무비율
    print("\n[4] 삼성전자 재무비율")
    financials = analyzer.get_financial_ratios("005930")
    ratios = financials.get('ratios', {})
    print(f"ROE: {ratios.get('roe', 0):.2f}%")
    print(f"부채비율: {ratios.get('debt_ratio', 0):.1f}%")
    print(f"유동비율: {ratios.get('current_ratio', 0):.1f}%")

    print("\n" + "=" * 80)
    print("분석 완료!")
    print("=" * 80)
