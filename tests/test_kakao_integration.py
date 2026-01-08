"""
카카오 포맷터 실제 데이터 연동 테스트
"""
import sys
import json
from datetime import datetime

# 티커 지정
ticker = "035720"  # 카카오

print("=" * 70)
print(f"테스트: {ticker} 종목 리포트 생성 및 카카오 포맷 변환")
print("=" * 70)
print()

# Step 1: 실제 리포트 생성
print(f"[1단계] {ticker} 실시간 리포트 생성 중...")
print("-" * 70)

from stock_report_realtime import RealtimeStockReportGenerator

generator = RealtimeStockReportGenerator()
real_report = generator.generate_report(ticker)

if 'error' in real_report:
    print(f"에러: {real_report['error']}")
    sys.exit(1)

print()
print("=" * 70)
print("[2단계] 카카오톡 포맷으로 변환 중...")
print("=" * 70)
print()

# Step 2: 카카오톡 포맷으로 변환
from kakao_report_formatter import KakaoReportFormatter

formatter = KakaoReportFormatter()
result = formatter.format_for_kakao(
    real_report,
    detail_url=f"https://example.com/report/{ticker}"
)

# Step 3: 결과 출력
print()
print("[결과] 요약 데이터 (카카오톡용)")
print("-" * 70)
print(json.dumps(result['summary'], ensure_ascii=False, indent=2))
print()

print("[결과] 카카오톡 API 응답")
print("-" * 70)
print(json.dumps(result['kakao_response'], ensure_ascii=False, indent=2))
print()

# Step 4: JSON 파일로 저장
output_filename = f"kakao_format_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"결과 저장: {output_filename}")
print()
print("테스트 완료!")
