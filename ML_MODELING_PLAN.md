# 🤖 주식 예측 ML 모델링 계획

## 📊 현재 상태

### ✅ 준비된 것
- **데이터 수집**: 45개 파일 (주가, 재무제표, 공시, 지수)
- **기술적 지표**: RSI, 볼린저밴드, 이동평균선
- **재무 분석**: 부채비율, ROE, 유동비율

### ❌ 필요한 것
- 데이터 전처리 파이프라인
- ML 모델 구축
- 예측 API
- 모델 평가

---

## 🎯 구현할 ML 모델 (우선순위별)

### 1️⃣ **주가 방향 예측** (분류 모델) ⭐⭐⭐⭐⭐

**목표**: 내일 주가가 오를지/내릴지 예측

**입력 특성**:
- 기술적 지표: RSI, 볼린저밴드, MACD
- 이동평균: 5일, 20일, 60일
- 거래량 변화
- 시장 지수 (코스피, 코스닥)

**출력**:
- 0: 하락 예상 (매도 신호)
- 1: 상승 예상 (매수 신호)
- 2: 횡보 예상 (관망)

**모델**:
- Random Forest (시작)
- XGBoost (고급)
- LSTM (시계열)

**챗봇 활용**:
```
사용자: "삼성전자 내일 전망"
챗봇:
📊 삼성전자 AI 예측
━━━━━━━━━━━━━━━━━━━━
🔮 내일 예측: 상승 ↗️
📈 확률: 67%
💡 근거:
  - RSI 과매도 구간 탈출
  - 거래량 증가 (전일比 +25%)
  - 5일선 돌파

⚠️ 예측은 참고용입니다
```

---

### 2️⃣ **주가 변동폭 예측** (회귀 모델) ⭐⭐⭐⭐

**목표**: 내일 주가 변동률 예측 (예: +2.3%, -1.5%)

**입력**:
- 기술적 지표
- 과거 변동성
- 재무 지표 (ROE, 부채비율)

**출력**:
- 예상 변동률 (%)

**모델**:
- Linear Regression (기본)
- Random Forest Regressor
- LSTM (시계열)

**챗봇 활용**:
```
사용자: "카카오 주가 얼마나 오를까?"
챗봇:
🔮 카카오 변동 예측
━━━━━━━━━━━━━━━━━━━━
현재가: 52,000원
예상: 53,600원 (+3.1%)

📊 예측 범위:
  - 최저: 51,200원 (-1.5%)
  - 최고: 54,800원 (+5.4%)

신뢰도: 72%
```

---

### 3️⃣ **재무 건전성 예측** (분류 모델) ⭐⭐⭐

**목표**: 재무제표 기반 기업 등급 예측

**입력**:
- 재무비율 (부채비율, ROE, 유동비율)
- 매출/이익 성장률
- 산업 평균 비교

**출력**:
- A: 매우 우수
- B: 양호
- C: 보통
- D: 주의
- F: 위험

**모델**:
- Logistic Regression
- Random Forest Classifier

**챗봇 활용**:
```
사용자: "LG화학 재무 괜찮아?"
챗봇:
💰 LG화학 AI 재무 평가
━━━━━━━━━━━━━━━━━━━━
🏆 등급: A- (우수)

📊 AI 분석:
  - 부채비율 낮음 ✅
  - 수익성 우수 ✅
  - 유동성 안정 ✅

💡 투자 의견: 매수
```

---

### 4️⃣ **공시 중요도 분류** (NLP 모델) ⭐⭐⭐

**목표**: 공시문 내용 분석해서 중요도 판단

**입력**:
- 공시 제목
- 공시 내용 (텍스트)
- 공시 유형

**출력**:
- 🔴 긴급 (주가 영향 큼)
- 🟡 중요 (모니터링 필요)
- 🟢 일반 (참고)

**모델**:
- TF-IDF + Logistic Regression
- BERT (한국어 모델)

