# Implementation Plan: Fundamentals Analyst - Chinese A-Share Adaptation

## Executive Summary

Adapt the existing `fundamentals_analyst.py` to support Chinese A-share market fundamental analysis by:
1. Extracting and translating the English system prompt to Chinese
2. Implementing externalized prompt management using existing infrastructure
3. Providing Chinese fundamental analysis reports
4. Supporting language switching via existing `LANGUAGE` environment variable

**Key Design Decisions:**
- **Translation Strategy**: Literal translation (直译优先) preserving original structure
- **Scope**: Only modify `fundamentals_analyst.py` and prompt files (小步快跑,严格限制范围)
- **Reuse**: Completely follow the pattern established in market_analyst (003) and news_analyst (004)
- **Testing**: File verification only (no automated tests, no manual cases)
- **Documentation**: Complete specification document (this file)
- **A-Share Specifics**: Translation only, no A-share specific considerations needed

---

## 1. Current State Analysis

### 1.1 Existing Code Structure

**File**: `tradingagents/agents/analysts/fundamentals_analyst.py`

**Current Implementation**:
```python
def create_fundamentals_analyst(llm):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_fundamentals,
            get_balance_sheet,
            get_cashflow,
            get_income_statement,
        ]

        system_message = (
            "You are a researcher tasked with analyzing fundamental information "
            "over the past week about a company. Please write a comprehensive report "
            "of the company's fundamental information such as financial documents, "
            "company profile, basic company financials, and company financial history "
            "to gain a full view of the company's fundamental information to inform traders. "
            "Make sure to include as much detail as possible. Do not simply state the "
            "trends are mixed, provide detailed and finegrained analysis and insights "
            "that may help traders make decisions."
            + " Make sure to append a Markdown table at the end of the report to "
            "organize key points in the report, organized and easy to read."
            + " Use the available tools: `get_fundamentals` for comprehensive company "
            "analysis, `get_balance_sheet`, `get_cashflow`, and `get_income_statement` "
            "for specific financial statements."
        )

        prompt = ChatPromptTemplate.from_messages([...])
        # ...
```

**Key Components**:
1. **System Message**: Hardcoded English text (~115 words)
2. **Tools**: 4 financial tools
   - `get_fundamentals`: Comprehensive company analysis
   - `get_balance_sheet`: Balance sheet data
   - `get_cashflow`: Cash flow statement
   - `get_income_statement`: Income statement
3. **Placeholders**: `{tool_names}`, `{system_message}`, `{current_date}`, `{ticker}`
4. **Output Requirements**: Comprehensive report + Markdown table
5. **Time Scope**: "Over the past week" (to be preserved in translation)

### 1.2 Infrastructure (Already Exists)

**Function**: `load_prompt_template(agent_name, language)` in `agent_utils.py`

**Features**:
- Loads prompts from `prompts/{language}/{agent_name}.md`
- Supports `LANGUAGE` environment variable (default: 'zh')
- Validates language codes ('zh', 'en')
- Provides clear error messages
- Already used by market_analyst and news_analyst

**Directories**:
```
prompts/
├── zh/
│   ├── market_analyst.md  # (already exists)
│   └── news_analyst.md     # (already exists)
└── en/
    ├── market_analyst.md  # (already exists)
    └── news_analyst.md     # (already exists)
```

---

## 2. Target State Specification

### 2.1 Modified Code

**File**: `tradingagents/agents/analysts/fundamentals_analyst.py`

**Changes**:
1. Import `load_prompt_template` from `agent_utils`
2. Replace hardcoded `system_message` with loaded prompt
3. Keep all other logic unchanged

**Modified Code**:
```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement,
    get_insider_sentiment,
    get_insider_transactions,
    load_prompt_template
)
from tradingagents.dataflows.config import get_config


def create_fundamentals_analyst(llm):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_fundamentals,
            get_balance_sheet,
            get_cashflow,
            get_income_statement,
        ]

        # Load prompt from external file (supports multi-language)
        # Note: Uses existing load_prompt_template() infrastructure
        system_message = load_prompt_template('fundamentals_analyst')

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The company we want to look at is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
```

**Lines Modified**: 2 lines
- Line 4-7: Add `load_prompt_template` to imports
- Replace hardcoded `system_message` with `load_prompt_template('fundamentals_analyst')`
- Add comment explaining the change

### 2.2 Prompt File Specifications

#### 2.2.1 `prompts/en/fundamentals_analyst.md`

**Content**: Extract the original English `system_message` from current code

**Source Text**:
```markdown
You are a researcher tasked with analyzing fundamental information over the past week about a company. Please write a comprehensive report of the company's fundamental information such as financial documents, company profile, basic company financials, and company financial history to gain a full view of the company's fundamental information to inform traders. Make sure to include as much detail as possible. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions.

Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read.

Use the available tools: `get_fundamentals` for comprehensive company analysis, `get_balance_sheet`, `get_cashflow`, and `get_income_statement` for specific financial statements.
```

