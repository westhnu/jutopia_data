# Web_01 백엔드 데이터 가이드 (차트/종목 리스트)

> 작성: 데이터 파트
> 대상: 웹 백엔드 개발자
> 최종 업데이트: 2026-01-26

---

## 1. 전달 파일 및 설정

### 1.1 파일 목록

| 파일명 | 용도 |
|--------|------|
| `stock_chart_data.py` | 차트 페이지 데이터 + Plotly 차트 생성 |
| `stock_list_data.py` | 종목 리스트 데이터 |
| `HantuStock.py` | 한국투자증권 API 연동 (위 파일들이 내부 사용) |
| `.env` | API 인증 정보 (별도 전달) |

### 1.2 필수 패키지

```bash
pip install finance-datareader python-dotenv requests pandas plotly pykrx
```

### 1.3 .env 설정

```env
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCOUNT_ID=your_account_id
KIS_ENV=vps  # vps: 모의투자, prod: 실전
```

---

## 2. Quick Start

### 차트 API (가장 많이 사용)

```python
from stock_chart_data import StockChartDataProvider

provider = StockChartDataProvider()

# Plotly 차트 JSON 생성 - 프론트에 그대로 전달
result = provider.get_chart_api(
    symbol="005930",     # 종목코드
    range="3m",          # 1d, 1m, 3m, 1y
    type="candlestick"   # candlestick, line, technical, volume
)
# result["plotly"] → 프론트엔드 Plotly.js로 렌더링
```

### 종목 리스트 API

```python
from stock_list_data import StockListDataProvider

list_provider = StockListDataProvider()

# 전체 종목 (정렬 포함)
result = list_provider.get_sorted_market_stocks(
    market="KOSPI",        # KOSPI, KOSDAQ, ALL
    sort_by="change_rate", # price, change_rate, volume, name
    order="desc",          # asc, desc
    limit=100
)
```

---

## 3. 메서드 요약

### stock_chart_data.py - StockChartDataProvider

| 메서드 | 용도 | 주요 파라미터 |
|--------|------|---------------|
| `get_chart_api()` | **Plotly 차트 생성 (권장)** | symbol, range, type |
| `get_stock_info()` | 종목 기본 정보 (헤더용) | ticker |
| `get_chart_data()` | 일봉 Raw 데이터 | ticker, period |
| `get_minute_chart_data()` | 5분봉 Raw 데이터 (하루 탭) | ticker |
| `get_fundamental_metrics()` | PER/PBR/ROE 지표 | ticker |
| `get_technical_indicators()` | RSI/MA/추세 분석 | ticker |

### stock_list_data.py - StockListDataProvider

| 메서드 | 용도 | 주요 파라미터 |
|--------|------|---------------|
| `get_sorted_market_stocks()` | 전체 종목 리스트 (정렬) | market, sort_by, order, limit |
| `get_holding_stocks()` | 보유 종목 리스트 | sort_by, order |
| `get_watchlist_stocks()` | 관심 종목 리스트 | user_id, tickers (DB 조회 후 전달) |

---

## 4. API 응답 스키마

### 4.1 차트 API (`get_chart_api`)

```json
{
  "symbol": "005930",
  "range": "3m",
  "type": "candlestick",
  "plotly": "{ ... Plotly fig.to_json() 결과 ... }",
  "meta": {
    "ma": [5, 20, 60],
    "generatedAt": "2026-01-24T10:30:00"
  }
}
```

**에러 시:**
```json
{
  "plotly": null,
  "meta": { "reason": "에러 메시지" }
}
```

### 4.2 기본 정보 (`get_stock_info`)

```json
{
  "company_name": "삼성전자",
  "ticker": "005930",
  "current_price": 55000,
  "price_change": -200,
  "change_rate": -0.36,
  "open": 55200,
  "high": 55500,
  "low": 54800,
  "volume": 12345678
}
```

### 4.3 펀더멘탈 지표 (`get_fundamental_metrics`)

```json
{
  "ticker": "005930",
  "name": "삼성전자",
  "per": 12.5,
  "pbr": 1.2,
  "roe": 9.6,
  "eps": 4400,
  "bps": 45833,
  "w52_high": 88000,
  "w52_low": 52600,
  "market_cap": 3280000
}
```

### 4.4 종목 리스트 (`get_sorted_market_stocks`)

```json
{
  "date": "20260124",
  "market": "KOSPI",
  "sort_by": "change_rate",
  "order": "desc",
  "count": 100,
  "stocks": [
    {
      "ticker": "005930",
      "name": "삼성전자",
      "current_price": 55000,
      "change_rate": 3.25,
      "volume": 12345678
    }
  ]
}
```

### 4.5 보유 종목 (`get_holding_stocks`)

```json
{
  "count": 5,
  "total_eval_amount": 15000000,
  "total_profit_amount": 500000,
  "stocks": [
    {
      "ticker": "005930",
      "name": "삼성전자",
      "quantity": 10,
      "avg_price": 50000,
      "current_price": 55000,
      "eval_amount": 550000,
      "profit_amount": 50000,
      "profit_rate": 10.0
    }
  ]
}
```

---

## 5. 파라미터 값 정리

### range (기간)

| 값 | 의미 | 차트 타입 |
|----|------|-----------|
| `1d` | 하루 | 5분봉 |
| `1m` | 1달 (30일) | 일봉 |
| `3m` | 3달 (90일) | 일봉 |
| `1y` | 1년 (365일) | 일봉 |

### type (차트 타입)

| 값 | 내용 |
|----|------|
| `candlestick` | 캔들스틱 + MA(5,20,60) + 거래량 (기본) |
| `line` | 종가 라인 차트 |
| `technical` | 볼린저밴드 + RSI |
| `volume` | 거래량 바 차트 |

### sort_by (정렬 기준)

**전체 종목:**
| 값 | 의미 |
|----|------|
| `price` | 주가순 (기본) |
| `change_rate` | 등락률순 |
| `volume` | 거래량순 |
| `name` | 종목명순 |

**보유 종목:**
| 값 | 의미 |
|----|------|
| `eval_amount` | 평가금액순 (기본) |
| `profit_rate` | 수익률순 |
| `quantity` | 보유수량순 |
| `name` | 종목명순 |

---

## 6. 주의사항

### API 호출 제한 (한국투자증권)

| 제한 | 값 | 대응 |
|------|----|------|
| 토큰 발급 | 1분당 1회 | 토큰 캐싱 필요 |
| API 호출 | 초당 20회 | 요청 간격 조절 |

### 권장 캐싱 TTL

| Range | TTL |
|-------|-----|
| 1d (5분봉) | 10~60초 |
| 1m | 5분 |
| 3m | 15분 |
| 1y | 30분 |

### 에러 응답

- 일반: `{"error": "메시지"}`
- `get_chart_api()`: `{"plotly": null, "meta": {"reason": "메시지"}}`

---

## 7. 문의

데이터 관련 문의사항은 데이터 파트로 연락 바랍니다.
