"""
물타기 평단가 계산기
Averaging Down Calculator for Stock Investments

This module provides functionality to calculate average purchase prices
when buying additional shares at different prices (averaging down strategy).
"""

from typing import Dict, List


class AveragingCalculator:
    """물타기 평단가 계산 클래스"""

    def calculate(
        self,
        avg_price: float,      # 현재 평단가
        quantity: int,         # 보유 수량
        current_price: float,  # 현재가 (추가 매수 가격)
        add_quantity: int      # 추가 매수량
    ) -> Dict:
        """
        물타기 시뮬레이션 - 추가 매수 후 새로운 평단가 계산

        Args:
            avg_price: 현재 보유 주식의 평균 매수가
            quantity: 현재 보유 수량
            current_price: 현재 주가 (추가 매수할 가격)
            add_quantity: 추가로 매수할 수량

        Returns:
            Dict containing:
                - new_avg: 새로운 평단가
                - change: 평단가 변화 금액
                - change_pct: 평단가 변화율 (%)
                - total_qty: 총 보유 수량
                - total_cost: 총 투자 금액
                - breakeven_price: 손익분기점 (= new_avg)
                - profit_if_sell_now: 현재가에 전량 매도 시 손익
        """

        # 기존 투자금
        existing_cost = avg_price * quantity

        # 추가 투자금
        additional_cost = current_price * add_quantity

        # 총 투자금
        total_cost = existing_cost + additional_cost

        # 총 보유 수량
        total_qty = quantity + add_quantity

        # 새로운 평단가
        new_avg = total_cost / total_qty if total_qty > 0 else 0

        # 평단가 변화
        change = new_avg - avg_price
        change_pct = (change / avg_price * 100) if avg_price > 0 else 0

        # 현재가에 전량 매도 시 손익
        current_value = current_price * total_qty
        profit_if_sell_now = current_value - total_cost
        profit_pct = (profit_if_sell_now / total_cost * 100) if total_cost > 0 else 0

        return {
            'new_avg': int(new_avg),
            'change': int(change),
            'change_pct': round(change_pct, 2),
            'total_qty': total_qty,
            'total_cost': int(total_cost),
            'breakeven_price': int(new_avg),
            'profit_if_sell_now': int(profit_if_sell_now),
            'profit_pct': round(profit_pct, 2)
        }

    def calculate_scenarios(
        self,
        avg_price: float,
        quantity: int,
        current_price: float,
        scenarios: List[int] = [1, 5, 10, 20]
    ) -> List[Dict]:
        """
        여러 수량 시나리오 계산 (1주/5주/10주/20주 등)

        Args:
            avg_price: 현재 평단가
            quantity: 현재 보유 수량
            current_price: 현재 주가
            scenarios: 시나리오별 추가 매수 수량 리스트

        Returns:
            List of calculation results for each scenario
        """
        results = []

        for add_qty in scenarios:
            result = self.calculate(avg_price, quantity, current_price, add_qty)
            result['add_qty'] = add_qty
            results.append(result)

        return results

    def calculate_target_quantity(
        self,
        avg_price: float,
        quantity: int,
        current_price: float,
        target_avg: float
    ) -> Dict:
        """
        목표 평단가를 맞추기 위해 필요한 추가 매수 수량 계산

        Args:
            avg_price: 현재 평단가
            quantity: 현재 보유 수량
            current_price: 현재 주가
            target_avg: 목표 평단가

        Returns:
            Dict containing:
                - required_qty: 필요한 추가 매수 수량
                - additional_cost: 추가 투자 필요 금액
                - feasible: 목표 달성 가능 여부
                - reason: 불가능한 경우 사유
        """

        # 목표 평단가 검증
        # 현재가가 현재 평단가보다 낮을 때만 평단가를 낮출 수 있음
        if current_price >= avg_price:
            # 평단가를 올리는 목표인 경우
            if target_avg > avg_price:
                pass  # 가능
            else:
                return {
                    'required_qty': 0,
                    'additional_cost': 0,
                    'feasible': False,
                    'reason': '현재가가 평단가보다 높아서 평단가를 낮출 수 없습니다'
                }
        else:
            # 평단가를 낮추는 목표인 경우
            if target_avg < avg_price:
                # 목표 평단가가 현재가보다 낮으면 불가능
                if target_avg < current_price:
                    return {
                        'required_qty': 0,
                        'additional_cost': 0,
                        'feasible': False,
                        'reason': f'목표 평단가({target_avg:,}원)가 현재가({current_price:,}원)보다 낮아 달성 불가능합니다'
                    }
            else:
                return {
                    'required_qty': 0,
                    'additional_cost': 0,
                    'feasible': False,
                    'reason': '현재가가 평단가보다 낮아서 평단가를 올릴 수 없습니다'
                }

        # 역산 공식
        # target_avg = (avg_price * quantity + current_price * X) / (quantity + X)
        # target_avg * (quantity + X) = avg_price * quantity + current_price * X
        # target_avg * quantity + target_avg * X = avg_price * quantity + current_price * X
        # target_avg * X - current_price * X = avg_price * quantity - target_avg * quantity
        # X * (target_avg - current_price) = quantity * (avg_price - target_avg)
        # X = quantity * (avg_price - target_avg) / (target_avg - current_price)

        denominator = target_avg - current_price

        if abs(denominator) < 0.01:  # 거의 0에 가까우면
            return {
                'required_qty': 0,
                'additional_cost': 0,
                'feasible': False,
                'reason': '목표 평단가와 현재가가 거의 같아 계산이 불가능합니다'
            }

        required_qty = quantity * (avg_price - target_avg) / denominator

        # 수량은 양수여야 함
        if required_qty < 0:
            return {
                'required_qty': 0,
                'additional_cost': 0,
                'feasible': False,
                'reason': '목표 평단가 달성을 위한 조건이 맞지 않습니다'
            }

        # 정수로 올림
        import math
        required_qty_ceil = math.ceil(required_qty)

        # 추가 투자 금액
        additional_cost = current_price * required_qty_ceil

        # 검증: 실제로 계산해보기
        verify_result = self.calculate(avg_price, quantity, current_price, required_qty_ceil)

        return {
            'required_qty': required_qty_ceil,
            'additional_cost': int(additional_cost),
            'feasible': True,
            'actual_avg': verify_result['new_avg'],
            'target_avg': int(target_avg),
            'difference': verify_result['new_avg'] - int(target_avg)
        }

    def format_result(self, result: Dict, ticker_name: str = "종목") -> str:
        """
        계산 결과를 카카오톡 메시지 형식으로 포맷팅

        Args:
            result: calculate() 메서드의 반환값
            ticker_name: 종목명

        Returns:
            Formatted string for KakaoTalk message
        """

        # 상승/하락 표시
        change_symbol = "▲" if result['change'] >= 0 else "▼"
        profit_symbol = "💰" if result['profit_if_sell_now'] >= 0 else "📉"

        message = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 물타기 계산 결과
