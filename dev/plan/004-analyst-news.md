# Implementation Plan: News Analyst - Chinese A-Share Adaptation

## Executive Summary

Adapt the existing `news_analyst.py` to support Chinese A-share market news analysis by:
1. Extracting and translating the English system prompt to Chinese
2. Implementing externalized prompt management using existing infrastructure
3. Providing Chinese news analysis reports with A-share market considerations
4. Supporting language switching via existing `LANGUAGE` environment variable

**Key Design Decisions:**
- **Translation Strategy**: Literal translation (直译优先) preserving original structure
- **Scope**: Only modify `news_analyst.py` and prompt files (小步快跑,严格限制范围)
- **Reuse**: Completely follow the pattern established in market_analyst (plan/003)
- **Testing**: File verification only (no automated tests, no manual cases)
- **Documentation**: Code comments only (no separate spec or summary documents)

---

## 1. Current State Analysis

### 1.1 Existing Code Structure

**File**: `tradingagents/agents/analysts/news_analyst.py`

**Current Implementation**:
```python
def create_news_analyst(llm):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        tools = [get_news, get_global_news]

        system_message = (
            "You are a news researcher tasked with analyzing recent news "
            "and trends over the past week. Please write a comprehensive report "
            "of the current state of the world that is relevant for trading and "
            "macroeconomics. Use the available tools: get_news(query, start_date, "
            "end_date) for company-specific or targeted news searches, and "
            "get_global_news(curr_date, look_back_days, limit) for broader "
            "macroeconomic news. Do not simply state the trends are mixed, "
            "provide detailed and finegrained analysis and insights that may help "
            "traders make decisions."
            + """ Make sure to append a Markdown table at the end of the report
            to organize key points in the report, organized and easy to read."""
        )

        prompt = ChatPromptTemplate.from_messages([...])
        # ...
```

**Key Components**:
1. **System Message**: Hardcoded English text (~120 words)
2. **Tools**: `get_news`, `get_global_news`
3. **Placeholders**: `{tool_names}`, `{current_date}`, `{ticker}`
4. **Output Requirements**: Detailed analysis + Markdown table

### 1.2 Infrastructure (Already Exists)

**Function**: `load_prompt_template(agent_name, language)` in `agent_utils.py`

**Features**:
- Loads prompts from `prompts/{language}/{agent_name}.md`
- Supports `LANGUAGE` environment variable (default: 'zh')
- Validates language codes ('zh', 'en')
- Provides clear error messages

**Directories**:
```
prompts/
├── zh/
│   └── market_analyst.md  # (already exists)
└── en/
    └── market_analyst.md  # (already exists)
```

---

## 2. Target State Specification

### 2.1 Modified Code

**File**: `tradingagents/agents/analysts/news_analyst.py`

**Changes**:
1. Import `load_prompt_template` from `agent_utils`
2. Replace hardcoded `system_message` with loaded prompt
3. Keep all other logic unchanged

**Modified Code**:
```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_news, get_global_news, load_prompt_template
from tradingagents.dataflows.config import get_config


def create_news_analyst(llm):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        tools = [
            get_news,
            get_global_news,
        ]

        # Load prompt from external file (supports multi-language)
        # Note: Uses existing load_prompt_template() infrastructure
        system_message = load_prompt_template('news_analyst')

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
                    "For your reference, the current date is {current_date}. We are looking at the company {ticker}",
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
            "news_report": report,
        }

    return news_analyst_node
```

**Lines Modified**: 3 lines
- Line 4: Add `load_prompt_template` to imports
- Line 19: Replace hardcoded message with `load_prompt_template('news_analyst')`
- Add comment explaining the change

### 2.2 Prompt File Specifications

#### 2.2.1 `prompts/en/news_analyst.md`

**Content**: Extract the original English `system_message` from current code

**Source Text**:
```markdown
You are a news researcher tasked with analyzing recent news and trends over the past week. Please write a comprehensive report of the current state of the world that is relevant for trading and macroeconomics. Use the available tools: get_news(query, start_date, end_date) for company-specific or targeted news searches, and get_global_news(curr_date, look_back_days, limit) for broader macroeconomic news. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions.

Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read.
```