#### 2.2.2 `prompts/zh/fundamentals_analyst.md`

**Translation Strategy**: Literal translation (直译)

**Content**:
```markdown
你是一位负责分析基本面信息的研究员，任务是分析过去一周内关于公司的基本面信息。请撰写一份关于公司基本面信息的综合报告，包括财务文档、公司概况、基本公司财务状况和公司财务历史，以全面了解公司的基本面信息，帮助交易者做出决策。请尽可能包含详细信息。不要简单地说趋势不明，要提供详细和精细的分析和见解，帮助交易者做出决策。

确保在报告末尾附加 Markdown 表格来组织报告中的关键要点，使其有条理且易于阅读。

请使用可用工具：`get_fundamentals` 用于综合公司分析，`get_balance_sheet`、`get_cashflow` 和 `get_income_statement` 用于特定财务报表。
```

**Translation Notes**:
- "researcher tasked with analyzing fundamental information" → "负责分析基本面信息的研究员"
- "over the past week" → "过去一周内" (preserved time scope)
- "fundamental information" → "基本面信息"
- "financial documents" → "财务文档"
- "company profile" → "公司概况"
- "basic company financials" → "基本公司财务状况"
- "company financial history" → "公司财务历史"
- "include as much detail as possible" → "尽可能包含详细信息"
- "Do not simply state the trends are mixed" → "不要简单地说趋势不明"
- "detailed and finegrained analysis" → "详细和精细的分析"
- Markdown table requirement preserved
- Tool names preserved in English
- Tool descriptions translated

**What NOT to Change**:
- All placeholders: `{tool_names}`, `{system_message}`, `{current_date}`, `{ticker}`
- Tool function names: `get_fundamentals`, `get_balance_sheet`, `get_cashflow`, `get_income_statement`
- Time scope: "over the past week"
- Core requirements: detailed analysis, comprehensive report, Markdown table
- Emphasis on detail: "include as much detail as possible"

**No A-Share Specific Considerations**:
- Fundamental analysis is universal across markets
- No A-share specific additions needed (unlike news_analyst)
- Pure translation, no content adaptation

---

## 3. Implementation Tasks

### Phase 1: Extract English Prompt (Priority: High)
- [ ] Extract current `system_message` from `fundamentals_analyst.py`
- [ ] Save to `prompts/en/fundamentals_analyst.md`
- [ ] Verify file is created correctly

### Phase 2: Translate to Chinese (Priority: High)
- [ ] Translate English prompt to Chinese (literal translation)
- [ ] Save to `prompts/zh/fundamentals_analyst.md`
- [ ] Verify all placeholders are preserved
- [ ] Verify translation quality
- [ ] Ensure no A-share specific content added

### Phase 3: Modify Code (Priority: High)
- [ ] Add `load_prompt_template` to imports in `fundamentals_analyst.py`
- [ ] Replace hardcoded `system_message` with `load_prompt_template('fundamentals_analyst')`
- [ ] Add explanatory comment
- [ ] Verify no other code changes needed

### Phase 4: Verification (Priority: Medium)
- [ ] Verify prompt files exist in correct locations
- [ ] Verify code compiles without errors
- [ ] Verify `load_prompt_template` works for 'fundamentals_analyst'
- [ ] Check that language switching works via `LANGUAGE` env var

### Phase 5: Documentation (Priority: Low)
- [ ] Update this plan document if needed
- [ ] Add inline comments in code (already done in Phase 3)

---

## 4. Behavior Specifications

### 4.1 Language Selection

**Mechanism**: Use existing `load_prompt_template()` function

**Logic**:
1. Check `LANGUAGE` environment variable
2. If not set → default to 'zh' (Chinese)
3. Load prompt from: `prompts/{LANGUAGE}/fundamentals_analyst.md`
4. Inject into `system_message` placeholder

**Environment Variable Values**:
- `LANGUAGE=zh` → Load Chinese prompt
- `LANGUAGE=en` → Load English prompt
- Not set → Default to Chinese prompt

**Default Behavior**: Chinese (zh) - consistent with market_analyst and news_analyst

### 4.2 Report Output

**Language**: Fully Chinese report (when LANGUAGE=zh)

**Components**:
1. **Fundamental Analysis** (Chinese)
   - Financial documents (财务文档)
   - Company profile (公司概况)
   - Basic financials (基本财务状况)
   - Financial history (财务历史)
   - As much detail as possible (尽可能详细)
   - Detailed and nuanced insights (详细和精细的见解)

2. **Markdown Table** (Chinese)
   - Organized key points
   - Easy to read structure
   - Localized content

