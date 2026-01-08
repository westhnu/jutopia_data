"""
용어 사전 API
Financial Glossary API

Provides search and lookup functionality for financial terms.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path


class GlossaryAPI:
    """금융 용어 사전 API"""

    def __init__(self, glossary_path: str = "glossary.json"):
        """
        Initialize Glossary API

        Args:
            glossary_path: Path to glossary JSON file
        """
        self.glossary_path = Path(glossary_path)
        self.terms = self._load_glossary()

    def _load_glossary(self) -> Dict:
        """용어 사전 로드"""
        try:
            with open(self.glossary_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 용어 사전 파일을 찾을 수 없습니다: {self.glossary_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 파싱 오류: {e}")
            return {}

    def lookup(self, term: str) -> Dict:
        """
        용어 검색 (정확한 매칭)

        Args:
            term: 검색할 용어 (예: "PER", "주가수익비율")

        Returns:
            Dict containing:
                - found: 검색 성공 여부
                - term: 검색한 용어
                - data: 용어 정보 (found=True일 때)
                - similar: 유사 용어 목록 (found=False일 때)
        """
        # 대소문자 무시
        term_upper = term.upper()

        # 1차 검색: 영문 약어로 검색
        if term_upper in self.terms:
            return {
                'found': True,
                'term': term_upper,
                'data': self.terms[term_upper]
            }

        # 2차 검색: 한글 이름으로 검색
        for key, value in self.terms.items():
            # full_name 매칭
            if value.get('full_name', '').upper() == term_upper:
                return {
                    'found': True,
                    'term': key,
                    'data': value
                }

            # 부분 매칭 (한글명에 검색어 포함)
            if term.lower() in value.get('full_name', '').lower():
                return {
                    'found': True,
                    'term': key,
                    'data': value
                }

        # 3차 검색: 유사 용어 찾기
        similar = self.find_similar(term)

        return {
            'found': False,
            'term': term,
            'similar': similar
        }

    def find_similar(self, query: str, limit: int = 5) -> List[str]:
        """
        유사한 용어 찾기

        Args:
            query: 검색 쿼리
            limit: 반환할 최대 개수

        Returns:
            유사 용어 목록 (영문 약어 또는 한글명)
        """
        query_lower = query.lower()
        similar = []

        for key, value in self.terms.items():
            # 영문 약어 부분 매칭
            if query_lower in key.lower():
                similar.append(key)
                continue

            # 한글명 부분 매칭
            full_name = value.get('full_name', '')
            if query in full_name:
                similar.append(f"{key} ({full_name})")
                continue

            # 영문명 부분 매칭
            english = value.get('english', '')
            if query_lower in english.lower():
                similar.append(f"{key} ({full_name})")

        return similar[:limit]

    def search_by_category(self, category: str) -> List[Dict]:
        """
        카테고리별 용어 검색

        Args:
            category: 카테고리 (예: "재무비율", "기술적지표")

        Returns:
            해당 카테고리의 용어 목록
        """
        results = []

        for key, value in self.terms.items():
            if value.get('category') == category:
                results.append({
                    'term': key,
                    'full_name': value.get('full_name'),
                    'description': value.get('description', '')[:100] + '...'
                })

        return results

    def get_categories(self) -> List[str]:
        """모든 카테고리 목록 반환"""
        categories = set()
        for value in self.terms.values():
            if 'category' in value:
                categories.add(value['category'])
        return sorted(list(categories))

    def get_related_terms(self, term: str) -> List[Dict]:
        """
        연관 용어 조회

        Args:
            term: 기준 용어

        Returns:
            연관 용어 목록
        """
        result = self.lookup(term)

        if not result['found']:
            return []

        related_list = result['data'].get('related_terms', [])
        related_data = []

        for related_term in related_list:
            related_result = self.lookup(related_term)
            if related_result['found']:
                related_data.append({
                    'term': related_result['term'],
                    'full_name': related_result['data'].get('full_name'),
                    'description': related_result['data'].get('description', '')[:80] + '...'
                })

        return related_data

    def format_term_card(self, term: str) -> str:
        """
        용어 정보를 카카오톡 메시지 형식으로 포맷팅

        Args:
            term: 용어

        Returns:
            Formatted string for KakaoTalk message
        """
        result = self.lookup(term)

        if not result['found']:
            # 검색 실패
            message = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 용어를 찾을 수 없습니다
━━━━━━━━━━━━━━━━━━━━━━━━━━

검색어: {result['term']}
"""

            if result['similar']:
                message += f"\n💡 혹시 이 용어를 찾으셨나요?\n"
                for idx, sim in enumerate(result['similar'], 1):
                    message += f"  {idx}. {sim}\n"

            message += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━"
            return message

        # 검색 성공
        data = result['data']
        term_abbr = result['term']
        full_name = data.get('full_name', '')
        english = data.get('english', '')
        category = data.get('category', '')
        description = data.get('description', '')
        formula = data.get('formula', '')
        example = data.get('example', '')
        interpretation = data.get('interpretation', {})
        related_terms = data.get('related_terms', [])

        message = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 용어 사전: {term_abbr}
