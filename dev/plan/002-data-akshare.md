# Specification: Akshare Data Vendor Integration

## Overview
Integrate Akshare as an independent data vendor for the TradingAgents dataflows system, providing Chinese stock market data (A-shares, Hong Kong stocks, etc.) while maintaining full compatibility with the existing interface architecture.

## Current State Analysis

### Existing Dataflows Architecture (`tradingagents/dataflows/interface.py`)

The system uses a vendor-agnostic routing mechanism:

```python
# Category-based vendor configuration
"data_vendors": {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "alpha_vantage",
    "news_data": "alpha_vantage"
}

# Tool-level override
"tool_vendors": {
    "get_stock_data": "akshare"  # Override category default
}
```

### Vendor Method Mapping Pattern

```python
VENDOR_METHODS = {
    "get_stock_data": {
        "alpha_vantage": get_alpha_vantage_stock,
        "yfinance": get_YFin_data_online,
        "local": get_YFin_data,
    },
    # ... other methods
}
```

### Fallback Mechanism
The system supports automatic fallback through the `route_to_vendor` function, which tries primary vendors first, then falls back to alternatives if they fail.

## Requirements

### 1. Scope of Integration

#### Data Types to Support
- ✅ **Stock Price Data (core_stock_apis)**: OHLCV historical data
- ✅ **Technical Indicators (technical_indicators)**: MACD, RSI, etc.
- ✅ **News Data (news_data)**: Chinese stock market news
- ✅ **Fundamental Data (fundamental_data)**: Financial statements and ratios

#### Market Coverage
- **Primary**: A-share market (Shanghai, Shenzhen, Beijing)
- **Extended**: Hong Kong stocks, US stocks (Chinese focus)
- **Approach**: Full market coverage via Akshare's comprehensive interfaces

### 2. Implementation Strategy

#### Architecture Approach
- **Independent Vendor**: Create `tradingagents/dataflows/akshare.py` module
- **Pattern**: Follow the same structure as `yfinance.py` and `alpha_vantage.py`
- **Integration**: Add to `VENDOR_METHODS` mapping in `interface.py`

#### Configuration Priority
Akshare should be configurable as the preferred vendor for:
```python
"data_vendors": {
    "core_stock_apis": "akshare",        # Primary for stock data
    "technical_indicators": "akshare",    # Primary for indicators
    "fundamental_data": "akshare",        # Primary for fundamentals
    "news_data": "akshare"                # Primary for news
}
```

### 3. Technical Requirements

#### Stock Code Conversion

**Problem**: Akshare uses specific format (e.g., "sh000001", "sz000001") while existing system may use different formats.

**Solution**: Prefix-based recognition and conversion
```python
def convert_to_akshare_code(symbol: str) -> str:
    """
    Convert stock symbol to Akshare format.

    Rules:
    - 6xxxxx → shXXXXXX (Shanghai)
    - 0xxxxx, 3xxxxx → szXXXXXX (Shenzhen)
    - 8xxxxx, 4xxxxx → bjXXXXXX (Beijing)
    - Already has prefix → return as-is
    """
    if len(symbol) == 6 and symbol.isdigit():
        if symbol.startswith('6'):
            return f"sh{symbol}"
        elif symbol.startswith(('0', '3')):
            return f"sz{symbol}"
        elif symbol.startswith(('8', '4')):
            return f"bj{symbol}"
    return symbol
```

#### Data Format Compatibility

**Requirement**: Strict compatibility with existing vendor return formats

**Key Fields**:
- ✅ **OHLCV**: Open, High, Low, Close, Volume (must match exactly)
- ✅ **Adjusted Prices**: QFQ (forward-adjusted), HFQ (backward-adjusted)
- ✅ **Technical Indicators**: MA, MACD, RSI, etc. (standard format)
- ✅ **Flexible Fields**: Additional metadata allowed (e.g., Chinese names)

**Implementation**:
```python
# Return format should match existing vendors
{
    "date": [...],
    "open": [...],
    "high": [...],
    "low": [...],
    "close": [...],
    "volume": [...],
    "adj_factor": [...],  # For adjusted prices
    # Optional Chinese fields
    "name": "股票名称",
    "symbol": "sh000001"
}
```

#### Technical Indicators Strategy

