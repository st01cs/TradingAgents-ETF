# Bug Fix Spec: Akshare get_stock_data Returns No Data

## Problem Summary

When calling `get_stock_data` with symbol `601939` (China Construction Bank) for date range `2025-03-10` to `2025-05-10`, the Akshare vendor reports success but returns no data:

```
DEBUG: get_stock_data - Primary: [akshare]
DEBUG: Attempting PRIMARY vendor 'akshare'
SUCCESS: get_akshare_stock from vendor 'akshare' completed successfully
SUCCESS: Vendor 'akshare' succeeded - Got 1 result(s)

Result: "No data found for symbol '601939' between 2025-03-10 and 2025-05-10"
```

## Root Cause Analysis

### Technical Details

1. **Code Format Mismatch**: The `convert_to_akshare_code()` function adds market prefixes (e.g., `sh`, `sz`) to 6-digit stock codes:
   - Input: `601939` → Converts to: `sh601939`

2. **API Inconsistency**: Different Akshare APIs have conflicting requirements:
   - `ak.stock_zh_a_hist()` (stock price data): **Requires plain 6-digit code** `601939`
   - `ak.stock_cash_flow_sheet_by_quarterly_em()`: **Requires prefix** `sh601939`
   - `ak.stock_profit_sheet_by_quarterly_em()`: **Requires prefix** `sh601939`
   - `ak.stock_individual_info_em()`: **Requires plain 6-digit code** `601939`

3. **Verification Tests**:
   ```python
   # With prefix (current behavior) - FAILS
   ak.stock_zh_a_hist(symbol="sh601939", ...)
   # Result: Empty DataFrame (0, 0)

   # Without prefix (correct) - WORKS
   ak.stock_zh_a_hist(symbol="601939", ...)
   # Result: 41 records
   ```

## Solution Design

### Strategy

Make `convert_to_akshare_code()` configurable to support both formats:
- Add optional parameter `add_prefix` (default: `None`)
- When `add_prefix=False`, return plain 6-digit code
- Maintain backward compatibility with existing callers

### API Changes

#### 1. `convert_to_akshare_code()` Function Signature

```python
def convert_to_akshare_code(
    symbol: str,
    add_prefix: Optional[bool] = None
) -> str:
    """
    Convert stock symbol to Akshare format.

    Args:
        symbol: Stock symbol (6-digit code or Akshare format with prefix)
        add_prefix: Whether to add market prefix
            - None (default): Add prefix for backward compatibility
            - True: Force add prefix
            - False: Return plain 6-digit code

    Returns:
        Akshare-formatted stock symbol

    API Format Requirements:
        - stock_zh_a_hist: Requires NO prefix (use add_prefix=False)
        - stock_individual_info_em: Requires NO prefix
        - stock_cash_flow_sheet_by_quarterly_em: Requires prefix
        - stock_profit_sheet_by_quarterly_em: Requires prefix
        - stock_news_em: Requires prefix
    """
```

#### 2. Modified Function Calls

```python
# In get_akshare_stock() - FIX
akshare_symbol = convert_to_akshare_code(symbol, add_prefix=False)

# In get_akshare_indicators() - FIX (calls get_akshare_stock internally)
# No change needed - inherits fix from get_akshare_stock()

# In get_akshare_news() - NO CHANGE
akshare_symbol = convert_to_akshare_code(symbol)  # Uses default (add prefix)

# In get_akshare_fundamentals() - VERIFY AND ADJUST
akshare_symbol = convert_to_akshare_code(symbol, add_prefix=False)

# In get_akshare_balance_sheet() - VERIFY AND ADJUST
akshare_symbol = convert_to_akshare_code(symbol)  # Requires prefix

# In get_akshare_cashflow() - NO CHANGE
akshare_symbol = convert_to_akshare_code(symbol)  # Requires prefix

# In get_akshare_income_statement() - NO CHANGE
akshare_symbol = convert_to_akshare_code(symbol)  # Requires prefix
```

### Implementation Details

#### Validation and Error Handling

1. **Duplicate Prefix Detection**:
   ```python
   if add_prefix is False and symbol[:2].lower() in ['sh', 'sz', 'bj']:
       logger.warning(f"Symbol '{symbol}' already has prefix but add_prefix=False specified")
       # Strip prefix and return plain code
       return symbol[2:] if len(symbol) == 8 else symbol
   ```

