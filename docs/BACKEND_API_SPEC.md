# 종목 리포트 API 데이터 명세서

## 📄 개요

이 문서는 **종목 리포트 생성 시스템**의 API 응답 형식을 정의합니다.
백엔드 팀은 이 형식에 맞춰 API 엔드포인트를 구현해주시면 됩니다.

---

## 📦 샘플 데이터

실제 종목으로 생성한 샘플 데이터: **`backend_sample_data_*.json`**

샘플에 포함된 종목:
- `005930` - 삼성전자
- `035720` - 카카오
- `000660` - SK하이닉스

---

## 🔗 API 엔드포인트 제안

### 1. 종목 리포트 생성

**POST** `/api/v1/report/generate`

#### Request Body
```json
{
  "ticker": "005930",
  "report_type": "comprehensive"  // optional: "summary" | "comprehensive"
}
```

#### Response (200 OK)
```json
{
  "ticker": "005930",
  "company_name": "삼성전자",
  "generated_at": "2026-01-02 19:12:02",
  "full_report": {
    "metadata": { ... },
    "report": { ... },
    "raw_data": { ... }
  },
  "kakao": {
    "summary": { ... },
    "detail": { ... },
    "kakao_response": { ... }
  }
}
```

자세한 구조는 아래 **데이터 구조** 섹션 참고.

---

### 2. 카카오톡 챗봇용 엔드포인트

**POST** `/api/v1/kakao/skill/report`

카카오 오픈빌더 스킬 서버 요청을 받아 처리하는 엔드포인트

#### Request Body (카카오 스킬 서버 형식)
```json
{
  "intent": {
    "id": "...",
    "name": "종목리포트"
  },
  "userRequest": {
    "utterance": "삼성전자 리포트",
    "params": {
      "ticker": "005930"
    }
  },
  "action": {
    "name": "getStockReport",
    "params": {
      "ticker": "005930"
    }
  }
}
```

#### Response (카카오 스킬 서버 형식)
```json
{
  "version": "2.0",
  "template": {
    "outputs": [
      {
        "basicCard": {
          "title": "📊 삼성전자 (005930)",
          "description": "한 줄 요약...",
          "thumbnail": {
            "imageUrl": "https://example.com/chart/005930.png"
          },
          "buttons": [
            {
              "action": "webLink",
              "label": "📄 상세 리포트 보기",
              "webLinkUrl": "https://example.com/report/005930"
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
              "description": "128,500원\n📈 +1,500원 (+1.18%)"
            },
            {
              "title": "밸류에이션",
              "description": "PER 15.2배 | PBR 1.3배 | ROE 8.5%"
            },
            {
              "title": "투자 의견",
              "description": "🟢 매수\n목표주가: 150,000원"
            }
          ],
          "buttons": [
            {
              "action": "webLink",
              "label": "📄 상세 리포트 보기",
              "webLinkUrl": "https://example.com/report/005930"
            }
          ]
        }
      }
    ]
  }
}
```

---

## 📋 데이터 구조

### 최상위 구조

```typescript
interface StockReportResponse {
  ticker: string;              // 종목 코드 (예: "005930")
  company_name: string;        // 회사명 (예: "삼성전자")
  generated_at: string;        // 생성 시각 (ISO 8601 형식)
  full_report: FullReport;     // 전체 리포트 데이터
  kakao: KakaoFormat;          // 카카오톡 포맷 데이터
}
```

---

### 1. full_report 구조

```typescript
interface FullReport {
  metadata: Metadata;
  report: Report;
  raw_data: RawData;
}

interface Metadata {
  ticker: string;              // "005930"
  company_name: string;        // "삼성전자"
  generated_at: string;        // "2026-01-02 19:12:02"
  has_financials: boolean;     // 재무제표 포함 여부
}

interface Report {
  title: string;               // "삼성전자(005930) 투자 분석 리포트"
  full_text: string;           // 전체 리포트 텍스트 (마크다운)
  sections: ReportSections;    // 섹션별 분리된 텍스트
  has_financials: boolean;     // 재무제표 포함 여부
}

interface ReportSections {
  summary: string;             // [1. 투자 요약] 섹션
  price_analysis: string;      // [2. 주가 동향 분석] 섹션
  financial_analysis: string;  // [3. 재무 상태 분석] 섹션
  valuation: string;           // [4. 밸류에이션] 섹션
  investment_opinion: string;  // [5. 투자 의견] 섹션
}

interface RawData {
  basic: BasicInfo;
  price_trend: PriceTrend;
  metrics: Metrics;
  technical: Technical;
  financial_trend: FinancialTrend;
}
```

