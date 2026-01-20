"""
거래 내역 리포트 모듈 (2-4)
기간 선택 -> 거래 내역 요약 -> 종목별 수익률 -> 웹 상세 제공
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


class TransactionReportGenerator:
    """
    거래 내역 리포트 생성기
    기획 2-4: 기간 선택 -> 거래 내역 요약 -> 종목별 수익률
    """

    def __init__(self):
        """Initialize"""
        print("🔧 거래 내역 리포트 생성기 초기화 중...")

        try:
            self.hantu = HantuStock()
            print("✅ 한국투자증권 API 초기화 완료\n")
        except Exception as e:
            raise ValueError(f"한투 API 초기화 실패: {e}")

    def generate_report(self, period: str = "1m") -> Dict:
        """
        거래 내역 리포트 생성

        Args:
            period: 기간 ("1m": 1개월, "3m": 3개월, "1y": 1년)

        Returns:
            거래 내역 리포트 딕셔너리
        """
        print(f"📊 거래 내역 리포트 생성 중 (기간: {period})...\n")

        # Step 1: 거래 내역 조회
        print("[ Step 1 ] 거래 내역 조회")
        transactions = self.hantu.get_transaction_history(period=period)
        print(f"✅ {len(transactions)}건 거래 조회 완료\n")

        if len(transactions) == 0:
            return {
                'error': '해당 기간에 거래 내역이 없습니다.',
                'period': period
            }

        # Step 2: 거래 요약
        print("[ Step 2 ] 거래 요약 계산")
        summary = self.hantu.get_transaction_summary(period=period)
        print(f"✅ 총 {summary['total_trades']}건, "
              f"매수 {summary['buy_trades']}건, 매도 {summary['sell_trades']}건\n")

        # Step 3: 현재 보유 종목 정보
        print("[ Step 3 ] 현재 보유 종목 조회")
        holdings = self.hantu.get_holding_stock_detail()
        cash = self.hantu.get_holding_cash()
        print(f"✅ 보유 종목 {len(holdings)}개, 현금 {cash:,.0f}원\n")

        # Step 4: 종합 리포트 생성
        print("[ Step 4 ] 리포트 생성")
        report = self._build_report(period, transactions, summary, holdings, cash)
        print("✅ 리포트 생성 완료\n")

        return report

    def _build_report(
        self,
        period: str,
        transactions: list,
        summary: dict,
        holdings: list,
        cash: float
    ) -> Dict:
        """리포트 데이터 구성"""

        # 기간 텍스트
        period_text = {"1m": "최근 1개월", "3m": "최근 3개월", "1y": "최근 1년"}.get(period, period)

        # 종목별 요약
        stock_summary = []
        for pdno, data in summary.get("by_stock", {}).items():
            stock_summary.append({
                "pdno": pdno,
                "prdt_name": data["prdt_name"],
                "buy_amount": data["buy_amount"],
                "sell_amount": data["sell_amount"],
                "buy_qty": data["buy_qty"],
                "sell_qty": data["sell_qty"],
                "trades": data["trades"],
                "realized_profit": data.get("realized_profit", 0),
                "profit_rate": data.get("profit_rate", 0),
            })

        # 수익률 기준 정렬
        stock_summary.sort(key=lambda x: x["profit_rate"], reverse=True)

        # 현재 보유 종목 평가
        total_eval = sum(h["evlu_amt"] for h in holdings)
        total_profit = sum(h["evlu_pfls_amt"] for h in holdings)

        return {
            "metadata": {
                "period": period,
                "period_text": period_text,
                "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            },
            "summary": {
                "total_buy_amount": summary["total_buy_amount"],
                "total_sell_amount": summary["total_sell_amount"],
                "net_amount": summary["net_amount"],
                "total_trades": summary["total_trades"],
                "buy_trades": summary["buy_trades"],
                "sell_trades": summary["sell_trades"],
            },
            "holdings": {
                "stocks": holdings,
                "total_eval": total_eval,
                "total_profit": total_profit,
                "cash": cash,
                "total_asset": total_eval + cash,
            },
            "stock_summary": stock_summary,
            "transactions": transactions,
        }

    def format_for_kakao(self, report: Dict) -> Dict:
        """
        카카오톡 응답 형식으로 변환

        Returns:
            카카오톡 API 2.0 응답 형식
        """
        if 'error' in report:
            return {
                "version": "2.0",
                "template": {
                    "outputs": [{
                        "simpleText": {
                            "text": f"❌ {report['error']}"
                        }
                    }]
                }
            }

        meta = report["metadata"]
        summary = report["summary"]
        holdings = report["holdings"]

        # 수익/손실 이모지
        net_emoji = "📈" if summary["net_amount"] >= 0 else "📉"

        # 종목별 요약 (상위 3개)
        top_stocks = report["stock_summary"][:3]
        stock_items = []
        for s in top_stocks:
            profit_emoji = "🟢" if s["profit_rate"] >= 0 else "🔴"
            stock_items.append({
                "title": s["prdt_name"],
                "description": f"{profit_emoji} 수익률: {s['profit_rate']:+.2f}%\n거래 {s['trades']}건"
            })

        return {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "textCard": {
                            "title": f"📊 {meta['period_text']} 거래 리포트",
                            "description": f"총 {summary['total_trades']}건 거래\n"
                                          f"매수: {summary['total_buy_amount']:,.0f}원\n"
                                          f"매도: {summary['total_sell_amount']:,.0f}원\n"
                                          f"{net_emoji} 순손익: {summary['net_amount']:+,.0f}원",
                            "buttons": [
                                {
                                    "action": "webLink",
                                    "label": "📄 상세 내역 보기",
                                    "webLinkUrl": "https://example.com/transactions"
                                }
                            ]
                        }
                    },
                    {
                        "listCard": {
                            "header": {
                                "title": "📈 종목별 수익률 TOP 3"
                            },
                            "items": stock_items if stock_items else [{"title": "거래 내역 없음", "description": "-"}],
                        }
                    }
                ],
                "quickReplies": [
                    {"action": "message", "label": "1개월", "messageText": "거래내역 1개월"},
                    {"action": "message", "label": "3개월", "messageText": "거래내역 3개월"},
                    {"action": "message", "label": "1년", "messageText": "거래내역 1년"},
                ]
            }
        }

    def print_report(self, report: Dict):
        """리포트 출력"""
        if 'error' in report:
            print(f"❌ 에러: {report['error']}")
            return

        meta = report["metadata"]
        summary = report["summary"]
        holdings = report["holdings"]

        print("=" * 60)
        print(f"  📊 {meta['period_text']} 거래 내역 리포트")
        print("=" * 60)
        print(f"  생성일시: {meta['generated_at']}")
        print("=" * 60)
        print()

        # 거래 요약
        print("[ 거래 요약 ]")
        print(f"  총 거래: {summary['total_trades']}건 (매수 {summary['buy_trades']}건, 매도 {summary['sell_trades']}건)")
        print(f"  총 매수금액: {summary['total_buy_amount']:,.0f}원")
        print(f"  총 매도금액: {summary['total_sell_amount']:,.0f}원")
        print(f"  순손익: {summary['net_amount']:+,.0f}원")
        print()

        # 현재 보유 현황
        print("[ 현재 보유 현황 ]")
        print(f"  총 평가금액: {holdings['total_eval']:,.0f}원")
        print(f"  평가손익: {holdings['total_profit']:+,.0f}원")
        print(f"  현금: {holdings['cash']:,.0f}원")
        print(f"  총 자산: {holdings['total_asset']:,.0f}원")
        print()

        # 종목별 요약
        print("[ 종목별 거래 요약 ]")
        for s in report["stock_summary"][:5]:
            emoji = "🟢" if s["profit_rate"] >= 0 else "🔴"
            print(f"  {s['prdt_name']} ({s['pdno']})")
            print(f"    {emoji} 수익률: {s['profit_rate']:+.2f}% | 거래 {s['trades']}건")
            print(f"    매수: {s['buy_amount']:,.0f}원 | 매도: {s['sell_amount']:,.0f}원")
            print()

        print("=" * 60)


# ========================================
# 테스트
# ========================================

if __name__ == "__main__":
    print("=" * 60)
    print("📊 거래 내역 리포트 테스트")
    print("=" * 60)
    print()

    try:
        generator = TransactionReportGenerator()

        # 1개월 거래 내역
        report = generator.generate_report(period="1m")
        generator.print_report(report)

        # 카카오톡 형식
        print("\n📱 카카오톡 응답 형식:")
        print("-" * 40)
        kakao_response = generator.format_for_kakao(report)
        print(json.dumps(kakao_response, ensure_ascii=False, indent=2))

        # JSON 저장
        print("\n💾 결과 저장 중...")
        output_file = f"transaction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"✅ 저장 완료: {output_file}")

    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
