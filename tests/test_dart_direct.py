"""
DART API 직접 테스트 - 연도와 보고서 코드 확인
"""
import os
from dotenv import load_dotenv
from dart_client import DartClient

load_dotenv()

dart_key = os.environ.get("DART_API_KEY")
client = DartClient(api_key=dart_key)

# 삼성전자 고유번호 확인
ticker = "005930"
corp_code = client.get_corp_code(ticker)
print(f"Samsung ({ticker}) DART code: {corp_code}")
print()

# 여러 연도와 보고서 코드 테스트
test_cases = [
    (2024, "11011", "CFS", "2024 Annual Report (Consolidated)"),
    (2024, "11012", "CFS", "2024 Semi-Annual Report (Consolidated)"),
    (2024, "11014", "CFS", "2024 Q3 Report (Consolidated)"),
    (2023, "11011", "CFS", "2023 Annual Report (Consolidated)"),
]

for year, reprt_code, fs_div, desc in test_cases:
    try:
        df = client.get_financials(corp_code, year, reprt_code, fs_div)
        if df is not None and not df.empty:
            print(f"[OK] {desc}: {len(df)} items")
            # 주요 계정 확인
            accounts = df['account_nm'].unique()[:5]
            print(f"     Key accounts: {', '.join(accounts)}")
        else:
            print(f"[FAIL] {desc}: No data")
    except Exception as e:
        print(f"[ERROR] {desc}: {e}")
    print()
