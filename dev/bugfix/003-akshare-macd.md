# Bug Fix Spec: Akshare get_indicators MACD CSV Parsing Error

## Problem Summary

When calling `get_indicators` with symbol `601939` for indicator `macd`, the function fails with a CSV parsing error:

```
Akshare indicators failed for 601939: Error tokenizing data. C error: Expected 1 fields in line 6, saw 13

FAILED: get_akshare_indicators from vendor 'akshare' failed: Failed to calculate indicators: Error tokenizing data. C error: Expected 1 fields in line 6, saw 13
```

**Parameters**:
- symbol: `601939`
- indicator: `macd`
- curr_date: `2025-05-10`
- look_back_days: `30`

**Context**: Other indicators (RSI, Bollinger Bands, etc.) work correctly.

## Root Cause Analysis

### Technical Details

1. **CSV Format Issue**: `get_akshare_stock()` returns CSV data with header comments:
   ```csv
   # Stock data for 601939 from 2025-04-10 to 2025-05-10
   # Total records: 19
   # Adjustment: qfq
   # Data retrieved on: 2026-01-07 11:28:19

   ,Date,股票代码,Open,Close,High,Low,Volume,Amount,Amplitude,ChangePct,ChangeAmount,Turnover
   0,2025-04-10,601939,8.43,8.35,8.43,8.31,1250340,1090796889.0,1.43,-0.71,-0.06,1.3
   ...
   ```

2. **Parsing Failure**: In `get_akshare_indicators()`:
   ```python
   df = pd.read_csv(io.StringIO(stock_data_csv))  # Line 301
   ```
   This line fails because:
   - Lines 1-4 are comment lines (starting with `#`)
   - Line 5 is empty
   - Line 6 is the CSV header
   - pandas CSV parser encounters line 6 with 13 fields but expected only 1 field based on earlier lines

3. **Existing Workaround Attempt**: Code at line 304 tries to filter comments:
   ```python
   df = df[~df['Date'].astype(str).str.startswith('#')]
   ```
   But this never executes because the `pd.read_csv()` call fails first.

4. **Why Other Indicators Work**: The bug report states other indicators work correctly. This suggests:
   - Either they were tested with different data/format
   - Or there's a data-specific issue with MACD date range

### Verification

```python
# Test shows CSV format:
# Stock data for 601939 from 2025-04-10 to 2025-05-10
# Total records: 19
# Adjustment: qfq
# Data retrieved on: 2026-01-07 11:28:19

,Date,股票代码,Open,Close,High,Low,Volume,Amount,Amplitude,ChangePct,ChangeAmount,Turnover
0,2025-04-10,601939,8.43,8.35,8.43,8.31,1250340,...
```

## Solution Design

### Strategy

Use pandas `read_csv()` built-in `comment` parameter to handle comment lines during parsing, eliminating the need for manual filtering.

### Implementation

**Location**: `tradingagents/dataflows/akshare.py`, line 301

**Current Code**:
```python
df = pd.read_csv(io.StringIO(stock_data_csv))

# Remove comment lines (starting with #)
df = df[~df['Date'].astype(str).str.startswith('#')]
```

**Fixed Code**:
```python
# Parse CSV data to DataFrame
# Note: get_akshare_stock() returns CSV with comment lines starting with '#'
# Use comment parameter to automatically skip these lines during parsing
df = pd.read_csv(io.StringIO(stock_data_csv), comment='#')

# Remove comment lines (starting with #) - now redundant but kept for safety
df = df[~df['Date'].astype(str).str.startswith('#')]
```

### Benefits

1. **Simple**: Single parameter addition, no complex logic
2. **Robust**: Uses pandas built-in functionality designed for this purpose
3. **Backward Compatible**: `comment='#'` parameter is standard, doesn't affect other callers
4. **Performance**: Negligible performance impact
5. **Safe**: Keeps existing filtering as fallback

## Implementation Details

### Error Handling

Add try-except wrapper around CSV parsing to provide clearer error messages:

