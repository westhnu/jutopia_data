# Chatbot_05 백엔드 데이터 가이드 (뉴스/커뮤니티)

> 작성: 데이터 파트
> 대상: 챗봇 백엔드 개발자
> 최종 업데이트: 2026-01-28

---

## 1. 전달 파일 및 설정

### 1.1 파일 목록

| 파일명 | 용도 |
|--------|------|
| `chatbot_news_community.py` | Chatbot_05 메인 API |
| `stock_news_data.py` | 뉴스/커뮤니티 데이터 프로바이더 (의존) |
| `tavily_search.py` | 웹 검색 모듈 (의존) |
| `.env` | API 인증 정보 (별도 전달) |

### 1.2 필수 패키지

```bash
pip install python-dotenv tavily-python google-generativeai
```

### 1.3 .env 설정

```env
TAVILY_API_KEY=your_tavily_key
GEMINI_API_KEY=your_gemini_key
```

---

## 2. Quick Start

### 기본 사용법

```python
from chatbot_news_community import ChatbotNewsCommunity

chatbot = ChatbotNewsCommunity()

# 1단계: 커뮤니티 요약
community = chatbot.get_community_summary(
    symbol="005930",
    company_name="삼성전자"
)

# 2단계: 뉴스 요약
news = chatbot.get_news_summary(
    symbol="005930",
    company_name="삼성전자"
)

# 3단계: 카카오톡 형식 변환
kakao_community = chatbot.format_community_for_kakao(community, user_name="홍길동")
kakao_news = chatbot.format_news_for_kakao(news)
```

---

## 3. API 메서드 요약

### chatbot_news_community.py - ChatbotNewsCommunity

| 메서드 | 용도 | 주요 파라미터 |
|--------|------|---------------|
| `get_community_summary()` | 커뮤니티 분위기 요약 | symbol, company_name |
| `get_news_summary()` | 뉴스 핵심 이슈 | symbol, company_name |
| `format_community_for_kakao()` | 커뮤니티 → 카카오톡 형식 | summary, user_name |
| `format_news_for_kakao()` | 뉴스 → 카카오톡 형식 | summary |

---

## 4. 데이터 제공 순서 (기획 준수)

챗봇 기획에 따라 **"커뮤니티 → 뉴스"** 순서로 제공:

```
[사용자: "삼성전자 뉴스/커뮤니티"]
         ↓
[1단계] 커뮤니티 분위기 제공
         ↓
[퀵 버튼] 뉴스도 보기 클릭
         ↓
[2단계] 뉴스 핵심 이슈 제공
```

### 챗봇 플로우 예시

```python
# Step 1: 종목 선택 후 커뮤니티부터 제공
def chatbot_news_community_flow(symbol, company_name, user_name):
    chatbot = ChatbotNewsCommunity()

    # 1. 커뮤니티 요약
    community = chatbot.get_community_summary(symbol, company_name)
    kakao_comm = chatbot.format_community_for_kakao(community, user_name)
    send_to_user(kakao_comm)  # 카카오톡 API로 전송

    # 사용자가 "뉴스도 보기" 버튼 클릭 시
    # 2. 뉴스 요약
    news = chatbot.get_news_summary(symbol, company_name)
    kakao_news = chatbot.format_news_for_kakao(news)
    send_to_user(kakao_news)  # 카카오톡 API로 전송
```

---

## 5. API 응답 스키마

### 5.1 커뮤니티 요약 (`get_community_summary`)

```json
{
  "symbol": "005930",
  "company_name": "삼성전자",
  "sentiment_tone": "긍정",
  "sentiment_emoji": "😊",
  "summary_text": "전반적으로 긍정적인 의견이 많아요\n• 실적 개선 기대감이 주요 이유예요",
  "key_opinions": [
    "실적 바닥은 지난 것 같다",
    "외국인 수급이 계속 유입 중",
    "단기 급등은 부담"
  ],
  "timestamp": "방금 전까지",
  "web_url": "https://jutopia.com/stock/005930/community",
  "fetched_at": "2026-01-28 10:30:00"
}
```

### 5.2 뉴스 요약 (`get_news_summary`)

```json
{
  "symbol": "005930",
  "company_name": "삼성전자",
  "key_issues": [
    {
      "title": "2분기 실적이 시장 예상치를 상회했어요",
      "source": "한국경제",
      "url": "https://...",
      "impact": "HIGH"
    },
    {
      "title": "반도체 업황 회복 기대가 언급되고 있어요",
      "source": "매일경제",
      "url": "https://...",
      "impact": "MEDIUM"
    }
  ],
  "timestamp": "최근",
  "web_url": "https://jutopia.com/stock/005930/news",
  "fetched_at": "2026-01-28 10:30:00"
}
```

### 5.3 카카오톡 응답 (`format_community_for_kakao`)

**커뮤니티 응답 구조:**

