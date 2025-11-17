# 📈 주식 차트 시각화 시스템

실시간 한국 주식 데이터 분석 및 인터랙티브 차트 대시보드

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## 🌐 온라인 데모

**배포된 앱**: https://your-app.streamlit.app (배포 후 업데이트)

---

## 🚀 로컬 실행

### 1. 저장소 클론
```bash
git clone https://github.com/westhnu/stock-chart-dashboard.git
cd stock-chart-dashboard
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 실행
```bash
streamlit run app.py
```

그게 끝입니다! 🎉

---

## 📁 파일 구조

```
PythonProject/
├── 📊 차트 시각화 (핵심)
│   ├── app.py                      # Streamlit 웹 앱
│   ├── stock_analyzer.py           # 데이터 분석 엔진 (CSV + 실시간 API)
│   └── stock_chart_visualizer.py   # Plotly 차트 생성
│
├── 📥 데이터 수집 (선택적)
│   ├── main.py                     # 데이터 수집 실행
│   ├── HantuStock.py               # 한국투자증권 API
│   ├── dart_client.py              # DART 재무제표
│   └── collectors.py               # FinanceDataReader/pykrx
│
└── 📚 문서
    ├── README.md                   # 이 파일
    └── QUICK_START.md              # 상세 가이드
```

---

## 🎯 주요 기능

### 1. 실시간 데이터 수집
- **FinanceDataReader API** 사용
- 종목 검색 시 즉시 최신 데이터
- CSV 파일 불필요

### 2. 인터랙티브 차트
- 캔들스틱 차트 (이동평균선 포함)
- 기술적 분석 (볼린저밴드, RSI, 거래량)
- 줌/패닝 가능

### 3. 종목 검색
- 종목 코드 직접 입력
- 빠른 선택 버튼

---

## 💻 사용 방법

### Streamlit 웹 앱
```bash
streamlit run app.py
```

### Python 코드로 사용
```python
from stock_analyzer import StockAnalyzer
from stock_chart_visualizer import StockChartVisualizer

# 실시간 모드
analyzer = StockAnalyzer(use_realtime=True)
visualizer = StockChartVisualizer(analyzer=analyzer)

# 종목 정보
info = visualizer.get_stock_info('005930')
print(f"{info['name']}: {info['current_price']:,}원")

# 차트 생성
fig = visualizer.create_candlestick_chart('005930', days=60)
fig.show()  # 브라우저에서 열림
```

---

## 🔧 모드 전환

### CSV 모드 (오프라인)
```python
# CSV 파일에서 데이터 읽기
analyzer = StockAnalyzer()  # use_realtime=False (기본)
```

먼저 데이터 수집 필요:
```bash
python main.py
```

### 실시간 모드 (온라인)
```python
# API로 실시간 데이터
analyzer = StockAnalyzer(use_realtime=True)
```

---

## 📊 차트 종류

### 1. 캔들스틱 차트
```python
fig = visualizer.create_candlestick_chart(ticker='005930', days=60)
```
- 캔들스틱 (빨강: 상승, 파랑: 하락)
- 5일/20일/60일 이동평균선

### 2. 기술적 분석 차트
```python
fig = visualizer.create_technical_chart(ticker='005930', days=60)
```
- 볼린저 밴드
- 거래량
- RSI

### 3. 가격 라인 차트
```python
fig = visualizer.create_price_line_chart(ticker='005930', days=60)
```

### 4. 종목 비교
```python
fig = visualizer.create_comparison_chart(['005930', '000660', '035420'], days=60)
```

### 5. 시장 지수
```python
fig = visualizer.create_index_chart(index_code='KS11', days=120)
```

---

## 🌐 웹 프레임워크 통합

### FastAPI
```python
from fastapi import FastAPI
from stock_chart_visualizer import StockChartVisualizer

app = FastAPI()
visualizer = StockChartVisualizer(analyzer=StockAnalyzer(use_realtime=True))

@app.get("/chart/{ticker}")
def get_chart(ticker: str):
    fig = visualizer.create_candlestick_chart(ticker, days=60)
    return {"html": fig.to_html(include_plotlyjs='cdn')}
```

### Flask
```python
from flask import Flask
from stock_chart_visualizer import StockChartVisualizer

app = Flask(__name__)
visualizer = StockChartVisualizer(analyzer=StockAnalyzer(use_realtime=True))

@app.route('/chart/<ticker>')
def chart(ticker):
    fig = visualizer.create_candlestick_chart(ticker, days=60)
    return fig.to_html(include_plotlyjs='cdn')
```

---

## 🔑 주요 클래스

### StockAnalyzer
- `load_price_data(ticker, days)` - 주가 데이터
- `analyze_stock_technical(ticker, indicators)` - 기술적 분석
- `calculate_rsi(prices)` - RSI 계산

### StockChartVisualizer
- `create_candlestick_chart(ticker, days)` - 캔들스틱
- `create_technical_chart(ticker, days)` - 기술적 분석
- `create_comparison_chart(tickers, days)` - 종목 비교
- `get_stock_info(ticker)` - 종목 정보

---

## 📦 필수 패키지

```bash
pip install streamlit plotly pandas numpy FinanceDataReader
```

---

## 🎨 커스터마이징

### 차트 크기 변경
```python
fig = visualizer.create_candlestick_chart('005930', days=60)
fig.update_layout(height=800, width=1200)
```

### 테마 변경
```python
fig.update_layout(template='plotly_dark')  # 다크 모드
```

---

## 🔧 문제 해결

### Q1. "데이터를 찾을 수 없습니다"
**A:** 실시간 모드를 사용하세요.
```python
analyzer = StockAnalyzer(use_realtime=True)
```

### Q2. "ModuleNotFoundError: No module named 'FinanceDataReader'"
**A:** 패키지를 설치하세요.
```bash
pip install FinanceDataReader
```

### Q3. 차트가 느려요
**A:** Streamlit 캐싱 사용
```python
@st.cache_data(ttl=600)  # 10분 캐시
def get_stock_data(ticker, days):
    return analyzer.load_price_data(ticker, days)
```

---

## 📚 더 알아보기

- [QUICK_START.md](QUICK_START.md) - 상세 가이드
- Streamlit 앱: `streamlit run app.py`

---

**버전**: 1.0
**업데이트**: 2024-11-17
