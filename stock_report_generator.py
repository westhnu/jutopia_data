# -*- coding: utf-8 -*-
"""
종목 리포트 생성기 (LLM 기반)
- report.simple: 간단한 리포트 (30초)
- report.detail: 상세 리포트 (1분)
"""

import os
from typing import Dict, Optional
from stock_analyzer import StockAnalyzer
from financial_analyzer import FinancialAnalyzer


class StockReportGenerator:
    """LLM 기반 종목 리포트 생성"""

    def __init__(self, llm_api_key: Optional[str] = None):
        """
        Args:
            llm_api_key: OpenAI API 키 or Anthropic API 키
        """
        self.analyzer = StockAnalyzer(use_realtime=True)
        self.financial = FinancialAnalyzer()
        self.llm_api_key = llm_api_key or os.getenv("OPENAI_API_KEY")

    # ========================================
    # 1. 데이터 수집 (규칙 기반 - LLM 불필요)
    # ========================================

    def collect_stock_data(self, ticker: str) -> Dict:
        """
        종목 데이터 수집 (규칙 기반)

        Returns:
            {
                'basic': {...},        # 기본 정보
                'technical': {...},    # 기술적 분석
                'financial': {...},    # 재무 분석
                'news': [...]          # 최근 공시
            }
        """
        # 1. 기본 정보
        stock_name = self.analyzer.get_stock_name(ticker)
        df = self.analyzer.load_price_data(ticker, days=120)

        if df.empty:
            return {'error': f'종목 {ticker} 데이터를 찾을 수 없습니다'}

        current_price = df.iloc[-1]['close']
        prev_price = df.iloc[-2]['close'] if len(df) > 1 else current_price
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price * 100) if prev_price > 0 else 0

        basic_info = {
            'ticker': ticker,
            'name': stock_name,
            'current_price': int(current_price),
            'price_change': int(price_change),
            'price_change_pct': round(price_change_pct, 2),
            'volume': int(df.iloc[-1]['volume'])
        }

        # 2. 기술적 분석
        technical = self.analyzer.analyze_stock_technical(
            ticker,
            indicators=['rsi', 'bollinger', 'moving_averages']
        )

        # RSI 해석
        rsi = technical.get('rsi', {}).get('rsi', 50)
        if rsi > 70:
            rsi_signal = "과매수 (조정 가능성)"
        elif rsi < 30:
            rsi_signal = "과매도 (반등 가능성)"
        else:
            rsi_signal = "중립"

        # 이동평균 추세
        ma_data = technical.get('moving_averages', {})
        ma5 = ma_data.get('ma5', 0)
        ma20 = ma_data.get('ma20', 0)
        ma60 = ma_data.get('ma60', 0)

        if ma5 > ma20 > ma60:
            trend = "강한 상승 추세 (정배열)"
        elif ma5 < ma20 < ma60:
            trend = "강한 하락 추세 (역배열)"
        elif ma5 > ma20:
            trend = "상승 전환 신호"
        else:
            trend = "하락 또는 횡보"

        technical_summary = {
            'rsi': round(rsi, 1),
            'rsi_signal': rsi_signal,
            'ma5': int(ma5),
            'ma20': int(ma20),
            'ma60': int(ma60),
            'trend': trend
        }

        # 3. 재무 분석 (DART 데이터 있으면)
        financial_summary = {}
        try:
            fin_result = self.financial.calculate_financial_ratios(ticker)
            if 'error' not in fin_result:
                ratios = fin_result['ratios']
                grades = fin_result['grades']
                financial_summary = {
                    'debt_ratio': ratios['debt_ratio'],
                    'roe': ratios['roe'],
                    'current_ratio': ratios['current_ratio'],
                    'grade': grades['overall'],
                    'comment': fin_result['comments']['summary']
                }
        except:
            financial_summary = {'error': '재무 데이터 없음'}

        # 4. 최근 공시 (있으면)
        recent_filings = []
        # TODO: collectors.py에서 공시 데이터 로드

        return {
            'basic': basic_info,
            'technical': technical_summary,
            'financial': financial_summary,
            'filings': recent_filings
        }

    # ========================================
    # 2. LLM 리포트 생성
    # ========================================

    def generate_simple_report(self, ticker: str) -> str:
        """
        간단한 리포트 생성 (LLM 사용)

        Returns:
            카카오톡 전송용 텍스트
        """
        # 1. 데이터 수집 (규칙 기반)
        data = self.collect_stock_data(ticker)

        if 'error' in data:
            return f"❌ {data['error']}"

        # 2. LLM 없이 템플릿 기반 (빠른 응답)
        return self._format_simple_report_template(data)

    def generate_detail_report(self, ticker: str) -> str:
        """
        상세 리포트 생성 (LLM 사용)

        Returns:
            카카오톡 전송용 텍스트
        """
        # 1. 데이터 수집
        data = self.collect_stock_data(ticker)

        if 'error' in data:
            return f"❌ {data['error']}"

        # 2. LLM 호출 (상세 분석)
        if self.llm_api_key:
            return self._generate_llm_report(data)
        else:
            # LLM 없으면 템플릿 사용
            return self._format_detail_report_template(data)

    # ========================================
    # 3. 템플릿 기반 리포트 (LLM 불필요)
    # ========================================

    def _format_simple_report_template(self, data: Dict) -> str:
        """템플릿 기반 간단 리포트 (LLM 불필요)"""
        basic = data['basic']
        tech = data['technical']

        # 변동 기호
        change_symbol = "▲" if basic['price_change'] >= 0 else "▼"
        change_text = f"{change_symbol} {abs(basic['price_change']):,}원 ({abs(basic['price_change_pct']):.2f}%)"

        report = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 {basic['name']} 간단 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 현재가: {basic['current_price']:,}원