```json
{
  "version": "2.0",
  "template": {
    "outputs": [
      {
        "simpleText": {
          "text": "방금 전까지 삼성전자에 대한\n커뮤니티 분위기부터 알려드릴게요 😊\n\n전반적으로 긍정적인 의견이 많아요\n• 실적 개선 기대감이 주요 이유예요"
        }
      },
      {
        "simpleText": {
          "text": "대표적인 의견을 몇 개 보면 아래와 같아요 :)\n\n- \"실적 바닥은 지난 것 같다\"\n- \"외국인 수급이 계속 유입 중\"\n- \"단기 급등은 부담\"\n\n자세한 커뮤니티는 하단의 퀵 버튼을 눌러 웹에서 확인하세요 !"
        }
      }
    ],
    "quickReplies": [
      {
        "action": "block",
        "label": "뉴스도 보기",
        "messageText": "삼성전자 뉴스",
        "blockId": "news_block"
      },
      {
        "action": "block",
        "label": "다른 종목 보기",
        "messageText": "다른 종목",
        "blockId": "select_stock_block"
      },
      {
        "action": "webLink",
        "label": "웹에서 자세히 보기",
        "webLinkUrl": "https://jutopia.com/stock/005930/community"
      },
      {
        "action": "block",
        "label": "기능 종료",
        "messageText": "메인으로",
        "blockId": "main_block"
      }
    ]
  }
}
```

**뉴스 응답 구조:**

```json
{
  "version": "2.0",
  "template": {
    "outputs": [
      {
        "simpleText": {
          "text": "최근 삼성전자 관련\n주요 뉴스도 정리해봤어요.\n\n• 2분기 실적이 시장 예상치를 상회했어요\n• 반도체 업황 회복 기대가 언급되고 있어요"
        }
      }
    ],
    "quickReplies": [
      {
        "action": "webLink",
        "label": "기사 원문 보기",
        "webLinkUrl": "https://..."
      },
      {
        "action": "block",
        "label": "다른 종목 보기",
        "messageText": "다른 종목",
        "blockId": "select_stock_block"
      },
      {
        "action": "webLink",
        "label": "웹에서 더 보기",
        "webLinkUrl": "https://jutopia.com/stock/005930/news"
      },
      {
        "action": "block",
        "label": "기능 종료",
        "messageText": "메인으로",
        "blockId": "main_block"
      }
    ]
  }
}
```

### 5.4 에러 응답

```json
{
  "error": "에러 메시지",
  "fetched_at": "2026-01-28 10:30:00"
}
```

**카카오톡 에러 응답:**

```json
{
  "version": "2.0",
  "template": {
    "outputs": [{
      "simpleText": {
        "text": "❌ 에러 메시지\n잠시 후 다시 시도해주세요."
      }
    }]
  }
}
```

---

## 6. 파라미터 값 정리

### sentiment_tone (감정 톤)

| 값 | 의미 | 이모지 |
|----|------|--------|
| `긍정` | 전반적으로 긍정적 의견 | 😊 |
| `중립` | 긍정/부정 비슷 | 😐 |
| `부정` | 조심스러운 의견 | 😟 |

### impact (투자 영향도)

| 값 | 의미 | 노출 |
|----|------|------|
| `HIGH` | 투자 판단에 큰 영향 | O |
| `MEDIUM` | 투자 참고 가능 | O |
| `LOW` | 낮은 영향 | X (필터링됨) |

### timestamp (실시간성 표현)

| 값 | 의미 |
|----|------|
| `방금 전까지` | 최근 몇 분~몇 시간 |
| `최근 몇 시간 기준으로` | 오늘 기준 |
| `오늘 기준` | 당일 데이터 |

---

## 7. 기획 준수 사항

### 7.1 챗봇의 역할

| 항목 | 내용 |
|------|------|
| 역할 | **요약 채널** (목록 제공 X) |
| 커뮤니티 | 분위기 (감정 톤) |
| 뉴스 | 사실 (이벤트/이슈) |
| 제공 개수 | 3~5개 핵심만 |
| 상세 정보 | 웹으로 연결 |

### 7.2 실시간성 표현

- 언어적 표현으로 실시간성 전달
- 사용 문구: "방금 전까지", "최근 몇 시간 기준으로", "오늘 기준"

### 7.3 뉴스 필터링 기준

**1차 필터: 제목 키워드 기반**

| 카테고리 | 키워드 |
|---------|--------|
| 실적 | 실적, 매출, 영업이익, 순이익 |
| 주가 | 급등, 급락, 주가, 목표가 |
| 주주환원 | 배당, 자사주, 증자 |
| 공시/규제 | 공시, 규제, 승인 |
| M&A | 인수, 합병, M&A |

**2차 필터: 투자 영향도 분류**
- HIGH: 키워드 2개 이상 매칭
- MEDIUM: 키워드 1개 매칭
- LOW: 매칭 없음 → 필터링

---

## 8. 챗봇 블록 연동 가이드

### 8.1 필요한 블록 ID

카카오톡 챗봇 빌더에서 다음 블록들을 생성하고 ID를 설정해야 합니다:

