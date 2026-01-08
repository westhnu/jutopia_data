"""
카카오톡 챗봇용 리포트 포맷터
요약본 + 상세 리포트 분리
"""

from typing import Dict, Any
from datetime import datetime


class KakaoReportFormatter:
    """카카오톡 챗봇용 리포트 포맷팅"""

    @staticmethod
    def format_for_kakao(report_data: Dict[str, Any], detail_url: str = None) -> Dict:
        """
        카카오톡 응답 형식으로 변환

        처리 순서:
        1. 상세 리포트 생성 (전체 리포트 데이터)
        2. 상세 리포트로부터 요약 데이터 추출
        3. 요약 데이터로 카카오톡 API 응답 생성

        Args:
            report_data: 생성된 리포트 JSON (stock_report_realtime.py의 출력)
            detail_url: 상세 리포트 웹 URL (예: https://example.com/report/005930)

        Returns:
            {
                'summary': {...},      # 카카오톡에 표시할 요약 데이터 (detail로부터 추출)
                'detail': {...},       # 웹에서 보여줄 상세 데이터 (전체 리포트)
                'kakao_response': {...}  # 카카오톡 API 응답 포맷 (summary 기반)
            }
        """
        # Step 1: 상세 리포트 먼저 생성 (전체 데이터)
        detail = KakaoReportFormatter._create_detail(report_data)

        # Step 2: 상세 리포트로부터 요약 추출
        summary = KakaoReportFormatter._create_summary_from_detail(detail)

        # Step 3: 요약 데이터로 카카오톡 응답 생성
        kakao_response = KakaoReportFormatter._create_kakao_response(
            summary,
            detail_url or f"https://example.com/report/{detail['metadata']['ticker']}"
        )

        return {
            'summary': summary,      # detail에서 추출된 요약
            'detail': detail,        # 전체 상세 리포트
            'kakao_response': kakao_response  # 카카오톡 API 응답
        }

    # ========================================
    # 1. 상세 데이터 (웹페이지용) - 먼저 생성
    # ========================================

    @staticmethod
    def _create_detail(report_data: Dict[str, Any]) -> Dict:
        """
        웹에서 보여줄 상세 데이터 (전체 리포트)

        Returns:
            {
                'metadata': {...},
                'sections': {
                    'summary': str,
                    'price_analysis': str,
                    'financial_analysis': str,
                    'valuation': str,
                    'investment_opinion': str
                },
                'raw_data': {
                    'basic': {...},
                    'price_trend': {...},
                    'metrics': {...},
                    'technical': {...},
                    'financial_trend': {...}
                }
            }
        """
        return {
            'metadata': report_data['metadata'],
            'sections': report_data['report']['sections'],
            'raw_data': report_data.get('raw_data', {})
        }

    # ========================================
    # 2. 요약 데이터 (카카오톡용) - 상세에서 추출
    # ========================================

    @staticmethod
    def _create_summary_from_detail(detail: Dict[str, Any]) -> Dict:
        """
        상세 리포트로부터 카카오톡용 요약 데이터 추출

        ⚠️ 중요: 이 메서드는 detail 데이터를 기반으로 요약을 생성합니다.
        상세 리포트가 먼저 생성되어야 하며, 요약은 상세로부터 추출됩니다.

        Args:
            detail: _create_detail()의 반환값 (전체 상세 리포트)

        Returns:
            {
                'basic_info': {...},        # 기본 정보 (종목명, 현재가)
                'key_metrics': {...},       # 핵심 지표 (PER/PBR/ROE)
                'investment_opinion': {...}, # 투자 의견 (매수/보유/매도)
                'brief_summary': str        # 한 줄 요약
            }
        """
        meta = detail['metadata']
        raw_data = detail['raw_data']
        sections = detail['sections']

        # 기본 정보 (상세 리포트의 raw_data에서 추출)
        basic = raw_data.get('basic', {})
        basic_info = {
            'ticker': meta['ticker'],
            'company_name': meta['company_name'],
            'current_price': basic.get('current_price', 'N/A'),
            'price_change': basic.get('price_change', 0),
            'price_change_pct': basic.get('price_change_pct', 0)
        }

        # 핵심 지표 (상세 리포트의 raw_data에서 추출)
        metrics = raw_data.get('metrics', {})
        key_metrics = {
            'per': metrics.get('per', 'N/A'),
            'pbr': metrics.get('pbr', 'N/A'),
            'roe': metrics.get('roe', 'N/A')
        }

        # 투자 의견 (상세 리포트의 investment_opinion 섹션에서 추출)
        opinion_text = sections.get('investment_opinion', '')
        investment_opinion = KakaoReportFormatter._extract_opinion(opinion_text)

        # 한 줄 요약 (상세 리포트의 summary 섹션 첫 문장 추출)
        summary_text = sections.get('summary', '')
        brief_summary = summary_text.split('.')[0] + '.' if summary_text else ''
        if len(brief_summary) > 100:
            brief_summary = brief_summary[:97] + '...'

        return {
            'basic_info': basic_info,
            'key_metrics': key_metrics,
            'investment_opinion': investment_opinion,
            'brief_summary': brief_summary
        }

    # ========================================
    # 3. 카카오톡 API 응답 포맷 - 요약 기반
    # ========================================

    @staticmethod
    def _create_kakao_response(summary: Dict, detail_url: str) -> Dict:
        """
        카카오톡 스킬 서버 응답 포맷

        Returns:
            카카오톡 API 2.0 응답 형식
        """
        basic = summary['basic_info']
        metrics = summary['key_metrics']
        opinion = summary['investment_opinion']

        # 가격 변동 표시
        price_change_emoji = "📈" if basic['price_change'] > 0 else "📉" if basic['price_change'] < 0 else "➡️"
        price_change_text = f"{price_change_emoji} {basic['price_change']:+,}원 ({basic['price_change_pct']:+.2f}%)"

        # 투자 의견 이모지
        opinion_emoji = {
            '매수': '🟢',
            '보유': '🟡',
            '매도': '🔴',
            '관망': '⚪'
        }.get(opinion['opinion'], '⚪')

        return {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "basicCard": {
                            "title": f"📊 {basic['company_name']} ({basic['ticker']})",
                            "description": summary['brief_summary'],
                            "thumbnail": {
                                "imageUrl": f"https://example.com/chart/{basic['ticker']}.png"
                            },
                            "buttons": [
                                {
                                    "action": "webLink",
                                    "label": "📄 상세 리포트 보기",
                                    "webLinkUrl": detail_url
                                }
                            ]
                        }
                    },
                    {
                        "listCard": {
                            "header": {
                                "title": "📈 핵심 정보"
                            },
                            "items": [
                                {
                                    "title": "현재가",
                                    "description": f"{basic['current_price']:,}원\n{price_change_text}"
                                },
                                {
                                    "title": "밸류에이션",
                                    "description": f"PER {metrics['per']}배 | PBR {metrics['pbr']}배 | ROE {metrics['roe']}%"
                                },
                                {
                                    "title": "투자 의견",
                                    "description": f"{opinion_emoji} {opinion['opinion']}\n목표주가: {opinion['target_price']}"
                                }
                            ],
                            "buttons": [
                                {
                                    "action": "webLink",
                                    "label": "📄 상세 리포트 보기",
                                    "webLinkUrl": detail_url
                                }
                            ]
                        }
                    }
                ]
            }
        }

    # ========================================
    # 헬퍼 메서드
    # ========================================

    @staticmethod
    def _extract_opinion(opinion_text: str) -> Dict:
        """
        투자 의견 텍스트에서 핵심 정보 추출

        Returns:
            {
                'opinion': '매수/보유/매도',
                'target_price': '목표주가',
                'risk_level': '리스크 수준'
            }
        """
        opinion = 'N/A'
        target_price = 'N/A'
        risk_level = 'N/A'

        if not opinion_text:
            return {'opinion': opinion, 'target_price': target_price, 'risk_level': risk_level}

        # 투자 의견 추출
        opinion_lower = opinion_text.lower()
        if '매수' in opinion_text or 'buy' in opinion_lower:
            opinion = '매수'
        elif '보유' in opinion_text or 'hold' in opinion_lower:
            opinion = '보유'
        elif '매도' in opinion_text or 'sell' in opinion_lower:
            opinion = '매도'
        elif '관망' in opinion_text:
            opinion = '관망'

        # 목표주가 추출
        import re

        # 패턴 1: 목표주가: 115,000원
        target_match = re.search(r'목표주가[:\s]*([0-9,]+)\s*원', opinion_text)
        if target_match:
            target_price = target_match.group(1) + '원'
        else:
            # 패턴 2: 115,000원으로 제시
            number_match = re.search(r'([0-9,]+)\s*원', opinion_text)
            if number_match:
                target_price = number_match.group(1) + '원'

        # 리스크 수준 추출
        if '높은 리스크' in opinion_text or 'high risk' in opinion_lower:
            risk_level = '높음'
        elif '중간 리스크' in opinion_text or 'medium risk' in opinion_lower:
            risk_level = '중간'
        elif '낮은 리스크' in opinion_text or 'low risk' in opinion_lower:
            risk_level = '낮음'

        return {
            'opinion': opinion,
            'target_price': target_price,
            'risk_level': risk_level
        }


