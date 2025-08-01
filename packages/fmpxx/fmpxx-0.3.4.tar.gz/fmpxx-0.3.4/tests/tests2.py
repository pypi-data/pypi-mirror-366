import sys
import os
import dotenv
import pandas as pd

# Set pandas display options for better output in console
# 不换行显示配置
pd.set_option('display.width', 1000)          # 宽度足够大
pd.set_option('display.max_columns', None)     # 显示所有列
pd.set_option('display.max_colwidth', 30)      # 限制单列宽度
pd.set_option('display.expand_frame_repr', False)  # 禁用折叠
pd.set_option('display.max_rows', None) 

# 获取项目根目录的绝对路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 将项目根目录添加到 Python 模块搜索路径
sys.path.append(project_root)

# 然后再导入你的模块
from fmpxx import FMPClient
from fmpxx.exceptions import FMPAPIError, InvalidAPIKeyError, SymbolNotFoundError, RateLimitExceededError, FMPConnectionError

dotenv.load_dotenv()

API_Key = os.getenv("FMP_KEY")
ticker = 'AAPL' # Changed to AAPL for consistency

if not API_Key:
    print("Error: FMP_KEY environment variable not set. Please set it in your .env file or environment.")
    sys.exit(1)

client = FMPClient(api_key=API_Key, output_format='pandas')

# print("\n--- Testing Financials ---")

# # Test income statement
# # print(f"Fetching income statement for {ticker}...")
# income_statement = client.financials.get_financials(statement='income',symbol=ticker, limit=4)
# # print("Income Statement (first row):\n", income_statement)
# merged_data = client.financials.get_merged_financials(symbol=ticker,limit=4)
# if merged_data is not None:
#     merged_data.to_csv(f'tests/{ticker}.csv')
# else:
#     print("Failed to get merged financials")
# # print(client.stocks.historical_price_full(symbol=ticker,period=1))

# print("\n--- Testing Stock Performance ---")
# performance = client.financials.get_stock_performance(symbol=ticker, limit=8)
# if performance is not None:
#     print("Stock Performance Data:")
#     print(performance)
#     print(f"Columns: {list(performance.columns)}")
#     performance.to_csv(f'tests/performance_{ticker}.csv')
#     print(f"Performance data saved to tests/performance_{ticker}.csv")
# else:
#     print("Failed to get stock performance data")

# print("\n--- Testing Historical Earnings Calendar ---")
# earnings = client.financials.get_earnings_his(symbol=ticker, period=2)
# if not earnings.empty:
#     print("Historical Earnings Calendar:")
#     print(earnings)
#     print(f"Columns: {list(earnings.columns)}")
#     earnings.to_csv(f'tests/earnings_{ticker}.csv')
#     print(f"Earnings data saved to tests/earnings_{ticker}.csv")
# else:
#     print("Failed to get historical earnings data")

# print("\n--- Testing EPS & PE Merge ---")
# eps_pe_data = client.financials.merge_eps_his(symbol=ticker, period=2, enable_logging=True)
# if not eps_pe_data.empty:
#     print("EPS & PE Data:")
#     print(eps_pe_data)
#     print(f"Columns: {list(eps_pe_data.columns)}")
#     eps_pe_data.to_csv(f'tests/eps_pe_{ticker}.csv')
#     print(f"EPS & PE data saved to tests/eps_pe_{ticker}.csv")
# else:
#     print("Failed to get EPS & PE data")

# print("\n--- Testing Fiscal Close Change ---")
# fiscal_chg_data = client.financials.get_fiscal_close_chg(symbol=ticker, period=2, enable_logging=True)
# if not fiscal_chg_data.empty:
#     print("Fiscal Close Change Data:")
#     print(fiscal_chg_data)
#     print(f"Columns: {list(fiscal_chg_data.columns)}")
#     fiscal_chg_data.to_csv(f'tests/fiscal_chg_{ticker}.csv')
#     print(f"Fiscal close change data saved to tests/fiscal_chg_{ticker}.csv")
# else:
#     print("Failed to get fiscal close change data")


revenue_seg = client.financials.revenue_by_segment(symbol=ticker,output_format='pandas')
print(revenue_seg)