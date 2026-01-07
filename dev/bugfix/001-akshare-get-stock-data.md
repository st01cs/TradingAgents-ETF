# Bug Fix Specification: Fix Akshare get_stock_data Parameter Order

## Issue Summary

**Bug ID:** 001-akshare-get-stock-data
**Priority:** High
**Status:** Design Phase
**Affected Component:** `tradingagents/dataflows/akshare.py`

### Problem Description

When using akshare as the data vendor, calling `get_stock_data` fails with:

```
Akshare stock data failed for 601939: '2024-12-01'
FAILED: get_akshare_stock from vendor 'akshare' failed: Failed to retrieve stock data: '2024-12-01'
```

**Root Cause:**
- The `get_stock_data` tool interface has a consistent 3-parameter signature: `symbol`, `start_date`, `end_date`
- Other vendors (alpha_vantage, yfinance) follow this pattern
- `get_akshare_stock()` has 5 parameters with the order: `symbol`, `period`, `start_date`, `end_date`, `adjust`
- When `route_to_vendor()` calls `get_akshare_stock(symbol, start_date, end_date)`, the parameters are misaligned:
  - `symbol` → `symbol` ✓
  - `start_date` (e.g., "2024-12-01") → `period` ✗ **This causes the error!**
  - `end_date` → `start_date` ✗

**Current Behavior:**
- Date strings are passed to wrong parameters
- Akshare library receives invalid `period` parameter
- Function fails with date format error

---

## Solution Specification

### 1. Design Overview

**Strategy:** Adjust parameter order to match interface contract
- Reorder parameters in `get_akshare_stock()` to align with other data vendors
- Move optional parameters (`period`, `adjust`) to the end with default values
- Maintain all existing functionality while fixing the parameter misalignment

### 2. Functional Requirements

#### 2.1 Updated Function Signature

**Current (BROKEN):**
```python
def get_akshare_stock(
    symbol: str,
    period: str = "daily",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    adjust: str = "qfq"
) -> str:
```

**Fixed:**
```python
def get_akshare_stock(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "daily",
    adjust: str = "qfq"
) -> str:
    """
    Get historical stock price data from Akshare.

    Args:
        symbol: Stock symbol (6-digit code or Akshare format with prefix)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        period: Time period (daily, weekly, monthly) - default "daily"
        adjust: Adjustment type - default "qfq" (前复权)

    Returns:
        CSV-formatted string with OHLCV data

    Raises:
        AkshareCodeError: If stock code is invalid
        AkshareDataError: If data retrieval fails
    """
```

**Key Changes:**
- ✅ Parameter order: `symbol`, `start_date`, `end_date`, `period`, `adjust`
- ✅ Matches interface contract: `symbol`, `start_date`, `end_date` as first 3 parameters
- ✅ Optional parameters moved to end with default values
- ✅ Maintains backward compatibility (internal function called via `route_to_vendor`)

#### 2.2 Alignment with Other Data Vendors

**alpha_vantage:**
```python
def get_stock(symbol: str, start_date: str, end_date: str) -> str:
    # 3 parameters: symbol, start_date, end_date
```

**yfinance:**
```python
def get_YFin_data_online(symbol: str, start_date: str, end_date: str) -> str:
    # 3 parameters: symbol, start_date, end_date
```

**akshare (after fix):**
```python
def get_akshare_stock(symbol: str, start_date: str, end_date: str,
                      period: str = "daily", adjust: str = "qfq") -> str:
    # First 3 parameters match: symbol, start_date, end_date
    # Additional optional parameters at end
```

### 3. Implementation Details

#### 3.1 Modified Code

**File:** `tradingagents/dataflows/akshare.py`

**Changes:**
1. Reorder function parameters
2. Update docstring
3. Keep all existing logic intact

**Modified Function:**
```python
def get_akshare_stock(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "daily",
    adjust: str = "qfq"
) -> str:
    """
    Get historical stock price data from Akshare.

    Args:
        symbol: Stock symbol (6-digit code or Akshare format with prefix)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        period: Time period (daily, weekly, monthly) - default "daily"
        adjust: Adjustment type - default "qfq" (前复权)

    Returns:
        CSV-formatted string with OHLCV data

    Raises:
        AkshareCodeError: If stock code is invalid
        AkshareDataError: If data retrieval fails

    Example:
        >>> get_akshare_stock("000001", "2023-01-01", "2023-12-31")
        '# Stock data for sz000001 from 2023-01-01 to 2023-12-31...'
    """
    try:
        logger.info(f"Akshare: Fetching stock data for {symbol}, period={period}")

        # Convert symbol to Akshare format
        akshare_symbol = convert_to_akshare_code(symbol)
        logger.debug(f"Converted symbol: {symbol} -> {akshare_symbol}")

        # Convert date format from YYYY-MM-DD to YYYYMMDD for Akshare
        start_date_ak = start_date.replace("-", "") if start_date else "19900101"
        end_date_ak = end_date.replace("-", "") if end_date else datetime.now().strftime("%Y%m%d")

        # Fetch data from Akshare
        data = ak.stock_zh_a_hist(
            symbol=akshare_symbol,
            period=period,
            start_date=start_date_ak,
            end_date=end_date_ak,
            adjust=adjust
        )

        # ... rest of function unchanged ...
```

### 4. Testing Strategy

#### 4.1 Integration Test with Real Data

**Test Case:** Using real A-share stock code from bug report

