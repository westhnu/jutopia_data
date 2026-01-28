# Web_03 백엔드 데이터 가이드 (물타기 계산기)

> 작성: 데이터 파트
> 대상: 웹 백엔드 개발자
> 최종 업데이트: 2026-01-28

---

## 1. 전달 파일 및 설정

### 1.1 파일 목록

| 파일명 | 용도 |
|--------|------|
| `stock_averaging_data.py` | Web_03 메인 API (신규) |
| `averaging_calculator.py` | 물타기 계산 로직 (기존) |
| `HantuStock.py` | 보유 종목 조회 (의존) |
| `.env` | API 인증 정보 (별도 전달) |

### 1.2 필수 패키지

```bash
pip install python-dotenv pandas finance-datareader
```

### 1.3 .env 설정

```env
# 한국투자증권 API (보유 종목 조회)
KIS_APP_KEY=your_kis_app_key
KIS_APP_SECRET=your_kis_app_secret
KIS_ACCOUNT_ID=your_account_id
KIS_ENV=prod  # prod: 실전, vps: 모의
```

---

## 2. Quick Start

### 기본 사용법

```python
from stock_averaging_data import StockAveragingDataProvider

provider = StockAveragingDataProvider()

# 1단계: 보유 종목 정보 조회
holding = provider.get_holding_info(symbol="005930")

# 2단계: 물타기 계산 (수량 기준)
result = provider.calculate_by_quantity(
    symbol="005930",
    additional_price=70000,
    additional_quantity=10
)

# 3단계: 물타기 계산 (금액 기준)
result = provider.calculate_by_amount(
    symbol="005930",
    investment_amount=1000000,
    purchase_price=70000
)

# 4단계: 계산 결과 저장
saved = provider.save_calculation(
    symbol="005930",
    calculation_result=result,
    input_mode="quantity"
)

# 5단계: 계산 히스토리 조회
history = provider.get_calculation_history(symbol="005930")
```

---

## 3. API 메서드 요약

### stock_averaging_data.py - StockAveragingDataProvider

| 메서드 | 용도 | 주요 파라미터 |
|--------|------|---------------|
| `get_holding_info()` | 보유 종목 정보 조회 | symbol |
| `calculate_by_quantity()` | 수량 기준 계산 | symbol, additional_price, additional_quantity |
| `calculate_by_amount()` | 금액 기준 계산 | symbol, investment_amount, purchase_price |
| `save_calculation()` | 계산 결과 저장 | symbol, calculation_result, input_mode |
| `get_calculation_history()` | 계산 히스토리 조회 | symbol, limit |
| `delete_calculation()` | 계산 결과 삭제 | calculation_id |

---

## 4. 기능 위치 및 전제

### 4.1 페이지 구조

```
[종목 상세 페이지]
├─ 헤더 (종목명, 현재가)
├─ 차트 영역
├─ 뉴스/커뮤니티 탭
└─ 물타기 계산기 영역 ← 스크롤 하단
```

### 4.2 접근 조건

| 조건 | 상태 | 노출 |
|------|------|------|
| 계좌 미연동 | ❌ | 안내 메시지 + 연동 버튼 |
| 계좌 연동 + 보유 종목 | ✅ | 계산기 활성화 |
| 계좌 연동 + 비보유 종목 | ❌ | "보유 중이 아닙니다" 안내 |

---

## 5. API 응답 스키마

### 5.1 보유 종목 정보 (`get_holding_info`)

**요청:**
```python
GET /api/web/averaging/holding/{symbol}
```

**응답:**
```json
{
  "symbol": "005930",
  "company_name": "삼성전자",
  "is_holding": true,
  "holding_info": {
    "quantity": 100,
    "avg_price": 75000,
    "current_price": 71300,
    "total_cost": 7500000,
    "current_value": 7130000,
    "profit_loss": -370000,
    "profit_loss_pct": -4.93,
    "fetched_at": "2026-01-28 10:30:00"
  }
}
```

**보유하지 않은 경우:**
```json
{
  "symbol": "005930",
  "company_name": "삼성전자",
  "is_holding": false,
  "message": "현재 보유 중이 아닙니다"
}
```

