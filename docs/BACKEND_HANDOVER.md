# 백엔드 팀 전달 자료

## 📦 완료된 기능 (서비스 기획 기준)

> 전체 서비스: S01~S12 중 **핵심 비즈니스 로직이 완료된 기능**만 정리

---

## S02 종목 리포트 조회

> 사용자가 종목코드를 입력하면 AI가 투자 분석 리포트를 자동 생성

### ✅ 완료된 기능
- **LLM 기반 리포트 생성**: 5개 섹션 자동 생성 (투자요약, 주가동향, 재무분석, 밸류에이션, 투자의견)
- **실시간 재무제표 조회**: DART API 연동 (2025년 Q3 데이터)
- **투자지표 자동 계산**: PER, PBR, ROE, EPS, 배당수익률 등
- **기술적 분석**: 1개월/3개월/1년 수익률, RSI, 이동평균선
- **카카오톡 포맷 예제**: basicCard + listCard

### 📁 사용 파일
```python
# 핵심 엔진
stock_report_realtime.py       # LLM 리포트 생성
stock_report_api.py            # 주가/지표 데이터 수집
dart_financial_loader.py       # DART 재무제표 조회
metrics_calculator.py          # PER/PBR/ROE 계산

# 포맷 변환
kakao_report_formatter.py      # 카카오톡 basicCard 예제

# 지원 모듈
dart_client.py                 # DART API 클라이언트
stock_data_fetcher.py          # 주가 데이터 수집
```

### 🎯 사용법

```python
from stock_report_realtime import RealtimeStockReportGenerator

# 리포트 생성
generator = RealtimeStockReportGenerator()
report = generator.generate_report("005930")  # 삼성전자

# 결과 구조
{
    'metadata': {
        'ticker': '005930',
        'company_name': '삼성전자',
        'generated_at': '2026-01-02 19:12:02',
        'has_financials': True
    },
    'report': {
        'title': '삼성전자(005930) 투자 분석 리포트',
        'sections': {
            'summary': '투자 요약 텍스트...',
            'price_analysis': '주가 동향 분석...',
            'financial_analysis': '재무제표 분석...',
            'valuation': '밸류에이션...',
            'investment_opinion': '투자의견...'
        }
    },
    'raw_data': {
        'basic': {'current_price': 128500, 'price_change': 1500, ...},
        'price_trend': {'1m': -2.81, '3m': 37.55, '1y': 71.76},
        'metrics': {'per': 16.62, 'pbr': 1.42, 'roe': 8.57},
        'technical': {'rsi': 50, 'rsi_signal': '중립'},
        'financial_trend': {...}
    }
}
```

### 📊 샘플 데이터
- `sample_data_*.json` - 삼성전자, 카카오, SK하이닉스 실제 리포트

### 🧪 테스트
```bash
python stock_report_realtime.py
# 입력: 005930
```

### 🔗 관련 엔드포인트 (백엔드 구현 필요)
- `POST /api/v1/report/generate` - 리포트 생성
- `POST /api/v1/kakao/skill/report` - 카카오톡 스킬 서버

---

## S03 주식 용어 사전

> 초보자를 위한 주식 용어 검색 및 설명 (73개 용어)

### ✅ 완료된 기능
- **용어 데이터베이스**: 73개 주식 용어 (18개 카테고리)
- **정확한 용어 검색**: "PER" 입력 시 정의/공식/예시 제공
- **유사 용어 검색**: "저평가" → PER, PBR, PSR 추천
- **카테고리별 조회**: 재무비율, 기술적지표 등 18개 카테고리
- **연관 용어 추천**: 각 용어마다 관련 용어 4-5개 제공

### 📁 사용 파일
```python
glossary_api.py    # 용어 검색 API
glossary.json      # 73개 용어 데이터
```

### 🎯 사용법

```python
from glossary_api import GlossaryAPI

api = GlossaryAPI()

# 1. 정확한 용어 검색
term = api.lookup("PER")
# {
#   'full_name': '주가수익비율',
#   'english': 'Price Earnings Ratio',
#   'category': '재무비율',
#   'description': '주가를 주당순이익으로 나눈 값...',
#   'formula': 'PER = 주가 / EPS',
#   'example': 'PER 10배라면 10년치 순이익...',
#   'interpretation': {
#     'low': '저평가 가능성',
#     'high': '고평가 또는 고성장 기대',
#     'standard': 'KOSPI 평균: 10-15배'
#   },
#   'related_terms': ['PBR', 'EPS', 'ROE', 'PSR']
# }

# 2. 유사 용어 검색
similar = api.find_similar("저평가", limit=5)
# ['PER', 'PBR', 'PSR', 'EV/EBITDA', 'ROE']

# 3. 카테고리별 조회
terms = api.search_by_category("재무비율")
# ['PER', 'PBR', 'ROE', 'ROA', ...]

# 4. 전체 카테고리 목록 (18개)
categories = api.get_categories()

# 5. 카카오톡 ListCard 포맷
card = api.format_term_card("PER")
```

