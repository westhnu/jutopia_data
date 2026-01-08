# 프로젝트 모듈 및 기능 전체 정리

## 📋 목차
1. [핵심 기능별 모듈 분류](#1-핵심-기능별-모듈-분류)
2. [모듈 의존성 관계도](#2-모듈-의존성-관계도)
3. [재사용 가능한 공통 모듈](#3-재사용-가능한-공통-모듈)
4. [독립 실행 가능한 모듈](#4-독립-실행-가능한-모듈)
5. [통합 모듈 (여러 모듈 조합)](#5-통합-모듈-여러-모듈-조합)
6. [백엔드 전달용 핵심 파일](#6-백엔드-전달용-핵심-파일)

---

## 1. 핵심 기능별 모듈 분류

### 🔷 A. 데이터 수집 (Data Collection)

#### A1. 주가 데이터
| 파일명 | 크기 | 역할 | 의존성 | 재사용 |
|--------|------|------|--------|--------|
| `stock_analyzer.py` | 701줄 | 주가 데이터 로드 및 분석 | FinanceDataReader, pykrx | ✅ 높음 |
| `collectors.py` | 138줄 | 주가/지수 데이터 수집 오케스트레이터 | stock_analyzer.py | △ 중간 |
| `main.py` | 138줄 | 전체 데이터 수집 실행 | collectors.py | ❌ 낮음 |

**주요 메서드:**
```python
# stock_analyzer.py
load_price_data(ticker, days)           # 주가 OHLCV 조회
analyze_stock_technical(ticker, indicators)  # 기술적 분석
calculate_rsi(prices, period)           # RSI 계산
calculate_bollinger_bands(prices)       # 볼린저밴드
```

---

#### A2. 재무제표 데이터
| 파일명 | 크기 | 역할 | 의존성 | 재사용 |
|--------|------|------|--------|--------|
| `dart_client.py` | 67줄 | DART API 클라이언트 | requests, xml | ✅ 높음 |
| `dart_financial_loader.py` | 166줄 | 재무제표 로더 | dart_client.py | ✅ 높음 |
| `financial_analyzer.py` | 274줄 | 재무비율 계산 | pandas | ✅ 높음 |
| `metrics_calculator.py` | 179줄 | PER/PBR/ROE 계산 | pandas | ✅ 높음 |

**주요 메서드:**
```python
# dart_client.py
get_corp_code(stock_code)              # 종목코드 → DART 코드 변환
get_financials(corp_code, year, ...)   # 재무제표 조회

# dart_financial_loader.py
load_financials(ticker)                # 재무제표 조회 + 텍스트 변환

# metrics_calculator.py
calculate_from_dataframe(df, price)    # 재무제표 → PER/PBR/ROE
```

---

#### A3. 한국투자증권 API
| 파일명 | 크기 | 역할 | 의존성 | 재사용 |
|--------|------|------|--------|--------|
| `HantuStock.py` | 361줄 | 한투 API 래퍼 | requests | ✅ 높음 |

**주요 메서드:**
```python
get_holding_stock_detail()             # 보유 종목 상세 조회
get_holding_stock(ticker)              # 특정 종목 보유 수량
get_holding_cash()                     # 현금 잔고
```

---

### 🔷 B. 데이터 분석 (Data Analysis)

#### B1. 주식 리포트 API
| 파일명 | 크기 | 역할 | 의존성 | 재사용 |
|--------|------|------|--------|--------|
| `stock_report_api.py` | 558줄 | 종목 리포트 API | stock_analyzer, financial_analyzer | ✅ 높음 |

**주요 메서드:**
```python
get_basic_info(ticker)                 # 기본 정보 (현재가, 시총)
get_price_trend(ticker)                # 가격 추세 (1m/3m/1y)
get_key_metrics(ticker)                # PER/PBR/ROE 등
get_technical_analysis(ticker)         # 기술적 분석
get_financial_trend(ticker)            # 재무 추세
get_chart_data(ticker, days)           # 차트 데이터
get_complete_report(ticker)            # 전체 통합 리포트
```

**재사용:**
- ✅ **stock_report_realtime.py**에서 사용
- ✅ **stock_report_with_rag.py**에서 사용
- ✅ 백엔드 API 엔드포인트로 사용 가능

---

#### B2. 물타기 계산기
| 파일명 | 크기 | 역할 | 의존성 | 재사용 |
|--------|------|------|--------|--------|
| `averaging_calculator.py` | 369줄 | 물타기 평단가 계산 | 없음 (순수 계산) | ✅ 높음 |

**주요 메서드:**
```python
calculate(avg_price, qty, curr_price, add_qty)  # 기본 계산
calculate_scenarios(avg, qty, curr, scenarios)  # 시나리오 분석
calculate_target_quantity(avg, qty, curr, target)  # 목표 평단가 역산
format_result(result, ticker_name)              # 카카오톡 포맷
```

**재사용:**
- ✅ 백엔드 물타기 API에서 사용 예정
- ✅ 카카오톡 챗봇 통합 예정

---

### 🔷 C. LLM 리포트 생성 (Report Generation)

#### C1. 실시간 리포트 생성
| 파일명 | 크기 | 역할 | 의존성 | 재사용 |
|--------|------|------|--------|--------|
| `stock_report_realtime.py` | 300줄+ | 실시간 리포트 생성 | stock_report_api, dart_financial_loader, Gemini | ✅ 높음 |

**주요 메서드:**
```python
generate_report(ticker)                # 전체 리포트 생성
_collect_quantitative_data(ticker)     # 정량 데이터 수집
_generate_report_with_llm(...)         # LLM 리포트 생성
```

**출력 형식:**
```python
{
    'metadata': {'ticker', 'company_name', 'generated_at', 'has_financials'},
    'report': {
        'title': '...',
        'full_text': '...',
        'sections': {
            'summary': '투자 요약',
            'price_analysis': '주가 동향 분석',
            'financial_analysis': '재무 상태 분석',
            'valuation': '밸류에이션',
            'investment_opinion': '투자 의견'
        }
    },
    'raw_data': {'basic', 'price_trend', 'metrics', 'technical', 'financial_trend'}
}
```

**재사용:**
- ✅ **kakao_report_formatter.py**에서 사용
- ✅ **generate_sample.py**에서 사용
- ✅ 백엔드 리포트 API로 사용 가능

---

#### C2. RAG 기반 리포트 생성
| 파일명 | 크기 | 역할 | 의존성 | 재사용 |
|--------|------|------|--------|--------|
| `stock_report_with_rag.py` | 451줄 | RAG 기반 리포트 | financial_rag_gemini, stock_report_api | △ 중간 |
| `financial_rag_gemini.py` | 441줄 | Gemini RAG 시스템 | Pinecone, Gemini | △ 중간 |

**주요 메서드:**
```python
# stock_report_with_rag.py
generate_report(ticker, report_type)   # RAG 리포트 생성

# financial_rag_gemini.py
ingest_dart_financials(ticker)         # 재무제표 임베딩
search(query, ticker, k)               # 유사 문서 검색
ask(question, ticker)                  # RAG 질의응답
```

**재사용:**
- △ Pinecone 필요 (옵션)
- △ 뉴스 크롤링 RAG에 활용 가능

---

### 🔷 D. 카카오톡 챗봇 통합 (Kakao Integration)

#### D1. 리포트 포맷터
| 파일명 | 크기 | 역할 | 의존성 | 재사용 |
|--------|------|------|--------|--------|
| `kakao_report_formatter.py` | 363줄 | 카카오톡 API 2.0 포맷 | 없음 (포맷만) | ✅ 높음 |

**주요 메서드:**
```python
format_for_kakao(report_data, detail_url)  # 카카오톡 응답 생성
_create_detail(report_data)                # 상세 리포트
_create_summary_from_detail(detail)        # 요약 추출
_create_kakao_response(summary, url)       # API 응답 포맷
_extract_opinion(opinion_text)             # 투자 의견 추출
```

**출력 형식:**
```python
{
    'summary': {
        'basic_info': {...},
        'key_metrics': {...},
        'investment_opinion': {...},
        'brief_summary': '...'
    },
    'detail': {...},
    'kakao_response': {
        'version': '2.0',
        'template': {
            'outputs': [
                {'basicCard': {...}},
                {'listCard': {...}}
            ]
        }
    }
}
```

**재사용:**
- ✅ 백엔드 카카오톡 스킬 서버에서 사용
- ✅ 다른 카드 형식 추가 가능

---

#### D2. 용어 사전 API
| 파일명 | 크기 | 역할 | 의존성 | 재사용 |
|--------|------|------|--------|--------|
| `glossary_api.py` | 362줄 | 주식 용어 검색 | glossary.json | ✅ 높음 |
| `glossary.json` | 974줄 | 용어 데이터 (73개) | 없음 | ✅ 높음 |

**주요 메서드:**
```python
lookup(term)                           # 용어 검색
search_by_category(category)           # 카테고리별 검색
get_related_terms(term)                # 연관 용어 조회
find_similar(query, limit)             # 유사 용어 검색
format_term_card(term)                 # 카카오톡 카드 포맷
get_categories()                       # 카테고리 목록
count_terms()                          # 총 용어 수
```

**재사용:**
- ✅ 백엔드 용어 사전 API로 사용
- ✅ Full Context LLM으로 확장 가능

---

### 🔷 E. 리포트 포맷팅 (Report Formatting)

| 파일명 | 크기 | 역할 | 의존성 | 재사용 |
|--------|------|------|--------|--------|
| `report_formatter.py` | 233줄 | 리포트 텍스트 포맷 | 없음 | ✅ 높음 |

**주요 메서드:**
```python
format_full_report(report_data)        # 전체 리포트 텍스트
format_summary(report_data)            # 요약 텍스트
format_metrics_table(report_data)      # 지표 테이블
extract_investment_opinion(report_data) # 투자 의견 추출
```

---

### 🔷 F. 차트 시각화 (Visualization)

| 파일명 | 크기 | 역할 | 의존성 | 재사용 |
|--------|------|------|--------|--------|
| `stock_chart_visualizer.py` | 477줄 | Plotly 차트 생성 | stock_analyzer, plotly | ✅ 높음 |
| `app.py` | 211줄 | Streamlit 대시보드 | stock_analyzer, stock_chart_visualizer | △ 중간 |

**주요 메서드:**
```python
# stock_chart_visualizer.py
create_candlestick_chart(ticker, days)     # 캔들스틱 차트
create_technical_chart(ticker, days)       # 기술적 지표 차트
create_price_line_chart(ticker, days)      # 가격 라인 차트
create_volume_chart(ticker, days)          # 거래량 차트
create_comparison_chart(tickers, days)     # 다중 종목 비교
create_index_chart(index_code, days)       # 지수 차트
```

**재사용:**
- ✅ 웹 대시보드
- ✅ 카카오톡 차트 이미지 전송

---

### 🔷 G. 웹 크롤링 (Web Crawling)

| 파일명 | 크기 | 역할 | 의존성 | 재사용 |
|--------|------|------|--------|--------|
| `Taviliy_Ingestion/3-3.Tavily_ingestion.py` | 500줄 | Tavily 웹 크롤러 | Tavily API, Pinecone | △ 중간 |

**주요 기능:**
- 웹사이트 사이트맵 크롤링
- 배치 처리로 URL 추출
- Pinecone 벡터 저장

**재사용:**
- △ 뉴스 크롤링 RAG에 활용 가능

---

### 🔷 H. 테스트 및 샘플 생성 (Testing & Samples)

| 파일명 | 크기 | 역할 | 의존성 | 재사용 |
|--------|------|------|--------|--------|
| `generate_sample.py` | 107줄 | 백엔드 샘플 데이터 생성 | stock_report_realtime, kakao_report_formatter | ✅ 높음 |
| `test_kakao_integration.py` | 67줄 | 카카오 통합 테스트 | stock_report_realtime, kakao_report_formatter | △ 중간 |
| `quick_report.py` | 42줄 | 간단 리포트 생성 | stock_report_realtime | △ 중간 |
| `generate_report_simple.py` | 107줄 | 단순 리포트 생성 | stock_report_realtime | △ 중간 |

---

## 2. 모듈 의존성 관계도

### 계층 구조 (Layer Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: 애플리케이션 (Application)                         │
│  - app.py (Streamlit)                                       │
│  - generate_sample.py (백엔드 샘플 생성)                     │
│  - test_kakao_integration.py (테스트)                       │
└─────────────────────────────────────────────────────────────┘
                           ↓ 의존
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: 통합/포맷팅 (Integration & Formatting)             │
│  - stock_report_realtime.py (실시간 리포트 생성)             │
│  - stock_report_with_rag.py (RAG 리포트 생성)               │
│  - kakao_report_formatter.py (카카오톡 포맷)                │
│  - report_formatter.py (텍스트 포맷)                        │
└─────────────────────────────────────────────────────────────┘
                           ↓ 의존
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: 비즈니스 로직 (Business Logic)                     │
│  - stock_report_api.py (리포트 API)                         │
│  - averaging_calculator.py (물타기 계산)                    │
│  - glossary_api.py (용어 사전)                              │
│  - financial_rag_gemini.py (RAG 시스템)                     │
│  - stock_chart_visualizer.py (차트 생성)                    │
└─────────────────────────────────────────────────────────────┘
                           ↓ 의존
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: 데이터 처리 (Data Processing)                     │
│  - stock_analyzer.py (주가 분석)                            │
│  - financial_analyzer.py (재무 분석)                        │
│  - metrics_calculator.py (지표 계산)                        │
│  - dart_financial_loader.py (재무제표 로더)                │
└─────────────────────────────────────────────────────────────┘
                           ↓ 의존
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: 데이터 소스 (Data Sources)                         │
│  - dart_client.py (DART API)                                │
│  - HantuStock.py (한투 API)                                 │
│  - FinanceDataReader (외부 라이브러리)                       │
│  - pykrx (외부 라이브러리)                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 재사용 가능한 공통 모듈

### 🔵 최고 재사용성 (Core Modules) ⭐⭐⭐

| 파일명 | 용도 | 의존성 | 재사용처 |
|--------|------|--------|----------|
| `stock_analyzer.py` | 주가 데이터 로드 | FinanceDataReader | stock_report_api, stock_chart_visualizer, app |
| `stock_report_api.py` | 종목 리포트 API | stock_analyzer, financial_analyzer | stock_report_realtime, stock_report_with_rag |
| `dart_client.py` | DART API 클라이언트 | requests | dart_financial_loader, collectors |
| `averaging_calculator.py` | 물타기 계산 | 없음 | 백엔드 API (예정) |
| `kakao_report_formatter.py` | 카카오톡 포맷 | 없음 | 백엔드 스킬 서버 (예정) |
| `glossary_api.py` | 용어 사전 | glossary.json | 백엔드 API (예정) |

**특징:**
- ✅ 의존성 최소
- ✅ 테스트 완료
- ✅ 문서화됨
- ✅ 다른 프로젝트에도 사용 가능

---

### 🔵 중간 재사용성 (Support Modules) ⭐⭐

| 파일명 | 용도 | 의존성 | 재사용처 |
|--------|------|--------|----------|
| `dart_financial_loader.py` | 재무제표 로더 | dart_client | stock_report_realtime |
| `metrics_calculator.py` | 지표 계산 | pandas | stock_report_realtime |
| `financial_analyzer.py` | 재무 분석 | pandas | stock_report_api |
| `report_formatter.py` | 텍스트 포맷 | 없음 | stock_report_realtime |
| `stock_chart_visualizer.py` | 차트 생성 | plotly, stock_analyzer | app |

**특징:**
- ✅ 특정 기능에 특화
- △ 일부 의존성 있음
- ✅ 관련 모듈에서 재사용

---

### 🔵 낮은 재사용성 (Specific Modules) ⭐

| 파일명 | 용도 | 이유 |
|--------|------|------|
| `stock_report_realtime.py` | 실시간 리포트 | 통합 모듈 (여러 모듈 조합) |
| `stock_report_with_rag.py` | RAG 리포트 | Pinecone 의존 |
| `financial_rag_gemini.py` | RAG 시스템 | Pinecone 필요 |
| `app.py` | Streamlit 앱 | UI 특화 |
| `main.py` | 데이터 수집 | 오케스트레이터 |
| `collectors.py` | 데이터 수집 | 특정 작업 전용 |

**특징:**
- △ 여러 모듈 통합
- △ 특정 환경 의존
- ❌ 직접 재사용 어려움

---

## 4. 독립 실행 가능한 모듈

### ✅ 단독 실행 가능 (if __name__ == "__main__":)

| 파일명 | 실행 방법 | 용도 |
|--------|----------|------|
| `stock_analyzer.py` | `python stock_analyzer.py` | 주가 분석 테스트 |
| `stock_chart_visualizer.py` | `python stock_chart_visualizer.py` | 차트 생성 테스트 |
| `dart_financial_loader.py` | `python dart_financial_loader.py` | 재무제표 조회 테스트 |
| `averaging_calculator.py` | `python averaging_calculator.py` | 물타기 계산 테스트 |
| `glossary_api.py` | `python glossary_api.py` | 용어 검색 테스트 |
| `kakao_report_formatter.py` | `python kakao_report_formatter.py` | 카카오 포맷 테스트 |
| `generate_sample.py` | `python generate_sample.py` | 백엔드 샘플 생성 |
| `test_kakao_integration.py` | `python test_kakao_integration.py` | 통합 테스트 |
| `app.py` | `streamlit run app.py` | 대시보드 실행 |

---

## 5. 통합 모듈 (여러 모듈 조합)

### 패턴 1: 리포트 생성 파이프라인

```
stock_report_realtime.py
    ├─ stock_report_api.py
    │   ├─ stock_analyzer.py
    │   └─ financial_analyzer.py
    ├─ dart_financial_loader.py
    │   └─ dart_client.py
    ├─ metrics_calculator.py
    └─ report_formatter.py
```

**사용처:**
- 백엔드 리포트 API
- 카카오톡 챗봇 (종목 리포트 기능)

---

### 패턴 2: 카카오톡 통합

```
generate_sample.py
    ├─ stock_report_realtime.py (리포트 생성)
    └─ kakao_report_formatter.py (카카오톡 포맷)
```

**사용처:**
- 백엔드 샘플 데이터 생성
- 카카오톡 스킬 서버 테스트

---

### 패턴 3: 물타기 계산

```
[백엔드 API - 구현 예정]
    ├─ HantuStock.py (계좌 조회)
    ├─ stock_report_api.py (현재가 조회)
    └─ averaging_calculator.py (물타기 계산)
```

**사용처:**
- 카카오톡 챗봇 (물타기 계산기)

---

## 6. 백엔드 전달용 핵심 파일

### 📦 Package 1: 종목 리포트 API

```
stock_report_package/
├── stock_analyzer.py              # 주가 분석 (필수)
├── stock_report_api.py            # 리포트 API (필수)
├── financial_analyzer.py          # 재무 분석 (필수)
├── dart_client.py                 # DART API (필수)
├── dart_financial_loader.py       # 재무제표 로더 (필수)
├── metrics_calculator.py          # 지표 계산 (필수)
├── stock_report_realtime.py       # 실시간 리포트 생성 (필수)
├── kakao_report_formatter.py      # 카카오톡 포맷 (필수)
├── report_formatter.py            # 텍스트 포맷 (선택)
└── generate_sample.py             # 샘플 생성 (선택)
```

**의존 라이브러리:**
```
pandas
numpy
FinanceDataReader
pykrx
requests
google-generativeai
plotly (차트 필요 시)
```

---

### 📦 Package 2: 물타기 계산기 API

```
averaging_package/
├── HantuStock.py                  # 한투 API (필수)
├── stock_report_api.py            # 현재가 조회용 (필수)
├── stock_analyzer.py              # 주가 데이터 (필수)
├── averaging_calculator.py        # 물타기 계산 (필수)
└── averaging_samples.json         # API 스펙 (선택)
```

**의존 라이브러리:**
```
requests
pandas
FinanceDataReader
```

---

### 📦 Package 3: 용어 사전 API

```
glossary_package/
├── glossary_api.py                # 용어 API (필수)
├── glossary.json                  # 용어 데이터 (필수)
└── GLOSSARY_RAG_ANALYSIS.md       # 분석 문서 (선택)
```

**의존 라이브러리:**
```
json (내장)
```

---

### 📦 Package 4: 차트 생성 API

```
chart_package/
├── stock_analyzer.py              # 주가 데이터 (필수)
├── stock_chart_visualizer.py      # 차트 생성 (필수)
└── app.py                         # Streamlit 앱 (선택)
```

**의존 라이브러리:**
```
plotly
pandas
FinanceDataReader
streamlit (대시보드 필요 시)
```

---

## 7. 모듈 재사용 매트릭스

### 어떤 모듈이 어디에 쓰이는가?

| 모듈 | 리포트 API | 물타기 API | 용어 API | 차트 API | RAG 시스템 |
|------|-----------|-----------|---------|---------|-----------|
| `stock_analyzer.py` | ✅ | ✅ | ❌ | ✅ | ✅ |
| `stock_report_api.py` | ✅ | ✅ | ❌ | ❌ | ✅ |
| `dart_client.py` | ✅ | ❌ | ❌ | ❌ | ✅ |
| `dart_financial_loader.py` | ✅ | ❌ | ❌ | ❌ | ✅ |
| `metrics_calculator.py` | ✅ | ❌ | ❌ | ❌ | ❌ |
| `financial_analyzer.py` | ✅ | ❌ | ❌ | ❌ | ✅ |
| `HantuStock.py` | ❌ | ✅ | ❌ | ❌ | ❌ |
| `averaging_calculator.py` | ❌ | ✅ | ❌ | ❌ | ❌ |
| `glossary_api.py` | ❌ | ❌ | ✅ | ❌ | ❌ |
| `kakao_report_formatter.py` | ✅ | ✅ (예정) | ✅ (예정) | ❌ | ❌ |
| `stock_chart_visualizer.py` | ❌ | ❌ | ❌ | ✅ | ❌ |
| `financial_rag_gemini.py` | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 8. 파일 크기 및 복잡도

### Large Files (300줄 이상)
| 파일명 | 줄 수 | 복잡도 | 주요 기능 |
|--------|-------|--------|----------|
| `stock_analyzer.py` | 701 | 높음 | 주가 분석, 기술적 지표 |
| `stock_report_api.py` | 558 | 중간 | 리포트 API (8개 메서드) |
| `stock_chart_visualizer.py` | 477 | 중간 | 6가지 차트 생성 |
| `stock_report_with_rag.py` | 451 | 높음 | RAG 리포트 생성 |
| `financial_rag_gemini.py` | 441 | 높음 | RAG 시스템 |
| `averaging_calculator.py` | 369 | 중간 | 물타기 계산 (5개 메서드) |
| `glossary_api.py` | 362 | 낮음 | 용어 검색 API |
| `HantuStock.py` | 361 | 중간 | 한투 API 래퍼 |
| `kakao_report_formatter.py` | 363 | 중간 | 카카오톡 포맷 |

### Medium Files (100-300줄)
| 파일명 | 줄 수 | 복잡도 |
|--------|-------|--------|
| `financial_analyzer.py` | 274 | 중간 |
| `report_formatter.py` | 233 | 낮음 |
| `app.py` | 211 | 중간 |
| `metrics_calculator.py` | 179 | 중간 |
| `dart_financial_loader.py` | 166 | 낮음 |
| `collectors.py` | 138 | 낮음 |
| `main.py` | 138 | 낮음 |

### Small Files (100줄 이하)
| 파일명 | 줄 수 | 용도 |
|--------|-------|------|
| `generate_sample.py` | 107 | 샘플 생성 |
| `test_kakao_integration.py` | 67 | 테스트 |
| `dart_client.py` | 67 | DART API |
| `quick_report.py` | 42 | 간단 리포트 |

---

## 9. 환경 변수 요구사항

### 전체 프로젝트에 필요한 환경 변수

```bash
# .env 파일
# DART API (공시 정보)
DART_API_KEY=your_dart_api_key_here

# Gemini API (LLM)
GEMINI_API_KEY=your_gemini_api_key_here

# 한국투자증권 API (계좌 조회)
KIS_APP_KEY=your_kis_app_key_here
KIS_APP_SECRET=your_kis_app_secret_here
KIS_ACCOUNT_ID=12345678
KIS_ACCOUNT_SUFFIX=01
KIS_ENV=prod  # 또는 vps, paper, demo

# Pinecone (RAG - 선택사항)
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_INDEX_NAME=embedding-index

# OpenAI (일부 RAG 기능 - 선택사항)
OPENAI_API_KEY=your_openai_key_here
```

### 모듈별 필요 환경 변수

| 모듈 | 필요 환경 변수 |
|------|---------------|
| 리포트 API | DART_API_KEY, GEMINI_API_KEY |
| 물타기 API | KIS_APP_KEY, KIS_APP_SECRET, KIS_ACCOUNT_ID |
| 용어 API | 없음 |
| 차트 API | 없음 (FinanceDataReader 무료) |
| RAG 시스템 | GEMINI_API_KEY, PINECONE_API_KEY (선택) |

---

## 10. 백엔드 전달 체크리스트

### ✅ 전달할 파일 목록

#### 핵심 모듈 (12개)
- [ ] `stock_analyzer.py`
- [ ] `stock_report_api.py`
- [ ] `financial_analyzer.py`
- [ ] `dart_client.py`
- [ ] `dart_financial_loader.py`
- [ ] `metrics_calculator.py`
- [ ] `stock_report_realtime.py`
- [ ] `kakao_report_formatter.py`
- [ ] `HantuStock.py`
- [ ] `averaging_calculator.py`
- [ ] `glossary_api.py`
- [ ] `report_formatter.py`

#### 데이터 파일 (3개)
- [ ] `glossary.json`
- [ ] `averaging_samples.json`
- [ ] `sample_data_*.json` (샘플 리포트)

#### 문서 파일 (5개)
- [ ] `BACKEND_API_SPEC.md`
- [ ] `RAG_USAGE_PLAN.md`
- [ ] `GLOSSARY_RAG_ANALYSIS.md`
- [ ] `PROJECT_MODULES_SUMMARY.md` (이 파일)
- [ ] `README.md` (작성 필요)

#### 환경 설정 (2개)
- [ ] `.env.example` (환경 변수 템플릿)
- [ ] `requirements.txt` (의존성 목록)

---

## 요약

### 📊 전체 통계
- **총 파일 수**: 30개+
- **핵심 재사용 모듈**: 12개
- **독립 실행 가능**: 9개
- **테스트 완료**: 모든 핵심 모듈
- **문서화**: 주요 모듈 완료

### 🎯 재사용성 Top 5
1. `stock_analyzer.py` - 모든 주가 관련 기능의 기반
2. `stock_report_api.py` - 리포트 생성의 핵심
3. `averaging_calculator.py` - 물타기 계산 (독립적)
4. `kakao_report_formatter.py` - 카카오톡 통합
5. `glossary_api.py` - 용어 사전 (독립적)

### ✅ 백엔드 전달 준비 완료
- 모든 핵심 로직 구현 완료
- API 명세서 작성 완료
- 샘플 데이터 생성 완료
- 남은 작업: FastAPI 엔드포인트 구현 (백엔드 팀)