---

### 5.2 수량 기준 계산 (`calculate_by_quantity`)

**요청:**
```python
POST /api/web/averaging/calculate/quantity
```

**Request Body:**
```json
{
  "symbol": "005930",
  "additional_price": 70000,
  "additional_quantity": 10
}
```

**응답:**
```json
{
  "symbol": "005930",
  "company_name": "삼성전자",
  "calculation_mode": "quantity",
  "input": {
    "current_avg_price": 75000,
    "current_quantity": 100,
    "current_price": 71300,
    "additional_price": 70000,
    "additional_quantity": 10
  },
  "result": {
    "new_avg_price": 74545,
    "avg_price_change": -455,
    "avg_price_change_pct": -0.61,
    "total_quantity": 110,
    "total_cost": 8200000,
    "additional_cost": 700000,
    "breakeven_price": 74545,
    "profit_if_sell_now": -137000,
    "profit_pct": -1.67
  },
  "fetched_at": "2026-01-28 10:30:00"
}
```

---

### 5.3 금액 기준 계산 (`calculate_by_amount`)

**요청:**
```python
POST /api/web/averaging/calculate/amount
```

**Request Body:**
```json
{
  "symbol": "005930",
  "investment_amount": 1000000,
  "purchase_price": 70000
}
```

**응답:**
```json
{
  "symbol": "005930",
  "company_name": "삼성전자",
  "calculation_mode": "amount",
  "input": {
    "current_avg_price": 75000,
    "current_quantity": 100,
    "current_price": 71300,
    "investment_amount": 1000000,
    "purchase_price": 70000,
    "calculated_quantity": 14
  },
  "result": {
    "new_avg_price": 74561,
    "avg_price_change": -439,
    "avg_price_change_pct": -0.59,
    "total_quantity": 114,
    "total_cost": 8500000,
    "additional_cost": 980000,
    "breakeven_price": 74561,
    "profit_if_sell_now": -168000,
    "profit_pct": -1.98
  },
  "fetched_at": "2026-01-28 10:30:00"
}
```

---

### 5.4 계산 결과 저장 (`save_calculation`)

**요청:**
```python
POST /api/web/averaging/save
```

**Request Body:**
```json
{
  "symbol": "005930",
  "calculation_mode": "quantity",
  "input": {
    "additional_price": 70000,
    "additional_quantity": 10
  },
  "result": {
    "new_avg_price": 74545,
    "total_quantity": 110,
    "total_cost": 8200000
  }
}
```

**응답:**
```json
{
  "calculation_id": "calc_20260128_103000_005930",
  "symbol": "005930",
  "saved_at": "2026-01-28 10:30:00",
  "message": "계산 결과가 저장되었습니다"
}
```

---

### 5.5 계산 히스토리 조회 (`get_calculation_history`)

**요청:**
```python
GET /api/web/averaging/history/{symbol}?limit=10
```

**응답:**
```json
{
  "symbol": "005930",
  "company_name": "삼성전자",
  "total_count": 5,
  "calculations": [
    {
      "calculation_id": "calc_20260128_103000_005930",
      "saved_at": "2026-01-28 10:30:00",
      "calculation_mode": "quantity",
      "input": {
        "additional_price": 70000,
        "additional_quantity": 10
      },
      "result_summary": {
        "new_avg_price": 74545,
        "total_quantity": 110,
        "total_cost": 8200000
      }
    },
    {
      "calculation_id": "calc_20260127_151500_005930",
      "saved_at": "2026-01-27 15:15:00",
      "calculation_mode": "amount",
      "input": {
        "investment_amount": 1000000,
        "purchase_price": 69000
      },
      "result_summary": {
        "new_avg_price": 74421,
        "total_quantity": 114,
        "total_cost": 8500000
      }
    }
  ]
}
```

---

## 6. 데이터 흐름

### 6.1 페이지 진입 시