2. **Boundary Cases**:
   - Empty string or None → Raise `AkshareCodeError`
   - Invalid format (e.g., '123', 'abcdef') → Return as-is with warning
   - Already has prefix → Respect `add_prefix` parameter

3. **Logging**:
   - Use WARNING level when format mismatch detected
   - Maintain existing DEBUG level for normal operation
   - Add assertion in `get_akshare_stock()` to verify format

#### Backward Compatibility

- Default parameter value `add_prefix=None` preserves existing behavior
- All existing callers continue to work without modification
- New callers can explicitly specify `add_prefix=False` for price data APIs

## Testing Strategy

### Unit Tests

#### Test File: `tests/test_akshare_vendor.py`

**Test Case 1: Convert with add_prefix=False**
```python
def test_convert_to_akshare_code_no_prefix():
    """Test conversion without adding prefix for stock price APIs."""
    assert convert_to_akshare_code("601939", add_prefix=False) == "601939"
    assert convert_to_akshare_code("000001", add_prefix=False) == "000001"
    assert convert_to_akshare_code("300001", add_prefix=False) == "300001"
```

**Test Case 2: Convert with default behavior (add prefix)**
```python
def test_convert_to_akshare_code_default():
    """Test default behavior adds prefix."""
    assert convert_to_akshare_code("601939") == "sh601939"
    assert convert_to_akshare_code("000001") == "sz000001"
    assert convert_to_akshare_code("300001") == "sz300001"
```

**Test Case 3: Handle existing prefix**
```python
def test_convert_to_akshare_code_with_existing_prefix():
    """Test handling of symbols that already have prefix."""
    # Default behavior preserves prefix
    assert convert_to_akshare_code("sh601939") == "sh601939"

    # add_prefix=False strips prefix
    assert convert_to_akshare_code("sh601939", add_prefix=False) == "601939"
```

**Test Case 4: Error handling**
```python
def test_convert_to_akshare_code_invalid_input():
    """Test error handling for invalid inputs."""
    with pytest.raises(AkshareCodeError):
        convert_to_akshare_code("")

    with pytest.raises(AkshareCodeError):
        convert_to_akshare_code(None)
```

### Integration Tests

#### Test File: `tests/test_akshare_stock_data.py`

**Test Case 1: Original failing scenario**
```python
@pytest.mark.integration
def test_get_akshare_stock_original_bug():
    """Test the exact scenario from the bug report."""
    result = get_akshare_stock(
        symbol="601939",
        start_date="2025-03-10",
        end_date="2025-05-10"
    )
    # Should return data, not "No data found"
    assert "No data found" not in result
    assert "Stock data for" in result
```

**Test Case 2: Verify code format assertion**
```python
@pytest.mark.integration
def test_get_akshare_stock_code_format():
    """Test that get_akshare_stock uses correct code format."""
    symbol = "601939"
    result = get_akshare_stock(symbol, "2024-01-01", "2024-01-31")

    # Verify the symbol wasn't prefixed in the API call
    # (This test requires mocking or inspecting internal calls)
```

**Test Case 3: Historical data retrieval**
```python
@pytest.mark.integration
def test_get_akshare_stock_historical():
    """Test retrieval of historical stock data."""
    result = get_akshare_stock(
        symbol="601939",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )

    assert "601939" in result
    assert len(result) > 0
```

### Test Execution

**With mock (CI/CD)**:
```bash
pytest tests/test_akshare_vendor.py -v
pytest tests/test_akshare_stock_data.py -v -m "not integration"
```

**With real API calls (local development)**:
```bash
pytest tests/test_akshare_stock_data.py -v -m integration
```

## Implementation Steps

### Phase 1: Core Function Modification

1. **Modify `tradingagents/dataflows/akshare.py`**
   - Update `convert_to_akshare_code()` function signature
   - Add `add_prefix` parameter with default `None`
   - Implement conditional logic to skip prefix when `add_prefix=False`
   - Add duplicate prefix detection and warning
   - Update docstring with API format requirements table