# ========================================
# 테스트 코드
# ========================================

if __name__ == "__main__":
    import sys
    import json

    print("="*70)
    print("📱 카카오톡 리포트 포맷터 테스트 (실제 데이터 연동)")
    print("="*70)
    print()

    # 사용자로부터 티커 입력 받기
    ticker = input("종목 코드를 입력하세요 (예: 005930=삼성전자, 035720=카카오): ").strip()

    if not ticker:
        print("❌ 종목 코드를 입력해주세요.")
        sys.exit(1)

    print()
    print(f"🔄 {ticker} 종목의 실시간 리포트 생성 중...")
    print("="*70)
    print()

    # 실제 리포트 생성기 import 및 실행
    try:
        from stock_report_realtime import RealtimeStockReportGenerator

        generator = RealtimeStockReportGenerator()
        real_report = generator.generate_report(ticker)

        if 'error' in real_report:
            print(f"❌ 에러: {real_report['error']}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ 리포트 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print()
    print("="*70)
    print("🎨 카카오톡 포맷으로 변환 중...")
    print("="*70)
    print()

    # 카카오톡 포맷으로 변환
    formatter = KakaoReportFormatter()
    result = formatter.format_for_kakao(
        real_report,
        detail_url=f"https://example.com/report/{ticker}"
    )

    # 결과 출력
    print("📌 1. 요약 데이터 (카카오톡용)")
    print("-" * 70)
    print(json.dumps(result['summary'], ensure_ascii=False, indent=2))
    print()

    print("📌 2. 카카오톡 API 응답")
    print("-" * 70)
    print(json.dumps(result['kakao_response'], ensure_ascii=False, indent=2))
    print()

    # JSON 파일로 저장
    output_filename = f"kakao_format_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"💾 결과 저장: {output_filename}")
    print()
    print("✅ 테스트 완료")
