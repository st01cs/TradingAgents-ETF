# Bug Fix Specification: Akshare get_indicators Implementation

## Issue Summary

**Bug ID:** 000-akshare-get-indicators
**Priority:** High
**Status:** Design Phase
**Affected Component:** `tradingagents/dataflows/akshare.py`

### Problem Description

When using akshare as the data vendor, calling `get_indicators` fails with:

```
get_akshare_indicators() takes from 1 to 3 positional arguments but 4 were given
```

**Root Cause:**
- The `get_indicators` tool interface accepts 4 parameters: `symbol`, `indicator`, `curr_date`, `look_back_days`
- The `get_akshare_indicators()` function only accepts 3 parameters: `symbol`, `period`, `indicator_names`
- Parameter mismatch causes runtime error when `route_to_vendor()` attempts to call the function

**Current Behavior:**
- `get_akshare_indicators()` returns a placeholder message indicating implementation is pending
- No actual technical indicators are calculated for Chinese stocks
- Fallback to other vendors (alpha_vantage, yfinance) fails for Chinese market data

---

## Solution Specification

### 1. Design Overview

**Strategy:** Hybrid Implementation with Local Calculation
- Primary: Attempt akshare built-in indicators (if available)
- Fallback: Calculate indicators locally using stockstats library
- Data Source: Fetch OHLCV data via `get_akshare_stock()` internally
- Return Format: Text summary with raw CSV data

### 2. Functional Requirements

#### 2.1 Function Signature

**Updated signature for `get_akshare_indicators()`:**

```python
def get_akshare_indicators(
    symbol: str,
    indicator: str,
    curr_date: str,
    look_back_days: int = 30
) -> str:
    """
    Calculate technical indicators for Chinese stocks.

    Args:
        symbol: Stock symbol (6-digit code or akshare format)
        indicator: Technical indicator name(s) (comma-separated for multiple)
        curr_date: Current date (YYYY-MM-DD) for determining date range
        look_back_days: Number of days to look back from curr_date (default: 30)

    Returns:
        Text summary with calculated indicators in CSV format

    Raises:
        AkshareCodeError: If stock code is invalid
        AkshareDataError: If data retrieval or calculation fails
    """
```

**Key Changes:**
- ✅ Full parameter mapping to match `get_indicators` tool interface
- ✅ Renamed `indicator_names` → `indicator` for consistency
- ✅ Removed unused `period` parameter
- ✅ Added `curr_date` and `look_back_days` parameters
- ✅ Default `look_back_days=30` for backward compatibility

#### 2.2 Indicator Support

**Complete Indicator Support (Phase 1):**

Must support all indicators used by `market_analyst`:

**Moving Averages:**
- `close_50_sma`: 50-day Simple Moving Average
- `close_200_sma`: 200-day Simple Moving Average
- `close_10_ema`: 10-day Exponential Moving Average

**MACD Related:**
- `macd`: MACD line
- `macds`: MACD Signal line
- `macdh`: MACD Histogram

**Momentum Indicators:**
- `rsi`: Relative Strength Index

**Volatility Indicators:**
- `boll`: Bollinger Bands Middle (20 SMA)
- `boll_ub`: Bollinger Bands Upper
- `boll_lb`: Bollinger Bands Lower
- `atr`: Average True Range

**Volume Indicators:**
- `vwma`: Volume Weighted Moving Average

**Total: 13 indicators**

#### 2.3 Implementation Architecture

**Module Structure:**

```
tradingagents/
├── dataflows/
│   ├── akshare.py                    # Modified: get_akshare_indicators()
│   └── indicators/
│       ├── __init__.py
│       ├── calculator.py             # NEW: Indicator calculation logic
│       └── mappings.py               # NEW: Indicator name mappings
└── agents/
    └── utils/
        └── technical_indicators_tools.py  # Existing: No changes needed
```

**New Module: `indicators/calculator.py`**

