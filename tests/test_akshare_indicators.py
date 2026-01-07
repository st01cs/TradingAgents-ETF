"""
Unit tests for akshare get_indicators functionality.

Tests the indicator calculation and integration with akshare data vendor.
"""

import pytest
import pandas as pd
import numpy as np
from tradingagents.dataflows.akshare import get_akshare_indicators
from tradingagents.dataflows.indicators.calculator import IndicatorCalculator


class TestIndicatorParsing:
    """Test indicator list parsing."""

    def test_single_indicator(self):
        result = IndicatorCalculator.parse_indicator_list("rsi")
        assert result == ["rsi"]

    def test_multiple_indicators(self):
        result = IndicatorCalculator.parse_indicator_list("rsi,macd,atr")
        assert result == ["rsi", "macd", "atr"]

    def test_indicators_with_spaces(self):
        result = IndicatorCalculator.parse_indicator_list("rsi, macd , atr")
        assert result == ["rsi", "macd", "atr"]

    def test_empty_string(self):
        result = IndicatorCalculator.parse_indicator_list("")
        assert result == []


class TestIndicatorCalculation:
    """Test indicator calculation."""

    @pytest.fixture
    def sample_ohlcv_data(self):
        """Generate sample OHLCV data for testing."""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        np.random.seed(42)

        data = {
            'Date': dates,
            'Open': np.random.uniform(95, 105, 100),
            'High': np.random.uniform(100, 110, 100),
            'Low': np.random.uniform(90, 100, 100),
            'Close': np.random.uniform(95, 105, 100),
            'Volume': np.random.randint(1000000, 10000000, 100)
        }
        return pd.DataFrame(data)

    def test_calculate_rsi(self, sample_ohlcv_data):
        result_df = IndicatorCalculator.calculate(
            sample_ohlcv_data,
            ['rsi']
        )
        assert 'rsi' in result_df.columns
        assert result_df['rsi'].iloc[-1] >= 0
        assert result_df['rsi'].iloc[-1] <= 100

    def test_calculate_macd(self, sample_ohlcv_data):
        result_df = IndicatorCalculator.calculate(
            sample_ohlcv_data,
            ['macd', 'macds', 'macdh']
        )
        assert 'macd' in result_df.columns
        assert 'macds' in result_df.columns
        assert 'macdh' in result_df.columns

    def test_calculate_bollinger_bands(self, sample_ohlcv_data):
        result_df = IndicatorCalculator.calculate(
            sample_ohlcv_data,
            ['boll', 'boll_ub', 'boll_lb']
        )
        assert 'boll' in result_df.columns
        assert 'boll_ub' in result_df.columns
        assert 'boll_lb' in result_df.columns

    def test_calculate_multiple_indicators(self, sample_ohlcv_data):
        indicators = ['rsi', 'macd', 'atr', 'close_50_sma']
        result_df = IndicatorCalculator.calculate(
            sample_ohlcv_data,
            indicators
        )
        for ind in indicators:
            assert ind in result_df.columns

    def test_calculate_all_market_analyst_indicators(self, sample_ohlcv_data):
        """Test all 13 indicators used by market_analyst."""
        all_indicators = [
            'close_50_sma', 'close_200_sma', 'close_10_ema',
            'macd', 'macds', 'macdh',
            'rsi',
            'boll', 'boll_ub', 'boll_lb',
            'atr',
            'vwma'
        ]

        result_df = IndicatorCalculator.calculate(
            sample_ohlcv_data,
            all_indicators
        )

        # Verify at least some indicators were calculated
        assert len(result_df.columns) > 0

    def test_missing_required_columns(self):
        """Test error handling for missing required columns."""
        invalid_data = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=10),
            'Open': [100] * 10,
            # Missing High, Low, Close, Volume
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            IndicatorCalculator.calculate(invalid_data, ['rsi'])

    def test_format_as_text(self):
        """Test text formatting of indicator results."""
        summary_df = pd.DataFrame({
            'rsi': [65.5],
            'macd': [0.5],
            'atr': [2.3]
        })

        result = IndicatorCalculator.format_as_text(
            symbol="600000",
            summary_df=summary_df,
            curr_date="2024-01-15",
            look_back_days=30
        )

        assert "# Technical Indicators for 600000" in result
        assert "# Date: 2024-01-15" in result
        assert "# Lookback Period: 30 days" in result
        assert "# Total Indicators: 3" in result
        assert "rsi" in result
        assert "macd" in result
        assert "atr" in result


