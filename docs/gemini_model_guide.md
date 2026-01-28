# Gemini API 모델 가이드

> 프로젝트 전체에서 사용하는 Gemini API 설정
> 최종 업데이트: 2026-01-28

---

## 📌 현재 설정

### 모델 버전: **gemini-2.5-flash**

모든 모듈에서 통일하여 사용 중입니다.

---

## 🎯 사용 현황

| 기능 | 파일 | 모델 | 용도 |
|------|------|------|------|
| **Web_02 뉴스** | stock_news_data.py | `gemini-2.5-flash` | 투자 관련 뉴스 필터링 |
| **Web_02 커뮤니티** | stock_news_data.py | `gemini-2.5-flash` | 영문 AI 요약 → 한글 번역 |
| **Chatbot_05 커뮤니티** | chatbot_news_community.py | `gemini-2.5-flash` | 대표 의견 추출 |
| **Chatbot_05 뉴스** | chatbot_news_community.py | `gemini-2.5-flash` | 핵심 이슈 요약 |
| **뉴스 종합 요약** | news_summary.py | `gemini-2.5-flash` | 전체 뉴스 요약 |
| **실시간 리포트** | stock_report_realtime.py | `gemini-2.5-flash` | 종합 리포트 생성 |
| **월간 요약** | summary_report.py | `gemini-2.5-flash` | 월간 투자 요약 |

---

## 💰 비용 및 한도

### Gemini 2.5 Flash 특징

| 항목 | 내용 |
|------|------|
| **속도** | ⚡⚡⚡ 매우 빠름 |
| **품질** | ⭐⭐⭐⭐ 고품질 |
| **입력 토큰** | $0.075 / 1M tokens |
| **출력 토큰** | $0.30 / 1M tokens |
| **컨텍스트** | 최대 1M tokens |
| **무료 한도** | RPM: 10, RPD: 1,500 |

### 프로젝트 크레딧

- **현재 잔액**: $300 (유료)
- **예상 사용량**: 월 $10-20
- **충분 기간**: 약 15-30개월

---

## 📊 비용 추정

### 시나리오 1: 저사용량 (일 100회 요청)

```
뉴스 요약 (50회/일):
  입력: 500 tokens/요청 × 50 = 25,000 tokens
  출력: 200 tokens/요청 × 50 = 10,000 tokens

커뮤니티 요약 (50회/일):
  입력: 500 tokens/요청 × 50 = 25,000 tokens
  출력: 150 tokens/요청 × 50 = 7,500 tokens

일일 총비용:
  입력: 50,000 tokens × $0.075 / 1M = $0.00375
  출력: 17,500 tokens × $0.30 / 1M = $0.00525
  합계: $0.009/일 → 월 $0.27
```

### 시나리오 2: 중사용량 (일 1,000회 요청)

```
일일 총비용: $0.09/일 → 월 $2.7
```

### 시나리오 3: 고사용량 (일 10,000회 요청)

```
일일 총비용: $0.9/일 → 월 $27
```

**결론**: $300 크레딧으로 **10-30개월** 사용 가능

---

## ⚙️ API 설정

### .env 파일

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 코드 패턴

```python
import os
import google.generativeai as genai

# API 설정
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 모델 초기화
model = genai.GenerativeModel('gemini-2.5-flash')

# 콘텐츠 생성
response = model.generate_content(prompt)
result = response.text
```

---

## 🔧 최적화 팁

### 1. 캐싱 전략

```python
# 동일 요청 캐싱 (30초-5분)
@cache(ttl=300)
def get_news_summary(symbol):
    return chatbot.get_news_summary(symbol, company_name)
```

### 2. 배치 처리

```python
# 여러 뉴스를 한 번에 처리
prompt = f"""
다음 뉴스들을 요약해주세요:
1. {news_1}
2. {news_2}
3. {news_3}
"""
```

### 3. 토큰 제한

```python
# 입력 토큰 제한 (비용 절감)
content = content[:2000]  # 약 500 tokens

# 출력 토큰 제한
response = model.generate_content(
    prompt,
    generation_config={
        "max_output_tokens": 200
    }
)
```

---

## 🚨 에러 처리

### 1. 쿼터 초과 (429)

```python
try:
    response = model.generate_content(prompt)
except Exception as e:
    if "429" in str(e):
        # Fallback: 간단한 방법 사용
        return fallback_method()
```

### 2. 타임아웃

```python
import time

for attempt in range(3):
    try:
        response = model.generate_content(prompt)
        break
    except Exception as e:
        if attempt < 2:
            time.sleep(2 ** attempt)  # 1초, 2초, 4초
        else:
            return fallback_method()
```

---

## 📈 모니터링

### API 사용량 확인

1. Google AI Studio 접속: https://aistudio.google.com
2. API Keys 메뉴
3. Usage 탭에서 사용량 확인

### 로깅

```python
import logging

logger = logging.getLogger(__name__)

# API 호출 로깅
logger.info(f"Gemini API called: {model_name}")
logger.info(f"Input tokens: {len(prompt.split())}")
logger.info(f"Output tokens: {len(response.text.split())}")
```

---

## 🔄 모델 변경 가이드

### 다른 모델로 변경 시

```bash
# 1. 모든 파일에서 모델명 교체
grep -rl "gemini-2.5-flash" . --include="*.py" | xargs sed -i '' 's/gemini-2.5-flash/gemini-1.5-flash/g'

# 2. 테스트
python3 test_env.py
python3 chatbot_news_community.py

# 3. 확인
grep -r "GenerativeModel" --include="*.py" .
```

---

## 📚 참고 자료

- Gemini API 문서: https://ai.google.dev/gemini-api/docs
- 가격 정보: https://ai.google.dev/pricing
- Rate Limits: https://ai.google.dev/gemini-api/docs/rate-limits
- Python SDK: https://github.com/google-gemini/generative-ai-python

---

## 📝 변경 이력

| 날짜 | 변경 내용 | 담당자 |
|------|-----------|--------|
| 2026-01-28 | gemini-2.5-flash로 통일 | 데이터팀 |
| 2026-01-26 | 초기 설정 (gemini-2.0-flash) | 데이터팀 |

---

## ✅ 체크리스트

프로젝트 배포 전 확인:

- [x] .env에 GEMINI_API_KEY 설정
- [x] 모든 모듈이 gemini-2.5-flash 사용
- [ ] 캐싱 구현
- [ ] 에러 처리 테스트
- [ ] API 사용량 모니터링 설정
- [ ] Fallback 로직 구현

---

문의: 데이터 파트