#### 2.2.2 `prompts/zh/news_analyst.md`

**Translation Strategy**: Literal translation (直译)

**Content**:
```markdown
你是一位负责分析新闻的研究员，任务是分析过去一周内的近期新闻和趋势。请撰写一份关于世界当前状况的综合报告，内容需与交易和宏观经济学相关。请使用可用工具：get_news(query, start_date, end_date) 用于公司特定或定向新闻搜索，get_global_news(curr_date, look_back_days, limit) 用于更广泛的宏观经济新闻。不要简单地说趋势不明，要提供详细和精细的分析和见解，帮助交易者做出决策。

确保在报告末尾附加 Markdown 表格来组织报告中的关键要点，使其有条理且易于阅读。

## A股市场注意事项

中国A股市场具有以下特征，在分析新闻时需要特别关注：

- **涨跌停限制**：A股有10%的日涨跌幅限制（主板），可能导致新闻对价格的影响受到限制
- **政策市特征**：政府政策、监管动态对市场影响显著
- **行业和板块**：关注行业新闻和板块轮动，这对A股投资尤为重要
- **舆论影响**：新闻传播速度快，舆论对市场情绪影响较大

在分析时，请特别关注：
1. 政策和监管相关的新闻
2. 行业层面的动态和板块轮动
3. 宏观经济政策对市场的影响
```

**Translation Notes**:
- "news researcher" → "负责分析新闻的研究员"
- "past week" → "过去一周内"
- "trading and macroeconomics" → "交易和宏观经济学"
- "Do not simply state the trends are mixed" → "不要简单地说趋势不明"
- "detailed and finegrained analysis" → "详细和精细的分析"
- Markdown table requirement preserved
- Added A-share market considerations section

**What NOT to Change**:
- All placeholders: `{tool_names}`, `{system_message}`, `{current_date}`, `{ticker}`
- Tool function names: `get_news`, `get_global_news`
- Tool parameter descriptions: `query`, `start_date`, `end_date`, `curr_date`, `look_back_days`, `limit`
- Core requirements: detailed analysis, Markdown table

---

## 3. Implementation Tasks

### Phase 1: Extract English Prompt (Priority: High)
- [ ] Extract current `system_message` from `news_analyst.py`
- [ ] Save to `prompts/en/news_analyst.md`
- [ ] Verify file is created correctly

### Phase 2: Translate to Chinese (Priority: High)
- [ ] Translate English prompt to Chinese (literal translation)
- [ ] Add A-share market considerations section
- [ ] Save to `prompts/zh/news_analyst.md`
- [ ] Verify all placeholders are preserved
- [ ] Verify translation quality

### Phase 3: Modify Code (Priority: High)
- [ ] Add `load_prompt_template` to imports in `news_analyst.py`
- [ ] Replace hardcoded `system_message` with `load_prompt_template('news_analyst')`
- [ ] Add explanatory comment
- [ ] Verify no other code changes needed

### Phase 4: Verification (Priority: Medium)
- [ ] Verify prompt files exist in correct locations
- [ ] Verify code compiles without errors
- [ ] Verify `load_prompt_template` works for 'news_analyst'
- [ ] Check that language switching works via `LANGUAGE` env var

### Phase 5: Documentation (Priority: Low)
- [ ] Add inline comments in code
- [ ] Update this plan document if needed

---

## 4. Behavior Specifications

### 4.1 Language Selection

**Mechanism**: Use existing `load_prompt_template()` function

**Logic**:
1. Check `LANGUAGE` environment variable
2. If not set → default to 'zh' (Chinese)
3. Load prompt from: `prompts/{LANGUAGE}/news_analyst.md`
4. Inject into `system_message` placeholder

**Environment Variable Values**:
- `LANGUAGE=zh` → Load Chinese prompt
- `LANGUAGE=en` → Load English prompt
- Not set → Default to Chinese prompt

**Default Behavior**: Chinese (zh) - consistent with market_analyst