| 블록명 | 블록 ID | 용도 |
|--------|---------|------|
| 뉴스 블록 | `news_block` | "뉴스도 보기" 버튼 클릭 시 |
| 종목 선택 블록 | `select_stock_block` | "다른 종목 보기" 클릭 시 |
| 메인 블록 | `main_block` | "기능 종료" 클릭 시 |

### 8.2 블록 ID 수정 방법

`chatbot_news_community.py`의 다음 부분을 실제 블록 ID로 교체:

```python
# format_community_for_kakao() 메서드 내
"quickReplies": [
    {
        "action": "block",
        "label": "뉴스도 보기",
        "blockId": "YOUR_ACTUAL_NEWS_BLOCK_ID"  # ← 여기 수정
    },
    # ...
]
```

---

## 9. API 호출 최적화

### 9.1 캐싱 권장

| 데이터 | TTL | 이유 |
|--------|-----|------|
| 커뮤니티 | 30초~1분 | 실시간성 중요 |
| 뉴스 | 5분 | 뉴스 업데이트 주기 |

### 9.2 비용 최적화

| API | 호출 시점 | 비용 |
|-----|-----------|------|
| Tavily | 커뮤니티/뉴스 요청 시 | 검색당 과금 |
| Gemini | 대표 의견/핵심 이슈 추출 시 | 토큰당 과금 |

**최적화 팁:**
- 동일 종목 반복 요청 시 캐싱 필수
- LLM 호출 최소화 (필요시만 활성화)

---

## 10. 에러 처리

### 10.1 주요 에러 시나리오

| 에러 | 원인 | 대응 |
|------|------|------|
| `Tavily 검색 불가` | API 키 오류 | .env 확인 |
| `데이터 없음` | 검색 결과 0건 | 사용자에게 안내 |
| `LLM 호출 실패` | Gemini API 오류 | 원본 데이터 사용 |

### 10.2 에러 응답 예시

```python
if "error" in community:
    # 사용자에게 친절한 메시지 전송
    error_msg = {
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {
                    "text": "❌ 데이터를 불러올 수 없습니다.\n잠시 후 다시 시도해주세요."
                }
            }]
        }
    }
```

---

## 11. 테스트

### 11.1 단위 테스트

```bash
# 모듈 테스트
python chatbot_news_community.py
```

**출력 예시:**
```
====================================
Chatbot_05 뉴스/커뮤니티 테스트
====================================

[1단계] 커뮤니티 요약
----------------------------------------
감정 톤: 긍정 😊
요약: 전반적으로 긍정적인 의견이 많아요
• 실적 개선 기대감이 주요 이유예요
대표 의견:
  - 실적 바닥은 지난 것 같다
  - 외국인 수급이 계속 유입 중

[2단계] 뉴스 요약
----------------------------------------
핵심 이슈 3건:
  [HIGH] 2분기 실적이 시장 예상치를 상회했어요
  [MEDIUM] 반도체 업황 회복 기대가 언급되고 있어요
  [HIGH] 목표주가 20만원 유지

✅ 테스트 완료
```

### 11.2 통합 테스트

```python
# 챗봇 플로우 전체 테스트
def test_full_flow():
    chatbot = ChatbotNewsCommunity()

    # 1. 커뮤니티
    community = chatbot.get_community_summary("005930", "삼성전자")
    assert "sentiment_tone" in community
    assert len(community.get("key_opinions", [])) <= 3

    # 2. 뉴스
    news = chatbot.get_news_summary("005930", "삼성전자")
    assert len(news.get("key_issues", [])) >= 3
    assert len(news.get("key_issues", [])) <= 5

    # 3. 카카오톡 형식
    kakao_comm = chatbot.format_community_for_kakao(community)
    assert kakao_comm["version"] == "2.0"
    assert len(kakao_comm["template"]["outputs"]) == 2  # 2개 메시지

    print("✅ 통합 테스트 통과")

test_full_flow()
```

---

## 12. 배포 체크리스트

- [ ] `.env` 파일에 API 키 설정 (TAVILY_API_KEY, GEMINI_API_KEY)
- [ ] 필수 패키지 설치 (`tavily-python`, `google-generativeai`)
- [ ] 카카오톡 블록 ID 수정 (`news_block`, `select_stock_block`, `main_block`)
- [ ] 캐싱 구현 (커뮤니티 30초, 뉴스 5분)
- [ ] 에러 핸들링 테스트
- [ ] 단위 테스트 통과
- [ ] 통합 테스트 통과

---

## 13. 문의

데이터 관련 문의사항은 데이터 파트로 연락 바랍니다.

---

## 14. 참고 문서

- [docs/chatbot_specification.md](chatbot_specification.md) - 챗봇 전체 기획
- [docs/backend_data_guide_web02.md](backend_data_guide_web02.md) - Web_02 뉴스/커뮤니티 API
- [stock_news_data.py](../stock_news_data.py) - 데이터 프로바이더 소스코드
- [chatbot_news_community.py](../chatbot_news_community.py) - Chatbot_05 API 소스코드
