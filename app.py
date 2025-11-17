# app.py - 실시간 주식 차트 Streamlit 앱
# -*- coding: utf-8 -*-
"""
검색 기능이 포함된 실시간 주식 차트 대시보드
"""

import streamlit as st
from stock_analyzer import StockAnalyzer
from stock_chart_visualizer import StockChartVisualizer

# 페이지 설정
st.set_page_config(page_title="주식 차트", page_icon="📈", layout="wide")

# 초기화 (실시간 모드)
@st.cache_resource
def get_analyzer():
    return StockAnalyzer(use_realtime=True)

@st.cache_resource
def get_visualizer():
    analyzer = StockAnalyzer(use_realtime=True)
    return StockChartVisualizer(analyzer=analyzer)

analyzer = get_analyzer()
visualizer = get_visualizer()

# CSS
st.markdown("""
    <style>
    .main { padding: 1rem; }
    .stMetric { background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.header("🔍 종목 검색")

    # 검색 방법 선택
    search_method = st.radio(
        "검색 방법",
        ["종목 코드", "종목명"],
        horizontal=True
    )

    ticker = None

    if search_method == "종목코드":
        ticker = st.text_input(
            "종목 코드 (6자리)",
            value="005930",
            max_chars=6,
            placeholder="예: 005930"
        )

    else:  # 검색하기
        search_keyword = st.text_input(
            "종목명",
            placeholder="예: 삼성, 카카오"
        )

        if search_keyword:
            with st.spinner("🔍 검색 중..."):
                search_results = analyzer.search_stock(search_keyword)

            if search_results:
                st.success(f"✅ {len(search_results)}개 종목 발견")

                # 검색 결과 선택
                options = {
                    f"{r['name']} ({r['ticker']}) - {r['market']}": r['ticker']
                    for r in search_results
                }
                selected = st.selectbox("종목 선택", options=list(options.keys()))
                ticker = options[selected]
            else:
                st.warning("⚠️ 검색 결과가 없습니다.")
                ticker = "005930"
        else:
            ticker = "005930"

    # 기간 선택
    st.markdown("---")
    days = st.slider("데이터 수집 기간 (일)", 30, 365, 120, 10)

    st.markdown("---")

    # 빠른 선택
    st.subheader("📌 주요 종목")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("삼성전자", use_container_width=True):
            st.session_state.ticker = "005930"
        if st.button("네이버", use_container_width=True):
            st.session_state.ticker = "035420"
    with col2:
        if st.button("SK하이닉스", use_container_width=True):
            st.session_state.ticker = "000660"
        if st.button("카카오", use_container_width=True):
            st.session_state.ticker = "035720"

# 버튼으로 선택한 경우
if 'ticker' in st.session_state:
    ticker = st.session_state.ticker

# 메인
st.title("📈 주식 차트 대시보드")

if not ticker:
    st.info("👈 사이드바에서 종목을 선택하세요")
    st.stop()

st.markdown(f"**종목 코드**: `{ticker}` | **기간**: {days}일")
st.markdown("---")

# 데이터 수집
with st.spinner(f"📡 {ticker} 데이터 수집 중..."):
    info = visualizer.get_stock_info(ticker)

if 'error' in info:
    st.error(f"❌ {info['error']}")
    st.info("💡 다른 종목을 검색해보세요.")
    st.stop()

st.success(f"✅ {info['name']} 데이터 수집 완료!")

# 종목 정보 카드
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📌 종목명",
        value=info['name']
    )

with col2:
    st.metric(
        label="💰 현재가",
        value=f"{info['current_price']:,.0f}원"
    )

with col3:
    rsi = info['rsi']
    rsi_color = "🔴" if rsi > 70 else "🔵" if rsi < 30 else "🟢"
    st.metric(
        label="📊 RSI",
        value=f"{rsi:.1f}",
        delta=f"{rsi_color} {info['rsi_signal']}"
    )

with col4:
    st.metric(
        label="📈 추세",
        value=info['trend']
    )

# 이동평균선 정보
with st.expander("📉 이동평균선 정보"):
    col1, col2, col3 = st.columns(3)
    col1.metric("MA5", f"{info['ma5']:,.0f}원")
    col2.metric("MA20", f"{info['ma20']:,.0f}원")
    col3.metric("MA60", f"{info['ma60']:,.0f}원")

st.markdown("---")

# 차트 탭
tab1, tab2, tab3 = st.tabs([
    "📊 캔들스틱",
    "📈 기술적 분석",
    "📉 가격 추이"
])

with tab1:
    st.subheader(f"{info['name']} 캔들스틱 차트")
    with st.spinner("차트 생성 중..."):
        fig = visualizer.create_candlestick_chart(ticker, days)
        st.plotly_chart(fig, use_container_width=True)
    st.info("💡 차트를 드래그하여 줌인/줌아웃할 수 있습니다.")

with tab2:
    st.subheader(f"{info['name']} 기술적 분석")
    with st.spinner("차트 생성 중..."):
        fig = visualizer.create_technical_chart(ticker, days)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("ℹ️ 기술적 지표 설명"):
        st.markdown("""
        - **볼린저 밴드**: 주가의 변동성을 측정하는 지표
        - **RSI**: 과매수/과매도 여부를 판단 (70 이상: 과매수, 30 이하: 과매도)
        - **거래량**: 매매 활동의 강도
        """)

with tab3:
    st.subheader(f"{info['name']} 가격 추이")
    with st.spinner("차트 생성 중..."):
        fig = visualizer.create_price_line_chart(ticker, days)
        st.plotly_chart(fig, use_container_width=True)

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #7f8c8d; padding: 1rem 0;'>
        <p>📡 실시간 데이터 | FinanceDataReader API</p>
        <p style='font-size: 0.9rem;'>종목 검색 → 즉시 최신 데이터 수집</p>
    </div>
    """,
    unsafe_allow_html=True
)