### 4.2 Report Output

**Language**: Fully Chinese report (when LANGUAGE=zh)

**Components**:
1. **News Analysis** (Chinese)
   - Recent news and trends
   - Macroeconomic relevance
   - Detailed and nuanced insights
   - Focus on policy, industry sectors, and regulations (per Chinese prompt)

2. **Markdown Table** (Chinese)
   - Organized key points
   - Easy to read structure
   - Localized column names

**Example Table Structure** (implied):
```markdown
### 关键要点总结

| 维度 | 内容 |
|------|------|
| 政策影响 | ... |
| 行业动态 | ... |
| 宏观经济 | ... |
| 风险提示 | ... |
```

**Note**: Table structure not strictly specified - LLM has flexibility to organize appropriately

### 4.3 A-Share Market Considerations

**Added Content in Chinese Prompt**:
- **Price Limits**: 10% daily limit may moderate news impact
- **Policy-Driven Market**: Government decisions significantly affect market
- **Sector Rotation**: Industry news and sector rotation are important
- **Public Opinion**: Fast news dissemination, high impact on sentiment

**Focus Areas**:
1. Policy and regulation news
2. Industry-level dynamics
3. Macroeconomic policy impact

---

## 5. Testing Strategy

### 5.1 File Verification Tests

**Test Cases**:
1. **English Prompt File Exists**
   ```bash
   test -f prompts/en/news_analyst.md
   ```

2. **Chinese Prompt File Exists**
   ```bash
   test -f prompts/zh/news_analyst.md
   ```

3. **Prompt Loading Works**
   ```python
   from tradingagents.agents.utils.agent_utils import load_prompt_template

   # Test English
   prompt_en = load_prompt_template('news_analyst', 'en')
   assert 'news researcher' in prompt_en.lower()

   # Test Chinese
   prompt_zh = load_prompt_template('news_analyst', 'zh')
   assert '负责分析新闻的研究员' in prompt_zh
   assert 'A股市场' in prompt_zh
   ```

4. **Default Language is Chinese**
   ```python
   import os
   os.environ.pop('LANGUAGE', None)
   prompt = load_prompt_template('news_analyst')
   assert '负责分析新闻的研究员' in prompt
   ```

### 5.2 Code Verification

**Checks**:
1. Import statement added correctly
2. No syntax errors
3. All placeholders preserved
4. Function signature unchanged

### 5.3 No Automated Testing

**Scope Limitation**:
- No unit tests for news_analyst functionality
- No integration tests
- No manual case testing
- Only file verification to ensure basic correctness

**Rationale**:
- Follows "小步快跑" (small steps, fast iteration) principle
- Focus on infrastructure setup first
- Testing can be added in future iterations
- Consistent with minimal change requirement

---

## 6. Risk Assessment

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Translation quality issues | Medium | Literal translation strategy, preserve all technical details |
| Placeholder corruption | Medium | Careful review of all placeholders during translation |
| LangChain integration | Low | Keep existing code structure, only swap prompt source |
| File path resolution | Low | Reuse existing `load_prompt_template()` function |

### Operational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| A-share considerations incomplete | Medium | Add comprehensive coverage of key A-share features |
| Table structure too vague | Low | Trust LLM to organize appropriately |
| Language switching issues | Low | Reuse existing tested infrastructure |

---

## 7. Design Rationale

### 7.1 Why Literal Translation?

**Reasoning**:
- Preserves original analysis framework
- Ensures consistent behavior between languages
- Reduces risk of introducing errors
- Validated approach from market_analyst

### 7.2 Why Add A-Share Considerations?

**Reasoning**:
- Chinese market has unique characteristics
- A-share investors care about policy and regulation
- Industry sector rotation is critical in A-shares
- Adds value without changing core logic

### 7.3 Why No Testing Beyond File Verification?

**Reasoning**:
- Follows "小步快跑" principle
- Infrastructure change is minimal
- Reuses existing tested components
- Fast iteration, validate later if needed

### 7.4 Why Reuse market_analyst Pattern?