### 📋 용어 데이터 구조

```json
{
  "PER": {
    "full_name": "주가수익비율",
    "english": "Price Earnings Ratio",
    "category": "재무비율",
    "description": "...",
    "formula": "PER = 주가 / EPS",
    "example": "...",
    "interpretation": {...},
    "related_terms": ["PBR", "EPS", "ROE", "PSR"]
  }
}
```

### 🏷️ 카테고리 (18개)
```
재무비율, 재무지표, 재무정보, 재무분석
기술적지표, 거래개념, 거래방식, 거래제도
투자개념, 투자상품, 투자전략, 투자주체
시장지수, 시장지표, 안전장치
공시자료, 정보시스템, 파생상품
```

### 🧪 테스트
```bash
python glossary_api.py
# 대화형 검색 테스트
```

### 🔗 관련 엔드포인트 (백엔드 구현 필요)
- `GET /api/v1/glossary/{term}` - 용어 검색
- `GET /api/v1/glossary/category/{category}` - 카테고리별 조회
- `POST /api/v1/kakao/skill/terms` - 카카오톡 용어 사전

---

## S05 물타기 계산기

> 평단가 낮추기 위한 추가 매수 시뮬레이션

### ✅ 완료된 기능
- **평단가 계산**: 현재 보유 종목 기준 평단가 자동 계산
- **시나리오별 시뮬레이션**: 1주, 5주, 10주 추가 매수 시 평단가 계산
- **목표 평단가 역산**: 원하는 평단가 달성에 필요한 매수 수량 계산
- **카카오톡 텍스트 포맷**: 계산 결과를 읽기 쉬운 텍스트로 변환

### 📁 사용 파일
```python
averaging_calculator.py    # 물타기 계산 전체 로직
```

### 🎯 사용법

```python
from averaging_calculator import AveragingCalculator

# 1. 계산기 초기화
calc = AveragingCalculator(
    current_price=70000,    # 현재 주가
    avg_price=80000,        # 내 평단가
    quantity=10,            # 보유 수량
    target_price=75000      # 목표 평단가 (선택)
)

# 2. 시나리오별 계산
scenarios = calc.calculate_scenarios()
# [
#   {
#     'add_quantity': 1,
#     'new_avg_price': 79090,
#     'total_quantity': 11,
#     'additional_investment': 70000,
#     'total_investment': 870000
#   },
#   {'add_quantity': 5, 'new_avg_price': 76666, ...},
#   {'add_quantity': 10, 'new_avg_price': 75000, ...}
# ]

# 3. 목표 평단가 달성에 필요한 수량
result = calc.calculate_target_quantity()
# {
#   'required_quantity': 10,
#   'new_avg_price': 75000,
#   'total_quantity': 20,
#   'additional_investment': 700000
# }

# 4. 카카오톡 텍스트 포맷
text = calc.format_result()
```

### 🧪 테스트
```bash
python averaging_calculator.py
```

### 🔗 관련 엔드포인트 (백엔드 구현 필요)
- `POST /api/v1/averaging/calculate` - 물타기 계산
- `POST /api/v1/kakao/skill/averaging` - 카카오톡 물타기 스킬

---

## S08 주식 계좌 연결 (한국투자증권)

> 사용자 증권 계좌와 연동하여 보유 종목/잔고 조회

### ✅ 완료된 기능
- **한국투자증권 OpenAPI 연동**: OAuth 토큰 발급 및 인증
- **보유 종목 조회**: 종목코드, 수량, 평단가, 평가손익
- **현금 잔고 조회**: 예수금, 출금가능금액

### 📁 사용 파일
```python
HantuStock.py    # 한국투자증권 API 래퍼
```

### 🎯 사용법

```python
from HantuStock import HantuStock

# 1. 초기화 (환경 변수에서 자동 로드)
client = HantuStock()

# 2. 보유 종목 조회
holdings = client.get_holding_stock_detail()
# [
#   {
#     'ticker': '005930',
#     'name': '삼성전자',
#     'quantity': 10,
#     'avg_price': 70000,
#     'current_price': 75000,
#     'profit': 50000,
#     'profit_rate': 7.14
#   }
# ]

# 3. 현금 잔고 조회
cash = client.get_holding_cash()
# {
#   'available_cash': 1000000,
#   'total_balance': 1500000,
#   'securities_value': 750000
# }
```