```
[종목 상세 페이지 로드]
         ↓
[계좌 연동 확인]
         ├─ 미연동 → 안내 메시지
         └─ 연동 → 보유 종목 확인
                    ├─ 미보유 → 안내 메시지
                    └─ 보유 → 계산기 활성화
                              ↓
                    [보유 정보 조회]
                    - HantuStock API
                    - 보유수량, 평단가, 현재가
                              ↓
                    [계산기 초기화]
                    - 자동 세팅
                    - 입력 필드 활성화
```

### 6.2 계산 실행

```
[사용자 입력]
├─ 수량 기준: 추가 단가 + 수량
└─ 금액 기준: 투자 금액 + 매수 단가
         ↓
[계산 API 호출]
- averaging_calculator.py 사용
- 새로운 평단가 계산
         ↓
[결과 표시]
- 새 평단가
- 평단가 변화
- 총 투자금
- 손익 변화
         ↓
[사용자 선택]
├─ 저장 → 히스토리 저장
└─ 다시 계산 → 입력 초기화
```

---

## 7. 계산 로직 상세

### 7.1 수량 기준 계산

**입력:**
- 현재 평단가: 75,000원
- 현재 보유: 100주
- 추가 단가: 70,000원
- 추가 수량: 10주

**계산:**
```
기존 투자금 = 75,000 × 100 = 7,500,000원
추가 투자금 = 70,000 × 10 = 700,000원
총 투자금 = 7,500,000 + 700,000 = 8,200,000원
총 수량 = 100 + 10 = 110주
새 평단가 = 8,200,000 ÷ 110 = 74,545원
평단가 변화 = 74,545 - 75,000 = -455원 (-0.61%)
```

### 7.2 금액 기준 계산

**입력:**
- 현재 평단가: 75,000원
- 현재 보유: 100주
- 투자 금액: 1,000,000원
- 매수 단가: 70,000원

**계산:**
```
매수 가능 수량 = 1,000,000 ÷ 70,000 = 14.28주 → 14주 (소수점 버림)
실제 투자금 = 70,000 × 14 = 980,000원
총 투자금 = 7,500,000 + 980,000 = 8,480,000원
총 수량 = 100 + 14 = 114주
새 평단가 = 8,480,000 ÷ 114 = 74,386원
```

---

## 8. 기획 준수 사항

### 8.1 UI 구성 요구사항

| 항목 | 요구사항 | 구현 |
|------|----------|------|
| **위치** | 종목 상세 페이지 하단 | ✅ |
| **페이지 이동** | 없음 (페이지 내 통합) | ✅ |
| **계좌 연동** | 필수 | ✅ |
| **대상 종목** | 보유 종목만 | ✅ |
| **데이터 갱신** | 페이지 진입 시 1회 | ✅ |

### 8.2 입력 모드

| 모드 | 입력 필드 | 기본값 |
|------|-----------|--------|
| **수량 기준** | 추가 매수 단가, 추가 매수 수량 | 현재가 |
| **금액 기준** | 추가 투자 금액, 매수 단가 | 현재가 |

### 8.3 계산 결과 표시

| 항목 | 표시 내용 |
|------|-----------|
| 새로운 평균 단가 | ✅ 강조 |
| 평균 단가 변화 | ✅ 금액 + 비율 |
| 총 보유 수량 | ✅ |
| 총 투자 금액 | ✅ |
| 손익 변화 | ✅ 금액 + 비율 |

---

## 9. 저장 기능

### 9.1 저장 정책

- **저장 위치**: `./averaging_history/{symbol}/`
- **파일명**: `calc_{timestamp}.json`
- **저장 항목**:
  - 계산 시점
  - 입력 모드 (수량/금액)
  - 입력 값
  - 계산 결과

### 9.2 저장 예시

**파일**: `./averaging_history/005930/calc_20260128_103000.json`

```json
{
  "calculation_id": "calc_20260128_103000_005930",
  "symbol": "005930",
  "company_name": "삼성전자",
  "saved_at": "2026-01-28 10:30:00",
  "calculation_mode": "quantity",
  "snapshot": {
    "current_avg_price": 75000,
    "current_quantity": 100,
    "current_price": 71300
  },
  "input": {
    "additional_price": 70000,
    "additional_quantity": 10
  },
  "result": {
    "new_avg_price": 74545,
    "avg_price_change": -455,
    "avg_price_change_pct": -0.61,
    "total_quantity": 110,
    "total_cost": 8200000,
    "additional_cost": 700000
  }
}
```

