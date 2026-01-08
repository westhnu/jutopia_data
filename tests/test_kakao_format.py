"""
카카오톡 리포트 포맷 테스트
실제 리포트 데이터로 요약/상세 분리 테스트

사용법:
    python test_kakao_format.py                    # 기본 샘플 종목 테스트
    python test_kakao_format.py 005930             # 특정 종목 테스트
    python test_kakao_format.py 005930 035420      # 여러 종목 테스트
"""

import sys
import io
import json
from datetime import datetime
from stock_report_realtime import RealtimeStockReportGenerator
from kakao_report_formatter import KakaoReportFormatter

# Windows 인코딩
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*70)
print("📱 카카오톡 리포트 포맷 테스트")
print("="*70)
print()

# 초기화
generator = RealtimeStockReportGenerator()
formatter = KakaoReportFormatter()

# 테스트할 종목들
# 커맨드라인 인자가 있으면 사용, 없으면 기본 샘플
if len(sys.argv) > 1:
    # 커맨드라인에서 종목코드만 받음 (종목명은 리포트에서 자동 추출)
    test_tickers = [(ticker.strip(), None) for ticker in sys.argv[1:]]
    print(f"📋 입력된 종목: {', '.join([t[0] for t in test_tickers])}\n")
else:
    # 기본 샘플 종목들
    test_tickers = [
        ('005930', '삼성전자'),
        ('035420', '네이버'),
        ('035720', '카카오')
    ]
    print("📋 기본 샘플 종목 테스트 (종목코드를 인자로 전달하면 해당 종목 테스트)\n")

for ticker, name in test_tickers:
    print(f"\n{'='*70}")
    if name:
        print(f"📊 {name} ({ticker}) 리포트 생성 중...")
    else:
        print(f"📊 {ticker} 리포트 생성 중...")
    print(f"{'='*70}\n")

    try:
        # 1. 리포트 생성
        report = generator.generate_report(ticker)

        if 'error' in report:
            print(f"❌ 오류: {report['error']}")
            continue

        # 2. 카카오톡 형식으로 변환
        detail_url = f"https://example.com/report/{ticker}"
        kakao_data = formatter.format_for_kakao(report, detail_url)

        # 3. 결과 저장
        output_file = f"kakao_format_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'original_report': report,
                'kakao_format': kakao_data
            }, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 저장 완료: {output_file}\n")

        # 4. 요약 출력
        print("─" * 70)
        print("📱 카카오톡 요약본")
        print("─" * 70)
        summary = kakao_data['summary']

        print(f"\n[기본 정보]")
        print(f"종목명: {summary['basic_info']['company_name']} ({summary['basic_info']['ticker']})")
        print(f"현재가: {summary['basic_info']['current_price']:,}원")

        change = summary['basic_info']['price_change']
        change_pct = summary['basic_info']['price_change_pct']
        emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        print(f"등락: {emoji} {change:+,}원 ({change_pct:+.2f}%)")

        print(f"\n[핵심 지표]")
        metrics = summary['key_metrics']
        print(f"PER: {metrics['per']}배")
        print(f"PBR: {metrics['pbr']}배")
        print(f"ROE: {metrics['roe']}%")

        print(f"\n[투자 의견]")
        opinion = summary['investment_opinion']
        opinion_emoji = {
            '매수': '🟢',
            '보유': '🟡',
            '매도': '🔴',
            '관망': '⚪'
        }.get(opinion['opinion'], '⚪')
        print(f"{opinion_emoji} {opinion['opinion']}")
        print(f"목표주가: {opinion['target_price']}")

        print(f"\n[한 줄 요약]")
        print(f"{summary['brief_summary']}")

        print("\n" + "─" * 70)
        print("🌐 상세 리포트 (웹용)")
        print("─" * 70)
        detail = kakao_data['detail']

        print(f"\n섹션 개수: {len(detail['sections'])}개")
        for section_key, section_title in [
            ('summary', '투자 요약'),
            ('price_analysis', '주가 동향'),
            ('financial_analysis', '재무 상태'),
            ('valuation', '밸류에이션'),
            ('investment_opinion', '투자 의견')
        ]:
            content = detail['sections'].get(section_key, '')
            print(f"  - {section_title}: {len(content)}자")

        print("\n" + "─" * 70)
        print("📤 카카오톡 API 응답 미리보기")
        print("─" * 70)

        kakao_response = kakao_data['kakao_response']
        outputs = kakao_response['template']['outputs']

        print(f"\n[카드 1: BasicCard]")
        basic_card = outputs[0]['basicCard']
        print(f"제목: {basic_card['title']}")
        print(f"설명: {basic_card['description'][:50]}...")
        print(f"버튼: {basic_card['buttons'][0]['label']}")

        print(f"\n[카드 2: ListCard]")
        list_card = outputs[1]['listCard']
        print(f"헤더: {list_card['header']['title']}")
        print(f"항목 수: {len(list_card['items'])}개")
        for item in list_card['items']:
            print(f"  - {item['title']}: {item['description'][:30]}...")

        print("\n")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        continue

print("\n" + "="*70)
print("✅ 모든 테스트 완료!")
print("="*70)
print("\n생성된 파일들:")
print("  - kakao_format_*.json (카카오톡 포맷 + 원본 리포트)")
