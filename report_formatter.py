"""
리포트 출력 포맷터
콘솔/터미널 출력용 리포트 포맷팅
"""

from typing import Dict


class ReportFormatter:
    """리포트 출력 포맷터"""

    def format_full_report(self, report: Dict) -> str:
        """
        리포트 전체 텍스트 포맷

        Args:
            report: generate_report()의 반환값

        Returns:
            포맷된 리포트 텍스트
        """
        if 'error' in report:
            return f"[ERROR] {report['error']}"

        lines = []

        # 헤더
        meta = report.get('metadata', {})
        lines.append("=" * 70)
        lines.append(f"  {meta.get('company_name', 'N/A')} ({meta.get('ticker', 'N/A')}) 투자 리포트")
        lines.append("=" * 70)
        lines.append(f"  생성일시: {meta.get('generated_at', 'N/A')}")
        lines.append(f"  재무제표 포함: {'예' if meta.get('has_financials') else '아니오'}")
        lines.append(f"  뉴스 포함: {'예' if meta.get('has_news') else '아니오'}")
        lines.append("=" * 70)
        lines.append("")

        # 리포트 섹션
        report_content = report.get('report', {})

        if 'full_text' in report_content:
            lines.append(report_content['full_text'])
        elif 'sections' in report_content:
            sections = report_content['sections']

            section_names = {
                'summary': '투자 요약',
                'price_analysis': '주가 동향 분석',
                'financial_analysis': '재무 상태 분석',
                'valuation': '밸류에이션',
                'news_analysis': '시장 동향 및 뉴스',
                'investment_opinion': '투자 의견'
            }

            for key, title in section_names.items():
                content = sections.get(key, '')
                if content:
                    lines.append(f"### {title}")
                    lines.append("-" * 40)
                    lines.append(content)
                    lines.append("")

        lines.append("=" * 70)
        lines.append("  [END OF REPORT]")
        lines.append("=" * 70)

        return "\n".join(lines)

    def format_summary(self, report: Dict) -> str:
        """
        간단 요약 출력

        Args:
            report: generate_report()의 반환값

        Returns:
            한 줄 요약
        """
        if 'error' in report:
            return f"[ERROR] {report['error']}"

        meta = report.get('metadata', {})
        sections = report.get('report', {}).get('sections', {})

        summary = sections.get('summary', '')
        first_sentence = summary.split('.')[0] + '.' if summary else 'N/A'

        return f"{meta.get('company_name', 'N/A')} ({meta.get('ticker', 'N/A')}): {first_sentence}"
