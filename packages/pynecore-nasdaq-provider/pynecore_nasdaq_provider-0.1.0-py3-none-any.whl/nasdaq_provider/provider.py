"""Nasdaq Provider Implementation

This module implements the NasdaqProvider class that extends PyneCore's Provider base class.
Provides access to NASDAQ Data Link API (formerly Quandl) for financial data.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import ssl
from typing import Any, Callable
from datetime import datetime, timezone, timedelta, time
from pathlib import Path

from pynecore.providers.provider import Provider
from pynecore.types.ohlcv import OHLCV
from pynecore.core.syminfo import SymInfo, SymInfoInterval, SymInfoSession


class NasdaqProvider(Provider):
    """Nasdaq data provider for PyneCore
    
    This provider implements data access for nasdaq markets.
    """
    
    def __init__(self, *, symbol: str | None = None, timeframe: str | None = None,
                 ohlv_dir: Path | None = None, config_dir: Path | None = None):
        """Initialize Nasdaq provider
        
        Args:
            symbol: Trading symbol (e.g., 'EURUSD', 'BTCUSD')
            timeframe: Timeframe for data (e.g., '1m', '5m', '1h', '1d')
            ohlv_dir: Directory to save OHLCV data
            config_dir: Directory to read config file from
        """
        super().__init__(symbol=symbol, timeframe=timeframe, ohlv_dir=ohlv_dir, config_dir=config_dir)
        
        # Set provider-specific timezone
        self.timezone = timezone.utc  # Adjust based on your provider's timezone
        
        # Define configuration keys required for this provider
        self.config_keys = {
            '# Settings for nasdaq provider': '',
            "api_key": "your_nasdaq_api_key_here",
            "base_url": "https://data.nasdaq.com/api/v3",
            "default_database": "FRED",  # Default to FRED (more likely to be accessible)
            "rate_limit_delay": "0.1",  # Delay between API calls in seconds
        }
        
        # Initialize provider-specific client/connection
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the provider's client/connection"""
        self.api_key = self.config.get("api_key")
        self.base_url = self.config.get("base_url", "https://data.nasdaq.com/api/v3")
        self.default_database = self.config.get("default_database", "FRED")
        self.rate_limit_delay = float(self.config.get("rate_limit_delay", "0.1"))
        
        if not self.api_key or self.api_key == "your_nasdaq_api_key_here":
            raise ValueError("NASDAQ API key is required. Please set 'api_key' in providers.toml")
        
        # Simple client state
        self._client = {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "session_headers": {
                "User-Agent": "PyneCore-NASDAQ-Provider/0.1.0"
            }
        }
    
    @classmethod
    def to_tradingview_timeframe(cls, timeframe: str) -> str:
        """Convert provider timeframe to TradingView format
        
        Args:
            timeframe: Provider's native timeframe format
            
        Returns:
            TradingView compatible timeframe string
        """
        # NASDAQ Data Link primarily provides daily data
        timeframe_map = {
            "daily": "1D",
            "1d": "1D",
            "weekly": "1W",
            "1w": "1W",
            "monthly": "1M",
            "1M": "1M",
            "quarterly": "3M",
            "annual": "12M",
        }
        return timeframe_map.get(timeframe, "1D")
    
    @classmethod
    def to_exchange_timeframe(cls, timeframe: str) -> str:
        """Convert TradingView timeframe to provider format
        
        Args:
            timeframe: TradingView timeframe format
            
        Returns:
            Provider's native timeframe string
        """
        # Convert TradingView format to NASDAQ Data Link format
        timeframe_map = {
            "1D": "daily",
            "1W": "weekly",
            "1M": "monthly",
            "3M": "quarterly",
            "12M": "annual",
        }
        return timeframe_map.get(timeframe, "daily")
    
    def get_list_of_symbols(self, *args, **kwargs) -> list[str]:
        """Get list of available symbols from the provider
        
        Returns:
            List of available trading symbols
        """
        try:
            # Get database codes for the default database
            url = f"{self.base_url}/databases/{self.default_database}/codes"
            params = {
                "api_key": self.api_key,
                "per_page": 100  # Limit to first 100 symbols
            }
            
            query_string = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_string}"
            
            # Create SSL context that doesn't verify certificates (for development)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(full_url, context=ssl_context) as response:
                data = json.loads(response.read().decode())
                
            if "dataset_codes" in data:
                symbols = []
                for item in data["dataset_codes"]["dataset_codes"]:
                    if len(item) >= 1:
                        symbols.append(item[0])  # First element is the symbol code
                return symbols[:50]  # Return first 50 symbols
            else:
                # Fallback to potentially accessible symbols from various databases
                return [
                    "FRED/GDP", "FRED/UNRATE", "FRED/CPIAUCSL", "FRED/FEDFUNDS",
                    "BCHAIN/MKPRU", "BCHAIN/TOTBC", "BCHAIN/AVBLS", "BCHAIN/NTRAN",
                    "EOD/AAPL", "EOD/GOOGL", "EOD/MSFT"
                ]
                
        except Exception as e:
            # Return potentially accessible symbols from various databases as fallback
            return [
                "FRED/GDP", "FRED/UNRATE", "FRED/CPIAUCSL", "FRED/FEDFUNDS",
                "BCHAIN/MKPRU", "BCHAIN/TOTBC", "BCHAIN/AVBLS", "BCHAIN/NTRAN",
                "EOD/AAPL", "EOD/GOOGL", "EOD/MSFT"
            ]
    
    def update_symbol_info(self) -> SymInfo:
        """Update and return symbol information
        
        Returns:
            SymInfo object containing symbol information
        """
        try:
            # Get dataset metadata from NASDAQ Data Link
            symbol_code = self.symbol or "WIKI/AAPL"
            url = f"{self.base_url}/datasets/{symbol_code}/metadata"
            params = {"api_key": self.api_key}
            
            query_string = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_string}"
            
            # Create SSL context that doesn't verify certificates (for development)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(full_url, context=ssl_context) as response:
                data = json.loads(response.read().decode())
                
            dataset = data.get("dataset", {})
            name = dataset.get("name", symbol_code)
            description = dataset.get("description", f"{symbol_code} from NASDAQ Data Link")
            
            return SymInfo(
                prefix="nasdaq",
                description=description[:100],  # Limit description length
                ticker=symbol_code,
                currency="USD",
                period=self.timeframe or "daily",
                type="stock",
                mintick=0.01,
                pricescale=100,
                pointvalue=1.0,
                opening_hours=[],
                session_starts=[],
                session_ends=[],
                timezone=str(self.timezone),
                avg_spread=None,
                taker_fee=0.0
            )
            
        except Exception as e:
            # Fallback implementation
            return SymInfo(
                prefix="nasdaq",
                description=f"{self.symbol or 'UNKNOWN'} from NASDAQ Data Link",
                ticker=self.symbol or "UNKNOWN",
                currency="USD",
                period=self.timeframe or "daily",
                type="stock",
                mintick=0.01,
                pricescale=100,
                pointvalue=1.0,
                opening_hours=[],
                session_starts=[],
                session_ends=[],
                timezone=str(self.timezone),
                avg_spread=None,
                taker_fee=0.0
            )
    
    def get_opening_hours_and_sessions(self) -> tuple[list[SymInfoInterval], list[SymInfoSession], list[SymInfoSession]]:
        """Get trading hours and session information for symbol
        
        Returns:
            Tuple containing (opening_hours, sessions, session_ends)
        """
        # NASDAQ stock market hours (Monday to Friday, 9:30 AM - 4:00 PM ET)
        opening_hours = []
        sessions = []
        session_ends = []
        
        # Add trading hours for weekdays (Monday=0 to Friday=4)
        for day in range(5):  # Monday to Friday
            opening_hours.append(SymInfoInterval(
                day=day,
                start=time(9, 30, 0),  # 9:30 AM
                end=time(16, 0, 0)     # 4:00 PM
            ))
            sessions.append(SymInfoSession(
                day=day,
                time=time(9, 30, 0)    # Session starts at 9:30 AM
            ))
            session_ends.append(SymInfoSession(
                day=day,
                time=time(16, 0, 0)    # Session ends at 4:00 PM
            ))
        
        return opening_hours, sessions, session_ends
    
    def download_ohlcv(self, time_from: datetime, time_to: datetime,
                       on_progress: Callable[[datetime], None] | None = None):
        """Download OHLCV data from the NASDAQ Data Link API
        
        Args:
            time_from: Start datetime (timezone-aware)
            time_to: End datetime (timezone-aware)
            on_progress: Optional callback to call on progress
        """
        import time as time_module
        
        try:
            symbol_code = self.symbol or "WIKI/AAPL"
            
            # Format dates for NASDAQ Data Link API (YYYY-MM-DD)
            start_date = time_from.strftime("%Y-%m-%d")
            end_date = time_to.strftime("%Y-%m-%d")
            
            # Build API URL
            url = f"{self.base_url}/datasets/{symbol_code}/data"
            params = {
                "api_key": self.api_key,
                "start_date": start_date,
                "end_date": end_date,
                "order": "asc",  # Ascending order (oldest first)
                "collapse": self.to_exchange_timeframe(self.timeframe or "1D")
            }
            
            query_string = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_string}"
            
            if on_progress:
                on_progress(time_from)
            
            # Create SSL context that doesn't verify certificates (for development)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Make API request
            with urllib.request.urlopen(full_url, context=ssl_context) as response:
                data = json.loads(response.read().decode())
            
            # Rate limiting
            time_module.sleep(self.rate_limit_delay)
            
            if "dataset_data" not in data:
                raise RuntimeError("Invalid response from NASDAQ Data Link API")
            
            dataset_data = data["dataset_data"]
            column_names = dataset_data.get("column_names", [])
            rows = dataset_data.get("data", [])
            
            if not rows:
                return  # No data available
            
            # Find column indices (NASDAQ Data Link typically has: Date, Open, High, Low, Close, Volume, ...)
            try:
                date_idx = column_names.index("Date")
                open_idx = column_names.index("Open")
                high_idx = column_names.index("High")
                low_idx = column_names.index("Low")
                close_idx = column_names.index("Close")
                volume_idx = column_names.index("Volume") if "Volume" in column_names else None
            except ValueError as e:
                raise RuntimeError(f"Required OHLC columns not found in data: {e}")
            
            # Convert to OHLCV objects
            ohlcv_data = []
            total_rows = len(rows)
            
            for i, row in enumerate(rows):
                try:
                    # Parse date string to datetime
                    date_str = row[date_idx]
                    if isinstance(date_str, str):
                        dt = datetime.strptime(date_str, "%Y-%m-%d")
                    else:
                        continue  # Skip invalid dates
                    
                    # Convert to timezone-aware datetime
                    dt = dt.replace(tzinfo=timezone.utc)
                    
                    # Extract OHLCV values
                    open_price = float(row[open_idx]) if row[open_idx] is not None else 0.0
                    high_price = float(row[high_idx]) if row[high_idx] is not None else 0.0
                    low_price = float(row[low_idx]) if row[low_idx] is not None else 0.0
                    close_price = float(row[close_idx]) if row[close_idx] is not None else 0.0
                    volume = float(row[volume_idx]) if volume_idx is not None and row[volume_idx] is not None else 0.0
                    
                    # Skip rows with invalid data
                    if open_price <= 0 or high_price <= 0 or low_price <= 0 or close_price <= 0:
                        continue
                    
                    # Create OHLCV object
                    ohlcv = OHLCV(
                        timestamp=int(dt.timestamp() * 1000),  # Convert to milliseconds
                        open=open_price,
                        high=high_price,
                        low=low_price,
                        close=close_price,
                        volume=volume
                    )
                    ohlcv_data.append(ohlcv)
                    
                    # Update progress
                    if on_progress and i % max(1, total_rows // 10) == 0:
                        on_progress(dt)
                        
                except (ValueError, TypeError, IndexError) as e:
                    # Skip invalid rows
                    continue
            
            if ohlcv_data:
                # Save data using PyneCore's save method
                self.save_ohlcv_data(ohlcv_data)
                
                if on_progress:
                    on_progress(time_to)
            
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise RuntimeError("Invalid NASDAQ Data Link API key. Please check your configuration.")
            elif e.code == 403:
                error_msg = f"NASDAQ Data Link API error 403: Forbidden for {symbol_code}"
                error_msg += f"\n\nTroubleshooting 403 Forbidden for {symbol_code}:\n"
                error_msg += "• Most datasets (including WIKI, BCHAIN) require a premium subscription\n"
                error_msg += "• Try FRED database symbols (e.g., FRED/GDP, FRED/UNRATE)\n"
                error_msg += "• Check available symbols: pyne data download nasdaq --list-symbols\n"
                error_msg += "• Verify your API key has proper permissions\n"
                error_msg += "• Check if you've exceeded your free trial limit\n"
                error_msg += "• Visit https://data.nasdaq.com/databases to check pricing"
                raise RuntimeError(error_msg)
            elif e.code == 404:
                raise RuntimeError(f"Symbol '{symbol_code}' not found in NASDAQ Data Link.")
            elif e.code == 429:
                raise RuntimeError("Rate limit exceeded. Please wait before making more requests.")
            else:
                raise RuntimeError(f"NASDAQ Data Link API error {e.code}: {e.reason}")
        except Exception as e:
            raise RuntimeError(f"Failed to download OHLCV data from NASDAQ Data Link: {e}")