"""
밸류에이션 지표 계산 모듈
재무제표 DataFrame에서 PER, PBR, ROE 등을 계산
"""

from typing import Dict, Optional
import pandas as pd


class MetricsCalculator:
    """재무제표 기반 밸류에이션 지표 계산기"""

    @staticmethod
    def calculate_from_dataframe(df: pd.DataFrame, current_price: float) -> Optional[Dict]:
        """
        재무제표 DataFrame에서 밸류에이션 지표 계산

        Args:
            df: 재무제표 DataFrame (DART API 응답)
            current_price: 현재 주가

        Returns:
            dict: 계산된 지표들
            {
                'per': float,
                'pbr': float,
                'roe': float,
                'eps': int,
                'bps': int,
                'shares_outstanding': int,
                'dividend_yield': str,
                'dividend_per_share': str
            }
        """
        try:
            # 재무제표에서 핵심 값 추출
            net_income_parent = MetricsCalculator._extract_net_income(df)
            equity_parent = MetricsCalculator._extract_equity(df)
            eps = MetricsCalculator._extract_eps(df)

            if eps == 0:
                return None

            # 발행주식수 계산 (EPS로부터 역산)
            shares = net_income_parent / eps

            # 지표 계산
            metrics = {
                'shares_outstanding': int(shares),
                'eps': int(eps),
                'bps': int(equity_parent / shares) if shares > 0 else 0,
                'per': round(current_price / eps, 2) if eps > 0 else 0,
                'pbr': round(current_price / (equity_parent / shares), 2) if shares > 0 else 0,
                'roe': round((net_income_parent / equity_parent) * 100, 2) if equity_parent > 0 else 0,
                'dividend_yield': 'N/A',
                'dividend_per_share': 'N/A'
            }

            return metrics

        except Exception as e:
            import traceback
            print(f"  ❌ 지표 계산 실패: {e}")
            traceback.print_exc()
            return None

    @staticmethod
    def _extract_value(df: pd.DataFrame, account_name: str) -> float:
        """계정과목 값 추출"""
        row = df[df['account_nm'] == account_name]
        if row.empty:
            return 0
        try:
            return float(row.iloc[0]['thstrm_amount'])
        except:
            return 0

    @staticmethod
    def _extract_net_income(df: pd.DataFrame) -> float:
        """당기순이익 추출 (지배기업 소유주 귀속)"""
        # 우선순위 1: 지배기업의 소유주에게 귀속되는 당기순이익
        net_income = MetricsCalculator._extract_value(
            df, '지배기업의 소유주에게 귀속되는 당기순이익(손실)'
        )

        if net_income == 0:
            # 우선순위 2: 당기순이익
            net_income = MetricsCalculator._extract_value(df, '당기순이익(손실)')

        if net_income == 0:
            net_income = MetricsCalculator._extract_value(df, '당기순이익')

        return net_income

    @staticmethod
    def _extract_equity(df: pd.DataFrame) -> float:
        """자본총계 추출 (지배기업 소유주 귀속)"""
        # 우선순위 1: 지배기업의 소유주에게 귀속되는 자본
        equity = MetricsCalculator._extract_value(
            df, '지배기업의 소유주에게 귀속되는 자본'
        )

        if equity == 0:
            # 우선순위 2: 자본총계
            equity = MetricsCalculator._extract_value(df, '자본총계')

        return equity

    @staticmethod
    def _extract_eps(df: pd.DataFrame) -> float:
        """주당순이익(EPS) 추출"""
        eps_row = df[df['account_nm'].str.contains('기본주당순이익', na=False)]
        if not eps_row.empty:
            try:
                return float(eps_row.iloc[0]['thstrm_amount'])
            except:
                pass
        return 0


# ========================================
# 테스트 코드
# ========================================

if __name__ == "__main__":
    import sys
    import io
    from dart_client import DartClient
    import os
    from dotenv import load_dotenv

    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    load_dotenv()

    print("="*70)
    print("🧮 MetricsCalculator 테스트")
    print("="*70)
    print()

    # DART API로 재무제표 조회
    dart_key = os.environ.get("DART_API_KEY")
    dart_client = DartClient(api_key=dart_key)

    test_ticker = '005930'  # 삼성전자
    current_price = 96700

    print(f"📊 {test_ticker} 재무제표 조회 중...")
    corp_code = dart_client.get_corp_code(test_ticker)
    df = dart_client.get_financials(corp_code, 2023, "11011", "CFS")

    print(f"✅ {len(df)}개 계정과목 조회 완료\n")

    # 지표 계산
    print("📊 지표 계산 중...")
    try:
        calculator = MetricsCalculator()
        metrics = calculator.calculate_from_dataframe(df, current_price)

        if metrics:
            print("✅ 계산 완료!\n")
            print(f"발행주식수: {metrics['shares_outstanding']:,}주")
            print(f"EPS: {metrics['eps']:,}원")
            print(f"BPS: {metrics['bps']:,}원")
            print(f"PER: {metrics['per']}배")
            print(f"PBR: {metrics['pbr']}배")
            print(f"ROE: {metrics['roe']}%")
        else:
            print("❌ 계산 실패")
    except Exception as e:
        import traceback
        print(f"❌ 계산 실패: {e}")
        traceback.print_exc()

    print("\n" + "="*70)
    print("✅ 테스트 완료")
    print("="*70)