class TestGetAkshareIndicators:
    """Test get_akshare_indicators function."""

    @pytest.mark.integration
    def test_real_stock_single_indicator(self):
        """Test with real stock data (integration test)."""
        result = get_akshare_indicators(
            symbol="600000",  # Pudong Development Bank
            indicator="rsi",
            curr_date="2024-01-15",
            look_back_days=30
        )

        assert isinstance(result, str)
        assert "# Technical Indicators" in result
        assert "600000" in result or "sh600000" in result.lower()
        assert "rsi" in result.lower()

    @pytest.mark.integration
    def test_real_stock_multiple_indicators(self):
        """Test with multiple indicators (integration test)."""
        result = get_akshare_indicators(
            symbol="000001",  # Ping An Bank
            indicator="rsi,macd,atr",
            curr_date="2024-01-15",
            look_back_days=30
        )

        assert isinstance(result, str)
        assert "# Technical Indicators" in result
        # Verify at least some indicators are mentioned
        assert len(result) > 0

    @pytest.mark.integration
    def test_all_market_analyst_indicators(self):
        """Test all indicators used by market_analyst."""
        all_indicators = [
            'close_50_sma', 'close_200_sma', 'close_10_ema',
            'macd', 'macds', 'macdh',
            'rsi',
            'boll', 'boll_ub', 'boll_lb',
            'atr',
            'vwma'
        ]

        indicator_str = ','.join(all_indicators)
        result = get_akshare_indicators(
            symbol="600519",  # Kweichow Moutai
            indicator=indicator_str,
            curr_date="2024-01-15",
            look_back_days=250  # Enough data for 200 SMA
        )

        assert isinstance(result, str)
        assert "# Technical Indicators" in result
        # Verify at least some indicators were calculated
        assert len(result) > 100  # Should have substantial content

    @pytest.mark.integration
    def test_default_look_back_days(self):
        """Test default look_back_days parameter."""
        result = get_akshare_indicators(
            symbol="600000",
            indicator="rsi",
            curr_date="2024-01-15"
            # look_back_days defaults to 30
        )

        assert isinstance(result, str)
        assert "# Lookback Period: 30 days" in result

    @pytest.mark.integration
    def test_custom_look_back_days(self):
        """Test custom look_back_days parameter."""
        result = get_akshare_indicators(
            symbol="600000",
            indicator="rsi",
            curr_date="2024-01-15",
            look_back_days=60
        )

        assert isinstance(result, str)
        assert "# Lookback Period: 60 days" in result

    def test_invalid_stock_code(self):
        """Test error handling for invalid stock code."""
        with pytest.raises(Exception):  # AkshareCodeError or AkshareDataError
            get_akshare_indicators(
                symbol="invalid",
                indicator="rsi",
                curr_date="2024-01-15"
            )

    def test_empty_indicator_list(self):
        """Test error handling for empty indicator list."""
        with pytest.raises(Exception):  # AkshareDataError
            get_akshare_indicators(
                symbol="600000",
                indicator="",
                curr_date="2024-01-15"
            )