━━━━━━━━━━━━━━━━━━━━━━━━━━

【 결과 】
✅ 새 평단가: {result['new_avg']:,}원
{change_symbol} 평단가 변화: {abs(result['change']):,}원 ({result['change_pct']:+.2f}%)

【 투자 현황 】
├ 총 보유: {result['total_qty']:,}주
├ 총 투자금: {result['total_cost']:,}원
└ 손익분기: {result['breakeven_price']:,}원

【 현재 손익 】
{profit_symbol} 평가손익: {result['profit_if_sell_now']:,}원 ({result['profit_pct']:+.2f}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 평단가 {result['breakeven_price']:,}원 이상이면 수익!
"""
        return message

    def format_scenarios(self, scenarios: List[Dict], current_price: float) -> str:
        """
        여러 시나리오를 테이블 형태로 포맷팅

        Args:
            scenarios: calculate_scenarios() 메서드의 반환값
            current_price: 현재 주가

        Returns:
            Formatted string for multiple scenarios
        """

        message = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 물타기 시나리오 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━

현재가: {int(current_price):,}원

"""

        for idx, scenario in enumerate(scenarios, 1):
            add_qty = scenario['add_qty']
            new_avg = scenario['new_avg']
            change = scenario['change']
            change_pct = scenario['change_pct']
            additional_cost = int(current_price * add_qty)

            change_symbol = "▼" if change < 0 else "▲"

            message += f"""【 시나리오 {idx}: {add_qty}주 추가 매수 】
├ 추가 투자: {additional_cost:,}원
├ 새 평단가: {new_avg:,}원
└ 변화: {change_symbol} {abs(change):,}원 ({change_pct:+.2f}%)

"""

        message += "━━━━━━━━━━━━━━━━━━━━━━━━━━"

        return message


# 테스트 코드
if __name__ == "__main__":
    import sys
    import io

    # Windows console encoding fix
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    calc = AveragingCalculator()

    print("=== 물타기 계산기 테스트 ===\n")

    # 예시: 평단가 80,000원에 10주 보유
    # 현재 주가 70,000원에 10주 추가 매수
    print("📌 예시 1: 기본 계산")
    result = calc.calculate(
        avg_price=80000,
        quantity=10,
        current_price=70000,
        add_quantity=10
    )

    print(f"현재 평단가: 80,000원 (10주)")
    print(f"추가 매수: 70,000원 (10주)")
    print(f"\n결과:")
    print(f"  - 새 평단가: {result['new_avg']:,}원")
    print(f"  - 총 수량: {result['total_qty']}주")
    print(f"  - 총 투자금: {result['total_cost']:,}원")
    print(f"  - 평단가 변화: {result['change']:,}원 ({result['change_pct']:.2f}%)")

    print("\n" + "="*50 + "\n")

    # 시나리오 분석
    print("📌 예시 2: 시나리오 분석")
    scenarios = calc.calculate_scenarios(
        avg_price=100000,
        quantity=5,
        current_price=90000,
        scenarios=[1, 5, 10, 20]
    )

    print(f"현재 평단가: 100,000원 (5주)")
    print(f"현재 주가: 90,000원")
    print(f"\n시나리오별 결과:")

    for s in scenarios:
        print(f"  {s['add_qty']:2}주 추가 → 새 평단가: {s['new_avg']:,}원 ({s['change_pct']:+.2f}%)")

    print("\n" + "="*50 + "\n")

    # 목표 평단가 역산
    print("📌 예시 3: 목표 평단가 달성 계산")
    target_result = calc.calculate_target_quantity(
        avg_price=100000,
        quantity=10,
        current_price=80000,
        target_avg=90000
    )

    print(f"현재 평단가: 100,000원 (10주)")
    print(f"현재 주가: 80,000원")
    print(f"목표 평단가: 90,000원")
    print(f"\n결과:")
    if target_result['feasible']:
        print(f"  - 필요 수량: {target_result['required_qty']}주")
        print(f"  - 추가 투자금: {target_result['additional_cost']:,}원")
        print(f"  - 실제 평단가: {target_result['actual_avg']:,}원")
    else:
        print(f"  - 불가능: {target_result['reason']}")

    print("\n" + "="*50 + "\n")

    # 포맷팅 테스트
    print("📌 예시 4: 카카오톡 메시지 포맷")
    result = calc.calculate(
        avg_price=75000,
        quantity=20,
        current_price=70000,
        add_quantity=10
    )
    print(calc.format_result(result, "삼성전자"))