**챗봇 활용**:
```
사용자: "삼성전자 최근 공시"
챗봇:
📢 삼성전자 공시 분석
━━━━━━━━━━━━━━━━━━━━
🔴 긴급 (1건)
[11/15] 3분기 실적 발표
→ AI 분석: 실적 호조, 주가 상승 예상

🟡 중요 (2건)
[11/10] 자사주 매입
[11/08] 임원 변동
```

---

### 5️⃣ **포트폴리오 최적화** (최적화 모델) ⭐⭐

**목표**: 리스크 대비 최대 수익 포트폴리오 구성

**입력**:
- 보유 종목
- 목표 수익률
- 리스크 허용 범위

**출력**:
- 종목별 비중 추천

**모델**:
- Markowitz Portfolio Theory
- Monte Carlo Simulation

---

## 🛠️ 구현 단계 (4주 계획)

### ✅ Week 1: 데이터 전처리 (우선)

**목표**: ML 학습 가능한 데이터셋 생성

**Task**:
1. **특성 엔지니어링**
   ```python
   # stock_preprocessor.py 생성
   - 파생 변수 생성 (변동성, 추세, 모멘텀)
   - 시차 변수 (lag features)
   - 롤링 통계 (평균, 표준편차)
   ```

2. **데이터 정제**
   ```python
   - 결측치 처리 (보간)
   - 이상치 제거 (IQR 방법)
   - 데이터 스케일링 (MinMaxScaler)
   ```

3. **라벨링**
   ```python
   # 분류 라벨 생성
   - 다음날 상승/하락 라벨
   - 변동폭 라벨 (3개 구간)
   ```

**산출물**:
- `stock_preprocessor.py` - 전처리 클래스
- `processed/ml_train_data_{ticker}.csv` - 학습용 데이터

---

### ✅ Week 2: 기본 모델 구축

**목표**: 주가 방향 예측 모델 (분류)

**Task**:
1. **학습 데이터 준비**
   ```python
   # train_classifier.py
   X_train, X_test, y_train, y_test = train_test_split(...)
   ```

2. **모델 학습**
   ```python
   # Random Forest 시작
   from sklearn.ensemble import RandomForestClassifier

   model = RandomForestClassifier(n_estimators=100)
   model.fit(X_train, y_train)
   ```

3. **평가**
   ```python
   accuracy = model.score(X_test, y_test)
   print(f"정확도: {accuracy:.2%}")
   ```

4. **모델 저장**
   ```python
   import joblib
   joblib.dump(model, 'models/stock_classifier.pkl')
   ```

**산출물**:
- `train_classifier.py` - 학습 스크립트
- `models/stock_classifier.pkl` - 학습된 모델
- `model_evaluation.txt` - 성능 지표

**목표 성능**:
- 정확도: 60% 이상 (랜덤 50%보다 높으면 성공)

---

### ✅ Week 3: 고급 모델 + 예측 API

**Task**:
1. **XGBoost 모델**
   ```python
   import xgboost as xgb

   model = xgb.XGBClassifier(
       n_estimators=200,
       learning_rate=0.05
   )
   ```

2. **LSTM 시계열 모델**
   ```python
   from tensorflow.keras.models import Sequential
   from tensorflow.keras.layers import LSTM, Dense

   model = Sequential([
       LSTM(50, return_sequences=True),
       LSTM(50),
       Dense(3, activation='softmax')  # 3클래스
   ])
   ```

3. **예측 API 생성**
   ```python
   # stock_predictor.py
   class StockPredictor:
       def predict_tomorrow(self, ticker):
           """내일 주가 방향 예측"""
           return {
               'direction': '상승',
               'probability': 0.67,
               'confidence': 'medium'
           }
   ```

**산출물**:
- `models/stock_xgboost.pkl`
- `models/stock_lstm.h5`
- `stock_predictor.py` - 예측 클래스