```python
def test_real_a_share_stock_data():
    """Test with the exact scenario from bug report."""
    from tradingagents.agents.utils.core_stock_tools import get_stock_data

    # Test case from bug report
    result = get_stock_data(
        symbol="601939",  # Real A-share code
        start_date="2024-12-01",
        end_date="2025-05-10"
    )

    # Verify success
    assert isinstance(result, str)
    assert len(result) > 0
    assert "601939" in result or "sh601939" in result.lower()
    # Should contain OHLCV data
    assert any(col in result for col in ["Open", "Close", "High", "Low", "Volume"])
```

#### 4.2 Additional Test Cases

```python
def test_parameter_order_alignment():
    """Verify parameters are correctly aligned."""
    from tradingagents.dataflows.akshare import get_akshare_stock

    # Call with 3 parameters (as route_to_vendor does)
    result = get_akshare_stock(
        symbol="600000",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )

    # Should not fail
    assert isinstance(result, str)
    assert len(result) > 0

def test_with_optional_parameters():
    """Test with all parameters specified."""
    result = get_akshare_stock(
        symbol="000001",
        start_date="2024-01-01",
        end_date="2024-01-31",
        period="daily",
        adjust="qfq"
    )

    assert isinstance(result, str)

def test_different_periods():
    """Test different period parameters."""
    for period in ["daily", "weekly", "monthly"]:
        result = get_akshare_stock(
            symbol="600000",
            start_date="2024-01-01",
            end_date="2024-01-31",
            period=period
        )
        assert isinstance(result, str)
```

### 5. Implementation Tasks

- [ ] Update `get_akshare_stock()` function signature in `akshare.py`
- [ ] Update docstring to reflect new parameter order
- [ ] Verify no other code directly calls `get_akshare_stock()` with old parameter order
- [ ] Test with real A-share data (601939, 2024-12-01 to 2025-05-10)
- [ ] Verify all existing tests still pass
- [ ] Update bug report with fix details

### 6. Acceptance Criteria

The implementation is considered complete when:

1. ✅ `get_akshare_stock()` parameter order matches interface: `symbol`, `start_date`, `end_date`, `period`, `adjust`
2. ✅ Function can be called with 3 parameters: `get_akshare_stock(symbol, start_date, end_date)`
3. ✅ Original bug scenario works: `get_stock_data("601939", "2024-12-01", "2025-05-10")` succeeds
4. ✅ All existing tests pass (no regression)
5. ✅ Real A-share stock data can be retrieved successfully
6. ✅ Docstring updated to reflect new parameter order
7. ✅ Code remains clean and maintainable

### 7. Risk Assessment

#### Technical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking existing direct calls | Medium | Low | None - function is internal, only called via route_to_vendor |
| Parameter order confusion | Low | Low | Clear docstring and default values |
| Date format issues | Low | Low | Keep existing date validation logic |

#### Operational Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Vendor lock-in | Low | Low | Interface abstraction layer prevents lock-in |
| Future akshare API changes | Low | Low | Wrap akshare calls in try-except |

### 8. Design Rationale

#### 8.1 Why Parameter Order Matters

**Problem:**
- Python functions use positional arguments
- When `route_to_vendor` calls `impl_func(*args, **kwargs)`, arguments are mapped by position
- `get_akshare_stock(symbol, period, start_date, end_date, adjust)` expects period as 2nd argument
- Actual call passes `start_date` as 2nd argument → type mismatch

**Solution:**
- Move optional parameters to end
- First 3 positions match standard interface: `symbol`, `start_date`, `end_date`
- Additional parameters have default values and are optional

#### 8.2 Why This Approach

**Advantages:**
- ✅ **Minimal change**: Only reorder parameters, no logic changes
- ✅ **Interface compliance**: Matches other vendors (alpha_vantage, yfinance)
- ✅ **Backward compatible**: Function called via `route_to_vendor`, signature change invisible to callers
- ✅ **Clean code**: No wrapper functions or parameter mapping logic needed
- ✅ **Maintainable**: Clear parameter order consistent with interface

**Trade-offs:**
- None - this is a straightforward fix with no downsides

#### 8.3 Why Not Other Approaches

**Rejected: Parameter mapping wrapper**
- Adds unnecessary complexity
- Extra function call overhead
- Harder to maintain

**Rejected: Modify route_to_vendor**
- Would break other vendors
- Introduces vendor-specific logic in generic router
- Violates separation of concerns

**Rejected: Create wrapper function**
- Adds indirection
- Duplicate code
- Unclear which function to use

### 9. Future Enhancements (Out of Scope)

- Add support for more akshare-specific parameters (quote_type, ...)
- Support intraday/minutely data
- Add caching for repeated queries
- Support batch queries for multiple symbols

### 10. Timeline & Dependencies

**Dependencies:**
- None (uses existing libraries)

**Estimated Complexity:** Very Low
- Parameter reordering: 5 minutes
- Docstring update: 5 minutes
- Testing: 15 minutes
- Documentation: 5 minutes

**Total Estimated Effort:** 30 minutes

### 11. Backward Compatibility

**Impact:** None
- This is an internal function
- Only called via `route_to_vendor`
- External interface (`get_stock_data` tool) unchanged
- All calling code automatically benefits from fix

**Migration:** Not required - transparent fix

### 12. Related Issues

This fix complements the previous fix for `get_akshare_indicators` (bug 000).

---

## Document Metadata

**Version:** 1.0
**Last Updated:** 2026-01-06
**Status:** Draft Specification
**Author:** Claude (with detailed user requirements)
**Review Status:** Pending User Approval

---

**End of Specification**
