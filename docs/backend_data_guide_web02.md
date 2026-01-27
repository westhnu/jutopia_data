# Web_02 백엔드 데이터 가이드 (뉴스/커뮤니티)

> 작성: 데이터 파트
> 대상: 웹 백엔드 개발자
> 최종 업데이트: 2026-01-26 (AI 요약 한국어 번역 추가)

---

## 1. 전달 파일 및 설정

### 1.1 파일 목록

| 파일명 | 용도 |
|--------|------|
| `stock_news_data.py` | 뉴스/커뮤니티 데이터 프로바이더 |
| `tavily_search.py` | 웹 검색 모듈 (stock_news_data가 내부 사용) |
| `.env` | API 인증 정보 (별도 전달) |

### 1.2 필수 패키지

```bash
pip install python-dotenv tavily-python google-generativeai
```

### 1.3 .env 설정

```env
TAVILY_API_KEY=your_tavily_key
GEMINI_API_KEY=your_gemini_key  # AI 요약 한국어 번역용 (권장)
```

---

## 2. Quick Start

### 뉴스/커뮤니티 통합 API

```python
from stock_news_data import StockNewsDataProvider

provider = StockNewsDataProvider()

# 통합 API (권장)
result = provider.get_news_community_api(
    symbol="005930",
    company_name="삼성전자",
    tab="community"  # "news" 또는 "community"
)
```

### 뉴스 탭 (투자 관련 필터링)

```python
news = provider.get_news(
    symbol="005930",
    company_name="삼성전자",
    page=1,
    limit=10
)
```

### 커뮤니티 탭 (시장 반응 + AI 요약)

```python
community = provider.get_community(
    symbol="005930",
    company_name="삼성전자",
    page=1,
    limit=10
)
```

---

## 3. 메서드 요약

### stock_news_data.py - StockNewsDataProvider

| 메서드 | 용도 | 주요 파라미터 |
|--------|------|---------------|
| `get_news_community_api()` | **통합 API (권장)** | symbol, company_name, tab, page, limit |
| `get_news()` | 뉴스 탭 데이터 | symbol, company_name, page, limit |
| `get_community()` | 커뮤니티 탭 데이터 | symbol, company_name, page, limit |

---

## 4. API 응답 스키마

### 4.1 뉴스 탭 (`get_news`)

```json
{
  "symbol": "005930",
  "company_name": "삼성전자",
  "tab": "news",
  "page": 1,
  "limit": 10,
  "total_count": 15,
  "has_more": true,
  "items": [
    {
      "id": "news_1",
      "title": "삼성전자, HBM4 점유율 2배 확대 전망",
      "content": "KB증권은 삼성전자 목표주가를...",
      "url": "https://...",
      "source": "비즈니스포스트",
      "published_at": "2026-01-24 10:30:00",
      "is_investment_related": true
    }
  ],
  "fetched_at": "2026-01-24T10:30:00"
}
```

### 4.2 커뮤니티 탭 (`get_community`)

> **참고**: `ai_summary`는 `page=1`일 때만 생성됩니다. (비용 최적화)

```json
{
  "symbol": "005930",
  "company_name": "삼성전자",
  "tab": "community",
  "page": 1,
  "limit": 10,
  "total_count": 20,
  "has_more": true,
  "ai_summary": "애널리스트들은 삼성전자 HBM4 경쟁력에 긍정적...",
  "items": [
    {
      "id": "comm_1",
      "title": "KB증권 삼성전자 목표주가 20만원 유지",
      "content": "김동원 KB증권 연구원은...",
      "url": "https://...",
      "source": "비즈니스포스트",
      "sentiment": "positive",
      "published_at": "2026-01-24 10:30:00"
    }
  ],
  "fetched_at": "2026-01-24T10:30:00",
  "new_count": 0
}
```

### 4.3 에러 응답

```json
{
  "error": "에러 메시지",
  "items": [],
  "fetched_at": "2026-01-24T10:30:00"
}
```

---

## 5. 파라미터 값 정리

### tab

| 값 | 의미 |
|----|------|
| `community` | 커뮤니티 탭 (기본) |
| `news` | 뉴스 탭 |

### sentiment (커뮤니티)

| 값 | 의미 |
|----|------|
| `positive` | 긍정적 |
| `neutral` | 중립 |
| `negative` | 부정적 |

---

## 6. 뉴스 필터링 로직

### 2단계 필터링

| 단계 | 방식 | 설명 |
|------|------|------|
| 1단계 | 키워드 필터 | 투자 관련 키워드 포함 여부 |
| 2단계 | LLM 분류 | AI로 투자 판단 도움 여부 분류 (선택) |

### 투자 관련 키워드 (1단계)

```
주가, 주식, 투자, 매수, 매도, 목표가, 실적,
영업이익, 매출, 배당, 공시, IR, 애널리스트,
증권, 펀드, ETF, 상승, 하락, 전망
```

---

## 7. AI 요약 생성 로직

### 7.1 생성 흐름

```
Tavily 검색 (영어 answer) → Gemini 번역 → 한국어 AI 요약
```

### 7.2 최적화 사항

| 항목 | 설명 |
|------|------|
| page=1일 때만 생성 | 무한 스크롤 시 불필요한 Gemini 호출 방지 |
| Tavily answer 활용 | 이미 요약된 영어 텍스트를 번역만 수행 |

### 7.3 Gemini 미설정 시

- `GEMINI_API_KEY` 없으면 `ai_summary`가 빈 문자열(`""`)로 반환
- 나머지 기능(피드 리스트, 감성 분석)은 정상 동작

---

## 8. 주의사항

### API 호출 제한 (Tavily)

| 제한 | 값 | 대응 |
|------|----|------|
| Free Tier | 월 1,000회 | 캐싱 필수 |
| 검색 depth | basic/advanced | basic 권장 (비용 절감) |

### 권장 캐싱 TTL

| 탭 | TTL |
|----|-----|
| 커뮤니티 | 30초~1분 |
| 뉴스 | 5분 |

### API 호출 흐름

| 탭 | Page 1 | Page 2+ |
|----|--------|---------|
| 뉴스 | Tavily 1회 | Tavily 1회 |
| 커뮤니티 | Tavily 1회 + Gemini 1회 | Tavily 1회 |

---

## 9. 문의

데이터 관련 문의사항은 데이터 파트로 연락 바랍니다.