**Hybrid Approach**:
1. **Primary**: Try Akshare's built-in indicator interfaces
2. **Fallback**: Calculate using existing `stockstats_utils` if Akshare fails

```python
def get_akshare_indicators(symbol, period, indicator_names):
    try:
        # Try Akshare first
        return _get_akshare_native_indicators(symbol, indicator_names)
    except Exception:
        # Fallback to stockstats calculation
        stock_data = get_akshare_stock(symbol, period)
        return calculate_indicators_with_stockstats(stock_data, indicator_names)
```

#### News Data Aggregation

**Multi-Source Strategy**:
- Primary: East Money (东方财富)
- Secondary: Sina Finance (新浪财经)
- Tertiary: Xueqiu (雪球)

Return aggregated news from all sources:

```python
def get_akshare_news(symbol, start_date, end_date):
    sources = [
        get_eastmoney_news,
        get_sina_news,
        get_xueqiu_news
    ]
    all_news = []
    for source in sources:
        try:
            all_news.extend(source(symbol, start_date, end_date))
        except Exception:
            continue
    return aggregate_news(all_news)
```

#### Fundamental Data Strategy

Akshare provides comprehensive financial statement data for Chinese stocks through multiple interfaces:

**Data Coverage**:
1. **Balance Sheet (资产负债表)**
   - `ak.stock_balance_sheet_by_yearly_em(symbol)` - Annual data
   - `ak.stock_balance_sheet_by_quarterly_em(symbol)` - Quarterly data

2. **Income Statement (利润表)**
   - `ak.stock_profit_sheet_by_yearly_em(symbol)` - Annual data
   - `ak.stock_profit_sheet_by_quarterly_em(symbol)` - Quarterly data

3. **Cash Flow Statement (现金流量表)**
   - `ak.stock_cash_flow_sheet_by_yearly_em(symbol)` - Annual data
   - `ak.stock_cash_flow_sheet_by_quarterly_em(symbol)` - Quarterly data

4. **Financial Indicators (财务指标)**
   - `ak.stock_financial_abstract(symbol)` - Financial summary
   - `ak.stock_financial_analysis_indicator(symbol)` - Financial analysis indicators
   - `ak.stock_individual_info_em(symbol)` - Company basic information

**Implementation Approach**:
```python
def get_akshare_fundamentals(symbol: str, curr_date: str = None):
    """
    Get comprehensive fundamental analysis for a Chinese stock.

    Args:
        symbol: Stock code (6-digit or Akshare format)
        curr_date: Current date for reference

    Returns:
        str: Text summary including:
            - Company overview (name, industry, market cap)
            - Key financial ratios (PE, PB, ROE, etc.)
            - Recent financial highlights
    """
    akshare_symbol = convert_to_akshare_code(symbol)

    # Get company info
    company_info = ak.stock_individual_info_em(symbol=akshare_symbol)

    # Get financial indicators
    indicators = ak.stock_financial_analysis_indicator(symbol=akshare_symbol)

    # Get financial summary
    summary = ak.stock_financial_abstract(symbol=akshare_symbol)

    # Format as text summary
    return format_fundamentals_as_text(company_info, indicators, summary)


def get_akshare_balance_sheet(symbol: str, freq: str = "quarterly", curr_date: str = None):
    """Get balance sheet data from Akshare."""
    akshare_symbol = convert_to_akshare_code(symbol)

    if freq == "annual":
        data = ak.stock_balance_sheet_by_yearly_em(symbol=akshare_symbol)
    else:  # quarterly (default)
        data = ak.stock_balance_sheet_by_quarterly_em(symbol=akshare_symbol)

    return format_balance_sheet_as_text(data)


def get_akshare_cashflow(symbol: str, freq: str = "quarterly", curr_date: str = None):
    """Get cash flow statement data from Akshare."""
    akshare_symbol = convert_to_akshare_code(symbol)

    if freq == "annual":
        data = ak.stock_cash_flow_sheet_by_yearly_em(symbol=akshare_symbol)
    else:  # quarterly (default)
        data = ak.stock_cash_flow_sheet_by_quarterly_em(symbol=akshare_symbol)

    return format_cashflow_as_text(data)


def get_akshare_income_statement(symbol: str, freq: str = "quarterly", curr_date: str = None):
    """Get income statement data from Akshare."""
    akshare_symbol = convert_to_akshare_code(symbol)

    if freq == "annual":
        data = ak.stock_profit_sheet_by_yearly_em(symbol=akshare_symbol)
    else:  # quarterly (default)
        data = ak.stock_profit_sheet_by_quarterly_em(symbol=akshare_symbol)

    return format_income_statement_as_text(data)
```