```python
"""
Technical indicator calculator for Chinese stock market.

Uses stockstats library for local calculation when akshare built-in
indicators are not available.
"""

import pandas as pd
from stockstats import StockDataFrame
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """Calculate technical indicators from OHLCV data."""

    # Indicator name mappings (market_analyst names → stockstats names)
    INDICATOR_MAP = {
        # Moving Averages
        'close_50_sma': 'close_50_sma',
        'close_200_sma': 'close_200_sma',
        'close_10_ema': 'close_10_ema',

        # MACD
        'macd': 'macd',
        'macds': 'macds',
        'macdh': 'macdh',

        # Momentum
        'rsi': 'rsi_14',  # Default 14-period RSI

        # Bollinger Bands
        'boll': 'boll',
        'boll_ub': 'boll_ub',
        'boll_lb': 'boll_lb',

        # Volatility
        'atr': 'atr_14'  # Default 14-period ATR

        # Volume
        'vwma': 'vwma_20'  # Default 20-period VWMA
    }

    @staticmethod
    def parse_indicator_list(indicator_str: str) -> List[str]:
        """
        Parse comma-separated indicator string into list.

        Handles:
        - Single indicator: "rsi"
        - Multiple indicators: "rsi,macd,atr"
        - Spacing: "rsi, macd , atr"

        Args:
            indicator_str: Comma-separated indicator names

        Returns:
            List of normalized indicator names
        """
        if not indicator_str:
            return []

        # Split by comma, strip whitespace, filter empty
        indicators = [ind.strip() for ind in indicator_str.split(',')]
        return [ind for ind in indicators if ind]

    @staticmethod
    def calculate(
        df: pd.DataFrame,
        indicators: List[str]
    ) -> pd.DataFrame:
        """
        Calculate technical indicators using stockstats.

        Args:
            df: DataFrame with OHLCV data (columns: Date, Open, High, Low, Close, Volume)
            indicators: List of indicator names to calculate

        Returns:
            DataFrame with calculated indicators added as columns

        Raises:
            ValueError: If required columns missing from DataFrame
        """
        # Validate required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Convert to StockDataFrame
        stock = StockDataFrame.copy(df)

        # Calculate each indicator
        calculated_indicators = {}
        for indicator in indicators:
            try:
                # Map indicator name to stockstats format
                stockstats_name = IndicatorCalculator.INDICATOR_MAP.get(indicator)

                if not stockstats_name:
                    logger.warning(f"Indicator '{indicator}' not in mapping, skipping")
                    continue

                # Calculate indicator using stockstats
                indicator_value = stock[stockstats_name]

                # Store the last (most recent) value
                if not indicator_value.empty:
                    calculated_indicators[indicator] = indicator_value.iloc[-1]
                    logger.debug(f"Calculated {indicator}: {indicator_value.iloc[-1]}")

            except Exception as e:
                logger.error(f"Failed to calculate {indicator}: {e}")
                continue

        # Create summary DataFrame
        summary_df = pd.DataFrame([calculated_indicators])

        return summary_df

    @staticmethod
    def format_as_text(
        symbol: str,
        summary_df: pd.DataFrame,
        curr_date: str,
        look_back_days: int
    ) -> str:
        """
        Format indicator summary as text with CSV data.

        Args:
            symbol: Stock symbol
            summary_df: DataFrame with calculated indicators
            curr_date: Current date
            look_back_days: Lookback period

        Returns:
            Formatted text with CSV data
        """
        lines = [
            f"# Technical Indicators for {symbol}",
            f"# Date: {curr_date}",
            f"# Lookback Period: {look_back_days} days",
            f"# Total Indicators: {len(summary_df.columns)}",
            ""
        ]

        # Add CSV data
        csv_data = summary_df.to_csv(index=False)
        lines.append(csv_data)

        return "\n".join(lines)
```

#### 2.4 Modified `get_akshare_indicators()`

**Implementation in `tradingagents/dataflows/akshare.py`:**