### ⚙️ 환경 변수 설정
```env
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCOUNT_ID=12345678
KIS_ACCOUNT_SUFFIX=01
KIS_ENV=prod  # prod(실전), vps(모의), paper(테스트)
```

### 🧪 테스트
```bash
# 환경 변수 설정 후
python HantuStock.py
```

### 🔗 관련 엔드포인트 (백엔드 구현 필요)
- `POST /api/v1/account/connect` - 계좌 연결
- `GET /api/v1/account/holdings` - 보유 종목 조회
- `GET /api/v1/account/balance` - 잔고 조회

---

## S11 실시간 차트

> 종목의 가격 차트를 6가지 스타일로 생성

### ✅ 완료된 기능
- **캔들스틱 차트**: 이동평균선 (MA5, MA20, MA60) 포함
- **기술적 차트**: 볼린저밴드 + RSI
- **단순 라인 차트**: 가격 추이만
- **거래량 차트**: 거래량 분석
- **다중 종목 비교**: 여러 종목 수익률 비교
- **지수 차트**: KOSPI, KOSDAQ 등
- **Streamlit 대시보드**: 로컬 실행 가능

### 📁 사용 파일
```python
stock_chart_visualizer.py    # Plotly 차트 생성
stock_analyzer.py            # 주가 데이터 조회
app.py                       # Streamlit 대시보드
```

### 🎯 사용법

```python
from stock_chart_visualizer import StockChartVisualizer

viz = StockChartVisualizer()

# 1. 캔들스틱 차트 + 이동평균선
fig = viz.create_candlestick_chart("005930", days=60)

# 2. 기술적 차트 (볼린저밴드 + RSI)
fig = viz.create_technical_chart("005930", days=60)

# 3. 단순 라인 차트
fig = viz.create_price_line_chart("005930", days=60)

# 4. 거래량 차트
fig = viz.create_volume_chart("005930", days=60)

# 5. 다중 종목 비교
fig = viz.create_comparison_chart(
    tickers=["005930", "035720", "000660"],
    days=60
)

# 6. 지수 차트
fig = viz.create_index_chart("KS11", days=120)  # KOSPI
```

### 🌐 Streamlit 대시보드
```bash
streamlit run app.py
```

**기능**:
- 종목 코드 입력
- 기간 선택 (30일/60일/90일/180일/1년)
- 6가지 차트 탭으로 전환
- 차트 다운로드 (PNG, SVG)

### 📊 차트 종류

| 차트 타입 | 메서드 | 용도 |
|---------|--------|------|
| 캔들스틱 | `create_candlestick_chart()` | 기본 주가 차트 + 이동평균 |
| 기술적 차트 | `create_technical_chart()` | 볼린저밴드 + RSI |
| 라인 차트 | `create_price_line_chart()` | 단순 가격 추이 |
| 거래량 | `create_volume_chart()` | 거래량 분석 |
| 종목 비교 | `create_comparison_chart()` | 여러 종목 수익률 비교 |
| 지수 차트 | `create_index_chart()` | KOSPI, KOSDAQ 등 |

### 🧪 테스트
```bash
python stock_chart_visualizer.py
```

### 🔗 관련 엔드포인트 (백엔드 구현 필요)
- `GET /api/v1/chart/{ticker}` - 차트 데이터
- `GET /api/v1/chart/url/{ticker}` - 차트 웹 URL 생성

---

## 📊 전체 서비스 구조

```
┌──────────────────────────────────────────────────────┐
│                   카카오톡 챗봇                       │
│  (S01 온보딩, S00 도움말, S04 증권사 추천 등)        │
└──────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│              완료된 핵심 기능 (5개)                   │
├──────────────────────────────────────────────────────┤
│                                                        │
│  ✅ S02: 종목 리포트 (LLM 기반 분석)                 │
│  ✅ S03: 주식 용어 사전 (73개)                       │
│  ✅ S05: 물타기 계산기 (평단가 계산)                 │
│  ✅ S08: 계좌 연결 (한국투자증권)                    │
│  ✅ S11: 실시간 차트 (6가지)                         │
│                                                        │
└──────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│              미완성 기능 (백엔드 필요)                │
├──────────────────────────────────────────────────────┤
│                                                        │
│  ⚠️ S06: 커뮤니티/뉴스 반응 요약 (크롤링 필요)      │
│  ⚠️ S07: 거래내역 리포트 (데이터 연동 필요)         │
│  ⚠️ S09: 주식 매도/매수 (한투 API 연동 필요)        │
│  ⚠️ S10: 관심 종목 브리핑 (DB 필요)                 │
│  ⚠️ S12: 초보자 용어 사전 (S03 확장)                │
│                                                        │
└──────────────────────────────────────────────────────┘
```