---

### 2. raw_data 상세 구조

#### BasicInfo
```typescript
interface BasicInfo {
  ticker: string;              // "005930"
  name: string;                // "삼성전자"
  current_price: number;       // 128500
  price_change: number;        // 1500
  price_change_pct: number;    // 1.18
  volume: number;              // 거래량
  market_cap: number;          // 시가총액 (원)
  market_cap_rank: number;     // 시총 순위
}
```

#### PriceTrend
```typescript
interface PriceTrend {
  "1m": number;                // 1개월 수익률 (%)
  "3m": number;                // 3개월 수익률 (%)
  "1y": number;                // 1년 수익률 (%)
  "52w_high": number;          // 52주 최고가
  "52w_low": number;           // 52주 최저가
}
```

#### Metrics
```typescript
interface Metrics {
  per: number | "N/A";         // 주가수익비율 (배)
  pbr: number | "N/A";         // 주가순자산비율 (배)
  roe: number | "N/A";         // 자기자본이익률 (%)
  eps: number | "N/A";         // 주당순이익 (원)
  bps: number | "N/A";         // 주당순자산 (원)
  dividend_yield: number | "N/A"; // 배당수익률 (%)
}
```

#### Technical
```typescript
interface Technical {
  rsi: number | "N/A";         // RSI 지표 (0-100)
  rsi_signal: string;          // "과매수" | "과매도" | "중립"
  trend: string;               // "상승" | "하락" | "횡보"
  ma5: number | "N/A";         // 5일 이동평균
  ma20: number | "N/A";        // 20일 이동평균
  ma60: number | "N/A";        // 60일 이동평균
}
```

#### FinancialTrend
```typescript
interface FinancialTrend {
  revenue_trend: number[];     // 최근 3년 매출 추이 (억 원)
  profit_trend: number[];      // 최근 3년 영업이익 추이 (억 원)
  revenue_growth: number;      // 매출 성장률 (%)
  profit_growth: number;       // 영업이익 성장률 (%)
}
```

---

### 3. kakao 구조

```typescript
interface KakaoFormat {
  summary: KakaoSummary;       // 카카오톡 표시용 요약
  detail: ReportDetail;        // 웹 상세 페이지용 데이터
  kakao_response: KakaoResponse; // 카카오톡 API 응답 형식
}

interface KakaoSummary {
  basic_info: {
    ticker: string;
    company_name: string;
    current_price: number;
    price_change: number;
    price_change_pct: number;
  };
  key_metrics: {
    per: number | "N/A";
    pbr: number | "N/A";
    roe: number | "N/A";
  };
  investment_opinion: {
    opinion: string;           // "매수" | "보유" | "매도" | "관망"
    target_price: string;      // "150,000원" | "N/A"
    risk_level: string;        // "높음" | "중간" | "낮음" | "N/A"
  };
  brief_summary: string;       // 한 줄 요약 (100자 이내)
}

interface ReportDetail {
  metadata: Metadata;          // full_report의 metadata와 동일
  sections: ReportSections;    // full_report의 sections와 동일
  raw_data: RawData;           // full_report의 raw_data와 동일
}

interface KakaoResponse {
  version: "2.0";
  template: {
    outputs: Array<BasicCard | ListCard>;
  };
}
```

---

## 📊 샘플 응답 예시

### 전체 응답 (요약)

