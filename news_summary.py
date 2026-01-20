"""
뉴스/커뮤니티 요약 모듈 (2-5)
종목 선택 -> 뉴스 크롤링 -> LLM 요약 -> 주요 이슈 요약
"""

import sys
import io
import os
from typing import Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# Windows console encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

from tavily_search import TavilySearchClient
import google.generativeai as genai


class NewsSummaryGenerator:
    """
    뉴스/커뮤니티 요약 생성기
    기획 2-5: 종목 선택 -> 뉴스 크롤링 -> LLM 요약 -> 주요 이슈
    """

    def __init__(self):
        """Initialize"""
        print("🔧 뉴스 요약 생성기 초기화 중...")

        # Tavily 웹 검색
        try:
            self.tavily_client = TavilySearchClient()
            print("✅ Tavily 웹 검색 초기화 완료")
        except Exception as e:
            raise ValueError(f"Tavily 초기화 실패: {e}")

        # Gemini API (LLM)
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        genai.configure(api_key=self.gemini_key)
        print("✅ Gemini API 초기화 완료\n")

    def generate_summary(self, company_name: str, ticker: str) -> Dict:
        """
        뉴스/커뮤니티 요약 생성

        Args:
            company_name: 회사명 (예: "삼성전자")
            ticker: 종목코드 (예: "005930")

        Returns:
            요약 결과 딕셔너리
        """
        print(f"📰 {company_name}({ticker}) 뉴스 요약 생성 중...\n")

        # Step 1: 뉴스 검색
        print("[ Step 1 ] 뉴스 및 시장 반응 검색")
        news_data = self.tavily_client.search_stock_news(company_name, ticker, max_results=5)
        sentiment_data = self.tavily_client.search_market_sentiment(company_name, max_results=5)

        news_count = len(news_data.get('results', []))
        sentiment_count = len(sentiment_data.get('results', []))
        print(f"✅ 뉴스 {news_count}건, 시장 반응 {sentiment_count}건 검색 완료\n")

        if news_count == 0 and sentiment_count == 0:
            return {
                'error': '검색 결과가 없습니다.',
                'company_name': company_name,
                'ticker': ticker
            }

        # Step 2: LLM 요약
        print("[ Step 2 ] LLM 요약 생성")
        summary = self._generate_llm_summary(company_name, ticker, news_data, sentiment_data)
        print("✅ 요약 생성 완료\n")

        return {
            'metadata': {
                'company_name': company_name,
                'ticker': ticker,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'news_count': news_count,
                'sentiment_count': sentiment_count
            },
            'summary': summary,
            'raw_data': {
                'news': news_data,
                'sentiment': sentiment_data
            }
        }

    def _generate_llm_summary(
        self,
        company_name: str,
        ticker: str,
        news_data: Dict,
        sentiment_data: Dict
    ) -> Dict:
        """LLM으로 뉴스 요약 생성"""

        # 뉴스 텍스트 포맷
        news_text = self._format_search_results(news_data, "뉴스")
        sentiment_text = self._format_search_results(sentiment_data, "시장 반응")

        prompt = f"""
당신은 주식 시장 전문 애널리스트입니다. 다음 {company_name}({ticker}) 관련 뉴스와 시장 반응을 분석하여 요약해주세요.

## 수집된 데이터

### 최신 뉴스
{news_text}

### 시장 반응 / 투자자 의견
{sentiment_text}

---

## 요약 작성 요청

위 데이터를 바탕으로 다음 형식으로 요약해주세요:

### [1. 핵심 이슈] (3줄 이내)
가장 중요한 뉴스/이슈를 간결하게 요약

### [2. 시장 반응]
- 긍정적 요인: (있다면)
- 부정적 요인: (있다면)
- 전반적 분위기: (긍정/중립/부정)

### [3. 주요 키워드]
관련 키워드 3-5개 나열

### [4. 투자자 참고사항]
초보 투자자가 알아야 할 핵심 포인트 (2-3줄)

---

요약을 시작해주세요:
"""

        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            summary_text = response.text

            # 섹션 파싱
            sections = self._parse_summary_sections(summary_text)

            return {
                'full_text': summary_text,
                'sections': sections
            }

        except Exception as e:
            return {
                'error': str(e),
                'full_text': '',
                'sections': {}
            }

    def _format_search_results(self, data: Dict, label: str) -> str:
        """검색 결과를 텍스트로 포맷"""
        lines = []

        # AI 요약이 있으면 추가
        if data.get('answer'):
            lines.append(f"**AI 요약**: {data['answer'][:300]}")
            lines.append("")

        # 개별 결과
        for i, result in enumerate(data.get('results', [])[:5], 1):
            title = result.get('title', '제목 없음')
            content = result.get('content', '')[:200]
            lines.append(f"{i}. [{title}]")
            lines.append(f"   {content}...")
            lines.append("")

        return '\n'.join(lines) if lines else f"❌ {label} 데이터 없음"

    def _parse_summary_sections(self, text: str) -> Dict:
        """요약 텍스트를 섹션별로 파싱"""
        sections = {
            'key_issues': '',
            'market_reaction': '',
            'keywords': '',
            'investor_notes': ''
        }

        section_map = {
            '핵심 이슈': 'key_issues',
            '시장 반응': 'market_reaction',
            '주요 키워드': 'keywords',
            '투자자 참고': 'investor_notes'
        }

        lines = text.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            is_header = False
            for keyword, section_key in section_map.items():
                if keyword in line and ('[' in line or '#' in line):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = section_key
                    current_content = []
                    is_header = True
                    break

            if not is_header and current_section:
                current_content.append(line)

        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def format_for_kakao(self, result: Dict) -> Dict:
        """
        카카오톡 응답 형식으로 변환

        Returns:
            카카오톡 API 2.0 응답 형식
        """
        if 'error' in result:
            return {
                "version": "2.0",
                "template": {
                    "outputs": [{
                        "simpleText": {
                            "text": f"❌ {result['error']}"
                        }
                    }]
                }
            }

        meta = result['metadata']
        sections = result['summary'].get('sections', {})

        # 핵심 이슈 추출
        key_issues = sections.get('key_issues', '요약 정보 없음')
        if len(key_issues) > 200:
            key_issues = key_issues[:197] + "..."

        # 키워드 추출
        keywords = sections.get('keywords', '')

        return {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "textCard": {
                            "title": f"📰 {meta['company_name']} 뉴스 요약",
                            "description": key_issues,
                            "buttons": [
                                {
                                    "action": "webLink",
                                    "label": "📄 상세 보기",
                                    "webLinkUrl": f"https://example.com/news/{meta['ticker']}"
                                }
                            ]
                        }
                    }
                ],
                "quickReplies": [
                    {
                        "action": "message",
                        "label": "📊 종목 리포트",
                        "messageText": f"{meta['company_name']} 리포트"
                    },
                    {
                        "action": "message",
                        "label": "📈 차트 보기",
                        "messageText": f"{meta['company_name']} 차트"
                    }
                ]
            }
        }

    def print_summary(self, result: Dict):
        """요약 결과 출력"""
        if 'error' in result:
            print(f"❌ 에러: {result['error']}")
            return

        meta = result['metadata']
        summary = result['summary']

        print("=" * 60)
        print(f"  📰 {meta['company_name']} ({meta['ticker']}) 뉴스 요약")
        print("=" * 60)
        print(f"  생성일시: {meta['generated_at']}")
        print(f"  뉴스: {meta['news_count']}건 / 시장반응: {meta['sentiment_count']}건")
        print("=" * 60)
        print()
        print(summary.get('full_text', ''))
        print()
        print("=" * 60)


# ========================================
# 테스트
# ========================================

if __name__ == "__main__":
    import json

    print("=" * 60)
    print("📰 뉴스/커뮤니티 요약 테스트")
    print("=" * 60)
    print()

    generator = NewsSummaryGenerator()

    # 테스트: 삼성전자
    company = "삼성전자"
    ticker = "005930"

    result = generator.generate_summary(company, ticker)
    generator.print_summary(result)

    # 카카오톡 형식
    print("\n📱 카카오톡 응답 형식:")
    print("-" * 40)
    kakao_response = generator.format_for_kakao(result)
    print(json.dumps(kakao_response, ensure_ascii=False, indent=2))

    # JSON 저장
    print("\n💾 결과 저장 중...")
    output_file = f"news_summary_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ 저장 완료: {output_file}")
