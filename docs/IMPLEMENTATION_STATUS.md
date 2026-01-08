# 카카오톡 챗봇 기능 구현 현황

## 📋 기획서 대비 구현 상태

---

## 1. 종목 리포트 (B2-1)

### 기획 요구사항
- **인텐트**: `report.simple`
- **입력**: `ticker` (필수 파라미터)
- **출력**: Carousel(ItemCard 5장) + QuickReply
  - 카드 1: 투자 요약
  - 카드 2: 주가 동향 분석
  - 카드 3: 재무제표
  - 카드 4: 밸류에이션
  - 카드 5: 투자의견

### ✅ 구현 완료 (100%)

#### 백엔드 로직
| 구성 요소 | 파일 | 상태 | 비고 |
|----------|------|------|------|
| 리포트 생성 엔진 | `stock_report_realtime.py` | ✅ | LLM 기반 5개 섹션 생성 |
| 정량 데이터 수집 | `stock_report_api.py` | ✅ | 8개 메서드 (기본정보, 가격추세 등) |
| 재무제표 조회 | `dart_financial_loader.py` | ✅ | DART API 연동 (2025 Q3 조회 성공) |
| 밸류에이션 계산 | `metrics_calculator.py` | ✅ | PER/PBR/ROE 계산 |

#### 출력 데이터 구조
```python
{
    'metadata': {
        'ticker': '005930',
        'company_name': '삼성전자',
        'generated_at': '2026-01-02 19:12:02',
        'has_financials': True
    },
    'report': {
        'title': '삼성전자(005930) 투자 분석 리포트',
        'full_text': '...',
        'sections': {
            'summary': '투자 요약 텍스트...',              # → 카드 1
            'price_analysis': '주가 동향 분석 텍스트...',   # → 카드 2
            'financial_analysis': '재무제표 텍스트...',     # → 카드 3
            'valuation': '밸류에이션 텍스트...',            # → 카드 4
            'investment_opinion': '투자의견 텍스트...'      # → 카드 5
        }
    },
    'raw_data': {
        'basic': {'current_price': 128500, 'price_change': 1500, ...},
        'price_trend': {'1m': -2.81, '3m': 37.55, '1y': 71.76, ...},
        'metrics': {'per': 16.62, 'pbr': 1.42, 'roe': 8.57, ...},
        'technical': {'rsi': 50, 'rsi_signal': '중립', ...},
        'financial_trend': {...}
    }
}
```

#### 카카오톡 포맷 변환
| 구성 요소 | 파일 | 상태 | 비고 |
|----------|------|------|------|
| 기본 포맷터 | `kakao_report_formatter.py` | ✅ | basicCard + listCard 형식 |
| ItemCard 변환 | **❌ 미구현** | ⚠️ | Carousel(ItemCard) 형식 필요 |

#### 샘플 데이터
| 파일 | 내용 | 상태 |
|------|------|------|
| `sample_data_20260102_191414.json` | 실제 3개 종목 리포트 | ✅ |

### ⚠️ 부족한 부분 (20%)

1. **Carousel(ItemCard) 포맷터 필요**
   - 현재: basicCard + listCard
   - 필요: ItemCard × 5장 (투자요약, 주가동향, 재무제표, 밸류에이션, 투자의견)

2. **섹션 → ItemList 변환 로직**
   ```python
   # 필요한 변환 로직
   def section_to_itemlist(section_text: str, section_type: str) -> list:
       """
       LLM 생성 텍스트 → ItemCard의 itemList 형식으로 변환

       예:
       section_type = "price_analysis"
       section_text = "1개월 수익률은 -2.81%이고, 3개월은 +37.55%..."

       →
       [
           {"title": "1개월 수익률", "description": "-2.81%"},
           {"title": "3개월 수익률", "description": "+37.55%"},
           {"title": "1년 수익률", "description": "+71.76%"},
           ...
       ]
       """
   ```