**Key Financial Fields Available**:
- **Balance Sheet**: Total Assets, Total Liabilities, Shareholder Equity, Current Assets, Current Liabilities
- **Income Statement**: Total Revenue, Net Profit, Operating Income, EPS
- **Cash Flow**: Operating Cash Flow, Investing Cash Flow, Financing Cash Flow
- **Ratios**: PE Ratio, PB Ratio, ROE, Debt Ratio, Current Ratio
- **Market Data**: Market Cap, PE (TTM), PB, Dividend Yield

**Compatibility Note**: Akshare's Chinese financial terms (e.g., "总资产", "净利润") will be preserved in the data, with optional English translations provided in the text summary.

### 4. Error Handling

#### Custom Exception Hierarchy

```python
class AkshareError(Exception):
    """Base exception for Akshare-related errors"""
    pass

class AkshareDataError(AkshareError):
    """Data retrieval or parsing error"""
    pass

class AkshareRateLimitError(AkshareError):
    """API rate limit exceeded (similar to AlphaVantageRateLimitError)"""
    pass

class AkshareCodeError(AkshareError):
    """Invalid stock code or code conversion error"""
    pass
```

#### Error Handling Strategy

```python
def get_akshare_stock(symbol: str, period: str, **kwargs):
    try:
        akshare_symbol = convert_to_akshare_code(symbol)
        # ... call Akshare API
    except ValueError as e:
        raise AkshareCodeError(f"Invalid code '{symbol}': {e}")
    except Exception as e:
        logger.error(f"Akshare stock data failed for {symbol}: {e}")
        raise AkshareDataError(f"Failed to retrieve stock data: {e}")
```

**Integration with Fallback**:
- Custom exceptions propagate to `route_to_vendor`
- Fallback mechanism automatically tries next vendor

### 5. API Rate Limiting

**Strategy**: Logging-based monitoring (no automatic throttling)

```python
import logging
logger = logging.getLogger(__name__)

def get_akshare_stock(symbol: str, period: str, **kwargs):
    logger.info(f"Akshare: Fetching stock data for {symbol}, period={period}")
    try:
        result = ak.stock_zh_a_hist(symbol=akshare_symbol, ...)
        logger.debug(f"Akshare: Retrieved {len(result)} records for {symbol}")
        return result
    except Exception as e:
        logger.warning(f"Akshare request failed: {e}")
        raise
```

**Note**: Akshare is a web scraping library with relatively lenient limits compared to official APIs. Manual monitoring through logs should be sufficient for initial implementation.

### 6. Data Caching

**Strategy**: Reuse existing caching mechanism

The system already has `data_cache_dir` in `DEFAULT_CONFIG`:
```python
"data_cache_dir": os.path.join(..., "dataflows/data_cache")
```

**Implementation**:
- Check cache before making Akshare requests
- Store results in cache after successful retrieval
- Use existing caching utilities if available
- Otherwise, implement simple file-based caching

```python
def get_akshare_stock_cached(symbol: str, period: str, **kwargs):
    cache_key = f"akshare_stock_{symbol}_{period}"
    cached = load_from_cache(cache_key)
    if cached is not None:
        return cached

    result = get_akshare_stock(symbol, period, **kwargs)
    save_to_cache(cache_key, result)
    return result
```

### 7. Chinese Language Handling

**Strategy**: Preserve Chinese characters

**Rationale**:
- Akshare data includes Chinese column names and stock names
- Translation may lose information or introduce errors
- Upper layers can handle translation if needed

**Implementation**:
```python
# Preserve Chinese fields
{
    "open": [...],
    "high": [...],
    # ...
    "name": "平安银行",        # Chinese name preserved
    "symbol": "sz000001"
}
```

**Optional**: Provide English aliases for commonly used fields
```python
{
    "name": "平安银行",
    "name_en": "Ping An Bank",  # Optional translation
}
```

### 8. Dependency Management

**Strategy**: Add to core dependencies

