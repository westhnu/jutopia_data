"""
백엔드 팀 전달용 종목 리포트 예시 데이터 생성
여러 종목의 실제 데이터를 생성하여 JSON으로 저장
"""
import sys
import json
from datetime import datetime
from stock_report_realtime import RealtimeStockReportGenerator
from kakao_report_formatter import KakaoReportFormatter

# 샘플 종목 리스트
SAMPLE_TICKERS = [
    "005930",  # 삼성전자
    "035720",  # 카카오
    "000660",  # SK하이닉스
]

def generate_samples():
    """여러 종목의 샘플 데이터 생성"""

    print("=" * 70)
    print("샘플 데이터 생성")
    print("=" * 70)
    print()

    generator = RealtimeStockReportGenerator()
    formatter = KakaoReportFormatter()

    all_samples = {}

    for ticker in SAMPLE_TICKERS:
        print(f"[{ticker}] 리포트 생성 중...")

        try:
            # 1. 실시간 리포트 생성
            report = generator.generate_report(ticker)

            if 'error' in report:
                print(f"  ⚠️  {ticker} 스킵 (에러: {report['error']})")
                continue

            # 2. 카카오톡 포맷 변환
            kakao_result = formatter.format_for_kakao(
                report,
                detail_url=f"https://api.example.com/report/{ticker}"
            )

            # 3. 통합 데이터 구성
            all_samples[ticker] = {
                "ticker": ticker,
                "company_name": report['metadata']['company_name'],
                "generated_at": report['metadata']['generated_at'],

                # 원본 리포트 데이터
                "full_report": report,

                # 카카오톡 응답 데이터
                "kakao": kakao_result,
            }

            print(f"  ✅ {report['metadata']['company_name']} 완료")
            print()

        except Exception as e:
            print(f"  ❌ {ticker} 실패: {e}")
            import traceback
            traceback.print_exc()
            continue

    # 4. JSON 파일로 저장
    output_file = f"sample_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_samples, f, ensure_ascii=False, indent=2)

    print("=" * 70)
    print(f"✅ 저장 완료: {output_file}")
    print(f"✅ 생성된 종목 수: {len(all_samples)}")
    print("=" * 70)
    print()

    # 5. 데이터 구조 요약 출력
    if all_samples:
        first_ticker = list(all_samples.keys())[0]
        print("📋 데이터 구조 요약:")
        print("-" * 70)
        print(f"각 종목별 키: {list(all_samples[first_ticker].keys())}")
        print()
        print("full_report 구조:")
        print(f"  - metadata: {list(all_samples[first_ticker]['full_report']['metadata'].keys())}")
        print(f"  - report: {list(all_samples[first_ticker]['full_report']['report'].keys())}")
        print(f"  - raw_data: {list(all_samples[first_ticker]['full_report']['raw_data'].keys())}")
        print()
        print("kakao 구조:")
        print(f"  - {list(all_samples[first_ticker]['kakao'].keys())}")
        print()

    return output_file, all_samples

if __name__ == "__main__":
    output_file, data = generate_samples()

    print("💡 사용 방법:")
    print(f"   - 파일: {output_file}")
    print("   - API 응답 형식 참고용으로 사용")
