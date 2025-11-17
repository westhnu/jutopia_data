# stock_chart_visualizer.py - 주식 차트 시각화 전용 모듈
# -*- coding: utf-8 -*-
"""
Plotly를 사용한 주식 차트 시각화 함수 모음
다른 웹 프레임워크(Streamlit, FastAPI 등)에서 import하여 사용
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from stock_analyzer import StockAnalyzer


class StockChartVisualizer:
    """주식 차트 시각화 클래스 - Plotly 차트 생성"""

    def __init__(self, analyzer=None):
        """
        Args:
            analyzer: StockAnalyzer 인스턴스 (없으면 자동 생성)
        """
        self.analyzer = analyzer or StockAnalyzer()

    # ========================================================================
    # 1. 캔들스틱 차트 (이동평균선 포함)
    # ========================================================================

    def create_candlestick_chart(self, ticker: str, days: int = 60):
        """
        캔들스틱 차트 생성 (5/20/60일 이동평균선 포함)

        Args:
            ticker: 종목코드 (예: '005930')
            days: 표시할 기간 (일)

        Returns:
            plotly.graph_objects.Figure
        """
        df = self.analyzer.load_price_data(ticker, days=days)
        if df.empty:
            return self._create_error_figure(f"종목 {ticker} 데이터를 찾을 수 없습니다")

        stock_name = self.analyzer.get_stock_name(ticker)

        # 캔들스틱
        fig = go.Figure(data=[go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color='red',
            decreasing_line_color='blue',
            name='가격'
        )])

        # 이동평균선 추가
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()

        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['MA5'], name='MA5',
            line=dict(color='orange', width=1.5)
        ))
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['MA20'], name='MA20',
            line=dict(color='green', width=1.5)
        ))
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['MA60'], name='MA60',
            line=dict(color='purple', width=1.5)
        ))

        fig.update_layout(
            title=f"{stock_name} ({ticker}) 캔들스틱 차트",
            yaxis_title="가격 (원)",
            xaxis_title="날짜",
            height=600,
            xaxis_rangeslider_visible=False,
            hovermode='x unified',
            template='plotly_white'
        )

        return fig

    # ========================================================================
    # 2. 기술적 분석 차트 (볼린저밴드 + RSI + 거래량)
    # ========================================================================

    def create_technical_chart(self, ticker: str, days: int = 60):
        """
        기술적 분석 차트 (3개 서브플롯)
        - 볼린저 밴드
        - 거래량
        - RSI

        Args:
            ticker: 종목코드
            days: 표시할 기간

        Returns:
            plotly.graph_objects.Figure
        """
        df = self.analyzer.load_price_data(ticker, days=days)
        if df.empty:
            return self._create_error_figure(f"종목 {ticker} 데이터를 찾을 수 없습니다")

        stock_name = self.analyzer.get_stock_name(ticker)

        # 서브플롯 생성
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=(
                f"{stock_name} ({ticker}) 볼린저 밴드",
                "거래량",
                "RSI (14일)"
            )
        )

        # 1) 볼린저 밴드
        sma = df['close'].rolling(window=20).mean()
        std = df['close'].rolling(window=20).std()
        df['BB_upper'] = sma + (std * 2)
        df['BB_middle'] = sma
        df['BB_lower'] = sma - (std * 2)

        # 밴드 영역 채우기
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['BB_upper'],
            name='상단', line=dict(color='rgba(255,0,0,0.3)'),
            showlegend=False
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['BB_lower'],
            name='하단', line=dict(color='rgba(0,255,0,0.3)'),
            fill='tonexty', fillcolor='rgba(200,200,200,0.2)',
            showlegend=False
        ), row=1, col=1)

        # 종가 라인
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['close'], name='종가',
            line=dict(color='black', width=2)
        ), row=1, col=1)

        # 중간선
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['BB_middle'], name='중간(20MA)',
            line=dict(color='blue', width=1, dash='dash')
        ), row=1, col=1)

        # 2) 거래량
        colors = ['red' if df['close'].iloc[i] >= df['open'].iloc[i] else 'blue'
                  for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df['timestamp'], y=df['volume'], name='거래량',
            marker_color=colors, showlegend=False
        ), row=2, col=1)

        # 3) RSI
        df['RSI'] = self.analyzer.calculate_rsi(df['close'])
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['RSI'], name='RSI',
            line=dict(color='purple', width=2)
        ), row=3, col=1)

        # RSI 기준선
        fig.add_hline(y=70, line_dash="dash", line_color="red",
                     annotation_text="과매수(70)", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="blue",
                     annotation_text="과매도(30)", row=3, col=1)

        # 레이아웃
        fig.update_layout(
            height=900,
            hovermode='x unified',
            template='plotly_white'
        )
        fig.update_yaxes(title_text="가격 (원)", row=1, col=1)
        fig.update_yaxes(title_text="거래량", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1)
        fig.update_xaxes(title_text="날짜", row=3, col=1)

        return fig

    # ========================================================================
    # 3. 가격 추이 차트 (라인)
    # ========================================================================

    def create_price_line_chart(self, ticker: str, days: int = 60):
        """
        단순 가격 라인 차트

        Args:
            ticker: 종목코드
            days: 표시할 기간

        Returns:
            plotly.graph_objects.Figure
        """
        df = self.analyzer.load_price_data(ticker, days=days)
        if df.empty:
            return self._create_error_figure(f"종목 {ticker} 데이터를 찾을 수 없습니다")

        stock_name = self.analyzer.get_stock_name(ticker)

        fig = go.Figure()

        # 종가 라인
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['close'], name='종가',
            line=dict(color='#2980b9', width=2),
            mode='lines',
            fill='tozeroy', fillcolor='rgba(41,128,185,0.1)'
        ))

        fig.update_layout(
            title=f"{stock_name} ({ticker}) 가격 추이",
            xaxis_title="날짜",
            yaxis_title="가격 (원)",
            height=500,
            hovermode='x unified',
            template='plotly_white'
        )

        return fig

    # ========================================================================
    # 4. 거래량 차트
    # ========================================================================

    def create_volume_chart(self, ticker: str, days: int = 60):
        """
        거래량 막대 차트

        Args:
            ticker: 종목코드
            days: 표시할 기간

        Returns:
            plotly.graph_objects.Figure
        """
        df = self.analyzer.load_price_data(ticker, days=days)
        if df.empty:
            return self._create_error_figure(f"종목 {ticker} 데이터를 찾을 수 없습니다")

        stock_name = self.analyzer.get_stock_name(ticker)

        # 색상: 양봉(빨강), 음봉(파랑)
        colors = ['red' if df['close'].iloc[i] >= df['open'].iloc[i] else 'blue'
                  for i in range(len(df))]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df['timestamp'], y=df['volume'],
            marker_color=colors,
            name='거래량'
        ))

        fig.update_layout(
            title=f"{stock_name} ({ticker}) 거래량",
            xaxis_title="날짜",
            yaxis_title="거래량",
            height=400,
            hovermode='x unified',
            template='plotly_white'
        )

        return fig

    # ========================================================================
    # 5. 종목 비교 차트
    # ========================================================================

    def create_comparison_chart(self, tickers: list, days: int = 60):
        """
        여러 종목 수익률 비교 (정규화)

        Args:
            tickers: 종목코드 리스트 ['005930', '000660', ...]
            days: 표시할 기간

        Returns:
            plotly.graph_objects.Figure
        """
        fig = go.Figure()

        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']

        for i, ticker in enumerate(tickers):
            df = self.analyzer.load_price_data(ticker, days=days)
            if df.empty:
                continue

            # 정규화 (첫날 = 100)
            normalized = (df['close'] / df['close'].iloc[0]) * 100
            name = self.analyzer.get_stock_name(ticker)

            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=normalized,
                name=name,
                line=dict(color=colors[i % len(colors)], width=2),
                mode='lines'
            ))

        fig.add_hline(y=100, line_dash="dash", line_color="gray",
                     annotation_text="시작점(100)")

        fig.update_layout(
            title="종목 수익률 비교 (시작=100)",
            xaxis_title="날짜",
            yaxis_title="상대 수익률",
            height=600,
            hovermode='x unified',
            template='plotly_white'
        )

        return fig

    # ========================================================================
    # 6. 시장 지수 차트
    # ========================================================================

    def create_index_chart(self, index_code: str = 'KS11', days: int = 120):
        """
        시장 지수 차트 (이동평균선 포함)

        Args:
            index_code: 'KS11' (코스피) 또는 'KQ11' (코스닥)
            days: 표시할 기간

        Returns:
            plotly.graph_objects.Figure
        """
        df = self.analyzer.load_index_data(index_code)
        if df.empty:
            return self._create_error_figure(f"지수 {index_code} 데이터를 찾을 수 없습니다")

        df = df.tail(days)
        index_name = "코스피" if index_code == "KS11" else "코스닥"

        # 이동평균
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()

        fig = go.Figure()

        # 지수
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['close'], name=index_name,
            line=dict(color='#2980b9', width=2)
        ))

        # 이동평균선
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['MA20'], name='MA20',
            line=dict(color='orange', width=1.5, dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['MA60'], name='MA60',
            line=dict(color='green', width=1.5, dash='dash')
        ))

        fig.update_layout(
            title=f"{index_name} 지수 추이",
            xaxis_title="날짜",
            yaxis_title="지수",
            height=600,
            hovermode='x unified',
            template='plotly_white'
        )

        return fig

    # ========================================================================
    # 유틸리티
    # ========================================================================

    def _create_error_figure(self, error_message: str):
        """에러 메시지 표시용 Figure"""
        fig = go.Figure()
        fig.add_annotation(
            text=error_message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color="red")
        )
        fig.update_layout(height=400)
        return fig

    def get_stock_info(self, ticker: str):
        """
        종목 기본 정보 조회

        Args:
            ticker: 종목코드

        Returns:
            dict: 종목 정보
        """
        tech = self.analyzer.analyze_stock_technical(ticker, indicators=['RSI', 'MA'])

        if 'error' in tech:
            return tech

        return {
            'ticker': ticker,
            'name': tech['name'],
            'current_price': tech['current_price'],
            'trend': tech.get('trend', '-'),
            'rsi': tech['rsi']['value'],
            'rsi_signal': tech['rsi']['signal'],
            'ma5': tech['moving_averages'].get('MA5', 0),
            'ma20': tech['moving_averages'].get('MA20', 0),
            'ma60': tech['moving_averages'].get('MA60', 0),
        }


# ========================================================================
# 사용 예시
# ========================================================================

if __name__ == "__main__":
    import sys
    import io

    # Windows 콘솔 인코딩
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # 시각화 객체 생성
    visualizer = StockChartVisualizer()

    print("=" * 80)
    print("주식 차트 시각화 테스트")
    print("=" * 80)

    # 테스트: 삼성전자
    ticker = '005930'
    print(f"\n테스트 종목: {ticker}")

    # 1. 종목 정보 조회
    info = visualizer.get_stock_info(ticker)
    print(f"\n[종목 정보]")
    print(f"  이름: {info['name']}")
    print(f"  현재가: {info['current_price']:,.0f}원")
    print(f"  추세: {info['trend']}")
    print(f"  RSI: {info['rsi']:.1f} ({info['rsi_signal']})")

    # 2. 차트 생성 (HTML로 저장)
    print(f"\n[차트 생성]")

    # 캔들스틱
    fig1 = visualizer.create_candlestick_chart(ticker, days=60)
    fig1.write_html("test_candlestick.html")
    print("  ✓ 캔들스틱 차트: test_candlestick.html")

    # 기술적 분석
    fig2 = visualizer.create_technical_chart(ticker, days=60)
    fig2.write_html("test_technical.html")
    print("  ✓ 기술적 분석 차트: test_technical.html")

    # 가격 라인
    fig3 = visualizer.create_price_line_chart(ticker, days=60)
    fig3.write_html("test_price_line.html")
    print("  ✓ 가격 라인 차트: test_price_line.html")

    # 종목 비교
    fig4 = visualizer.create_comparison_chart(['005930', '000660', '035420'], days=60)
    fig4.write_html("test_comparison.html")
    print("  ✓ 종목 비교 차트: test_comparison.html")

    # 코스피 지수
    fig5 = visualizer.create_index_chart('KS11', days=120)
    fig5.write_html("test_index.html")
    print("  ✓ 코스피 지수 차트: test_index.html")

    print("\n" + "=" * 80)
    print("완료! HTML 파일을 브라우저에서 열어보세요.")
    print("=" * 80)