━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 정식 명칭: {full_name}
🔤 영문: {english}
📂 분류: {category}

📝 설명:
{description}
"""

        # 공식 (있는 경우)
        if formula:
            message += f"\n📐 공식:\n{formula}\n"

        # 예시
        if example:
            message += f"\n💡 예시:\n{example}\n"

        # 해석 (있는 경우)
        if interpretation and isinstance(interpretation, dict):
            message += f"\n📊 해석:\n"
            for key, value in interpretation.items():
                message += f"• {value}\n"

        # 연관 용어
        if related_terms:
            message += f"\n🔗 연관 용어: {', '.join(related_terms)}\n"

        message += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━"

        return message

    def format_category_list(self) -> str:
        """카테고리 목록을 포맷팅"""
        categories = self.get_categories()

        message = """━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 용어 사전 카테고리
━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        for idx, cat in enumerate(categories, 1):
            count = sum(1 for v in self.terms.values() if v.get('category') == cat)
            message += f"{idx}. {cat} ({count}개)\n"

        message += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "💡 카테고리명을 입력하면 해당 용어 목록을 볼 수 있어요!"

        return message

    def get_random_term(self) -> str:
        """랜덤 용어 하나 반환 (오늘의 용어 등에 활용)"""
        import random
        if not self.terms:
            return ""

        term = random.choice(list(self.terms.keys()))
        return self.format_term_card(term)

    def count_terms(self) -> int:
        """총 용어 개수 반환"""
        return len(self.terms)


# 테스트 코드
if __name__ == "__main__":
    import sys
    import io

    # Windows console encoding fix
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    api = GlossaryAPI()

    print(f"=== 용어 사전 API 테스트 ===\n")
    print(f"총 용어 개수: {api.count_terms()}개\n")
    print("="*50 + "\n")

    # 1. 정확한 검색
    print("📌 테스트 1: 영문 약어 검색 (PER)")
    result = api.lookup("PER")
    print(f"검색 성공: {result['found']}")
    if result['found']:
        print(f"용어명: {result['data']['full_name']}")
        print(f"설명: {result['data']['description'][:100]}...")

    print("\n" + "="*50 + "\n")

    # 2. 한글 검색
    print("📌 테스트 2: 한글 검색 (주가수익비율)")
    result = api.lookup("주가수익비율")
    print(f"검색 성공: {result['found']}")
    if result['found']:
        print(f"영문 약어: {result['term']}")

    print("\n" + "="*50 + "\n")

    # 3. 부분 검색
    print("📌 테스트 3: 부분 검색 (수익)")
    similar = api.find_similar("수익", limit=5)
    print(f"유사 용어: {len(similar)}개")
    for s in similar:
        print(f"  - {s}")

    print("\n" + "="*50 + "\n")

    # 4. 카테고리 검색
    print("📌 테스트 4: 카테고리 목록")
    categories = api.get_categories()
    print(f"카테고리: {len(categories)}개")
    for cat in categories:
        count = len(api.search_by_category(cat))
        print(f"  - {cat}: {count}개")

    print("\n" + "="*50 + "\n")

    # 5. 연관 용어
    print("📌 테스트 5: 연관 용어 (PER)")
    related = api.get_related_terms("PER")
    print(f"연관 용어: {len(related)}개")
    for r in related:
        print(f"  - {r['term']} ({r['full_name']})")

    print("\n" + "="*50 + "\n")

    # 6. 카카오톡 포맷팅
    print("📌 테스트 6: 카카오톡 메시지 포맷")
    message = api.format_term_card("RSI")
    print(message)

    print("\n" + "="*50 + "\n")

    # 7. 검색 실패 시
    print("📌 테스트 7: 없는 용어 검색")
    message = api.format_term_card("존재하지않는용어")
    print(message)