---

## 10. 히스토리 조회

### 10.1 조회 기능

- **정렬**: 최신순
- **페이징**: 10개씩
- **필터**: 종목별

### 10.2 UI 표시

**리스트 항목 (간략):**
```
2026-01-28 10:30
수량 기준 | +10주 @ 70,000원
→ 새 평단가: 74,545원
```

**상세 보기 (클릭 시):**
```
━━━━━━━━━━━━━━━━━━━━━━
💰 물타기 계산 결과
━━━━━━━━━━━━━━━━━━━━━━

저장일시: 2026-01-28 10:30

【 입력 조건 】
├ 모드: 수량 기준
├ 추가 단가: 70,000원
└ 추가 수량: 10주

【 계산 결과 】
✅ 새 평단가: 74,545원
▼ 평단가 변화: -455원 (-0.61%)

【 투자 현황 】
├ 총 보유: 110주
├ 총 투자금: 8,200,000원
└ 추가 투자: 700,000원
```

---

## 11. 에러 처리

### 11.1 주요 에러 시나리오

| 에러 | 원인 | 대응 |
|------|------|------|
| `계좌 미연동` | KIS API 미설정 | 연동 안내 |
| `보유 종목 아님` | 해당 종목 미보유 | 안내 메시지 |
| `API 호출 실패` | KIS API 오류 | 재시도 안내 |
| `잘못된 입력` | 0, 음수, 문자 | 인라인 에러 |

### 11.2 에러 응답 예시

```json
{
  "error": "NOT_HOLDING",
  "message": "현재 삼성전자를 보유하고 있지 않습니다",
  "symbol": "005930",
  "company_name": "삼성전자"
}
```

---

## 12. 성능 최적화

### 12.1 캐싱 권장

| 데이터 | TTL | 이유 |
|--------|-----|------|
| 보유 종목 정보 | 30초 | 실시간성 |
| 계산 히스토리 | 5분 | 자주 변경 없음 |

### 12.2 응답 시간

| API | 목표 시간 |
|-----|-----------|
| get_holding_info | < 1초 |
| calculate_* | < 0.5초 |
| save_calculation | < 0.5초 |
| get_history | < 1초 |

---

## 13. 테스트

### 13.1 단위 테스트

```bash
# 모듈 테스트
python stock_averaging_data.py
```

### 13.2 통합 테스트

```python
def test_full_flow():
    provider = StockAveragingDataProvider()

    # 1. 보유 종목 확인
    holding = provider.get_holding_info("005930")
    assert holding["is_holding"] == True

    # 2. 수량 기준 계산
    result = provider.calculate_by_quantity(
        symbol="005930",
        additional_price=70000,
        additional_quantity=10
    )
    assert "new_avg_price" in result["result"]

    # 3. 저장
    saved = provider.save_calculation(
        symbol="005930",
        calculation_result=result
    )
    assert "calculation_id" in saved

    # 4. 히스토리 조회
    history = provider.get_calculation_history("005930")
    assert len(history["calculations"]) > 0

    print("✅ 통합 테스트 통과")

test_full_flow()
```

---

## 14. 배포 체크리스트

- [ ] .env에 KIS API 키 설정
- [ ] averaging_history 디렉토리 생성 권한
- [ ] 보유 종목 조회 API 테스트
- [ ] 수량/금액 기준 계산 테스트
- [ ] 저장/조회 기능 테스트
- [ ] 에러 처리 검증

---

## 15. 참고 문서

- [averaging_calculator.py](../averaging_calculator.py) - 계산 로직 소스코드
- [HantuStock.py](../HantuStock.py) - KIS API 클라이언트
- Web_03 기획안 - 상세 요구사항

---

**작성**: 데이터 파트
**검토**: -
**승인**: -
**날짜**: 2026-01-28