**File**: `requirements.txt` or `pyproject.toml`

```txt
# Add to requirements.txt
akshare>=1.14.0
```

**Rationale**:
- Akshare is a core vendor for Chinese market data
- Users should not need to manually install it
- Version pinning ensures stability

### 9. Testing Strategy

#### Scope: Basic Functionality Tests

**Test File**: `tests/test_akshare_vendor.py`

**Test Cases**:
1. **Import Test**: Verify Akshare can be imported
2. **Code Conversion**: Test stock code conversion logic
3. **API Smoke Test**: Simple data fetch for known symbol
4. **Format Validation**: Verify return format matches expected structure

```python
def test_akshare_import():
    """Test that Akshare can be imported"""
    import akshare as ak
    assert ak is not None

def test_stock_code_conversion():
    """Test stock code conversion to Akshare format"""
    from tradingagents.dataflows.akshare import convert_to_akshare_code
    assert convert_to_akshare_code("600000") == "sh600000"
    assert convert_to_akshare_code("000001") == "sz000001"
    assert convert_to_akshare_code("sh600000") == "sh600000"

def test_akshare_stock_data_smoke():
    """Test basic stock data retrieval"""
    from tradingagents.dataflows.akshare import get_akshare_stock
    result = get_akshare_stock("000001", period="1year", start_date="2023-01-01")
    assert result is not None
    assert "close" in result
    assert len(result["close"]) > 0

def test_akshare_format_compatibility():
    """Test that return format is compatible"""
    from tradingagents.dataflows.akshare import get_akshare_stock
    result = get_akshare_stock("000001", period="1month")
    # Check required OHLCV fields exist
    required_fields = ["open", "high", "low", "close", "volume"]
    for field in required_fields:
        assert field in result
```

**Note**: Full integration tests (fallback mechanism) can be added later if needed.

### 10. Documentation

#### README Updates

Add section: "Using Akshare for Chinese Stock Data"

```markdown
### Akshare Configuration

Akshare provides comprehensive data for Chinese stock markets (A-shares, Hong Kong, etc.).

#### Installation

Akshare is included in requirements.txt:
```bash
pip install -r requirements.txt
```

#### Configuration

Set Akshare as the preferred vendor:

```python
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["data_vendors"] = {
    "core_stock_apis": "akshare",        # Use Akshare for stock prices
    "technical_indicators": "akshare",    # Use Akshare for indicators
    "news_data": "akshare"                # Use Akshare for news
}

# Override specific tools
config["tool_vendors"] = {
    "get_stock_data": "akshare"
}
```

#### Stock Code Format

Akshare uses market prefixes:
- Shanghai: `sh` + 6-digit code (e.g., `sh600000`)
- Shenzhen: `sz` + 6-digit code (e.g., `sz000001`)
- Beijing: `bj` + 6-digit code (e.g., `bj832566`)

The system auto-converts 6-digit codes to Akshare format:
- Input: `600000` → Converted to: `sh600000`
- Input: `000001` → Converted to: `sz000001`
```

#### Code Documentation

Add docstrings to all functions:
```python
def get_akshare_stock(symbol: str, period: str, start_date: str = None, end_date: str = None):
    """
    Get historical stock price data from Akshare.

    Args:
        symbol: Stock symbol (6-digit code or Akshare format with prefix)
        period: Time period (e.g., "daily", "weekly", "monthly")
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        Dictionary with OHLCV data and adjusted prices

    Raises:
        AkshareCodeError: If stock code is invalid
        AkshareDataError: If data retrieval fails

    Example:
        >>> get_akshare_stock("000001", "daily", "2023-01-01", "2023-12-31")
        {
            "date": ["2023-01-01", ...],
            "open": [10.5, ...],
            "high": [10.8, ...],
            "low": [10.4, ...],
            "close": [10.7, ...],
            "volume": [1000000, ...],
            "name": "平安银行"
        }
    """
```

### 11. Non-Requirements

Explicitly **NOT** included in initial implementation:
- ❌ Real-time streaming data (only historical data)
- ❌ Real-time news (only historical news)
- ❌ Chinese-specific features (北向资金, 龙虎榜, 股东数据)
- ❌ Automatic rate limiting/throttling
- ❌ Data translation (Chinese → English)
- ❌ Advanced caching strategies
- ❌ WebSocket or streaming APIs
- ❌ Futures, options, or derivatives data
- ❌ Fund market data

