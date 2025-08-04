"""Tests for NasdaqProvider"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
import tempfile

from nasdaq_provider import NasdaqProvider
from pynecore.types.ohlcv import OHLCV
from pynecore.core.syminfo import SymInfo


class TestNasdaqProvider:
    """Test suite for NasdaqProvider"""
    
    @pytest.fixture
    def temp_workdir(self):
        """Create temporary working directory for tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def provider(self, temp_workdir):
        """Create provider instance for testing"""
        # Create config directory and providers.toml
        config_dir = temp_workdir / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Create a minimal providers.toml file with test API key
        providers_toml = config_dir / "providers.toml"
        providers_toml.write_text("""
        [nasdaq]
        # Configuration for nasdaq provider
        api_key = "test_api_key_for_testing"
        base_url = "https://data.nasdaq.com/api/v3"
        default_database = "FRED"
        rate_limit_delay = "0.1"
        """)
        
        return NasdaqProvider(
            symbol="FRED/GDP",
            timeframe="daily",
            ohlv_dir=temp_workdir / "data",
            config_dir=config_dir
        )
    
    def test_initialization(self, provider):
        """Test provider initialization"""
        assert provider.symbol == "FRED/GDP"
        assert provider.timeframe == "daily"
        assert provider.timezone == timezone.utc
        assert isinstance(provider.config_keys, dict)
    
    def test_timeframe_conversion_to_tradingview(self, provider):
        """Test timeframe conversion to TradingView format"""
        test_cases = {
            "daily": "1D",
            "1d": "1D",
            "weekly": "1W",
            "1w": "1W",
            "monthly": "1M",
            "1M": "1M",
            "quarterly": "3M",
            "annual": "12M",
        }
        
        for provider_tf, expected_tv_tf in test_cases.items():
            result = NasdaqProvider.to_tradingview_timeframe(provider_tf)
            assert result == expected_tv_tf, f"Failed for {provider_tf}: expected {expected_tv_tf}, got {result}"
    
    def test_timeframe_conversion_to_exchange(self, provider):
        """Test timeframe conversion to exchange format"""
        test_cases = {
            "1D": "daily",
            "1W": "weekly",
            "1M": "monthly",
            "3M": "quarterly",
            "12M": "annual",
        }
        
        for tv_tf, expected_provider_tf in test_cases.items():
            result = NasdaqProvider.to_exchange_timeframe(tv_tf)
            assert result == expected_provider_tf, f"Failed for {tv_tf}: expected {expected_provider_tf}, got {result}"
    
    def test_get_list_of_symbols(self, provider):
        """Test symbol listing"""
        symbols = provider.get_list_of_symbols()
        assert isinstance(symbols, list)
        assert len(symbols) > 0
        assert all(isinstance(symbol, str) for symbol in symbols)
    
    def test_update_symbol_info(self, provider):
        """Test symbol information retrieval"""
        symbol_info = provider.update_symbol_info()
        
        assert isinstance(symbol_info, SymInfo)
        assert symbol_info.ticker == "FRED/GDP"
        assert symbol_info.description is not None
        assert symbol_info.type is not None
        assert symbol_info.currency is not None
    
    def test_get_opening_hours_and_sessions(self, provider):
        """Test trading hours and session information"""
        opening_hours, sessions, session_ends = provider.get_opening_hours_and_sessions()
        
        assert isinstance(opening_hours, list)
        assert isinstance(sessions, list)
        assert isinstance(session_ends, list)
    
    def test_download_ohlcv_basic(self, provider):
        """Test basic OHLCV data download"""
        # Skip test if using test API key
        if provider.api_key == "test_api_key_for_testing":
            pytest.skip("Skipping API test with test key")
            
        start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2023, 1, 2, tzinfo=timezone.utc)
        
        # Track progress calls
        progress_calls = []
        def progress_callback(timestamp):
            progress_calls.append(timestamp)
        
        # Download data (this saves to provider's OHLCV storage)
        provider.download_ohlcv(
            time_from=start_date,
            time_to=end_date,
            on_progress=progress_callback
        )
        
        # Verify progress was called
        assert len(progress_calls) > 0
        assert all(isinstance(ts, datetime) for ts in progress_calls)
        
        # Verify the download completed without errors
        # Note: The actual data is saved by PyneCore's base Provider class
        # We can't easily test the saved data without mocking the file system
    
    def test_download_ohlcv_with_progress(self, provider):
        """Test OHLCV download with progress callback"""
        # Skip test if using test API key
        if provider.api_key == "test_api_key_for_testing":
            pytest.skip("Skipping API test with test key")
            
        start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2023, 1, 2, tzinfo=timezone.utc)
        
        progress_calls = []
        
        def progress_callback(timestamp):
            progress_calls.append(timestamp)
            assert isinstance(timestamp, datetime)
        
        provider.download_ohlcv(
            time_from=start_date,
            time_to=end_date,
            on_progress=progress_callback
        )
        
        assert len(progress_calls) > 0
        # Verify all progress calls are datetime objects
        assert all(isinstance(ts, datetime) for ts in progress_calls)
        
        # Verify the download completed without errors
        # Note: The actual data is saved by PyneCore's base Provider class
    
    def test_download_ohlcv_empty_range(self, provider):
        """Test OHLCV download with invalid time range"""
        # Skip test if using test API key
        if provider.api_key == "test_api_key_for_testing":
            pytest.skip("Skipping API test with test key")
            
        start_date = datetime(2024, 1, 2, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 1, tzinfo=timezone.utc)  # Invalid range
        
        provider.download_ohlcv(
            time_from=start_date,
            time_to=end_date
        )
        
        # Verify the download completed without errors for invalid range
        # Note: The provider should handle invalid ranges gracefully
    
    def test_download_ohlcv_date_range(self, provider):
        """Test OHLCV download with specific date range"""
        # Skip test if using test API key
        if provider.api_key == "test_api_key_for_testing":
            pytest.skip("Skipping API test with test key")
            
        start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2023, 1, 3, tzinfo=timezone.utc)
        
        provider.download_ohlcv(
            time_from=start_date,
            time_to=end_date
        )
        
        # Verify the download completed without errors
        # Note: The actual data is saved by PyneCore's base Provider class
    
    @pytest.mark.parametrize("timeframe", ["daily", "weekly", "monthly"])
    def test_download_ohlcv_different_timeframes(self, provider, timeframe):
        """Test OHLCV download with different timeframes"""
        # Skip test if using test API key
        if provider.api_key == "test_api_key_for_testing":
            pytest.skip("Skipping API test with test key")
            
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)  # 1 month
        
        # Create provider with specific timeframe
        provider_tf = NasdaqProvider(
            symbol="FRED/GDP",
            timeframe=timeframe,
            ohlv_dir=provider.ohlcv_path.parent,
            config_dir=provider.config_dir
        )
        
        provider_tf.download_ohlcv(
            time_from=start_date,
            time_to=end_date
        )
        
        # Verify the download completed without errors for different timeframes
        # Note: The actual data is saved by PyneCore's base Provider class