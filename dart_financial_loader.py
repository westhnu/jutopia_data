"""
DART 재무제표 로딩 모듈
DART API를 통해 재무제표를 조회하고 텍스트로 변환
"""

from typing import Optional, Tuple
import pandas as pd
from dart_client import DartClient
from datetime import datetime


class DartFinancialLoader:
    """DART API를 통한 재무제표 로딩"""

    def __init__(self, dart_client: DartClient):
        self.dart_client = dart_client

    def load_financials(self, ticker: str) -> Tuple[Optional[str], Optional[pd.DataFrame]]:
        """
        재무제표 조회 및 텍스트 변환

        Args:
            ticker: 종목코드 (예: '005930')

        Returns:
            tuple: (financial_text, financial_df)
            - financial_text: 재무제표 텍스트 (없으면 None)
            - financial_df: 재무제표 DataFrame (없으면 None)
        """
        try:
            # Step 1: 종목코드 → 고유번호 변환
            corp_code = self.dart_client.get_corp_code(ticker)
            if not corp_code:
                print(f"  ❌ 종목코드 {ticker}에 대한 기업 고유번호를 찾을 수 없습니다")
                return None, None

            # Step 2: 최신 재무제표 조회
            # 현재 연도의 사업보고서는 다음 해 3월에 공시되므로 전년도 데이터 조회
            current_year = datetime.now().year
            year = current_year - 1 if datetime.now().month < 4 else current_year

            # 여러 보고서 유형 시도 (최신 데이터 우선)
            report_attempts = [
                (year, "11014", "3분기보고서"),      # 현재연도 3분기
                (year, "11012", "반기보고서"),       # 현재연도 반기
                (year - 1, "11011", "사업보고서"),  # 전년도 사업보고서
            ]

            df = None
            for attempt_year, reprt_code, report_name in report_attempts:
                try:
                    df = self.dart_client.get_financials(
                        corp_code=corp_code,
                        year=attempt_year,
                        reprt_code=reprt_code,
                        fs_div="CFS"  # 연결재무제표
                    )
                    if df is not None and not df.empty:
                        print(f"  ✅ {attempt_year}년 {report_name} 조회 성공")
                        break
                except:
                    continue

            if df is None or df.empty:
                print(f"  ⚠️  {ticker} 재무제표를 찾을 수 없습니다")
                return None, None

            # Step 3: DataFrame → 텍스트 변환
            financial_text = self._dataframe_to_text(df, ticker)
            print(f"  ✅ 재무제표 조회 완료 ({len(df)}개 항목)")

            return financial_text, df

        except Exception as e:
            print(f"  ❌ 재무제표 조회 실패: {e}")
            return None, None

    def _dataframe_to_text(self, df: pd.DataFrame, ticker: str) -> str:
        """
        재무제표 DataFrame을 텍스트로 변환

        Args:
            df: DART API 응답 DataFrame
            ticker: 종목코드

        Returns:
            str: 포맷된 재무제표 텍스트
        """
        lines = [f"# {ticker} 재무제표 (DART API)", ""]

        # 주요 계정과목 추출
        key_accounts = [
            # 포괄손익계산서
            "매출액",
            "영업이익(손실)",
            "당기순이익(손실)",
            "지배기업의 소유주에게 귀속되는 당기순이익(손실)",

            # 재무상태표
            "자산총계",
            "부채총계",
            "자본총계",
            "지배기업의 소유주에게 귀속되는 자본",

            # 현금흐름표
            "영업활동 현금흐름",
            "투자활동 현금흐름",
            "재무활동 현금흐름",

            # 주당정보
            "기본주당순이익(손실)",
        ]

        for account in key_accounts:
            row = df[df['account_nm'] == account]
            if not row.empty:
                try:
                    amount = float(row.iloc[0]['thstrm_amount'])
                    lines.append(f"- {account}: {amount:,.0f}")
                except:
                    pass

        # EPS 특별 처리 (부분 문자열 매칭)
        eps_row = df[df['account_nm'].str.contains('기본주당순이익', na=False)]
        if not eps_row.empty:
            try:
                eps = float(eps_row.iloc[0]['thstrm_amount'])
                lines.append(f"- 주당순이익(EPS): {eps:,.0f}원")
            except:
                pass

        return "\n".join(lines)


# ========================================
# 테스트 코드
# ========================================

if __name__ == "__main__":
    import sys
    import io
    import os
    from dotenv import load_dotenv

    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    load_dotenv()

    print("="*70)
    print("📊 DartFinancialLoader 테스트")
    print("="*70)
    print()

    # DART API 클라이언트 초기화
    dart_key = os.environ.get("DART_API_KEY")
    dart_client = DartClient(api_key=dart_key)
    loader = DartFinancialLoader(dart_client)

    # 테스트 케이스
    test_cases = [
        ('005930', '삼성전자'),
        ('005490', 'POSCO홀딩스'),
        ('000000', '존재하지않는종목')
    ]

    for ticker, name in test_cases:
        print(f"📌 {name} ({ticker}) 테스트")
        print("-" * 70)

        text, df = loader.load_financials(ticker)

        if text:
            print("\n[재무제표 텍스트]")
            print(text[:500])  # 처음 500자만 출력
            print(f"\n✅ DataFrame 크기: {len(df)} rows")
        else:
            print("❌ 재무제표 조회 실패")

        print("\n" + "="*70)
        print()

    print("✅ 테스트 완료")