These can be added in future iterations if needed.

## Implementation Plan

### Phase 1: Setup and Infrastructure

1. **Add Dependency**
   - Add `akshare>=1.14.0` to `requirements.txt`

2. **Create Module Structure**
   - Create `tradingagents/dataflows/akshare.py`
   - Implement code conversion utility
   - Define custom exception classes

3. **Update Interface**
   - Add `"akshare"` to `VENDOR_LIST` in `interface.py`
   - Add method mappings to `VENDOR_METHODS`

### Phase 2: Core Data Interfaces

1. **Stock Price Data**
   ```python
   def get_akshare_stock(symbol, period, start_date=None, end_date=None)
   ```

2. **Technical Indicators**
   ```python
   def get_akshare_indicators(symbol, period, indicator_names)
   ```

3. **News Data**
   ```python
   def get_akshare_news(symbol, start_date, end_date)
   def get_akshare_global_news(start_date, end_date)
   ```

4. **Fundamental Data**
   ```python
   def get_akshare_fundamentals(symbol, curr_date=None)
   def get_akshare_balance_sheet(symbol, freq="quarterly", curr_date=None)
   def get_akshare_cashflow(symbol, freq="quarterly", curr_date=None)
   def get_akshare_income_statement(symbol, freq="quarterly", curr_date=None)
   ```

### Phase 3: Data Processing

1. **Format Standardization**
   - Ensure OHLCV fields match existing format
   - Handle adjusted prices
   - Preserve Chinese metadata

2. **Error Handling**
   - Implement custom exceptions
   - Add comprehensive logging
   - Test fallback integration

3. **Caching Layer**
   - Implement cache checking
   - Implement cache storage
   - Test cache invalidation

### Phase 4: Testing and Documentation

1. **Unit Tests**
   - Code conversion tests
   - Format validation tests
   - Error handling tests

2. **Integration Tests**
   - Fallback mechanism tests
   - Multi-vendor configuration tests

3. **Documentation**
   - Update README with Akshare section
   - Add docstrings to all functions
   - Provide configuration examples

### Phase 5: Validation

1. **Manual Testing**
   - Test with real A-share symbols
   - Verify data accuracy
   - Check performance

2. **Configuration Examples**
   - Default config with Akshare
   - Hybrid config (Akshare + other vendors)
   - Tool-specific overrides

## File Structure

```
tradingagents/
├── dataflows/
│   ├── __init__.py
│   ├── interface.py           # Update: Add akshare to VENDOR_LIST and mappings
│   ├── akshare.py             # New: Main Akshare implementation
│   └── akshare_utils.py       # Optional: Utility functions
│
tests/
└── test_akshare_vendor.py     # New: Akshare tests

requirements.txt               # Update: Add akshare dependency
README.md                      # Update: Add Akshare documentation
```

## Code Examples

### Example 1: Basic Usage

```python
from tradingagents.dataflows.interface import route_to_vendor

# Use Akshare for stock data (configured as primary)
stock_data = route_to_vendor(
    "get_stock_data",
    symbol="000001",  # Will be converted to "sz000001"
    period="daily",
    start_date="2023-01-01",
    end_date="2023-12-31"
)
```

### Example 2: Configuration

```python
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["data_vendors"] = {
    "core_stock_apis": "akshare",
    "technical_indicators": "akshare",
    "news_data": "akshare"
}

# Initialize TradingAgentsGraph with Akshare
from tradingagents.graph.trading_graph import TradingAgentsGraph
ta = TradingAgentsGraph(debug=True, config=config)
```

### Example 3: Hybrid Configuration

```python
config["data_vendors"] = {
    "core_stock_apis": "akshare, yfinance",  # Try Akshare first, fallback to yfinance
    "news_data": "alpha_vantage, akshare"     # Try Alpha Vantage first, fallback to Akshare
}
```

## Success Criteria