**Example Table Structure** (implied):
```markdown
### 关键要点总结

| 维度 | 内容 |
|------|------|
| 财务状况 | ... |
| 盈利能力 | ... |
| 成长性 | ... |
| 风险因素 | ... |
```

**Note**: Table structure not strictly specified - LLM has flexibility to organize appropriately

### 4.3 Tools Usage

**Tools Available** (same in both languages):
1. `get_fundamentals` - Comprehensive company analysis
2. `get_balance_sheet` - Balance sheet data
3. `get_cashflow` - Cash flow statement
4. `get_income_statement` - Income statement

**Usage**: Tool names kept in English in Chinese prompt (backticks preserved)

---

## 5. Testing Strategy

### 5.1 File Verification Tests

**Test Cases**:
1. **English Prompt File Exists**
   ```bash
   test -f prompts/en/fundamentals_analyst.md
   ```

2. **Chinese Prompt File Exists**
   ```bash
   test -f prompts/zh/fundamentals_analyst.md
   ```

3. **Prompt Loading Works**
   ```python
   from tradingagents.agents.utils.agent_utils import load_prompt_template

   # Test English
   prompt_en = load_prompt_template('fundamentals_analyst', 'en')
   assert 'fundamental information' in prompt_en.lower()
   assert 'get_fundamentals' in prompt_en

   # Test Chinese
   prompt_zh = load_prompt_template('fundamentals_analyst', 'zh')
   assert '基本面信息' in prompt_zh
   assert 'get_fundamentals' in prompt_zh
   assert '过去一周内' in prompt_zh
   ```

4. **Default Language is Chinese**
   ```python
   import os
   os.environ.pop('LANGUAGE', None)
   prompt = load_prompt_template('fundamentals_analyst')
   assert '基本面信息' in prompt
   ```

5. **No A-Share Content Added**
   ```python
   prompt_zh = load_prompt_template('fundamentals_analyst', 'zh')
   assert 'A股' not in prompt_zh
   assert '涨跌停' not in prompt_zh
   ```

### 5.2 Code Verification

**Checks**:
1. Import statement added correctly
2. No syntax errors
3. All placeholders preserved
4. Function signature unchanged
5. All 4 tools still included

### 5.3 No Automated Testing

**Scope Limitation**:
- No unit tests for fundamentals_analyst functionality
- No integration tests
- No manual case testing
- Only file verification to ensure basic correctness

**Rationale**:
- Follows "小步快跑" (small steps, fast iteration) principle
- Consistent with news_analyst (004) approach
- Infrastructure change is minimal
- Reuses existing tested components

---

## 6. Risk Assessment

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Translation quality issues | Medium | Literal translation strategy, preserve all technical details |
| Placeholder corruption | Medium | Careful review of all placeholders during translation |
| Tool names lost in translation | Low | Keep tool names in English with backticks |
| LangChain integration | Low | Keep existing code structure, only swap prompt source |
| File path resolution | Low | Reuse existing `load_prompt_template()` function |

### Operational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing A-share considerations | Very Low | Fundamental analysis is universal, not market-specific |
| Table structure too vague | Low | Trust LLM to organize appropriately |
| Language switching issues | Low | Reuse existing tested infrastructure |

---

## 7. Design Rationale

### 7.1 Why Literal Translation?

**Reasoning**:
- Preserves original analysis framework
- Ensures consistent behavior between languages
- Reduces risk of introducing errors
- Validated approach from market_analyst and news_analyst
- Fundamental analysis is universal

### 7.2 Why No A-Share Specific Considerations?

**Reasoning**:
- Fundamental analysis principles are universal across markets
- Financial metrics (PE, PB, ROE, etc.) work the same way globally
- No need to add market-specific guidance (unlike news analysis)
- Keeps prompt simpler and more focused
- User's requirement: "只翻译"

### 7.3 Why "Over the Past Week" for Fundamentals?

**Reasoning**:
- User explicitly requested to keep this: "保持一周"
- Fundamental data may change weekly (earnings reports, guidance, etc.)
- Consistent with original prompt design
- May be removed in future iterations if not needed

### 7.4 Why No Testing Beyond File Verification?

**Reasoning**:
- Follows "小步快跑" principle
- Consistent with news_analyst approach
- Infrastructure change is minimal
- Reuses existing tested components
- Fast iteration, validate later if needed

### 7.5 Why Reuse market_analyst and news_analyst Pattern?

**Reasoning**:
- Consistent approach across all analysts
- Proven to work twice already
- Reduces development time
- Easier maintenance
- Established pattern in codebase

### 7.6 Why Complete Spec Document?

**Reasoning**:
- User explicitly requested: "需要完整 spec"
- Provides comprehensive documentation
- Useful for future reference
- Consistent with market_analyst (003) approach

---

## 8. Comparison with Previous Implementations