```python
try:
    # Parse CSV data to DataFrame
    # Note: get_akshare_stock() returns CSV with comment lines starting with '#'
    # Use comment parameter to automatically skip these lines during parsing
    df = pd.read_csv(io.StringIO(stock_data_csv), comment='#')

    # Remove comment lines (starting with #) - now redundant but kept for safety
    df = df[~df['Date'].astype(str).str.startswith('#')]
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date', ascending=True)

except pd.errors.ParserError as e:
    raise AkshareDataError(
        f"Failed to parse stock data CSV. "
        f"The CSV format may be invalid. Error: {e}"
    )
except Exception as e:
    raise AkshareDataError(f"Failed to parse stock data: {e}")
```

### Documentation Update

Update docstring of `get_akshare_indicators()`:

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
       - Returns CSV with metadata comments (lines starting with '#')
    2. Parse CSV with pandas (comment='#' to skip metadata)
    3. Calculate indicators using stockstats library
    4. Return formatted text summary with CSV data

    Args:
        symbol: Stock symbol (6-digit code or akshare format)
        indicator: Technical indicator name(s) (comma-separated for multiple)
        curr_date: Current date (YYYY-MM-DD) for determining date range
        look_back_days: Number of days to look back from curr_date (default: 30)

    Returns:
        Text summary with calculated indicators in CSV format

    Raises:
        AkshareCodeError: If stock code is invalid
        AkshareDataError: If data retrieval or parsing fails

    Example:
        >>> get_akshare_indicators("600000", "rsi,macd", "2024-01-15", 30)
        '# Technical Indicators for sh600000\\n# Date: 2024-01-15\\n...'
    """
```

## Testing Strategy

### Unit Tests

**File**: `tests/test_akshare_indicators.py` (extend existing)

**Test Case 1: CSV Parsing with Comments**
```python
def test_parse_csv_with_comment_lines():
    """Test that CSV with comment lines is parsed correctly."""
    from tradingagents.dataflows.akshare import get_akshare_indicators
    import io
    import pandas as pd

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
```

**Test Case 2: CSV Parsing without Comments**
```python
def test_parse_csv_without_comment_lines():
    """Test that CSV without comment lines still works."""
    import io
    import pandas as pd

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
```

**Test Case 3: Empty CSV**
```python
def test_parse_csv_empty_data():
    """Test handling of empty CSV."""
    import io
    import pandas as pd
    from tradingagents.dataflows.akshare import AkshareDataError

    # Mock CSV with only comments
    mock_csv = """# Stock data for 601939
# No data available
"""

    # Parse with comment parameter
    df = pd.read_csv(io.StringIO(mock_csv), comment='#')

    # Should result in empty DataFrame
    assert len(df) == 0
```

### Integration Test

**Test Case 4: Original Bug Scenario**
```python
@pytest.mark.integration
def test_get_akshare_indicators_macd_original_bug():
    """Test the exact scenario from bug report #003."""
    from tradingagents.dataflows.akshare import get_akshare_indicators

    # Use exact parameters from bug report
    result = get_akshare_indicators(
        symbol="601939",
        indicator="macd",
        curr_date="2025-05-10",
        look_back_days=30
    )

    # Should not raise parsing error
    assert isinstance(result, str)
    assert "Technical Indicators" in result or "MACD" in result.upper()
```

**Test Case 5: Other Indicators Still Work**
```python
@pytest.mark.integration
def test_get_akshare_indicators_other_indicators():
    """Verify other indicators (RSI, Bollinger Bands) still work."""
    from tradingagents.dataflows.akshare import get_akshare_indicators

    # Test RSI
    result_rsi = get_akshare_indicators(
        symbol="601939",
        indicator="rsi",
        curr_date="2025-05-10",
        look_back_days=30
    )
    assert isinstance(result_rsi, str)

    # Test Bollinger Bands
    result_bb = get_akshare_indicators(
        symbol="601939",
        indicator="bollinger",
        curr_date="2025-05-10",
        look_back_days=30
    )
    assert isinstance(result_bb, str)