1. ✅ Akshare can be configured as a data vendor
2. ✅ Stock data retrieval works for A-share symbols
3. ✅ Return format is compatible with existing vendors
4. ✅ Fallback mechanism works with Akshare
5. ✅ Stock code conversion handles all A-share patterns
6. ✅ News data aggregation works from multiple sources
7. ✅ Technical indicators use hybrid approach
8. ✅ **Fundamental data retrieval works for all three financial statements**
9. ✅ **Financial indicators and ratios are correctly formatted**
10. ✅ All unit tests pass
11. ✅ README documentation is complete
12. ✅ Manual testing with real symbols succeeds

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Akshare API changes | High | Version pin dependencies, monitor for breaking changes |
| Web scraping blocked | Medium | Provide fallback to other vendors, clear error messages |
| Data format inconsistency | Medium | Strict validation, comprehensive tests |
| Rate limiting/performance | Low | Logging for monitoring, caching to reduce requests |
| Chinese character encoding | Low | Preserve UTF-8, document encoding handling |

## Future Considerations

Out of scope for initial implementation but may be considered later:
1. Real-time data support
2. Advanced Chinese market features (北向资金, 龙虎榜)
3. Futures and options data
4. Fund market data
5. Bond market data
6. Automatic data translation
7. Performance optimizations
8. Advanced caching strategies
9. WebSocket support
10. Custom indicator calculations

## References

- Akshare Documentation: https://akshare.akfamily.xyz/
- Akshare GitHub: https://github.com/akfamily/akshare
- Existing Vendor Implementations:
  - `tradingagents/dataflows/yfinance.py`
  - `tradingagents/dataflows/alpha_vantage.py`
- Dataflows Interface: `tradingagents/dataflows/interface.py`

## Appendix

### Akshare Interface Reference

#### Stock Price Data
```python
import akshare as ak

# Individual stock historical data (A-share)
ak.stock_zh_a_hist(
    symbol="000001",      # Stock code
    period="daily",       # daily, weekly, monthly
    start_date="20230101",
    end_date="20231231",
    adjust="qfq"          # qfq (前复权), hfq (后复权), "" (不复权)
)

# Hong Kong stock
ak.stock_hk_hist()

# US stock
ak.stock_us_hist()
```

#### Technical Indicators
```python
# Some indicators available through specialized interfaces
ak.stock_zh_a_spot_em()  # Real-time quotes with some indicators
```

#### News Data
```python
# East Money news
ak.stock_news_em(symbol="000001")

# Sina Finance news
ak.stock_news_sina()

# Xueqiu news
# (May need custom implementation or web scraping)
```

#### Fundamental Data
```python
# Company Information
ak.stock_individual_info_em(symbol="000001")
# Returns: Company name, industry, listing date, market cap, etc.

# Balance Sheet (资产负债表)
ak.stock_balance_sheet_by_yearly_em(symbol="000001")   # Annual
ak.stock_balance_sheet_by_quarterly_em(symbol="000001") # Quarterly

# Income Statement (利润表)
ak.stock_profit_sheet_by_yearly_em(symbol="000001")   # Annual
ak.stock_profit_sheet_by_quarterly_em(symbol="000001") # Quarterly

# Cash Flow Statement (现金流量表)
ak.stock_cash_flow_sheet_by_yearly_em(symbol="000001")   # Annual
ak.stock_cash_flow_sheet_by_quarterly_em(symbol="000001") # Quarterly

# Financial Indicators (财务指标)
ak.stock_financial_analysis_indicator(symbol="000001")
# Returns: PE, PB, ROE, debt ratio, current ratio, etc.

# Financial Summary (财务摘要)
ak.stock_financial_abstract(symbol="000001")
# Returns: Key financial metrics and ratios summary

# Additional interfaces
ak.stock_profit_data_by_report_em(symbol="000001")  # Profitability data
ak.stock_operation_data_by_report_em(symbol="000001")  # Operational data
ak.stock_growth_data_by_report_em(symbol="000001")  # Growth data
ak.stock_debt_to_assetsby_yearly_em(symbol="000001")  # Debt ratios
```

### Stock Code Mapping

| Market | Prefix | Code Range | Example |
|--------|--------|------------|---------|
| Shanghai (沪市) | sh | 600xxx, 601xxx, 603xxx, 605xxx | sh600000 |
| Shenzhen (深市) | sz | 000xxx, 001xxx, 002xxx, 003xxx | sz000001 |
| Beijing (京市) | bj | 8xxxxx, 4xxxxx | bj832566 |
| Hong Kong | hk | 4-digit code | hk00700 |
| US | us | Symbol | usAAPL |