2. **Update `get_akshare_stock()` function**
   - Change call to `convert_to_akshare_code(symbol, add_prefix=False)`
   - Add assertion to verify returned code format
   - Add comment explaining why `add_prefix=False` is required

3. **Verify `get_akshare_indicators()`**
   - Ensure it calls `get_akshare_stock()` internally
   - No direct changes needed (inherits fix)

### Phase 2: Documentation and Comments

4. **Add inline comments**
   - In `convert_to_akshare_code()`: Document API format requirements
   - In `get_akshare_stock()`: Explain parameter choice
   - In other functions: Document why they use or don't use `add_prefix`

5. **Update module docstring**
   - Add table of Akshare APIs and their code format requirements
   - Document the `add_prefix` parameter usage guidelines

### Phase 3: Testing

6. **Create unit tests**
   - `tests/test_akshare_vendor.py`: Test `convert_to_akshare_code()` scenarios
   - Cover all boundary cases and parameter combinations

7. **Create integration tests**
   - `tests/test_akshare_stock_data.py`: Test `get_akshare_stock()` end-to-end
   - Mock akshare API calls for CI/CD
   - Include real API test for local validation

8. **Run test suite**
   ```bash
   pytest tests/test_akshare_vendor.py -v
   pytest tests/test_akshare_stock_data.py -v
   ```

### Phase 4: Verification

9. **Run full akshare test suite**
   ```bash
   pytest tests/test_akshare_*.py -v
   ```
   - Ensure no regressions in other akshare functions
   - Verify news, fundamentals, indicators still work

10. **Manual verification**
    - Test with original bug report parameters
    - Verify data is returned successfully
    - Check logs for appropriate warning levels

### Phase 5: Code Review

11. **Create pull request**
    - Include detailed description of changes
    - Reference this bug report
    - Highlight test coverage additions

12. **Code review checklist**
    - All API format requirements documented
    - Tests cover all scenarios
    - No regressions in existing functionality
    - Documentation is clear and accurate

## Risk Assessment

### Low Risk

**Reasoning**:
- Changes are localized to `convert_to_akshare_code()` function
- Default behavior maintains backward compatibility
- Comprehensive test coverage prevents regressions
- Changes are well-documented with clear rationale

**Mitigation**:
- Unit tests cover all parameter combinations
- Integration tests verify end-to-end functionality
- Full test suite execution ensures no regressions
- Code review process validates implementation

## Related Issues

### Known API Inconsistencies

The following Akshare APIs have different code format requirements:

| API Function | Code Format | Status |
|-------------|-------------|--------|
| stock_zh_a_hist | Plain (601939) | ✅ Fixed in this PR |
| stock_individual_info_em | Plain (601939) | ⚠️ Needs verification |
| stock_cash_flow_sheet_by_quarterly_em | Prefix (sh601939) | ✅ Current behavior correct |
| stock_profit_sheet_by_quarterly_em | Prefix (sh601939) | ✅ Current behavior correct |
| stock_news_em | Prefix (sh601939) | ✅ Current behavior correct |
| stock_balance_sheet_by_quarterly_em | Prefix (sh601939) | ⚠️ Needs verification |

**Note**: This fix focuses on `get_akshare_stock()`. Other functions should be verified in follow-up work if issues arise.

## Success Criteria

1. ✅ Original bug scenario returns data successfully
2. ✅ All unit tests pass
3. ✅ Integration tests pass (both mocked and real API)
4. ✅ Full akshare test suite passes without regressions
5. ✅ Code changes are well-documented
6. ✅ Code review approved

## Future Considerations

1. **API Format Monitoring**: Akshare library updates may change API requirements. Monitor release notes.

2. **Testing Strategy**: Consider adding automated tests that check actual Akshare API responses to catch format changes early.

3. **Documentation Maintenance**: Keep API format requirements table updated as new Akshare APIs are integrated.

4. **Performance**: If profiling shows `convert_to_akshare_code()` is a bottleneck, consider caching results or optimizing format checks.

## References

- Original bug report: `dev/bugfix/002-akshare-no-data-found.md`
- Related bug fix: `dev/bugfix/001-akshare-get-stock-data.md`
- Akshare documentation: https://akshare.akfamily.xyz/
- Test file: `tests/test_akshare_vendor.py`
- Implementation file: `tradingagents/dataflows/akshare.py`
