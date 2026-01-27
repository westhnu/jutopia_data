# 웹 백엔드 개발자용 데이터 가이드

> 작성: 데이터 파트
> 대상: 웹 백엔드 개발자
> 최종 업데이트: 2026-01-26

---

## 가이드 문서 목록

| 문서 | 대상 기능 | 파일 |
|------|----------|------|
| [Web_01 가이드](backend_data_guide_web01.md) | 차트 / 종목 리스트 | `stock_chart_data.py`, `stock_list_data.py` |
| [Web_02 가이드](backend_data_guide_web02.md) | 뉴스 / 커뮤니티 | `stock_news_data.py`, `tavily_search.py` |

---

## 전체 파일 목록

| 파일명 | 용도 | 관련 가이드 |
|--------|------|-------------|
| `stock_chart_data.py` | 차트 페이지 데이터 + Plotly 차트 생성 | Web_01 |
| `stock_list_data.py` | 종목 리스트 데이터 | Web_01 |
| `stock_news_data.py` | 뉴스/커뮤니티 데이터 | Web_02 |
| `tavily_search.py` | 웹 검색 모듈 | Web_02 |
| `HantuStock.py` | 한국투자증권 API 연동 | Web_01 |
| `.env` | API 인증 정보 (별도 전달) | 공통 |

---

## 전체 필수 패키지

```bash
# Web_01 (차트/종목)
pip install finance-datareader python-dotenv requests pandas plotly pykrx

# Web_02 (뉴스/커뮤니티)
pip install tavily-python google-generativeai
```

---

## 전체 .env 설정

```env
# 한국투자증권 API (Web_01)
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCOUNT_ID=your_account_id
KIS_ENV=vps  # vps: 모의투자, prod: 실전

# 뉴스/커뮤니티 API (Web_02)
TAVILY_API_KEY=your_tavily_key
GEMINI_API_KEY=your_gemini_key  # LLM 필터링용 (선택)
```

---

## 문의

데이터 관련 문의사항은 데이터 파트로 연락 바랍니다.