**Reasoning**:
- Consistent approach across analysts
- Proven to work
- Reduces development time
- Easier maintenance

### 7.5 Why Focus Only on news_analyst?

**Reasoning**:
- Incremental approach (小步快跑)
- Validate pattern before extending
- Limited scope reduces risk
- Can extend to other analysts later

---

## 8. Comparison with market_analyst (003)

### Similarities

| Aspect | market_analyst | news_analyst |
|--------|----------------|--------------|
| Use `load_prompt_template()` | ✅ | ✅ |
| External prompt files | ✅ | ✅ |
| LANGUAGE environment variable | ✅ | ✅ |
| Default to Chinese | ✅ | ✅ |
| Literal translation | ✅ | ✅ |
| Add A-share considerations | ✅ | ✅ |

### Differences

| Aspect | market_analyst | news_analyst |
|--------|----------------|--------------|
| Testing strategy | Unit + manual | File verification only |
| Documentation | Full spec | Code comments only |
| A-share specifics | Technical indicators | News categories (policy, sectors) |

---

## 9. Implementation Details

### 9.1 File Creation Checklist

**prompts/en/news_analyst.md**:
- [ ] Extracted from current code
- [ ] All text preserved
- [ ] No placeholders modified
- [ ] UTF-8 encoding

**prompts/zh/news_analyst.md**:
- [ ] Translated from English version
- [ ] A-share considerations added
- [ ] All placeholders preserved
- [ ] UTF-8 encoding
- [ ] Markdown formatting correct

### 9.2 Code Modification Checklist

**news_analyst.py**:
- [ ] Import added: `load_prompt_template`
- [ ] System message loaded from file
- [ ] Comment added explaining change
- [ ] All other code unchanged
- [ ] No syntax errors

---

## 10. Success Criteria

The implementation is considered complete when:

1. ✅ English prompt file exists at `prompts/en/news_analyst.md`
2. ✅ Chinese prompt file exists at `prompts/zh/news_analyst.md`
3. ✅ `news_analyst.py` loads prompts from external files
4. ✅ `LANGUAGE` environment variable controls language selection
5. ✅ Default language is Chinese when `LANGUAGE` is not set
6. ✅ Chinese prompt includes A-share market considerations
7. ✅ All placeholders preserved in both language versions
8. ✅ Code compiles without errors
9. ✅ File verification tests pass
10. ✅ Code comments added for clarity

---

## 11. Future Enhancements (Out of Scope)

### 11.1 Enhanced A-Share Features
- Add specific Chinese news sources (东方财富, 财新, etc.)
- Implement sentiment analysis for Chinese news
- Add real-time news filtering

### 11.2 Advanced Prompt Features
- Dynamic prompt adjustment based on market conditions
- Multi-language report generation
- Prompt A/B testing

### 11.3 Extending to Other Analysts
- Apply same pattern to other analyst agents
- Create unified prompt management
- Standardize across all agents

### 11.4 Testing
- Add unit tests for news_analyst
- Add integration tests
- Add manual case testing with real news
- Automated regression testing

---

## 12. Timeline & Dependencies

**Dependencies**:
- None (infrastructure already exists)

**Estimated Complexity**: Low
- Extract English prompt: 10 minutes
- Translate to Chinese: 30 minutes
- Modify code: 10 minutes
- Verification: 10 minutes

**Total Estimated Effort**: 1 hour

---

## 13. Acceptance Criteria

The implementation is accepted when:

1. ✅ Both prompt files are created and contain correct content
2. ✅ Code modification is minimal (3 lines)
3. ✅ All placeholders are preserved
4. ✅ Chinese version includes A-share considerations
5. ✅ Files are in correct locations
6. ✅ Code compiles and runs without errors
7. ✅ Language switching works as expected

---

## Document Metadata

**Version**: 1.0
**Date**: 2026-01-07
**Status**: Implementation Plan
**Scope**: news_analyst only (小步快跑)
**Pattern**: Reuse market_analyst (003)
**Testing**: File verification only
**Documentation**: Code comments

---

**End of Implementation Plan**
