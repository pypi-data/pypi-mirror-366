import sys
import os
import dotenv
import pandas as pd

# Set pandas display options for better output in console
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

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

print("\n--- Testing Financials ---")
try:
    # Test income statement
    print(f"Fetching income statement for {ticker}...")
    income_statement = client.financials.get_financials(statement='income', symbol=ticker, limit=1, period='quarter')
    print("Income Statement (first row):\n", income_statement.head(1))

    # Test balance sheet
    print(f"Fetching balance sheet for {ticker}...")
    balance_sheet = client.financials.get_financials(statement='balance', symbol=ticker, limit=1, period='quarter')
    print("Balance Sheet (first row):\n", balance_sheet.head(1))

    # Test cash flow statement
    print(f"Fetching cash flow statement for {ticker}...")
    cash_flow_statement = client.financials.get_financials(statement='cash', symbol=ticker, limit=1, period='quarter')
    print("Cash Flow Statement (first row):\n", cash_flow_statement.head(1))

    # Test merged financials
    print(f"Fetching merged financials for {ticker}...")
    merged_financials = client.financials.get_merged_financials(ticker, limit=1, period='quarter')
    print("Merged Financials (first row):\n", merged_financials.head(1))

except InvalidAPIKeyError:
    print("Test Failed: Invalid API Key. Please check your FMP_KEY.")
except SymbolNotFoundError as e:
    print(f"Test Failed: Symbol not found. {e}")
except RateLimitExceededError:
    print("Test Failed: Rate limit exceeded. Please wait and try again.")
except FMPConnectionError as e:
    print(f"Test Failed: Connection error. {e}")
except FMPAPIError as e:
    print(f"Test Failed: An FMP API error occurred. {e}")
except Exception as e:
    print(f"An unexpected error occurred during financials test: {e}")

print("\n--- Testing Stocks Data ---")
try:
    # Test historical price full
    print(f"Fetching historical daily prices for {ticker}...")
    historical_prices = client.stocks.historical_price_full(ticker, start="2023-01-01", end="2023-01-05")
    print("Historical Prices (first 5 rows):\n", historical_prices.head())

    print(f"Fetching historical daily prices for {ticker} for the last 1 year...")
    historical_prices_period = client.stocks.historical_price_full(ticker, period=1)
    print("Historical Prices (last 1 year, first 5 rows):\n", historical_prices_period.head())

    # Test stock list (limit to first 5 for brevity)
    print("Fetching stock list (first 5 entries)...")
    stock_list = client.stocks.stock_list()
    print("Stock List (first 5 rows):\n", stock_list.head())

    # Test quote
    print(f"Fetching quote for {ticker}...")
    quote = client.stocks.quote(ticker)
    print("Quote:\n", quote)

    # Test search
    print(f"Searching for 'Apple'...")
    search_results = client.stocks.search(query='Apple', limit=2)
    print("Search Results (first 2 rows):\n", search_results.head())

except InvalidAPIKeyError:
    print("Test Failed: Invalid API Key. Please check your FMP_KEY.")
except SymbolNotFoundError as e:
    print(f"Test Failed: Symbol not found. {e}")
except RateLimitExceededError:
    print("Test Failed: Rate limit exceeded. Please wait and try again.")
except FMPConnectionError as e:
    print(f"Test Failed: Connection error. {e}")
except FMPAPIError as e:
    print(f"Test Failed: An FMP API error occurred. {e}")
except Exception as e:
    print(f"An unexpected error occurred during stocks test: {e}")

# Old code commented out
# from fmpxx import FMPClient, Quote
# from fmpxx.financials import Financials
# import os
# import dotenv
# dotenv.load_dotenv()
# API_Key = os.getenv("FMP_KEY")
# ticker = 'aapl'
# fin = Financials(API_Key)
# # print(fin.get_income_statement(ticker))
# # print(fin.get_earnings_his(ticker))
# print(fin.get_earnings_transcript(ticker,period=3))
# # print(client.get_earnings_his('NVDA', period=1))
# # quote = Quote(api_key=API_Key)
# # print(quote.get_his_daily(symbol='aapl', period=1))
# # print(quote.get_simple_quote('aapl'))
# # print(quote.get_full_quote('aapl'))
