from typing import Optional, Literal
import pandas as pd
from agno.tools import Toolkit
from agno.utils.log import logger

from ..base import _BaseClient


class FinancialsTools(Toolkit):
    """Tools for accessing financial data from fmpxx financials module."""
    
    def __init__(self, api_key: str):
        super().__init__(name="financials_tools")
        from ..financials import Financials
        self.client = Financials(api_key, output_format='pandas')
        self.register(self.get_financials)
        self.register(self.get_merged_financials)
    
    def get_financials(
        self,
        symbol: str,
        statement: Literal["income", "balance", "cash"],
        limit: int = 10,
        period: Literal["annual", "quarter"] = "quarter"
    ) -> str:
        """
        Get financial statements (income, balance sheet, or cash flow) for a stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')
            statement: Type of financial statement - 'income', 'balance', or 'cash'
            limit: Number of periods to return (default: 10)
            period: Period type - 'annual' or 'quarter' (default: 'quarter')
        
        Returns:
            JSON string of financial data
        """
        try:
            logger.info(f"Getting {statement} statement for {symbol}")
            data = self.client.get_financials(
                symbol=symbol,
                statement=statement,
                limit=limit,
                period=period
            )
            
            if isinstance(data, pd.DataFrame):
                if data.empty:
                    return f"No {statement} statement data found for {symbol}"
                return data.to_json(orient='records', indent=2)
            else:
                return str(data)
                
        except Exception as e:
            logger.error(f"Error getting financials: {e}")
            return f"Error retrieving financial data: {str(e)}"
    
    def get_merged_financials(
        self,
        symbol: str,
        limit: int = 40,
        period: Literal["annual", "quarter"] = "quarter"
    ) -> str:
        """
        Get merged financial data combining income, balance sheet, and cash flow statements.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')
            limit: Number of periods to return (default: 40)
            period: Period type - 'annual' or 'quarter' (default: 'quarter')
        
        Returns:
            JSON string of merged financial data
        """
        try:
            logger.info(f"Getting merged financials for {symbol}")
            data = self.client.financials.get_merged_financials(
                symbol=symbol,
                limit=limit,
                period=period
            )
            
            if isinstance(data, pd.DataFrame):
                if data.empty:
                    return f"No merged financial data found for {symbol}"
                return data.to_json(orient='records', indent=2)
            else:
                return str(data)
                
        except Exception as e:
            logger.error(f"Error getting merged financials: {e}")
            return f"Error retrieving merged financial data: {str(e)}"


class StocksTools(Toolkit):
    """Tools for accessing stock market data from fmpxx stocks module."""
    
    def __init__(self, api_key: str):
        super().__init__(name="stocks_tools")
        from ..stocks import Stocks
        self.client = Stocks(api_key, output_format='pandas')
        self.register(self.get_historical_price_full)
        self.register(self.get_quote)
        self.register(self.search_stocks)
        self.register(self.get_stock_list)
    
    def get_historical_price_full(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        period: Optional[int] = None
    ) -> str:
        """
        Get historical daily price data for a stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')
            start: Start date in YYYY-MM-DD format
            end: End date in YYYY-MM-DD format
            period: Number of years to retrieve (takes precedence over start/end dates)
        
        Returns:
            JSON string of historical price data including OHLCV
        """
        try:
            logger.info(f"Getting historical price data for {symbol}")
            data = self.client.historical_price_full(
                symbol=symbol,
                start=start,
                end=end,
                period=period
            )
            
            if isinstance(data, pd.DataFrame):
                if data.empty:
                    return f"No historical price data found for {symbol}"
                return data.to_json(orient='records', indent=2)
            else:
                return str(data)
                
        except Exception as e:
            logger.error(f"Error getting historical price: {e}")
            return f"Error retrieving historical price data: {str(e)}"
    
    def get_quote(self, symbol: str) -> str:
        """
        Get real-time quote for a stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')
        
        Returns:
            JSON string of quote data
        """
        try:
            logger.info(f"Getting quote for {symbol}")
            data = self.client.quote(symbol=symbol)
            
            if isinstance(data, pd.DataFrame):
                if data.empty:
                    return f"No quote data found for {symbol}"
                return data.to_json(orient='records', indent=2)
            else:
                return str(data)
                
        except Exception as e:
            logger.error(f"Error getting quote: {e}")
            return f"Error retrieving quote data: {str(e)}"
    
    def search_stocks(self, query: str, limit: int = 10) -> str:
        """
        Search for stocks by company name or symbol.
        
        Args:
            query: Search query (company name or symbol)
            limit: Maximum number of results (default: 10)
        
        Returns:
            JSON string of search results
        """
        try:
            logger.info(f"Searching for stocks with query: {query}")
            data = self.client.search(query=query, limit=limit)
            
            if isinstance(data, pd.DataFrame):
                if data.empty:
                    return f"No stocks found for query: {query}"
                return data.to_json(orient='records', indent=2)
            else:
                return str(data)
                
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            return f"Error searching stocks: {str(e)}"
    
    def get_stock_list(self) -> str:
        """
        Get list of all available stocks.
        
        Returns:
            JSON string of stock list
        """
        try:
            logger.info("Getting stock list")
            data = self.client.stock_list()
            
            if isinstance(data, pd.DataFrame):
                if data.empty:
                    return "No stock list data available"
                return data.head(100).to_json(orient='records', indent=2)  # Limit to first 100
            else:
                return str(data)
                
        except Exception as e:
            logger.error(f"Error getting stock list: {e}")
            return f"Error retrieving stock list: {str(e)}"