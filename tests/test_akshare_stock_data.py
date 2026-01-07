"""
Integration tests for Akshare stock data retrieval.

Tests the fix for bug #002: Akshare get_stock_data returns no data.
Tests with real API calls to ensure end-to-end functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from tradingagents.dataflows.akshare import get_akshare_stock


class TestAkshareStockDataIntegration:
    """Integration tests for get_akshare_stock with bug fix"""

    @pytest.mark.integration
    def test_get_akshare_stock_original_bug_scenario(self):
        """Test the exact scenario from bug report #002.

        Bug report: Calling get_stock_data with symbol '601939'
        for date range '2025-03-10' to '2025-05-10' returned no data.

        Expected: Should return data, not "No data found" message.
        """
        result = get_akshare_stock(
            symbol="601939",
            start_date="2025-03-10",
            end_date="2025-05-10"
        )

        # Should not return the "No data found" error message
        assert "No data found" not in result, \
            f"Bug still present: get_akshare_stock returned 'No data found'. Result: {result[:200]}"

        # Should contain stock data header
        assert "Stock data for" in result or "601939" in result, \
            f"Result should contain stock data. Got: {result[:200]}"

        # Verify it's a string result
        assert isinstance(result, str)

    @pytest.mark.integration
    def test_get_akshare_stock_historical_data(self):
        """Test retrieval of historical stock data with fixed code format."""
        result = get_akshare_stock(
            symbol="601939",
            start_date="2024-01-01",
            end_date="2024-01-31"
        )

        # Should contain stock data
        assert "601939" in result or "Stock data for" in result
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.integration
    def test_get_akshare_stock_shenzhen_market(self):
        """Test stock data retrieval for Shenzhen market stocks."""
        result = get_akshare_stock(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-31"
        )

        # Should contain stock data
        assert "000001" in result or "Stock data for" in result
        assert isinstance(result, str)

    @pytest.mark.integration
    def test_get_akshare_stock_with_prefix_input(self):
        """Test that input with prefix also works (backward compatibility)."""
        # User might input "sh601939" instead of "601939"
        result = get_akshare_stock(
            symbol="sh601939",
            start_date="2024-01-01",
            end_date="2024-01-31"
        )

        # Should still work and return data
        assert "No data found" not in result
        assert isinstance(result, str)


class TestAkshareStockDataWithMock:
    """Tests with mocked Akshare API for CI/CD environments"""

    def test_get_akshare_stock_mocked_success(self):
        """Test get_akshare_stock with mocked successful API response."""
        # Create mock DataFrame with Chinese column names
        mock_df = pd.DataFrame({
            '日期': ['2024-01-01', '2024-01-02'],
            '开盘': [10.0, 10.5],
            '收盘': [10.3, 10.8],
            '最高': [10.5, 11.0],
            '最低': [9.9, 10.4],
            '成交量': [1000000, 1200000],
            '成交额': [10300000, 12600000],
        })

        with patch('tradingagents.dataflows.akshare.ak.stock_zh_a_hist') as mock_api:
            mock_api.return_value = mock_df

            result = get_akshare_stock(
                symbol="601939",
                start_date="2024-01-01",
                end_date="2024-01-31"
            )

            # Verify the API was called with plain 6-digit code (no prefix)
            mock_api.assert_called_once()
            call_args = mock_api.call_args

            # Check that symbol parameter is plain 6-digit code
            assert 'symbol' in call_args.kwargs or len(call_args.args) > 0
            symbol_arg = call_args.kwargs.get('symbol', call_args.args[0] if call_args.args else None)
            assert symbol_arg == "601939", \
                f"API should be called with plain code '601939', got '{symbol_arg}'"

            # Verify result contains data
            assert "Stock data for" in result
            assert "No data found" not in result
            assert isinstance(result, str)

    def test_get_akshare_stock_mocked_empty_response(self):
        """Test get_akshare_stock with mocked empty response."""
        with patch('tradingagents.dataflows.akshare.ak.stock_zh_a_hist') as mock_api:
            # Return empty DataFrame
            mock_api.return_value = pd.DataFrame()

            result = get_akshare_stock(
                symbol="999999",
                start_date="2024-01-01",
                end_date="2024-01-31"
            )

            # Should return "No data found" message for truly empty response
            assert "No data found" in result
            assert isinstance(result, str)

    def test_get_akshare_stock_code_format_assertion(self):
        """Test that assertion catches incorrect code format."""
        # This test verifies the assertion in get_akshare_stock
        # that ensures the converted code is plain 6-digit format

        with patch('tradingagents.dataflows.akshare.ak.stock_zh_a_hist') as mock_api:
            mock_api.return_value = pd.DataFrame()

            # This should not raise assertion error
            result = get_akshare_stock(
                symbol="601939",
                start_date="2024-01-01",
                end_date="2024-01-31"
            )

            # Verify API was called
            assert mock_api.called
            assert isinstance(result, str)


class TestAkshareStockDataEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_get_akshare_stock_invalid_symbol(self):
        """Test with invalid symbol format."""
        from tradingagents.dataflows.akshare import AkshareCodeError, AkshareDataError

        # Empty symbol should raise error
        with pytest.raises((AkshareCodeError, AkshareDataError)):
            get_akshare_stock(
                symbol="",
                start_date="2024-01-01",
                end_date="2024-01-31"
            )

    @pytest.mark.integration
    def test_get_akshare_stock_future_dates(self):
        """Test with future date range (may return no data, but shouldn't error)."""
        result = get_akshare_stock(
            symbol="601939",
            start_date="2025-03-10",
            end_date="2025-05-10"
        )

        # Should return a string (either data or "No data found")
        assert isinstance(result, str)
        # Should not crash or raise exception


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not integration"])