```json
{
  "ticker": "005930",
  "company_name": "삼성전자",
  "generated_at": "2026-01-02 19:12:02",
  "full_report": {
    "metadata": {
      "ticker": "005930",
      "company_name": "삼성전자",
      "generated_at": "2026-01-02 19:12:02",
      "has_financials": false
    },
    "report": {
      "title": "삼성전자(005930) 투자 분석 리포트",
      "full_text": "전체 리포트 마크다운 텍스트...",
      "sections": {
        "summary": "삼성전자는 글로벌 1위 반도체 기업...",
        "price_analysis": "현재가 128,500원은...",
        "financial_analysis": "안정적인 재무구조...",
        "valuation": "PER 15.2배로 평가...",
        "investment_opinion": "종합 투자 의견: 매수..."
      },
      "has_financials": false
    },
    "raw_data": {
      "basic": {
        "ticker": "005930",
        "name": "삼성전자",
        "current_price": 128500,
        "price_change": 1500,
        "price_change_pct": 1.18,
        "volume": 12345678,
        "market_cap": 580000000000000,
        "market_cap_rank": 1
      },
      "price_trend": {
        "1m": 5.2,
        "3m": 12.3,
        "1y": 45.6,
        "52w_high": 135000,
        "52w_low": 85000
      },
      "metrics": {
        "per": 15.2,
        "pbr": 1.3,
        "roe": 8.5,
        "eps": 8450,
        "bps": 98900,
        "dividend_yield": 2.1
      },
      "technical": {
        "rsi": 62.5,
        "rsi_signal": "중립",
        "trend": "상승",
        "ma5": 127800,
        "ma20": 125600,
        "ma60": 120300
      },
      "financial_trend": {
        "revenue_trend": [2800000, 3020000, 3250000],
        "profit_trend": [450000, 520000, 580000],
        "revenue_growth": 7.6,
        "profit_growth": 11.5
      }
    }
  },
  "kakao": {
    "summary": {
      "basic_info": {
        "ticker": "005930",
        "company_name": "삼성전자",
        "current_price": 128500,
        "price_change": 1500,
        "price_change_pct": 1.18
      },
      "key_metrics": {
        "per": 15.2,
        "pbr": 1.3,
        "roe": 8.5
      },
      "investment_opinion": {
        "opinion": "매수",
        "target_price": "150,000원",
        "risk_level": "중간"
      },
      "brief_summary": "삼성전자는 글로벌 1위 반도체 기업으로 안정적인 재무구조와 AI 반도체 수요 증가로 긍정적 전망입니다."
    },
    "detail": {
      "metadata": { ... },
      "sections": { ... },
      "raw_data": { ... }
    },
    "kakao_response": {
      "version": "2.0",
      "template": {
        "outputs": [ ... ]
      }
    }
  }
}
```

---

## 🔧 백엔드 구현 가이드

### 1. API 엔드포인트 구현

```python
# FastAPI 예시
from fastapi import FastAPI
from stock_report_realtime import RealtimeStockReportGenerator
from kakao_report_formatter import KakaoReportFormatter

app = FastAPI()
generator = RealtimeStockReportGenerator()
formatter = KakaoReportFormatter()

@app.post("/api/v1/report/generate")
async def generate_report(ticker: str):
    # 1. 리포트 생성
    report = generator.generate_report(ticker)

    # 2. 카카오톡 포맷 변환
    kakao = formatter.format_for_kakao(
        report,
        detail_url=f"https://api.example.com/report/{ticker}"
    )

    # 3. 응답 구성
    return {
        "ticker": ticker,
        "company_name": report['metadata']['company_name'],
        "generated_at": report['metadata']['generated_at'],
        "full_report": report,
        "kakao": kakao
    }
```

### 2. 에러 처리

```python
@app.post("/api/v1/report/generate")
async def generate_report(ticker: str):
    try:
        report = generator.generate_report(ticker)

        if 'error' in report:
            return {
                "error": True,
                "message": report['error'],
                "ticker": ticker
            }

        # 정상 응답
        return { ... }

    except Exception as e:
        return {
            "error": True,
            "message": str(e),
            "ticker": ticker
        }
```

### 3. 캐싱 (선택사항)

리포트 생성 시간이 오래 걸리므로 캐싱 권장:

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.post("/api/v1/report/generate")
async def generate_report(ticker: str, force_refresh: bool = False):
    # 캐시 확인
    cache_key = f"report:{ticker}"

    if not force_refresh:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

    # 리포트 생성
    report = generator.generate_report(ticker)
    kakao = formatter.format_for_kakao(report, ...)

    result = { ... }

    # 캐시 저장 (1시간)
    redis_client.setex(cache_key, 3600, json.dumps(result))

    return result
```

---

## 📝 체크리스트

백엔드 구현 시 확인 사항:

- [ ] POST `/api/v1/report/generate` 엔드포인트 구현
- [ ] POST `/api/v1/kakao/skill/report` 엔드포인트 구현 (카카오 챗봇용)
- [ ] 응답 형식이 명세서와 일치하는지 확인
- [ ] 에러 처리 구현 (종목 코드 오류, API 실패 등)
- [ ] 캐싱 구현 (선택사항, 성능 향상)
- [ ] CORS 설정 (프론트엔드 연동 시)
- [ ] 로깅 구현 (요청/응답 추적)
- [ ] 환경 변수 설정 (DART_API_KEY, GEMINI_API_KEY)

---

## 📞 문의

데이터 구조나 API 형식 관련 문의사항이 있으면 알려주세요.

**샘플 데이터 파일**: `backend_sample_data_*.json`를 참고하세요.