```python
def get_akshare_indicators(
    symbol: str,
    indicator: str,
    curr_date: str,
    look_back_days: int = 30
) -> str:
    """
    Calculate technical indicators for Chinese stocks using hybrid approach.

    Strategy:
    1. Fetch OHLCV data using get_akshare_stock()
    2. Calculate indicators using stockstats library
    3. Return formatted text summary with CSV data

    Args:
        symbol: Stock symbol (6-digit code or akshare format)
        indicator: Technical indicator name(s) (comma-separated for multiple)
        curr_date: Current date (YYYY-MM-DD) for determining date range
        look_back_days: Number of days to look back from curr_date (default: 30)

    Returns:
        Text summary with calculated indicators in CSV format

    Raises:
        AkshareCodeError: If stock code is invalid
        AkshareDataError: If data retrieval or calculation fails

    Example:
        >>> get_akshare_indicators("600000", "rsi,macd", "2024-01-15", 30)
        '# Technical Indicators for sh600000\\n# Date: 2024-01-15\\n...'
    """
    try:
        from tradingagents.dataflows.indicators.calculator import (
            IndicatorCalculator
        )

        logger.info(
            f"Akshare: Calculating indicators for {symbol}: {indicator}, "
            f"lookback={look_back_days} days"
        )

        # Parse indicator list
        indicator_list = IndicatorCalculator.parse_indicator_list(indicator)
        if not indicator_list:
            raise AkshareDataError("No valid indicators specified")

        logger.debug(f"Parsed indicators: {indicator_list}")

        # Calculate start date
        from datetime import datetime, timedelta
        curr_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        start_dt = curr_dt - timedelta(days=look_back_days)
        start_date = start_dt.strftime("%Y-%m-%d")

        # Step 1: Fetch OHLCV data
        logger.debug(f"Fetching stock data from {start_date} to {curr_date}")
        stock_data_csv = get_akshare_stock(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=curr_date,
            adjust="qfq"  # Use forward-adjusted prices
        )

        # Parse CSV data to DataFrame
        import io
        df = pd.read_csv(io.StringIO(stock_data_csv))

        # Remove comment lines (starting with #)
        df = df[~df['Date'].astype(str).str.startswith('#')]
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date', ascending=True)

        logger.info(f"Retrieved {len(df)} days of price data")

        # Step 2: Calculate indicators
        logger.debug("Calculating technical indicators...")
        summary_df = IndicatorCalculator.calculate(df, indicator_list)

        if summary_df.empty:
            return (
                f"# Technical Indicators for {symbol}\n"
                f"# Date: {curr_date}\n"
                f"# No indicators could be calculated\n"
                f"# Requested: {indicator}\n"
            )

        # Step 3: Format results
        result = IndicatorCalculator.format_as_text(
            symbol=symbol,
            summary_df=summary_df,
            curr_date=curr_date,
            look_back_days=look_back_days
        )

        logger.info(
            f"Akshare: Calculated {len(summary_df.columns)} indicators for {symbol}"
        )
        return result

    except AkshareCodeError:
        raise
    except Exception as e:
        logger.error(f"Akshare indicators failed for {symbol}: {e}")
        raise AkshareDataError(f"Failed to calculate indicators: {e}")
```

### 3. Error Handling Strategy

**Partial Degradation:**

```python
# If some indicators fail, return successful ones
try:
    calculated_indicators = {}
    for indicator in indicators:
        try:
            # Calculate indicator
            value = calculate_indicator(indicator, data)
            calculated_indicators[indicator] = value
        except Exception as e:
            logger.warning(f"Failed to calculate {indicator}: {e}, skipping...")
            continue

    if not calculated_indicators:
        raise AkshareDataError("All indicators failed to calculate")

    # Return partial results
    return format_results(calculated_indicators)
```

**Error Messages:**
- Invalid stock code → Clear error message with format example
- Missing data → Inform about date range and suggest alternative
- Calculation failure → Log specific indicator that failed, continue with others
- No successful indicators → Raise `AkshareDataError` with details

### 4. Dependencies

**Add to `requirements.txt`:**

```txt
stockstats>=0.5.4
```

**Installation:**

```bash
pip install stockstats
```

**Verification:**

```python
try:
    from stockstats import StockDataFrame
    logger.info("stockstats library available")
except ImportError:
    logger.warning("stockstats not installed, indicator calculation unavailable")
    raise AkshareDataError("stockstats library required for indicator calculation")
```

### 5. Testing Strategy

#### 5.1 Unit Tests

**Test File:** `tests/test_akshare_indicators.py`

```python
import pytest
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
        import pandas as pd
        import numpy as np

        # Generate 100 days of sample data
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


class TestGetAkshareIndicators:
    """Test get_akshare_indicators function."""

    @pytest.mark.integration
    def test_real_stock_indicators(self):
        """Test with real stock data (integration test)."""
        result = get_akshare_indicators(
            symbol="600000",  # Pudong Development Bank
            indicator="rsi,macd",
            curr_date="2024-01-15",
            look_back_days=30
        )

        assert isinstance(result, str)
        assert "# Technical Indicators" in result
        assert "rsi" in result.lower()
        assert "macd" in result.lower()

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
            symbol="000001",  # Ping An Bank
            indicator=indicator_str,
            curr_date="2024-01-15",
            look_back_days=200  # Enough data for 200 SMA
        )

        assert isinstance(result, str)
        # Verify at least some indicators were calculated
        assert len(result) > 0

    def test_invalid_stock_code(self):
        """Test error handling for invalid stock code."""
        with pytest.raises(Exception):  # AkshareCodeError
            get_akshare_indicators(
                symbol="invalid",
                indicator="rsi",
                curr_date="2024-01-15"
            )
```

#### 5.2 Integration Tests

**Test with market_analyst workflow:**