3. **LLM 한 문장 요약 생성**
   - 기획서 요구: 각 카드의 `description`에 한 문장 요약
   - 현재: 전체 텍스트만 있음
   - 필요: 섹션별 1-2줄 요약 추출

---

## 2. 계좌 연결 (B08 시리즈)

### 기획 요구사항

#### B08-1. 계좌 연결 시작 안내
- **인텐트**: `account.connect`
- **출력**: TextCard + QuickReply
  - TextCard: 안내 메시지
  - 버튼: "좋아요, 시작할게요" → B08-2로 이동

#### B08-2. OAuth URL 발급_skill
- 한국투자증권 OAuth 인증 URL 생성

#### B08-3. 계좌 연결 완료 안내
- **인텐트**: `account.connect.done`
- **출력**: SimpleText + QuickReply
  - QuickReply: 거래 내역, 물타기 계산기, 주식 리포트, 도움말

### ✅ 구현 완료 (70%)

#### 백엔드 로직
| 구성 요소 | 파일 | 상태 | 비고 |
|----------|------|------|------|
| 한투 API 연동 | `HantuStock.py` | ✅ | OAuth, 계좌 조회 완료 |
| 보유 종목 조회 | `get_holding_stock_detail()` | ✅ | 평단가, 수량 포함 |
| 현금 잔고 조회 | `get_holding_cash()` | ✅ | 예수금 조회 |

#### OAuth 플로우
```python
# HantuStock.py - OAuth 관련 메서드
class HantuStock:
    def __init__(self):
        # .env에서 KIS_APP_KEY, KIS_APP_SECRET, KIS_ACCOUNT_ID 로드
        self.base_url = "https://openapi.koreainvestment.com:9443"
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        # OAuth 토큰 발급
        pass
```

**환경 변수 필요**:
```
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCOUNT_ID=12345678
KIS_ACCOUNT_SUFFIX=01
KIS_ENV=prod  # 또는 vps, paper
```

### ⚠️ 부족한 부분 (30%)

1. **OAuth URL 생성 API 미구현**
   - 현재: 환경 변수로 직접 인증
   - 필요: 사용자별 OAuth URL 생성 엔드포인트

2. **토큰 저장/관리 시스템 없음**
   - 현재: 매번 새로 발급
   - 필요: 사용자별 토큰 DB 저장

3. **카카오톡 응답 포맷 미정의**
   - B08-1, B08-3의 TextCard/SimpleText 형식 미구현

---

## 3. 주식 초보 용어 (B12-1)

### 기획 요구사항
- **진입**: 온보딩 버튼 "주식 기초 용어 볼래요" 클릭
- **출력**: SimpleText + Carousel(ItemCard 8장) + QuickReply
  - 카드 1: 기본 개념 용어 (5개)
  - 카드 2: 가격·거래 관련 (5개)
  - 카드 3: 매매 관련 (5개)
  - 카드 4: 차트 관련 (5개)
  - 카드 5: 실전 용어 (5개)
  - 카드 6: ETF/상품 용어 (5개)
  - 카드 7: 계좌·시스템 용어 (5개)
  - 카드 8: 용어 사전 사용법 안내

### ✅ 구현 완료 (80%)

#### 백엔드 데이터
| 구성 요소 | 파일 | 상태 | 비고 |
|----------|------|------|------|
| 용어 데이터 | `glossary.json` | ✅ | 73개 용어 (18개 카테고리) |
| 용어 검색 API | `glossary_api.py` | ✅ | 정확/유사 검색, 카테고리별 조회 |

#### glossary.json 구조
```json
{
  "PER": {
    "full_name": "주가수익비율",
    "english": "Price Earnings Ratio",
    "category": "재무비율",
    "description": "주가를 주당순이익(EPS)으로 나눈 값...",
    "formula": "PER = 주가 / 주당순이익(EPS)",
    "example": "PER 10배라면...",
    "interpretation": {
      "low": "PER이 낮으면 저평가 가능성",
      "high": "PER이 높으면 고평가...",
      "standard": "KOSPI 평균: 10-15배"
    },
    "related_terms": ["PBR", "EPS", "ROE", "PSR"]
  }
}
```