### 8.1 Similarities

| Aspect | market_analyst (003) | news_analyst (004) | fundamentals_analyst (005) |
|--------|----------------------|---------------------|----------------------------|
| Use `load_prompt_template()` | ✅ | ✅ | ✅ |
| External prompt files | ✅ | ✅ | ✅ |
| LANGUAGE environment variable | ✅ | ✅ | ✅ |
| Default to Chinese | ✅ | ✅ | ✅ |
| Literal translation | ✅ | ✅ | ✅ |
| File verification testing | Unit + manual | File only | File only |
| Markdown table requirement | ✅ | ✅ | ✅ |

### 8.2 Differences

| Aspect | market_analyst (003) | news_analyst (004) | fundamentals_analyst (005) |
|--------|----------------------|---------------------|----------------------------|
| A-share specific content | Technical indicators | News categories | None |
| Documentation | Full spec | Summary only | Full spec |
| Domain knowledge | Market analysis | News analysis | Financial analysis |
| Tools used | 2 tools | 2 tools | 4 tools |
| Time scope | No scope | Past week | Past week |

---

## 9. Implementation Details

### 9.1 File Creation Checklist

**prompts/en/fundamentals_analyst.md**:
- [ ] Extracted from current code
- [ ] All text preserved
- [ ] No placeholders modified
- [ ] UTF-8 encoding
- [ ] Contains all tool descriptions

**prompts/zh/fundamentals_analyst.md**:
- [ ] Translated from English version
- [ ] No A-share considerations added
- [ ] All placeholders preserved
- [ ] Tool names kept in English
- [ ] UTF-8 encoding
- [ ] Markdown formatting correct

### 9.2 Code Modification Checklist

**fundamentals_analyst.py**:
- [ ] Import added: `load_prompt_template`
- [ ] System message loaded from file
- [ ] Comment added explaining change
- [ ] All 4 tools preserved
- [ ] All other code unchanged
- [ ] No syntax errors

---

## 10. Success Criteria

The implementation is considered complete when:

1. ✅ English prompt file exists at `prompts/en/fundamentals_analyst.md`
2. ✅ Chinese prompt file exists at `prompts/zh/fundamentals_analyst.md`
3. ✅ `fundamentals_analyst.py` loads prompts from external files
4. ✅ `LANGUAGE` environment variable controls language selection
5. ✅ Default language is Chinese when `LANGUAGE` is not set
6. ✅ All placeholders preserved in both language versions
7. ✅ Tool names kept in English in Chinese version
8. ✅ Code compiles without errors
9. ✅ File verification tests pass
10. ✅ No A-share specific content added
11. ✅ "Over the past week" time scope preserved

---

## 11. Future Enhancements (Out of Scope)

### 11.1 Enhanced Fundamental Analysis
- Add A-share specific financial metrics (市净率, 市销率, etc.)
- Implement industry comparison benchmarks
- Add Chinese accounting standard considerations

### 11.2 Advanced Prompt Features
- Dynamic prompt adjustment based on company type
- Multi-language report generation
- Prompt A/B testing

### 11.3 Extending to Other Analysts
- Apply same pattern to remaining analyst agents
- Create unified prompt management
- Standardize across all agents

### 11.4 Testing
- Add unit tests for fundamentals_analyst
- Add integration tests
- Add manual case testing with real companies
- Automated regression testing

### 11.5 Time Scope Evaluation
- Evaluate if "over the past week" is necessary for fundamental analysis
- May remove or make configurable in future iterations

---

## 12. Timeline & Dependencies

**Dependencies**:
- None (infrastructure already exists)

**Estimated Complexity**: Very Low
- Extract English prompt: 5 minutes
- Translate to Chinese: 15 minutes
- Modify code: 5 minutes
- Verification: 5 minutes

**Total Estimated Effort**: 30 minutes

**Note**: Simpler than news_analyst because no A-share specific content needed

---

## 13. Acceptance Criteria

The implementation is accepted when:

1. ✅ Both prompt files are created and contain correct content
2. ✅ Code modification is minimal (~2 lines)
3. ✅ All placeholders are preserved
4. ✅ No A-share specific content added
5. ✅ Files are in correct locations
6. ✅ Code compiles and runs without errors
7. ✅ Language switching works as expected
8. ✅ All 4 tools are preserved
9. ✅ Time scope ("past week") is preserved
10. ✅ Tool names remain in English in Chinese version

---

## Document Metadata

**Version**: 1.0
**Date**: 2026-01-07
**Status**: Implementation Plan
**Scope**: fundamentals_analyst only (小步快跑)
**Pattern**: Reuse market_analyst (003) and news_analyst (004)
**Testing**: File verification only
**Documentation**: Complete specification
**A-Share Specifics**: None (fundamental analysis is universal)

---

**End of Implementation Plan**