```python
def test_market_analyst_with_akshare():
    """Test that market_analyst can use akshare indicators."""
    from tradingagents.agents.analysts.market_analyst import create_market_analyst
    from tradingagents.dataflows.config import get_config

    # Configure to use akshare
    config = get_config()
    config['tool_vendors']['get_indicators'] = 'akshare'

    # Create analyst
    llm = config['llm']
    market_analyst = create_market_analyst(llm)

    # Test with Chinese stock
    state = {
        "trade_date": "2024-01-15",
        "company_of_interest": "600519.SH",  # Kweichow Moutai
        "messages": []
    }

    result = market_analyst(state)

    # Verify report generated
    assert result["market_report"] is not None
    assert len(result["market_report"]) > 0
```

### 6. Implementation Tasks

#### Phase 1: Infrastructure (Priority: High)
- [ ] Create `tradingagents/dataflows/indicators/` directory
- [ ] Implement `indicators/__init__.py`
- [ ] Implement `indicators/calculator.py` with `IndicatorCalculator` class
- [ ] Implement `indicators/mappings.py` with indicator name mappings
- [ ] Add `stockstats>=0.5.4` to `requirements.txt`

#### Phase 2: Core Functionality (Priority: High)
- [ ] Update `get_akshare_indicators()` function signature
- [ ] Implement data fetching via `get_akshare_stock()`
- [ ] Implement indicator calculation using stockstats
- [ ] Implement text formatting for results
- [ ] Add error handling with partial degradation

#### Phase 3: Testing (Priority: High)
- [ ] Create unit tests for `IndicatorCalculator`
- [ ] Create unit tests for `get_akshare_indicators()`
- [ ] Create integration tests with real stock data
- [ ] Test all 13 indicators used by market_analyst
- [ ] Verify parameter compatibility with `get_indicators` tool

#### Phase 4: Validation (Priority: Medium)
- [ ] Manual testing with real A-share stocks
- [ ] Verify compatibility with market_analyst prompt
- [ ] Performance testing with large datasets
- [ ] Edge case testing (missing data, invalid codes, etc.)

#### Phase 5: Documentation (Priority: Low)
- [ ] Update docstrings
- [ ] Add usage examples
- [ ] Document indicator mappings
- [ ] Update README if needed

### 7. Acceptance Criteria

The implementation is considered complete when:

1. ✅ `get_akshare_indicators()` accepts 4 parameters matching the tool interface
2. ✅ All 13 indicators used by market_analyst are supported
3. ✅ Indicators are calculated using stockstats library
4. ✅ Function returns text summary with CSV data
5. ✅ Error handling implements partial degradation (some failures OK)
6. ✅ Unit tests cover all 13 indicators
7. ✅ Integration tests pass with real stock data
8. ✅ market_analyst can successfully use akshare indicators
9. ✅ stockstats added to requirements.txt
10. ✅ No regression in existing functionality

### 8. Design Decisions

#### 8.1 Why Hybrid Strategy?

**Rationale:**
- **Flexibility**: Works regardless of akshare's built-in indicator support
- **Reliability**: stockstats is a mature, well-tested library
- **Maintainability**: Local calculation logic is easier to debug
- **Performance**: Stock data is fetched once, multiple indicators calculated

**Trade-offs:**
- ✅ Pros: Works for all indicators, no dependency on akshare updates
- ❌ Cons: Requires additional dependency (stockstats), calculation happens locally

#### 8.2 Why stockstats vs TA-Lib?

**Decision Factors:**
- **Installation**: stockstats is pure Python, no C compilation required
- **Compatibility**: Works on all platforms without build tools
- **API**: Simpler API, easier to integrate with pandas
- **Maintenance**: Active development, good documentation

**Alternatives Considered:**
- TA-Lib: More performant but harder to install (C extension)
- pandas-ta: Good but stockstats has simpler API
- Manual calculation: Too much maintenance burden

#### 8.3 Why Text Summary with CSV?

**Rationale:**
- **LLM-Friendly**: Text format is easy for LLMs to parse and understand
- **Structured**: CSV data provides structured information for analysis
- **Consistent**: Matches output format of other vendor implementations
- **Debuggable**: Easy to inspect raw data

**Format Example:**
```
# Technical Indicators for sh600000
# Date: 2024-01-15
# Lookback Period: 30 days
# Total Indicators: 3

close_50_sma,close_200_sma,rsi
10.23,9.87,55.43
```

#### 8.4 Why Partial Degradation?

**Rationale:**
- **Resilience**: One indicator failure doesn't break entire request
- **User Experience**: Returns as much useful data as possible
- **Debugging**: Logs specific failures for troubleshooting