#### glossary_api.py 주요 메서드
```python
class GlossaryAPI:
    def lookup(term: str) -> dict
    def search_by_category(category: str) -> list
    def get_related_terms(term: str) -> list
    def find_similar(query: str, limit: int) -> list
    def format_term_card(term: str) -> str  # 카카오톡 카드 포맷
    def get_categories() -> list  # 18개 카테고리
```

#### 카테고리 목록 (18개)
```
재무비율, 재무지표, 재무정보, 재무분석
기술적지표, 거래개념, 거래방식, 거래제도
투자개념, 투자상품, 투자전략, 투자주체
시장지수, 시장지표, 안전장치
공시자료, 정보시스템, 파생상품
```

### ⚠️ 부족한 부분 (20%)

1. **카테고리별 용어 그룹핑 미완성**
   - 기획서 요구: 카드 1 (기본 개념), 카드 2 (가격·거래) 등
   - 현재: 18개 카테고리로 분류되어 있음
   - 필요: 8개 주제로 재분류 + 각 5개씩 선별

2. **ItemCard 포맷 변환 미구현**
   ```python
   # 필요한 변환 로직
   def create_beginner_terms_carousel() -> dict:
       """
       glossary.json → Carousel(ItemCard × 8)

       Returns:
           {
               "outputs": [
                   {
                       "itemCard": {
                           "head": "기본 개념 용어",
                           "itemList": [
                               {"title": "주식", "description": "회사의 소유권..."},
                               {"title": "시가총액", "description": "주가 × 발행 주식수..."},
                               ...
                           ]
                       }
                   },
                   ...  # 8장
               ]
           }
       """
   ```

3. **용어 선별 및 우선순위 미정의**
   - 현재 73개 용어 중 초보자용 핵심 40개 선별 필요
   - 8개 카테고리 × 5개 = 40개 용어

---

## 4. 실시간 차트 (S11 / B11 시리즈)

### 기획 요구사항

#### B11-1. 실시간 차트 진입
- **인텐트**: `charts.realtime`
- **입력**: `ticker` (필수)
- **되묻기**: ticker 미인식 시

#### B11-2. 실시간 차트_skill
- **Case 0**: 종목 미인식 → SimpleText
- **Case 1**: 정상 → TextCard + webLink 버튼
- **Case 2**: 에러 → SimpleText

### ✅ 구현 완료 (60%)

#### 백엔드 로직
| 구성 요소 | 파일 | 상태 | 비고 |
|----------|------|------|------|
| 주가 데이터 조회 | `stock_analyzer.py` | ✅ | FinanceDataReader 사용 |
| 차트 생성 | `stock_chart_visualizer.py` | ✅ | Plotly 기반 6가지 차트 |
| Streamlit 대시보드 | `app.py` | ✅ | 로컬 실행 가능 |

#### 차트 종류 (6가지)
```python
# stock_chart_visualizer.py
class StockChartVisualizer:
    def create_candlestick_chart(ticker, days=60)  # 캔들스틱 + MA
    def create_technical_chart(ticker, days=60)    # 볼린저밴드 + RSI
    def create_price_line_chart(ticker, days=60)   # 단순 라인
    def create_volume_chart(ticker, days=60)       # 거래량
    def create_comparison_chart(tickers, days=60)  # 다중 종목 비교
    def create_index_chart(index_code, days=120)   # 지수 차트
```

#### Streamlit 앱 실행
```bash
streamlit run app.py
```

### ⚠️ 부족한 부분 (40%)

1. **차트 웹 배포 미완성**
   - 현재: 로컬 Streamlit 앱만 존재
   - 필요: 공개 URL (예: Streamlit Cloud, Heroku)
   - 기획서 요구: webLink 버튼 → 차트 웹링크

