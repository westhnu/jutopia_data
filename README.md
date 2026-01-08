# 주식 AI 챗봇 백엔드

카카오톡 기반 주식 초보자를 위한 AI 챗봇 서비스 - 핵심 비즈니스 로직

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📦 프로젝트 개요

주식 초보자를 위한 카카오톡 챗봇의 **핵심 비즈니스 로직**을 구현한 Python 프로젝트입니다.

**완료된 기능 (5개)**:
- ✅ S02: 종목 리포트 조회 (LLM 기반 AI 분석)
- ✅ S03: 주식 용어 사전 (73개 용어)
- ✅ S05: 물타기 계산기 (평단가 계산)
- ✅ S08: 계좌 연결 (한국투자증권 API)
- ✅ S11: 실시간 차트 (6가지 차트)

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 환경 변수 설정 (.env 파일)
GEMINI_API_KEY=your_gemini_api_key
DART_API_KEY=your_dart_api_key
KIS_APP_KEY=your_kis_app_key
KIS_APP_SECRET=your_kis_app_secret
```

### 2. 테스트 실행

```bash
# 종목 리포트 생성
python stock_report_realtime.py

# 주식 용어 검색
python glossary_api.py

# 물타기 계산
python averaging_calculator.py

# Streamlit 차트 대시보드
streamlit run app.py
```

---

## 📁 프로젝트 구조

```
PythonProject/
├── docs/                          # 📚 백엔드 전달 문서
│   ├── BACKEND_HANDOVER.md        # 핵심 핸드오버 문서
│   ├── BACKEND_API_SPEC.md        # API 명세서
│   ├── PROJECT_MODULES_SUMMARY.md # 모듈 구조
│   └── IMPLEMENTATION_STATUS.md   # 구현 현황
│
├── data/                          # 📊 데이터
│   ├── glossary.json              # 용어 사전 (73개)
│   └── sample_data_*.json         # 샘플 리포트
│
├── tests/                         # 🧪 테스트
│   ├── test_kakao_format.py
│   ├── test_kakao_integration.py
│   └── test_dart_direct.py
│
├── [핵심 Python 모듈]             # 🔧 비즈니스 로직
│   ├── stock_report_realtime.py   # S02: 리포트 생성
│   ├── glossary_api.py            # S03: 용어 사전
│   ├── averaging_calculator.py    # S05: 물타기 계산
│   ├── HantuStock.py              # S08: 계좌 연동
│   ├── stock_chart_visualizer.py  # S11: 차트 생성
│   └── ...                        # 지원 모듈들
│
└── README.md                      # 이 파일
```

---

## 💡 주요 기능

### S02 종목 리포트

LLM 기반 AI 투자 분석 리포트 자동 생성

```python
from stock_report_realtime import RealtimeStockReportGenerator

generator = RealtimeStockReportGenerator()
report = generator.generate_report("005930")  # 삼성전자

# 5개 섹션: 투자요약, 주가동향, 재무분석, 밸류에이션, 투자의견
print(report['report']['sections']['summary'])
```

**기능**:
- DART API 실시간 재무제표 조회
- PER, PBR, ROE 자동 계산
- 기술적 지표 분석 (RSI, 이동평균)

---

### S03 주식 용어 사전

73개 주식 용어 데이터베이스

```python
from glossary_api import GlossaryAPI

api = GlossaryAPI()
term = api.lookup("PER")
print(term['description'])  # 상세 설명
print(term['formula'])      # 계산 공식
print(term['related_terms']) # 연관 용어
```

**기능**:
- 정확한 용어 검색
- 유사 용어 검색
- 18개 카테고리별 분류

---

### S05 물타기 계산기

평단가 낮추기 위한 추가 매수 시뮬레이션

```python
from averaging_calculator import AveragingCalculator

calc = AveragingCalculator(
    current_price=70000,
    avg_price=80000,
    quantity=10
)

scenarios = calc.calculate_scenarios()  # 1주, 5주, 10주
print(scenarios[0]['new_avg_price'])    # 새로운 평단가
```

---

### S08 계좌 연결

한국투자증권 OpenAPI 연동

```python
from HantuStock import HantuStock

client = HantuStock()
holdings = client.get_holding_stock_detail()  # 보유 종목
cash = client.get_holding_cash()              # 잔고
```

---

### S11 실시간 차트

6가지 스타일의 차트 생성

```python
from stock_chart_visualizer import StockChartVisualizer

viz = StockChartVisualizer()
fig = viz.create_candlestick_chart("005930", days=60)
fig.show()  # 브라우저에서 열림
```

**차트 종류**:
- 캔들스틱 + 이동평균선
- 기술적 차트 (볼린저밴드 + RSI)
- 라인 차트
- 거래량 차트
- 다중 종목 비교
- 지수 차트 (KOSPI, KOSDAQ)

---

## 🔧 환경 변수

```env
# Google Gemini (리포트 생성)
GEMINI_API_KEY=your_key

# DART API (재무제표)
DART_API_KEY=your_key

# 한국투자증권 (계좌 연동)
KIS_APP_KEY=your_key
KIS_APP_SECRET=your_secret
KIS_ACCOUNT_ID=12345678
KIS_ACCOUNT_SUFFIX=01
KIS_ENV=prod  # prod, vps, paper
```

---

## 📚 문서

전체 문서는 [`docs/`](docs/) 폴더를 참고하세요:

- **[BACKEND_HANDOVER.md](docs/BACKEND_HANDOVER.md)** - 백엔드 팀 핸드오버 메인 문서
- **[BACKEND_API_SPEC.md](docs/BACKEND_API_SPEC.md)** - API 명세서
- **[PROJECT_MODULES_SUMMARY.md](docs/PROJECT_MODULES_SUMMARY.md)** - 모듈 구조 및 의존성
- **[IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md)** - 기획서 대비 구현 현황

---

## 🧪 테스트

```bash
# 각 기능별 테스트
cd tests/
python test_kakao_format.py
python test_kakao_integration.py
python test_dart_direct.py
```

---

## 📦 필수 패키지

```bash
# 핵심 패키지
google-generativeai  # Gemini LLM
FinanceDataReader    # 주가 데이터
pandas, numpy        # 데이터 처리
plotly               # 차트 생성
streamlit            # 대시보드
requests             # API 호출
```

---

## 🚧 백엔드 팀 작업 필요

이 프로젝트는 **핵심 비즈니스 로직**만 포함합니다. 다음 작업이 필요합니다:

1. **FastAPI 엔드포인트 구현**
   - `/api/v1/report/generate`
   - `/api/v1/glossary/{term}`
   - `/api/v1/averaging/calculate`
   - etc.

2. **카카오톡 스킬 서버 래핑**
   - ItemCard, TextCard, Carousel 포맷 구현

3. **웹 페이지 구현**
   - `/s/{ticker}` - 종목 차트
   - `/report/{ticker}` - 상세 리포트

자세한 내용은 [`docs/BACKEND_HANDOVER.md`](docs/BACKEND_HANDOVER.md)를 참고하세요.

---

## 📞 문의

프로젝트 관련 질문은 이슈를 등록해주세요.

---

**버전**: 2.0
**최종 업데이트**: 2026-01-06
**완료된 서비스**: S02, S03, S05, S08, S11
