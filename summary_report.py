"""
요약 리포트 모듈 (2-6)
자동 생성 리포트: 월간 요약, 총 수익률, 종목별 수익률
"""

import sys
import io
import os
from typing import Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
import json

# Windows console encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

from HantuStock import HantuStock
import google.generativeai as genai


class SummaryReportGenerator:
    """
    요약 리포트 생성기
    기획 2-6: 월간 요약, 총 수익률, 손익, 종목별 수익률
    """

    def __init__(self):
        """Initialize"""
        print("🔧 요약 리포트 생성기 초기화 중...")

        try:
            self.hantu = HantuStock()
            print("✅ 한국투자증권 API 초기화 완료")
        except Exception as e:
            raise ValueError(f"한투 API 초기화 실패: {e}")

        # Gemini API (LLM)
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.llm_available = True
            print("✅ Gemini API 초기화 완료\n")
        else:
            self.llm_available = False
            print("⚠️  Gemini API 없음 (인사이트 생략)\n")

    def generate_monthly_summary(self) -> Dict:
        """
        월간 요약 리포트 생성

        Returns:
            월간 요약 리포트 딕셔너리
        """
        print("📊 월간 요약 리포트 생성 중...\n")

        # Step 1: 거래 요약 (1개월)
        print("[ Step 1 ] 월간 거래 요약 조회")
        summary = self.hantu.get_transaction_summary(period="1m")
        print(f"✅ 거래 {summary['total_trades']}건 조회 완료\n")

        # Step 2: 현재 보유 종목
        print("[ Step 2 ] 현재 보유 종목 조회")
        holdings = self.hantu.get_holding_stock_detail()
        cash = self.hantu.get_holding_cash()
        print(f"✅ 보유 종목 {len(holdings)}개, 현금 {cash:,.0f}원\n")

        # Step 3: 수익률 계산
        print("[ Step 3 ] 수익률 계산")
        total_eval = sum(h["evlu_amt"] for h in holdings)
        total_profit = sum(h["evlu_pfls_amt"] for h in holdings)
        total_invested = sum(h["pchs_avg_prc"] * h["hldg_qty"] for h in holdings)

        if total_invested > 0:
            total_profit_rate = (total_profit / total_invested) * 100
        else:
            total_profit_rate = 0

        print(f"✅ 총 수익률: {total_profit_rate:+.2f}%\n")

        # Step 4: LLM 인사이트 생성 (옵션)
        insights = None
        if self.llm_available and (len(holdings) > 0 or summary['total_trades'] > 0):
            print("[ Step 4 ] AI 인사이트 생성")
            insights = self._generate_insights(summary, holdings, total_profit_rate)
            print("✅ 인사이트 생성 완료\n")

        # 리포트 구성
        return {
            "metadata": {
                "report_type": "monthly_summary",
                "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            },
            "portfolio": {
                "total_asset": total_eval + cash,
                "total_eval": total_eval,
                "cash": cash,
                "total_profit": total_profit,
                "total_profit_rate": round(total_profit_rate, 2),
                "stock_count": len(holdings),
            },
            "trading": {
                "total_trades": summary["total_trades"],
                "buy_trades": summary["buy_trades"],
                "sell_trades": summary["sell_trades"],
                "total_buy_amount": summary["total_buy_amount"],
                "total_sell_amount": summary["total_sell_amount"],
                "net_amount": summary["net_amount"],
            },
            "holdings": self._summarize_holdings(holdings),
            "top_performers": self._get_top_performers(holdings),
            "insights": insights,
        }

    def _summarize_holdings(self, holdings: list) -> list:
        """보유 종목 요약"""
        result = []
        for h in holdings:
            result.append({
                "pdno": h["pdno"],
                "prdt_name": h["prdt_name"],
                "hldg_qty": h["hldg_qty"],
                "evlu_amt": h["evlu_amt"],
                "evlu_pfls_amt": h["evlu_pfls_amt"],
                "evlu_pfls_rt": h["evlu_pfls_rt"],
            })
        # 평가금액 기준 정렬
        result.sort(key=lambda x: x["evlu_amt"], reverse=True)
        return result

    def _get_top_performers(self, holdings: list) -> Dict:
        """상위/하위 수익 종목"""
        if not holdings:
            return {"best": None, "worst": None}

        sorted_by_rate = sorted(holdings, key=lambda x: x["evlu_pfls_rt"], reverse=True)

        best = sorted_by_rate[0] if sorted_by_rate else None
        worst = sorted_by_rate[-1] if sorted_by_rate else None

        return {
            "best": {
                "prdt_name": best["prdt_name"],
                "evlu_pfls_rt": best["evlu_pfls_rt"],
            } if best else None,
            "worst": {
                "prdt_name": worst["prdt_name"],
                "evlu_pfls_rt": worst["evlu_pfls_rt"],
            } if worst else None,
        }

    def _generate_insights(self, summary: dict, holdings: list, profit_rate: float) -> str:
        """LLM으로 인사이트 생성"""

        # 보유 종목 요약
        holdings_text = ""
        for h in holdings[:5]:
            emoji = "🟢" if h["evlu_pfls_rt"] >= 0 else "🔴"
            holdings_text += f"- {h['prdt_name']}: {emoji} {h['evlu_pfls_rt']:+.2f}%\n"

        prompt = f"""
당신은 주식 초보 투자자를 위한 친절한 투자 어드바이저입니다.
다음 월간 투자 데이터를 분석하여 초보자도 이해하기 쉬운 인사이트를 제공해주세요.

## 이번 달 투자 현황

### 포트폴리오
- 총 수익률: {profit_rate:+.2f}%
- 보유 종목 수: {len(holdings)}개

### 보유 종목 수익률
{holdings_text if holdings_text else "보유 종목 없음"}

### 거래 활동
- 총 거래: {summary['total_trades']}건 (매수 {summary['buy_trades']}건, 매도 {summary['sell_trades']}건)
- 매수 금액: {summary['total_buy_amount']:,.0f}원
- 매도 금액: {summary['total_sell_amount']:,.0f}원

---

다음 형식으로 간단한 인사이트를 작성해주세요 (3-5문장):

1. 이번 달 포트폴리오 성과 한 줄 평가
2. 잘한 점 또는 개선할 점 1가지
3. 초보 투자자를 위한 간단한 조언 1가지

친근하고 이해하기 쉬운 말로 작성해주세요.
"""

        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"인사이트 생성 실패: {str(e)}"

    def format_for_kakao(self, report: Dict) -> Dict:
        """
        카카오톡 응답 형식으로 변환

        Returns:
            카카오톡 API 2.0 응답 형식
        """
        portfolio = report["portfolio"]
        trading = report["trading"]
        top = report["top_performers"]

        # 수익률 이모지
        profit_emoji = "📈" if portfolio["total_profit_rate"] >= 0 else "📉"

        # 인사이트 (있으면 추가)
        description = f"{profit_emoji} 총 수익률: {portfolio['total_profit_rate']:+.2f}%\n"
        description += f"총 자산: {portfolio['total_asset']:,.0f}원\n"
        description += f"이번 달 거래: {trading['total_trades']}건"

        # 상위/하위 종목
        items = []
        if top["best"]:
            items.append({
                "title": f"🏆 최고 수익: {top['best']['prdt_name']}",
                "description": f"{top['best']['evlu_pfls_rt']:+.2f}%"
            })
        if top["worst"]:
            items.append({
                "title": f"📉 최저 수익: {top['worst']['prdt_name']}",
                "description": f"{top['worst']['evlu_pfls_rt']:+.2f}%"
            })
        if not items:
            items.append({"title": "보유 종목 없음", "description": "-"})

        return {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "textCard": {
                            "title": "📊 이번 달 투자 요약",
                            "description": description,
                            "buttons": [
                                {
                                    "action": "webLink",
                                    "label": "📄 상세 리포트 보기",
                                    "webLinkUrl": "https://example.com/summary"
                                }
                            ]
                        }
                    },
                    {
                        "listCard": {
                            "header": {"title": "📈 종목 성과"},
                            "items": items,
                        }
                    }
                ],
                "quickReplies": [
                    {"action": "message", "label": "거래 내역", "messageText": "거래내역 1개월"},
                    {"action": "message", "label": "보유 종목", "messageText": "보유 종목"},
                ]
            }
        }

    def print_report(self, report: Dict):
        """리포트 출력"""
        portfolio = report["portfolio"]
        trading = report["trading"]
        holdings = report["holdings"]
        top = report["top_performers"]
        insights = report["insights"]

        print("=" * 60)
        print("  📊 월간 투자 요약 리포트")
        print("=" * 60)
        print(f"  생성일시: {report['metadata']['generated_at']}")
        print("=" * 60)
        print()

        # 포트폴리오 요약
        profit_emoji = "📈" if portfolio["total_profit_rate"] >= 0 else "📉"
        print("[ 포트폴리오 현황 ]")
        print(f"  총 자산: {portfolio['total_asset']:,.0f}원")
        print(f"  주식 평가: {portfolio['total_eval']:,.0f}원 ({portfolio['stock_count']}종목)")
        print(f"  현금: {portfolio['cash']:,.0f}원")
        print(f"  {profit_emoji} 총 수익률: {portfolio['total_profit_rate']:+.2f}%")
        print(f"  평가손익: {portfolio['total_profit']:+,.0f}원")
        print()

        # 거래 요약
        print("[ 이번 달 거래 ]")
        print(f"  총 거래: {trading['total_trades']}건 (매수 {trading['buy_trades']}건, 매도 {trading['sell_trades']}건)")
        print(f"  매수 금액: {trading['total_buy_amount']:,.0f}원")
        print(f"  매도 금액: {trading['total_sell_amount']:,.0f}원")
        print(f"  순매수/매도: {trading['net_amount']:+,.0f}원")
        print()

        # 상위/하위 종목
        print("[ 종목 성과 ]")
        if top["best"]:
            print(f"  🏆 최고: {top['best']['prdt_name']} ({top['best']['evlu_pfls_rt']:+.2f}%)")
        if top["worst"]:
            print(f"  📉 최저: {top['worst']['prdt_name']} ({top['worst']['evlu_pfls_rt']:+.2f}%)")
        print()

        # AI 인사이트
        if insights:
            print("[ AI 인사이트 ]")
            print("-" * 40)
            print(insights)
            print()

        print("=" * 60)


# ========================================
# 테스트
# ========================================

if __name__ == "__main__":
    print("=" * 60)
    print("📊 월간 요약 리포트 테스트")
    print("=" * 60)
    print()

    try:
        generator = SummaryReportGenerator()

        # 월간 요약
        report = generator.generate_monthly_summary()
        generator.print_report(report)

        # 카카오톡 형식
        print("\n📱 카카오톡 응답 형식:")
        print("-" * 40)
        kakao_response = generator.format_for_kakao(report)
        print(json.dumps(kakao_response, ensure_ascii=False, indent=2))

        # JSON 저장
        print("\n💾 결과 저장 중...")
        output_file = f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"✅ 저장 완료: {output_file}")

    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