2. **차트 URL 생성 API 미구현**
   ```python
   # 필요한 엔드포인트
   @app.post("/api/v1/chart/url")
   async def get_chart_url(ticker: str, chart_type: str = "candlestick"):
       """
       차트 URL 생성

       Returns:
           {
               "ticker": "005930",
               "chart_url": "https://your-chart-app.streamlit.app/?ticker=005930&type=candlestick"
           }
       """
   ```

3. **카카오톡 응답 포맷 미정의**
   - TextCard + webLink 버튼 형식 미구현

---

## 5. 종합 구현 현황 요약

### 📊 기능별 완성도

| 기능 | 기획서 ID | 백엔드 로직 | 카카오톡 포맷 | 전체 완성도 |
|------|----------|------------|--------------|------------|
| **종목 리포트** | B2-1 | ✅ 100% | ⚠️ 20% | **60%** |
| **계좌 연결** | B08 시리즈 | ✅ 90% | ❌ 0% | **45%** |
| **초보 용어** | B12-1 | ✅ 100% | ⚠️ 50% | **75%** |
| **실시간 차트** | B11 시리즈 | ✅ 80% | ⚠️ 30% | **55%** |
| **물타기 계산** | B5 시리즈 | ✅ 100% | ❌ 0% | **50%** |

**전체 평균 완성도**: **57%**

---

## 6. 부족한 부분 상세

### 🔴 공통 이슈

#### 1. 카카오톡 응답 포맷터 부재
**현재**:
- `kakao_report_formatter.py`는 basicCard + listCard만 지원

**필요**:
- ItemCard 포맷터
- TextCard 포맷터
- SimpleText 포맷터
- Carousel 포맷터

**추천 구조**:
```python
# kakao_formatters.py (신규)
class KakaoFormatter:
    @staticmethod
    def simple_text(text: str, quick_replies: list = None) -> dict:
        """SimpleText 응답"""

    @staticmethod
    def text_card(title: str, description: str, buttons: list = None) -> dict:
        """TextCard 응답"""

    @staticmethod
    def item_card(head: str, item_list: list) -> dict:
        """ItemCard 단일"""

    @staticmethod
    def carousel_item_cards(cards: list) -> dict:
        """Carousel(ItemCard) 응답"""
```

---

#### 2. LLM 텍스트 → 구조화 데이터 변환
**문제**:
- LLM이 생성한 텍스트는 자유 형식
- 카카오톡은 구조화된 JSON 필요 (title + description 쌍)

**예시**:
```
LLM 출력:
"최근 3개월간 주가는 37.55% 상승했으며, 1년 수익률은 71.76%를 기록했습니다.
RSI는 50으로 중립 상태입니다."

→ 변환 필요:
[
    {"title": "3개월 수익률", "description": "+37.55%"},
    {"title": "1년 수익률", "description": "+71.76%"},
    {"title": "RSI", "description": "50 (중립)"}
]
```

**해결 방안**:
1. **Option A**: raw_data 직접 사용 (정확하지만 유연성 부족)
2. **Option B**: LLM에게 JSON 형식으로 요청 (추천)
   ```python
   prompt = f"""
   다음 데이터를 itemList 형식으로 변환해주세요:

   데이터: {raw_data}

   출력 형식:
   [
       {{"title": "항목명", "description": "값"}},
       ...
   ]
   """
   ```

---

#### 3. FastAPI 엔드포인트 미구현
**필요한 엔드포인트**:

1. **종목 리포트**
   ```python
   POST /api/v1/kakao/skill/report
   Request: {"ticker": "005930"}
   Response: Carousel(ItemCard × 5)
   ```

2. **계좌 연결**
   ```python
   POST /api/v1/kakao/skill/account/connect/start
   Response: TextCard

   POST /api/v1/kakao/skill/account/connect/oauth
   Response: OAuth URL

   POST /api/v1/kakao/skill/account/connect/done
   Response: SimpleText
   ```

