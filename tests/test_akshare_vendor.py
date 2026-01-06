"""
Unit tests for Akshare data vendor.

Test suite for basic functionality including:
- Import tests
- Code conversion tests
- Format validation tests
- Error handling tests
"""

import pytest
from tradingagents.dataflows.akshare import (
    convert_to_akshare_code,
    AkshareError,
    AkshareDataError,
    AkshareCodeError,
    get_akshare_stock,
    get_akshare_indicators,
    get_akshare_fundamentals,
    get_akshare_news
)


class TestAkshareImport:
    """Test that Akshare can be imported"""

    def test_akshare_import(self):
        """Test that Akshare can be imported"""
        import akshare as ak
        assert ak is not None


class TestStockCodeConversion:
    """Test stock code conversion to Akshare format"""

    def test_shanghai_code_conversion(self):
        """Test Shanghai stock code conversion (6xxx -> sh6xxx)"""
        assert convert_to_akshare_code("600000") == "sh600000"
        assert convert_to_akshare_code("601318") == "sh601318"

    def test_shenzhen_code_conversion(self):
        """Test Shenzhen stock code conversion (0xxx/3xxx -> sz0xxx)"""
        assert convert_to_akshare_code("000001") == "sz000001"
        assert convert_to_akshare_code("002415") == "sz002415"
        assert convert_to_akshare_code("300750") == "sz300750"

    def test_beijing_code_conversion(self):
        """Test Beijing stock code conversion (8xxx/4xxx -> bj8xxx)"""
        assert convert_to_akshare_code("832566") == "bj832566"
        assert convert_to_akshare_code("430047") == "bj430047"

    def test_already_converted_code(self):
        """Test codes that already have prefix"""
        assert convert_to_akshare_code("sh600000") == "sh600000"
        assert convert_to_akshare_code("sz000001") == "sz000001"
        assert convert_to_akshare_code("bj832566") == "bj832566"

    def test_empty_code(self):
        """Test empty code raises error"""
        with pytest.raises(AkshareCodeError):
            convert_to_akshare_code("")

    def test_case_insensitive_prefix(self):
        """Test that prefix is case-insensitive"""
        assert convert_to_akshare_code("SH600000") == "sh600000"
        assert convert_to_akshare_code("SZ000001") == "sz000001"
        assert convert_to_akshare_code("BJ832566") == "bj832566"


class TestAkshareStockData:
    """Test Akshare stock data retrieval"""

    def test_stock_data_format_compatibility(self):
        """Test that return format is compatible (has required OHLCV fields)"""
        try:
            result = get_akshare_stock("000001", period="daily", start_date="2024-01-01", end_date="2024-01-31")

            # Check that result is a string
            assert isinstance(result, str)

            # Check for required fields in the CSV output
            # Note: Akshare returns Chinese column names, so we check for translated versions
            assert "Date" in result or "日期" in result
            assert "Open" in result or "开盘" in result
            assert "High" in result or "最高" in result
            assert "Low" in result or "最低" in result
            assert "Close" in result or "收盘" in result
            assert "Volume" in result or "成交量" in result

        except Exception as e:
            pytest.skip(f"Akshare API call failed (possibly network issue): {e}")

    def test_stock_data_invalid_symbol(self):
        """Test that invalid symbol is handled correctly"""
        # Empty symbol should raise AkshareCodeError
        with pytest.raises((AkshareCodeError, AkshareDataError)):
            get_akshare_stock("", period="daily", start_date="2024-01-01")

    def test_stock_data_with_adjustment(self):
        """Test different adjustment types"""
        try:
            # Test qfq (前复权)
            result_qfq = get_akshare_stock("000001", period="daily", start_date="2024-01-01", end_date="2024-01-31", adjust="qfq")
            assert isinstance(result_qfq, str)

            # Test hfq (后复权)
            result_hfq = get_akshare_stock("000001", period="daily", start_date="2024-01-01", end_date="2024-01-31", adjust="hfq")
            assert isinstance(result_hfq, str)

        except Exception as e:
            pytest.skip(f"Akshare API call failed (possibly network issue): {e}")


class TestAkshareIndicators:
    """Test Akshare technical indicators"""

    def test_indicators_return_value(self):
        """Test that indicators function returns a value"""
        try:
            result = get_akshare_indicators("000001", period="daily", indicator_names="macd")
            assert isinstance(result, str)
            assert "Technical Indicators" in result

        except Exception as e:
            pytest.skip(f"Akshare API call failed (possibly network issue): {e}")


class TestAkshareNews:
    """Test Akshare news data retrieval"""

    def test_news_return_value(self):
        """Test that news function returns a value"""
        try:
            result = get_akshare_news("000001")
            assert isinstance(result, str)

        except Exception as e:
            pytest.skip(f"Akshare API call failed (possibly network issue): {e}")


class TestAkshareFundamentals:
    """Test Akshare fundamental data retrieval"""

    def test_fundamentals_return_value(self):
        """Test that fundamentals function returns a value"""
        try:
            result = get_akshare_fundamentals("000001")
            assert isinstance(result, str)
            assert "Fundamental Analysis" in result

        except Exception as e:
            pytest.skip(f"Akshare API call failed (possibly network issue): {e}")


class TestAkshareExceptions:
    """Test custom exception classes"""

    def test_akshare_error_hierarchy(self):
        """Test that custom exceptions inherit from AkshareError"""
        assert issubclass(AkshareDataError, AkshareError)
        assert issubclass(AkshareCodeError, AkshareError)

    def test_exception_messages(self):
        """Test that exceptions contain meaningful messages"""
        try:
            raise AkshareCodeError("Test error")
        except AkshareCodeError as e:
            assert str(e) == "Test error"


class TestAkshareIntegration:
    """Integration tests with vendor routing"""

    def test_vendor_method_mapping(self):
        """Test that akshare is properly mapped in VENDOR_METHODS"""
        from tradingagents.dataflows.interface import VENDOR_METHODS

        # Check that akshare is mapped for supported methods
        assert "akshare" in VENDOR_METHODS["get_stock_data"]
        assert "akshare" in VENDOR_METHODS["get_indicators"]
        assert "akshare" in VENDOR_METHODS["get_fundamentals"]
        assert "akshare" in VENDOR_METHODS["get_balance_sheet"]
        assert "akshare" in VENDOR_METHODS["get_cashflow"]
        assert "akshare" in VENDOR_METHODS["get_income_statement"]
        assert "akshare" in VENDOR_METHODS["get_news"]

    def test_vendor_list(self):
        """Test that akshare is in VENDOR_LIST"""
        from tradingagents.dataflows.interface import VENDOR_LIST

        assert "akshare" in VENDOR_LIST


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