---

### ✅ Week 4: 챗봇 통합

**Task**:
1. **Streamlit 앱에 예측 탭 추가**
   ```python
   # app.py에 추가
   with tab_predict:
       st.subheader("AI 예측")
       prediction = predictor.predict_tomorrow(ticker)
       st.metric("예측", prediction['direction'])
   ```

2. **카카오톡 챗봇 API 개발**
   ```python
   # kakao_bot_api.py
   @app.post("/predict")
   def predict(ticker: str):
       result = predictor.predict_tomorrow(ticker)
       return format_kakao_message(result)
   ```

3. **모니터링 대시보드**
   ```python
   # 예측 정확도 추적
   # 실제 결과와 비교
   ```

---

## 📚 필요한 패키지

```bash
# ML 기본
pip install scikit-learn>=1.3.0
pip install xgboost>=2.0.0

# 딥러닝 (LSTM)
pip install tensorflow>=2.15.0

# 데이터 처리
pip install pandas numpy matplotlib seaborn

# 모델 저장
pip install joblib
```

---

## 📊 데이터셋 구조 (예시)

### 학습 데이터 형태
```csv
date,open,high,low,close,volume,rsi,ma5,ma20,bollinger_upper,bollinger_lower,volume_change,kospi,label
2024-11-01,71000,72000,70500,71500,1000000,45.2,71200,70800,73000,68000,1.05,2500,1
2024-11-02,71500,71800,70800,71200,950000,43.1,71300,70900,72900,68100,0.95,2505,0
...
```

**특성 (X)**:
- 기술적 지표: rsi, ma5, ma20, bollinger_*
- 거래량: volume, volume_change
- 시장 지수: kospi

**라벨 (y)**:
- 0: 하락
- 1: 상승
- 2: 횡보

---

## 🎯 최종 목표

### 카카오톡 챗봇 대화 예시

```
👤 사용자: "삼성전자 지금 사도 돼?"

🤖 챗봇:
━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 삼성전자 종합 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 현재가: 71,300원

🔮 AI 예측
├ 내일 전망: 상승 ↗️ (67%)
├ 예상가: 72,500원 (+1.7%)
└ 신뢰도: Medium

📈 기술적 분석
├ RSI: 45.2 (중립)
├ 추세: 상승 전환
└ 매수 신호: 5일선 돌파 ✅

💰 재무 건전성: A- (우수)
├ 부채비율: 27.9% ✅
├ ROE: 8.6%
└ AI 등급: 매수 추천

💡 투자 의견
✅ 매수 적기
- 기술적 매수 신호
- 재무 건전성 우수
- AI 상승 예측

⚠️ 리스크
- 반도체 업황 불확실
- 환율 변동성

[상세 차트] [포트폴리오 추가]
━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🚨 주의사항

1. **과적합 방지**
   - Cross-validation 사용
   - 테스트 데이터 별도 분리

2. **리스크 고지**
   - 예측은 참고용
   - 투자 책임은 본인

3. **지속적 재학습**
   - 주기적 모델 업데이트
   - 성능 모니터링

---

## 📈 성공 기준

| 모델 | 목표 정확도 | 실전 적용 |
|------|------------|----------|
| 주가 방향 예측 | 60% 이상 | ⭐⭐⭐⭐⭐ |
| 변동폭 예측 | RMSE < 3% | ⭐⭐⭐⭐ |
| 재무 등급 | 70% 이상 | ⭐⭐⭐ |

---

## 🎯 다음 액션

**즉시 시작 가능**:
1. `stock_preprocessor.py` 생성 - 데이터 전처리
2. 학습 데이터셋 생성
3. Random Forest 기본 모델 학습

**다음 주**:
- XGBoost 고급 모델
- Streamlit 예측 탭 추가
- 카카오톡 챗봇 연동

---

**이 계획으로 진행하시겠어요?** 🚀