```

## Implementation Steps

### Phase 1: Core Fix

1. **Modify `tradingagents/dataflows/akshare.py`**
   - Line 301: Add `comment='#'` parameter to `pd.read_csv()`
   - Add inline comment explaining the fix
   - Keep existing comment filtering as safety measure
   - Add try-except wrapper for clearer error messages

2. **Update `get_akshare_indicators()` docstring**
   - Document that CSV contains comment lines
   - Explain parsing strategy

### Phase 2: Testing

3. **Add unit tests**
   - `test_parse_csv_with_comment_lines()` - Test parsing with comments
   - `test_parse_csv_without_comment_lines()` - Test backward compatibility
   - `test_parse_csv_empty_data()` - Test empty data handling

4. **Add integration test**
   - `test_get_akshare_indicators_macd_original_bug()` - Verify bug fix
   - `test_get_akshare_indicators_other_indicators()` - Regression test

5. **Run test suite**
   ```bash
   pytest tests/test_akshare_indicators.py -v
   pytest tests/test_akshare*.py -v
   ```

### Phase 3: Verification

6. **Manual verification**
   ```python
   # Test with original bug parameters
   get_akshare_indicators("601939", "macd", "2025-05-10", 30)
   ```

7. **Run all indicator tests**
   ```bash
   pytest tests/ -k "indicator" -v
   ```

8. **Run full akshare test suite**
   ```bash
   pytest tests/test_akshare*.py -v
   ```

### Phase 4: Code Review

9. **Create pull request**
    - Summarize the fix (single parameter addition)
    - Reference bug report #003
    - Highlight test coverage

10. **Code review checklist**
    - Fix is minimal and focused
    - Error messages are clear
    - Tests cover bug scenario and edge cases
    - Documentation is updated
    - No regressions in other indicators

## Risk Assessment

### Low Risk

**Reasoning**:
- Change is minimal (one parameter addition)
- `comment='#'` is standard pandas functionality
- Backward compatible (works with and without comments)
- Existing filtering code kept as safety net
- Comprehensive test coverage

**Mitigation**:
- Unit tests verify CSV parsing behavior
- Integration tests verify actual indicator calculation
- Regression tests ensure other indicators work
- Manual verification with original bug scenario

## Related Issues

### Context

- Bug #002: Fixed `get_stock_data` code format mismatch
- Current bug #003: CSV parsing issue in `get_indicators`
- Both issues related to Akshare integration but different root causes

### Other Indicators

Bug report states other indicators work correctly. This suggests:
- Issue may be data-specific to MACD date range
- Or other indicators haven't been tested with recent data
- **Action**: Verify other indicators (RSI, Bollinger Bands) in testing

## Success Criteria

1. ✅ Original bug scenario (MACD with symbol 601939) works without error
2. ✅ Unit tests for CSV parsing pass
3. ✅ Integration test for MACD passes
4. ✅ Other indicator tests still pass (no regression)
5. ✅ Full akshare test suite passes
6. ✅ Error messages are clear and helpful
7. ✅ Code review approved

## Implementation Notes

### Why Not Alternative Approaches

**Alternative 1: Pre-process CSV string**
```python
# Remove comment lines before parsing
lines = [l for l in stock_data_csv.split('\n') if not l.startswith('#')]
clean_csv = '\n'.join(lines)
df = pd.read_csv(io.StringIO(clean_csv))
```
**Rejected**: More complex, error-prone, reinvents pandas functionality

**Alternative 2: Remove comments from get_akshare_stock()**
```python
# Don't include comments in CSV output
csv_string = data.to_csv()  # No header
return csv_string
```
**Rejected**: Breaks backward compatibility, affects other callers

**Alternative 3: Use different CSV format**
```python
# Return JSON instead of CSV
return data.to_json()
```
**Rejected**: Major refactor, outside scope of bug fix

**Chosen Approach**: `comment='#'` parameter
- Simple (one parameter)
- Standard pandas feature
- Backward compatible
- No side effects

## Future Considerations

1. **Standardize CSV Format**: Consider whether `get_akshare_stock()` should always return metadata-free CSV
2. **Error Handling**: Consider adding more robust CSV validation for all data vendors
3. **Testing**: Add more comprehensive integration tests for all indicators
4. **Documentation**: Document expected CSV formats in data vendor interface

## References

- Original bug report: `dev/bugfix/003-akshare-macd.md`
- Related bug fix: `dev/bugfix/002-akshare-no-data-found.md`
- Implementation file: `tradingagents/dataflows/akshare.py`
- Test file: `tests/test_akshare_indicators.py`
- Pandas CSV documentation: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
