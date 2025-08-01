from .base import _BaseClient
import pandas as pd
from datetime import datetime, timedelta

class Stocks(_BaseClient):
    """Client for FMP Stock API endpoints."""

    def __init__(self, api_key: str, timeout: int = 10, output_format: str = 'json'):
        super().__init__(api_key, timeout, output_format)

    def historical_price_full(self, symbol: str, series_type: str | None = None, start: str | None = None, end: str | None = None, period: int | None = None):
        """
        Get full historical daily prices for a given symbol.

        Args:
            symbol (str): Stock ticker symbol (e.g., 'AAPL').
            series_type (str, optional): Type of series (e.g., 'line').
            start (str, optional): Start date in YYYY-MM-DD format.
            end (str, optional): End date in YYYY-MM-DD format.
            period (int, optional): Number of years to retrieve data for, ending today. Takes precedence over `start` if both are provided.

        Returns:
            list or pandas.DataFrame: Historical price data.
        """
        endpoint = f"historical-price-full/{symbol}"
        params = {}
        if series_type: params['serietype'] = series_type

        if period is not None:
            today = datetime.now()
            start_date = today - timedelta(days=365 * period) # Approximate years
            params['from'] = start_date.strftime('%Y-%m-%d')
            params['to'] = today.strftime('%Y-%m-%d')
        else:
            if start: params['from'] = start
            if end: params['to'] = end

        data = self._make_request(endpoint, params)
        if data and 'historical' in data:
            df = self._process_response(data['historical'])
        else:
            df = self._process_response(data)

        if isinstance(df, pd.DataFrame) and not df.empty:
            # Ensure 'date' column is datetime for proper sorting and deduplication
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                # Sort by date (descending) and drop duplicates, keeping the latest
                df = df.sort_values(by='date', ascending=False).drop_duplicates(subset=['date'], keep='first')
                # Sort by date (ascending) for final output
                df = df.sort_values(by='date', ascending=True, ignore_index=True)

            # Select only the required columns
            required_columns = ['date', 'open', 'high', 'low', 'close']
            df = df[[col for col in required_columns if col in df.columns]]

            # Calculate pct_chg
            if 'close' in df.columns:
                df['pct_chg'] = df['close'].pct_change()

        return df

    def daily_prices(self, symbol: str, start: str | None = None, end: str | None = None, period: int | None = None):
        """
        Get historical daily prices for a given symbol (line series).

        Args:
            symbol (str): Stock ticker symbol (e.g., 'AAPL').
            start (str, optional): Start date in YYYY-MM-DD format.
            end (str, optional): End date in YYYY-MM-DD format.
            period (int, optional): Number of years to retrieve data for, ending today. Takes precedence over `start` if both are provided.

        Returns:
            list or pandas.DataFrame: Daily price data.
        """
        return self.historical_price_full(symbol, series_type='line', start=start, end=end, period=period)

    def stock_list(self):
        """
        Get a list of all available stocks.

        Returns:
            list or pandas.DataFrame: List of stocks.
        """
        endpoint = "stock/list"
        data = self._make_request(endpoint)
        return self._process_response(data)

    def quote(self, symbol: str):
        """
        Get real-time quote for a given symbol.

        Args:
            symbol (str): Stock ticker symbol (e.g., 'AAPL').

        Returns:
            list or pandas.DataFrame: Quote data.
        """
        endpoint = f"quote/{symbol}"
        data = self._make_request(endpoint)
        return self._process_response(data)

    def search(self, query: str, exchange: str | None = None, limit: int = 10):
        """
        Search for companies by name or symbol.

        Args:
            query (str): Search query.
            exchange (str, optional): Filter by exchange.
            limit (int): Number of results to return. Defaults to 10.

        Returns:
            list or pandas.DataFrame: Search results.
        """
        endpoint = "search"
        params = {'query': query, 'limit': limit}
        if exchange: params['exchange'] = exchange
        data = self._make_request(endpoint, params)
        return self._process_response(data)
