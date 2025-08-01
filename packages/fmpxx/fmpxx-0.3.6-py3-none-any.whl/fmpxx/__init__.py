from .base import _BaseClient
from .financials import Financials
from .stocks import Stocks

class FMPClient(_BaseClient):
    """Main client for interacting with the Financial Modeling Prep (FMP) API.

    This class provides a user-friendly and consistent interface to access
    various financial data endpoints offered by FMP.

    Args:
        api_key (str): Your FMP API key.
        timeout (int, optional): Request timeout in seconds. Defaults to 10.
        output_format (str, optional): Desired output format ('json' or 'pandas').
                                       Defaults to 'json'.

    Attributes:
        financials (Financials): Access to company fundamental data.
        stocks (Stocks): Access to stock market data.
    """

    def __init__(self, api_key: str, timeout: int = 10, output_format: str = 'json'):
        super().__init__(api_key, timeout, output_format)

        # Initialize categorized API modules
        self.financials = Financials(api_key, timeout, output_format)
        self.stocks = Stocks(api_key, timeout, output_format)

    # You can add more categorized properties here as you implement more modules
    # For example:
    # @property
    # def forex(self):
    #     return Forex(self.api_key, self.timeout, self.output_format)

    # @property
    # def cryptocurrencies(self):
    #     return Cryptocurrencies(self.api_key, self.timeout, self.output_format)