---

## 🔧 환경 설정

### 필수 환경 변수
```env
# Google Gemini API (리포트 생성)
GEMINI_API_KEY=your_gemini_api_key

# DART API (재무제표)
DART_API_KEY=your_dart_api_key

# 한국투자증권 API (계좌 연동)
KIS_APP_KEY=your_kis_app_key
KIS_APP_SECRET=your_kis_app_secret
KIS_ACCOUNT_ID=12345678
KIS_ACCOUNT_SUFFIX=01
KIS_ENV=prod
```

### Python 패키지
```bash
pip install -r requirements.txt
```

**주요 패키지**:
- `google-generativeai` - Gemini LLM
- `FinanceDataReader` - 주가 데이터
- `pandas`, `numpy` - 데이터 처리
- `plotly` - 차트 생성
- `streamlit` - 대시보드

---

## 📁 전달 파일 목록

### 핵심 모듈 (12개)
```
✅ S02 종목 리포트:
   - stock_report_realtime.py
   - stock_report_api.py
   - dart_financial_loader.py
   - dart_client.py
   - metrics_calculator.py
   - kakao_report_formatter.py

✅ S03 주식 용어 사전:
   - glossary_api.py
   - glossary.json

✅ S05 물타기 계산기:
   - averaging_calculator.py

✅ S08 계좌 연결:
   - HantuStock.py

✅ S11 실시간 차트:
   - stock_chart_visualizer.py
   - stock_analyzer.py
   - app.py
```

### 데이터 파일
- `glossary.json` - 73개 용어
- `sample_data_*.json` - 3개 종목 샘플 리포트

### 문서
- `BACKEND_API_SPEC.md` - API 명세서
- `PROJECT_MODULES_SUMMARY.md` - 모듈 구조도

---

## 🧪 테스트 가이드

### S02 종목 리포트
```bash
python stock_report_realtime.py
# 입력: 005930
```

### S03 용어 사전
```bash
python glossary_api.py
# 입력: PER
```

### S05 물타기 계산
```bash
python averaging_calculator.py
```

### S08 계좌 연결
```bash
# .env 설정 후
python HantuStock.py
```

### S11 차트 대시보드
```bash
streamlit run app.py
```

---

## 💡 종합 사용 예제

### 카카오톡 스킬 서버 예제 (S02 종목 리포트)

```python
from stock_report_realtime import RealtimeStockReportGenerator
from kakao_report_formatter import KakaoReportFormatter

def kakao_skill_report(ticker: str) -> dict:
    """
    카카오톡 종목 리포트 스킬

    Args:
        ticker: 종목 코드 (예: "005930")

    Returns:
        카카오톡 응답 JSON
    """
    # Step 1: 리포트 생성
    generator = RealtimeStockReportGenerator()
    report = generator.generate_report(ticker)

    # Step 2: 카카오톡 포맷 변환
    formatter = KakaoReportFormatter()
    kakao_response = formatter.format_for_kakao(
        report,
        detail_url=f"https://yourapp.com/report/{ticker}"
    )

    return kakao_response

# 사용
response = kakao_skill_report("005930")
```

---

## 📞 참고 문서

- **API 명세서**: `BACKEND_API_SPEC.md`
- **모듈 구조도**: `PROJECT_MODULES_SUMMARY.md`
- **상세 사용법**: 각 파일의 docstring
- **테스트 코드**: 각 파일의 `if __name__ == "__main__"` 블록

---

## 🚧 백엔드 팀 구현 필요 사항

### 1. FastAPI 엔드포인트 (S02, S03, S05, S08, S11)
```python
# 예시 구조
from fastapi import FastAPI
from stock_report_realtime import RealtimeStockReportGenerator

app = FastAPI()

@app.post("/api/v1/report/generate")
async def generate_report(ticker: str):
    generator = RealtimeStockReportGenerator()
    report = generator.generate_report(ticker)
    return report
```

### 2. 카카오톡 스킬 서버 래핑
- 각 서비스(S02, S03, S05 등)를 카카오톡 스킬 형식으로 래핑
- ItemCard, TextCard, Carousel 등 포맷 구현

### 3. 웹 페이지 구현
- `/s/{ticker}` - 종목 차트 페이지
- `/report/{ticker}` - 상세 리포트 페이지
- `/portfolio/monthly` - 월간 투자 요약

### 4. 미완성 기능 구현
- S06: 커뮤니티/뉴스 크롤링
- S07: 거래내역 데이터 연동
- S09: 주식 매도/매수
- S10: 관심 종목 브리핑

---

**생성일**: 2026-01-04
**Python 버전**: 3.8+
**완료된 서비스**: S02, S03, S05, S08, S11 (총 5개)