class TestIndicatorMapping:
    """Test indicator name mappings."""

    def test_all_indicators_mapped(self):
        """Verify all market_analyst indicators have mappings."""
        expected_indicators = [
            'close_50_sma', 'close_200_sma', 'close_10_ema',
            'macd', 'macds', 'macdh',
            'rsi',
            'boll', 'boll_ub', 'boll_lb',
            'atr',
            'vwma'
        ]

        for indicator in expected_indicators:
            assert indicator in IndicatorCalculator.INDICATOR_MAP, \
                f"Indicator '{indicator}' not found in mapping"

    def test_mapping_values_are_valid(self):
        """Verify mapped values are non-empty strings."""
        for key, value in IndicatorCalculator.INDICATOR_MAP.items():
            assert isinstance(value, str)
            assert len(value) > 0


class TestCSVParsing:
    """Test CSV parsing with comment lines (bug fix #003)."""

    def test_parse_csv_with_comment_lines(self):
        """Test that CSV with comment lines is parsed correctly."""
        import io

        # Mock CSV with comment lines (as returned by get_akshare_stock)
        mock_csv = """# Stock data for 601939 from 2025-04-10 to 2025-05-10
# Total records: 19
# Adjustment: qfq
# Data retrieved on: 2026-01-07 11:28:19

,Date,股票代码,Open,Close,High,Low,Volume,Amount
0,2025-04-10,601939,8.43,8.35,8.43,8.31,1250340,1090796889.0
1,2025-04-11,601939,8.36,8.4,8.4,8.29,1138682,994582346.0
"""

        # Parse with comment parameter
        df = pd.read_csv(io.StringIO(mock_csv), comment='#')

        # Verify parsing succeeded
        assert len(df) == 2
        assert 'Date' in df.columns
        assert 'Close' in df.columns
        assert df.iloc[0]['Close'] == 8.35

    def test_parse_csv_without_comment_lines(self):
        """Test that CSV without comment lines still works."""
        import io

        # Mock CSV without comment lines
        mock_csv = """,Date,Open,Close
0,2025-04-10,8.43,8.35
1,2025-04-11,8.36,8.4
"""

        # Parse with comment parameter (should still work)
        df = pd.read_csv(io.StringIO(mock_csv), comment='#')

        # Verify parsing succeeded
        assert len(df) == 2
        assert df.iloc[0]['Close'] == 8.35

    def test_parse_csv_empty_data(self):
        """Test handling of empty CSV."""
        import io

        # Mock CSV with only comments
        mock_csv = """# Stock data for 601939
# No data available
"""

        # Parse with comment parameter - should raise EmptyDataError
        with pytest.raises(pd.errors.EmptyDataError):
            df = pd.read_csv(io.StringIO(mock_csv), comment='#')


class TestMACDIndicator:
    """Integration tests for MACD indicator (bug fix #003)."""

    @pytest.mark.integration
    def test_get_akshare_indicators_macd_original_bug(self):
        """Test the exact scenario from bug report #003."""
        # Use exact parameters from bug report
        result = get_akshare_indicators(
            symbol="601939",
            indicator="macd",
            curr_date="2025-05-10",
            look_back_days=30
        )

        # Should not raise parsing error
        assert isinstance(result, str)
        # Should contain indicator results
        assert "Technical Indicators" in result or "MACD" in result.upper()

    @pytest.mark.integration
    def test_get_akshare_indicators_other_indicators(self):
        """Verify other indicators (RSI, Bollinger Bands) still work."""
        # Test RSI
        result_rsi = get_akshare_indicators(
            symbol="601939",
            indicator="rsi",
            curr_date="2025-05-10",
            look_back_days=30
        )
        assert isinstance(result_rsi, str)
        assert "Technical Indicators" in result_rsi or "RSI" in result_rsi.upper()

        # Test Bollinger Bands
        result_bb = get_akshare_indicators(
            symbol="601939",
            indicator="bollinger",
            curr_date="2025-05-10",
            look_back_days=30
        )
        assert isinstance(result_bb, str)
        assert "Technical Indicators" in result_bb or "BOLLINGER" in result_bb.upper()