**Example Scenario:**
- User requests: "rsi,macd,atr,custom_indicator"
- System calculates: rsi ✅, macd ✅, atr ✅, custom_indicator ❌
- Returns: Results for rsi, macd, atr with warning about custom_indicator

### 9. Risk Assessment

#### Technical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| stockstats API changes | Medium | Low | Version pin requirements.txt |
| Calculation errors | High | Medium | Comprehensive unit tests |
| Performance issues | Medium | Low | Cache OHLCV data, batch calculations |
| Data quality issues | High | Medium | Validate input data, handle missing values |

#### Operational Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Missing stockstats dependency | High | Low | Add to requirements.txt, check on import |
| Date range edge cases | Medium | Medium | Robust date parsing, validate ranges |
| A-share market specifics | Medium | Low | Test with real Chinese stocks |

### 10. Future Enhancements (Out of Scope)

- **Caching**: Cache calculated indicators to reduce redundant computations
- **Custom Indicators**: Support user-defined custom indicators
- **Multi-timeframe**: Support multiple timeframes (daily, weekly, monthly)
- **Real-time**: Support real-time indicator calculation
- **Advanced Indicators**: Add more sophisticated indicators (Fibonacci, Elliott Wave, etc.)
- **Performance Optimization**: Use numpy/pandas optimizations for faster calculation
- **Alternative Libraries**: Support ta-lib as optional faster backend

### 11. Timeline & Dependencies

**Dependencies:**
- stockstats library (to be added)
- pandas (existing)
- Existing akshare integration

**Estimated Complexity:** Medium
- Infrastructure setup: 2-3 hours
- Calculator implementation: 3-4 hours
- Integration with akshare.py: 2-3 hours
- Testing: 3-4 hours
- Documentation: 1 hour

**Total Estimated Effort:** 11-15 hours

### 12. Backward Compatibility

**Breaking Changes:**
- ✅ Function signature changes (necessary for bug fix)
- ✅ Return format changes (placeholder → actual data)

**Non-Breaking:**
- Default parameter values maintain compatibility
- Error messages are informative
- Fallback behavior preserved

**Migration Guide:**
No migration needed - this is a bug fix that implements previously missing functionality.

---

## Appendix A: Code Examples

### A.1 Usage Examples

**Single Indicator:**
```python
from tradingagents.dataflows.akshare import get_akshare_indicators

result = get_akshare_indicators(
    symbol="600000",
    indicator="rsi",
    curr_date="2024-01-15",
    look_back_days=30
)
print(result)
```

**Multiple Indicators:**
```python
result = get_akshare_indicators(
    symbol="000001",
    indicator="rsi,macd,atr,close_50_sma",
    curr_date="2024-01-15",
    look_back_days=100
)
print(result)
```

**All market_analyst Indicators:**
```python
all_indicators = (
    "close_50_sma,close_200_sma,close_10_ema,"
    "macd,macds,macdh,rsi,"
    "boll,boll_ub,boll_lb,atr,vwma"
)

result = get_akshare_indicators(
    symbol="600519",
    indicator=all_indicators,
    curr_date="2024-01-15",
    look_back_days=250  # Need 200 days for 200 SMA
)
print(result)
```

### A.2 Indicator Mappings

**Complete Mapping Table:**

| Market Analyst Name | Stockstats Name | Description | Default Period |
|---------------------|-----------------|-------------|----------------|
| close_50_sma | close_50_sma | 50-day Simple Moving Average | 50 |
| close_200_sma | close_200_sma | 200-day Simple Moving Average | 200 |
| close_10_ema | close_10_ema | 10-day Exponential Moving Average | 10 |
| macd | macd | MACD Line | 12, 26, 9 |
| macds | macds | MACD Signal Line | 12, 26, 9 |
| macdh | macdh | MACD Histogram | 12, 26, 9 |
| rsi | rsi_14 | Relative Strength Index | 14 |
| boll | boll | Bollinger Bands Middle | 20, 2 |
| boll_ub | boll_ub | Bollinger Bands Upper | 20, 2 |
| boll_lb | boll_lb | Bollinger Bands Lower | 20, 2 |
| atr | atr_14 | Average True Range | 14 |
| vwma | vwma_20 | Volume Weighted Moving Average | 20 |

---

## Document Metadata

**Version:** 1.0
**Last Updated:** 2026-01-06
**Status:** Draft Specification
**Author:** Claude (with detailed user requirements)
**Review Status:** Pending User Approval

---

**End of Specification**
