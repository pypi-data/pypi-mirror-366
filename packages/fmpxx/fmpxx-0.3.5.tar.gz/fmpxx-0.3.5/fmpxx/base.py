import requests
import pandas as pd
from .exceptions import FMPAPIError, InvalidAPIKeyError, SymbolNotFoundError, RateLimitExceededError, FMPConnectionError

class _BaseClient:
    BASE_URL = "https://financialmodelingprep.com/api/v3/"

    def __init__(self, api_key: str, timeout: int = 10, output_format: str = 'json'):
        if not api_key:
            raise ValueError("API key is required.")
        self.api_key = api_key
        self.timeout = timeout
        self.output_format = output_format
        self.session = requests.Session()
        self.session.params.update({'apikey': self.api_key})

    def _make_request(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{self.BASE_URL}{endpoint}"
        full_params = params.copy() if params else {}

        try:
            response = self.session.get(url, params=full_params, timeout=self.timeout)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise InvalidAPIKeyError("Invalid API key. Please check your API key.") from e
            elif response.status_code == 404:
                raise SymbolNotFoundError(f"Resource not found for endpoint: {endpoint}. Details: {response.text}") from e
            elif response.status_code == 429:
                raise RateLimitExceededError("API rate limit exceeded. Please wait and try again.") from e
            else:
                raise FMPAPIError(f"FMP API error: {response.status_code} - {response.text}") from e
        except requests.exceptions.ConnectionError as e:
            raise FMPConnectionError(f"Network connection error: {e}") from e
        except requests.exceptions.Timeout as e:
            raise FMPConnectionError(f"Request timed out after {self.timeout} seconds: {e}") from e
        except requests.exceptions.RequestException as e:
            raise FMPAPIError(f"An unexpected request error occurred: {e}") from e

        try:
            data = response.json()
        except ValueError as e:
            raise FMPAPIError(f"Failed to decode JSON response: {e}. Response content: {response.text}") from e

        return data

    def _process_response(self, data) -> list | pd.DataFrame:
        if self.output_format == 'pandas' and isinstance(data, list):
            if not data:
                return pd.DataFrame() # Return empty DataFrame for empty list
            try:
                df = pd.DataFrame(data)
                # Drop specific columns as requested
                df = df.drop(columns=["link", "finalLink"], errors="ignore")
                return df
            except Exception as e:
                # Fallback to JSON if pandas conversion fails for some reason
                print(f"Warning: Could not convert to Pandas DataFrame. Returning JSON. Error: {e}")
                return data
        return data

    def _ensure_dataframe(self, data) -> pd.DataFrame:
        """Ensure data is a DataFrame type"""
        if isinstance(data, list):
            return pd.DataFrame(data)
        return data if isinstance(data, pd.DataFrame) else pd.DataFrame()

    def _standardize_date_format(self, df: pd.DataFrame, date_col: str = 'date') -> pd.DataFrame:
        """Standardize date format to YYYY-MM-DD"""
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')
        return df