3. **초보 용어**
   ```python
   POST /api/v1/kakao/skill/terms/beginner
   Response: Carousel(ItemCard × 8)
   ```

4. **실시간 차트**
   ```python
   POST /api/v1/kakao/skill/chart/realtime
   Request: {"ticker": "005930"}
   Response: TextCard + webLink
   ```

---

## 7. 우선순위별 추가 작업

### 🔴 High Priority (1주일)

1. **카카오톡 공통 포맷터 구현**
   - ItemCard, TextCard, SimpleText, Carousel
   - 예상 시간: 2-3일

2. **종목 리포트 ItemCard 변환**
   - 5개 섹션 → 5장 ItemCard
   - 예상 시간: 1-2일

3. **FastAPI 스킬 서버 기본 구조**
   - 4개 기능의 엔드포인트
   - 예상 시간: 2-3일

### 🟡 Medium Priority (2주일)

4. **초보 용어 카테고리 재분류**
   - 18개 → 8개 주제
   - 73개 → 40개 핵심 용어 선별
   - 예상 시간: 1일

5. **LLM → JSON 변환 로직**
   - raw_data 기반 또는 LLM 재요청
   - 예상 시간: 2일

6. **차트 웹 배포**
   - Streamlit Cloud 배포
   - URL 생성 API
   - 예상 시간: 1일

### 🟢 Low Priority (3-4주일)

7. **계좌 연결 OAuth 플로우**
   - 사용자별 토큰 관리
   - DB 저장
   - 예상 시간: 3-5일

8. **에러 처리 고도화**
   - 3가지 Case별 응답
   - 예상 시간: 1-2일

---

## 8. 백엔드 전달 자료

### ✅ 준비된 것
1. ✅ 핵심 로직 모듈 (12개)
2. ✅ API 명세서 (`BACKEND_API_SPEC.md`)
3. ✅ 샘플 데이터 (실제 리포트 JSON)
4. ✅ 모듈 정리 문서 (`PROJECT_MODULES_SUMMARY.md`)

### 🔧 추가 필요
1. **카카오톡 응답 포맷 가이드**
   - ItemCard, TextCard, Carousel 예제
2. **스킬 서버 구현 예제**
   - FastAPI 템플릿 코드
3. **기획서 매핑 문서** (이 문서)

---

## 9. 다음 단계

### 백엔드 팀과 협의 필요 사항

1. **LLM 텍스트 → 구조화 변환 방식**
   - raw_data 직접 사용 vs LLM JSON 요청

2. **차트 웹 배포 방식**
   - Streamlit Cloud vs 별도 서버

3. **OAuth 토큰 관리 전략**
   - 세션 기반 vs DB 저장

4. **개발 일정**
   - High Priority 작업 우선 진행 제안

---

## 부록: 카카오톡 응답 포맷 참고

### ItemCard 예시
```json
{
  "itemCard": {
    "head": "주가 동향 분석",
    "itemList": [
      {"title": "1개월 수익률", "description": "-2.81%"},
      {"title": "3개월 수익률", "description": "+37.55%"},
      {"title": "1년 수익률", "description": "+71.76%"},
      {"title": "52주 고점 대비", "description": "-13.97%"},
      {"title": "RSI", "description": "50 (중립)"}
    ]
  }
}
```

### Carousel 예시
```json
{
  "carousel": {
    "type": "itemCard",
    "items": [
      {"itemCard": {...}},
      {"itemCard": {...}},
      ...
    ]
  }
}
```

### TextCard 예시
```json
{
  "textCard": {
    "title": "한국투자증권 계좌 연결",
    "description": "계좌를 연결하면 잔고·보유 종목을 확인할 수 있어요",
    "buttons": [
      {
        "action": "block",
        "label": "좋아요, 시작할게요",
        "blockId": "B08-2"
      }
    ]
  }
}
```