📈 변동: {change_text}

【 기술적 분석 】
├ RSI: {tech['rsi']} ({tech['rsi_signal']})
├ 추세: {tech['trend']}
└ MA5/20/60: {tech['ma5']:,} / {tech['ma20']:,} / {tech['ma60']:,}
"""

        # 재무 분석 (있으면)
        if 'error' not in data['financial']:
            fin = data['financial']
            report += f"""
【 재무 건전성 】
├ 등급: {fin['grade']}
├ 부채비율: {fin['debt_ratio']:.1f}%
└ ROE: {fin['roe']:.1f}%
"""

        report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 [상세 리포트] [차트 보기]
"""
        return report

    def _format_detail_report_template(self, data: Dict) -> str:
        """템플릿 기반 상세 리포트 (LLM 불필요)"""
        basic = data['basic']
        tech = data['technical']
        fin = data.get('financial', {})

        # 간단 리포트 + 추가 정보
        report = self._format_simple_report_template(data)

        # 투자 의견 (규칙 기반)
        signals = []
        if tech['rsi'] < 30:
            signals.append("✅ RSI 과매도 - 반등 가능성")
        if tech['rsi'] > 70:
            signals.append("⚠️ RSI 과매수 - 조정 주의")
        if "정배열" in tech['trend']:
            signals.append("✅ 이동평균 정배열 - 상승 추세")
        if 'error' not in fin and fin.get('grade') in ['A+', 'A', 'A-']:
            signals.append("✅ 재무 건전성 우수")

        if signals:
            report += "\n【 투자 포인트 】\n"
            report += "\n".join(signals)

        return report

    # ========================================
    # 4. LLM 기반 리포트 (선택사항)
    # ========================================

    def _generate_llm_report(self, data: Dict) -> str:
        """
        LLM을 사용한 상세 리포트 생성

        이 부분은 OpenAI/Claude API 연동
        """
        # LLM 프롬프트 구성
        prompt = self._create_llm_prompt(data)

        # TODO: LLM API 호출
        # response = openai.ChatCompletion.create(...)
        # return response['choices'][0]['message']['content']

        # 현재는 템플릿 반환
        return self._format_detail_report_template(data) + """

🤖 LLM 분석 (추가)
━━━━━━━━━━━━━━━━━━━━━━━━━━
(LLM API 키 설정 시 AI 분석 제공)
"""

    def _create_llm_prompt(self, data: Dict) -> str:
        """LLM 프롬프트 생성"""
        basic = data['basic']
        tech = data['technical']
        fin = data.get('financial', {})

        prompt = f"""
당신은 전문 증권 애널리스트입니다. 다음 데이터를 바탕으로 투자 리포트를 작성해주세요.

# 종목 정보
- 종목명: {basic['name']}
- 현재가: {basic['current_price']:,}원
- 등락: {basic['price_change_pct']:.2f}%

# 기술적 분석
- RSI: {tech['rsi']} ({tech['rsi_signal']})
- 추세: {tech['trend']}
- 이동평균: MA5({tech['ma5']:,}) / MA20({tech['ma20']:,}) / MA60({tech['ma60']:,})

# 재무 분석
"""
        if 'error' not in fin:
            prompt += f"""
- 부채비율: {fin['debt_ratio']:.1f}%
- ROE: {fin['roe']:.1f}%
- 등급: {fin['grade']}
"""

        prompt += """

다음 형식으로 리포트를 작성해주세요:

1. 현재 상황 요약 (2-3줄)
2. 기술적 관점 (매수/매도 신호)
3. 재무적 관점
4. 투자 의견 (매수/관망/매도)
5. 리스크 요인

카카오톡 메시지 형식으로, 이모지를 적절히 사용해주세요.
"""
        return prompt


# ========================================
# 사용 예시
# ========================================

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # 리포트 생성기
    generator = StockReportGenerator()

    # 삼성전자 간단 리포트
    print("=" * 50)
    print("📊 간단 리포트")
    print("=" * 50)
    report = generator.generate_simple_report('005930')
    print(report)

    print("\n" * 2)

    # 삼성전자 상세 리포트
    print("=" * 50)
    print("📊 상세 리포트")
    print("=" * 50)
    report = generator.generate_detail_report('005930')
    print(report)
