# Specification: Market Analyst - Chinese A-Share Adaptation

## Executive Summary

Adapt the existing `market_analyst.py` to support Chinese A-share market analysis by:
1. Translating the English prompt to Chinese while maintaining all technical indicator details
2. Implementing externalized prompt management with multi-language support
3. Providing fully-featured Chinese analysis reports (maintaining English technical indicator names)
4. Supporting language switching via environment variable configuration

**Key Design Decisions:**
- **Translation Strategy**: Literal translation (直译优先) preserving original structure and technical details
- **Technical Indicators**: Keep existing indicators (完全保留原有指标) with conservative parameter settings (保守参数设置)
- **Report Style**: Professional Chinese report (中文专业版) with price points, trend analysis, and risk warnings
- **Prompt Organization**: External Markdown files in `prompts/{lang}/` directory
- **Language Control**: `LANGUAGE` environment variable (zh/en)
- **Default Language**: Chinese (zh)
- **Testing**: Manual case testing with real A-share stocks
- **Scope**: Focus on market_analyst only (小步快跑，只修改 market analyst)

---

## Technical Architecture

### 1. Directory Structure

```
TradingAgents-ETF/
├── prompts/
│   ├── zh/
│   │   └── market_analyst.md      # Chinese prompt template
│   └── en/
│       └── market_analyst.md      # English prompt template (original)
├── tradingagents/
│   ├── agents/
│   │   ├── analysts/
│   │   │   └── market_analyst.py  # Modified to use external prompts
│   │   └── utils/
│   │       └── agent_utils.py     # Add prompt loading function
├── .env.example                   # Add LANGUAGE variable documentation
└── ...
```

### 2. File Changes

#### 2.1 `tradingagents/agents/utils/agent_utils.py`

**New Function:**
```python
def load_prompt_template(agent_name: str, language: str = None) -> str:
    """
    Load prompt template from external markdown file.

    Args:
        agent_name: Name of the agent (e.g., 'market_analyst')
        language: Language code ('zh' or 'en'). If None, reads from LANGUAGE
                  environment variable with default 'zh'.

    Returns:
        Prompt content as string

    Raises:
        FileNotFoundError: With detailed error message including:
            - File path that was not found
            - How to set LANGUAGE environment variable
            - Available language options

    Example:
        >>> prompt = load_prompt_template('market_analyst', 'zh')
        >>> prompt_en = load_prompt_template('market_analyst', 'en')
    """
```

**Implementation Details:**
- Base path: `Path(__file__).parent.parent.parent.parent / 'prompts'`
- File path: `{base_path}/{language}/{agent_name}.md`
- Environment variable: `LANGUAGE` (default: 'zh')
- Error handling: Custom FileNotFoundError with configuration guidance
- Comments: English (保持代码风格一致)

#### 2.2 `tradingagents/agents/analysts/market_analyst.py`

**Modifications:**
1. Import `load_prompt_template` from `agent_utils`
2. In `create_market_analyst()` function:
   - Load prompt using: `prompt_content = load_prompt_template('market_analyst')`
   - Replace hardcoded `system_message` with loaded content
   - Keep existing LangChain ChatPromptTemplate structure
   - Maintain all existing logic (tool binding, chain invocation, etc.)

**Code Changes:**
```python
from tradingagents.agents.utils.agent_utils import load_prompt_template

def create_market_analyst(llm):
    def market_analyst_node(state):
        # ... existing code ...

        # Load prompt from external file
        system_message = load_prompt_template('market_analyst')

        # Rest of the code remains unchanged
        prompt = ChatPromptTemplate.from_messages([...])
        # ...
```

#### 2.3 `.env.example`

**Add:**
```bash
# Language configuration for agent prompts
# Options: zh (Chinese), en (English)
# Default: zh
LANGUAGE=zh
```

---

## 3. Prompt File Specifications

### 3.1 `prompts/zh/market_analyst.md`

**Content Requirements:**
- **Translation Strategy**: Literal translation (直译优先)
- **Language**: Professional Chinese (中文专业版)
- **Technical Terms**: Keep English names (SMA, MACD, RSI, etc.)
- **Placeholders**: Maintain all placeholders (e.g., `{current_date}`, `{ticker}`, `{tool_names}`)

**Key Sections to Translate:**
1. **System Message**:
   - Agent role description
   - Technical indicator explanations (all indicators: SMA, MACD, RSI, Bollinger Bands, ATR, VWMA)
   - Indicator selection guidelines (max 8 indicators, complementary insights)
   - Analysis instructions (detailed and nuanced report)
   - Markdown table requirement

2. **A-Share Specific Additions** (Conservative Approach):
   - Brief warning about price limit impact on technical indicators
   - Note on conservative parameter settings
   - Maintain all original indicator parameters without modification

3. **Report Format Instructions**:
   - Detailed analysis requirements
   - Markdown table structure
   - Content requirements: price points (价格点位), trend judgment (趋势判断), risk warnings (风险提示)

**What NOT to Change:**
- All variable placeholders: `{tool_names}`, `{system_message}`, `{current_date}`, `{ticker}`
- Technical indicator names: SMA, EMA, MACD, RSI, Bollinger Bands, ATR, VWMA
- Technical parameter values (50, 200, 10, 70/30, etc.)
- Tool function names: `get_stock_data`, `get_indicators`

**Content Structure:**
```markdown
你是一位负责分析金融市场的交易助手。你的职责是从以下列表中为给定的市场状况或交易策略选择**最相关的技术指标**。目标是选择最多**8个指标**，提供互补的洞察而不产生冗余。

指标类别及每个类别的指标如下：

## 移动平均线 (Moving Averages):
- close_50_sma: 50日简单移动平均线...
- close_200_sma: 200日简单移动平均线...
- close_10_ema: 10日指数移动平均线...

## MACD相关指标:
- macd: MACD指标...
- macds: MACD信号线...
- macdh: MACD柱状图...

## 动量指标:
- rsi: 相对强弱指标...

## 波动率指标:
- boll: 布林带中轨...
- boll_ub: 布林带上轨...
- boll_lb: 布林带下轨...
- atr: 平均真实波幅...

## 成交量指标:
- vwma: 成交量加权移动平均线...

## 指标选择原则:
- 选择能够提供多样化互补信息的指标...
- 避免冗余...

## A股市场注意事项:
- 中国A股市场有10%的涨跌停限制，可能影响某些技术指标的有效性...
- 建议采用保守的参数设置进行分析...

## 分析要求:
请撰写非常详细和细致的趋势观察报告。不要简单地说趋势不明，要提供详细和精细的分析和见解，帮助交易者做出决策。

确保在报告末尾附加Markdown表格来组织关键要点，使其有条理且易于阅读。表格应包含：
- 关键价格点位（支撑位、阻力位）
- 趋势判断
- 风险提示
```

### 3.2 `prompts/en/market_analyst.md`

**Content:** Extract the original English `system_message` from current code and save as markdown file.

---

## 4. Behavior Specifications

### 4.1 Language Selection Logic

```
1. Check LANGUAGE environment variable
2. If not set → default to 'zh' (Chinese)
3. Load prompt from: prompts/{LANGUAGE}/market_analyst.md
4. If file not found → raise FileNotFoundError with detailed message
```

**Environment Variable Values:**
- `LANGUAGE=zh` → Load Chinese prompt
- `LANGUAGE=en` → Load English prompt
- Not set → Default to Chinese prompt

### 4.2 Report Output

**Language:** Fully Chinese report

**Exceptions:**
- Technical indicator names remain in English (e.g., SMA, MACD, RSI)
- Variable substitutions keep original format

**Report Components:**
1. **Detailed Analysis** (Chinese)
   - Trend observations
   - Indicator analysis
   - Nuanced insights

2. **Markdown Table** (Chinese)
   - 关键价格点位 (Key Price Points)
   - 趋势判断 (Trend Analysis)
   - 风险提示 (Risk Warnings)

**Example Table Structure:**
```markdown
### 关键要点总结

| 分析维度 | 具体内容 |
|---------|---------|
| 关键价格点位 | 支撑位：XXX元，阻力位：XXX元 |
| 趋势判断 | 当前处于上升/下降/震荡趋势 |
| 风险提示 | 注意XXX风险，建议设置止损位XXX元 |
```

### 4.3 Error Handling

**File Not Found Exception:**
```python
raise FileNotFoundError(
    f"Prompt file not found: {file_path}\n"
    f"Please ensure the prompt file exists for language: {language}\n"
    f"Available languages: zh, en\n"
    f"Set LANGUAGE environment variable: export LANGUAGE=zh"
)
```

---

## 5. Testing Strategy

### 5.1 Unit Tests

**Test File:** `tests/agents/test_market_analyst_prompt.py`

**Test Cases:**
1. **Multi-language Loading**
   ```python
   def test_load_chinese_prompt():
       prompt = load_prompt_template('market_analyst', 'zh')
       assert '你是一位负责分析金融市场的交易助手' in prompt

   def test_load_english_prompt():
       prompt = load_prompt_template('market_analyst', 'en')
       assert 'You are a trading assistant' in prompt
   ```

2. **Default Language**
   ```python
   def test_default_language_is_chinese():
       os.environ.pop('LANGUAGE', None)
       prompt = load_prompt_template('market_analyst')
       assert '你是一位负责分析金融市场的交易助手' in prompt
   ```

3. **Environment Variable**
   ```python
   def test_language_from_env_variable():
       os.environ['LANGUAGE'] = 'en'
       prompt = load_prompt_template('market_analyst')
       assert 'You are a trading assistant' in prompt
   ```

4. **File Not Found**
   ```python
   def test_prompt_file_not_found():
       with pytest.raises(FileNotFoundError) as exc_info:
           load_prompt_template('market_analyst', 'fr')
       assert 'Prompt file not found' in str(exc_info.value)
   ```

### 5.2 Manual Case Testing

**Test Stocks (Real A-Shares):**
1. 茅台 (600519.SH)
2. 腾讯控股 (00700.HK)
3. 平安银行 (000001.SZ)

**Validation Criteria:**
1. **Language Correctness** (语言正确性)
   - Report is in Chinese
   - Technical indicator names remain in English
   - No mixed English sentences

2. **Format Correctness** (格式正确)
   - Markdown table is properly formatted
   - Report structure follows template
   - All placeholders are replaced correctly

3. **Content Quality** (Manual Review)
   - Analysis is detailed and nuanced
   - Table contains: price points, trend judgment, risk warnings
   - No simply stating "trends are mixed"

**Test Procedure:**
```python
# Test script
import os
from tradingagents.agents.analysts.market_analyst import create_market_analyst
from tradingagents.dataflows.config import get_config

# Set language
os.environ['LANGUAGE'] = 'zh'

# Initialize
llm = get_config().llm
market_analyst = create_market_analyst(llm)

# Test with real stock
state = {
    "trade_date": "2024-01-15",
    "company_of_interest": "600519.SH",
    "messages": []
}

result = market_analyst(state)
print(result["market_report"])
```

---

## 6. Implementation Tasks

### Phase 1: Infrastructure (Priority: High)
- [ ] Create `prompts/zh/` and `prompts/en/` directories
- [ ] Implement `load_prompt_template()` in `agent_utils.py`
- [ ] Extract and save original English prompt to `prompts/en/market_analyst.md`
- [ ] Add unit tests for prompt loading

### Phase 2: Chinese Prompt (Priority: High)
- [ ] Translate prompt to Chinese (literal translation)
- [ ] Save to `prompts/zh/market_analyst.md`
- [ ] Review and verify translation quality
- [ ] Ensure all placeholders are preserved

### Phase 3: Integration (Priority: High)
- [ ] Modify `market_analyst.py` to use external prompts
- [ ] Update `.env.example` with LANGUAGE variable
- [ ] Add function docstrings
- [ ] Test with both languages

### Phase 4: Testing & Validation (Priority: Medium)
- [ ] Run unit tests
- [ ] Manual testing with real A-share stocks
- [ ] Validate report quality and format
- [ ] Fix any issues

### Phase 5: Documentation (Priority: Low)
- [ ] Update README.md with language configuration
- [ ] Add examples to `.env.example`
- [ ] Document usage in comments

---

## 7. Design Rationale

### 7.1 Why External Prompt Files?
- **Maintainability**: Easier to update prompts without modifying code
- **Version Control**: Track prompt changes independently
- **Multi-language**: Clean separation of language versions
- **Flexibility**: Easy to add new languages or variants

### 7.2 Why Literal Translation?
- **Accuracy**: Preserves original technical details and logic
- **Consistency**: Ensures English and Chinese versions have same behavior
- **Safety**: Reduces risk of introducing errors during adaptation

### 7.3 Why Conservative Approach to A-Share Adaptation?
- **Risk Minimization**: Focus on translation first, optimization later
- **Validation**: Use real testing to validate before making significant changes
- **Incremental**: Can add A-share specific features in future iterations

### 7.4 Why Environment Variable for Language?
- **Flexibility**: Easy to switch languages without code changes
- **Deployment**: Different environments can use different languages
- **Convention**: Standard approach for configuration
- **Global**: Consistent with existing pattern in codebase

### 7.5 Why Default to Chinese?
- **Market Focus**: Primary use case is Chinese A-share analysis
- **User Base**: Target users are Chinese-speaking traders
- **Explicit**: English users can set `LANGUAGE=en` explicitly

### 7.6 Why Focus Only on market_analyst?
- **Incremental Approach**: Small steps, fast iterations (小步快跑)
- **Validation**: Validate approach before extending to other analysts
- **Risk Control**: Limited scope reduces risk of breaking changes

---

## 8. Future Enhancements (Out of Scope)

### 8.1 A-Share Specific Features
- Add A-share specific technical indicators (换手率, 北向资金, etc.)
- Implement price limit detection logic
- Add T+1 trading rule considerations

### 8.2 Advanced Prompt Features
- Dynamic parameter adjustment based on market conditions
- Multi-language report generation (bilingual output)
- Prompt versioning and A/B testing

### 8.3 Architecture Improvements
- Generic prompt manager for all agents
- Template engine (Jinja2) for complex prompts
- Configuration file based prompt selection

### 8.4 Extending to Other Analysts
- Apply same pattern to other analyst agents
- Create unified prompt management system
- Standardize multi-language support across agents

---

## 9. Acceptance Criteria

The implementation is considered complete when:

1. ✅ Chinese and English prompt files exist in correct directories
2. ✅ `load_prompt_template()` function works for both languages
3. ✅ `market_analyst.py` loads prompts from external files
4. ✅ `LANGUAGE` environment variable controls language selection
5. ✅ Default language is Chinese when `LANGUAGE` is not set
6. ✅ Error message is clear when prompt file is missing
7. ✅ Chinese reports are generated with proper format
8. ✅ Manual testing with real stocks passes validation
9. ✅ Unit tests pass for all scenarios
10. ✅ `.env.example` documents LANGUAGE variable

---

## 10. Risk Assessment

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Translation quality issues | Medium | Manual review, literal translation strategy |
| File path resolution issues | Low | Use relative paths from `__file__` |
| LangChain integration issues | Low | Keep existing code structure, only swap prompt |
| Performance degradation | Very Low | File I/O is minimal and cached |

### Operational Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Users unaware of LANGUAGE variable | Medium | Update .env.example, add documentation |
| Missing prompt files in deployment | Medium | Clear error messages with setup instructions |
| Inconsistent behavior between languages | Low | Use literal translation, preserve structure |

---

## 11. Timeline & Dependencies

**Dependencies:**
- None (no new packages required)

**Estimated Complexity:** Low-Medium
- Prompt translation: 2-3 hours
- Infrastructure setup: 1-2 hours
- Integration and testing: 2-3 hours
- Documentation: 1 hour

**Total Estimated Effort:** 6-9 hours

---

## Appendix A: Code Templates

### A.1 `load_prompt_template()` Implementation Sketch

```python
from pathlib import Path
import os

def load_prompt_template(agent_name: str, language: str = None) -> str:
    """
    Load prompt template from external markdown file.

    Args:
        agent_name: Name of the agent (e.g., 'market_analyst')
        language: Language code ('zh' or 'en'). If None, reads from LANGUAGE
                  environment variable with default 'zh'.

    Returns:
        Prompt content as string

    Raises:
        FileNotFoundError: With detailed error message including configuration guidance
    """
    # Determine language
    if language is None:
        language = os.environ.get('LANGUAGE', 'zh')

    # Validate language
    valid_languages = ['zh', 'en']
    if language not in valid_languages:
        raise ValueError(
            f"Invalid language code: '{language}'. "
            f"Valid options: {', '.join(valid_languages)}"
        )

    # Build file path (relative to this file)
    base_path = Path(__file__).parent.parent.parent.parent / 'prompts'
    file_path = base_path / language / f'{agent_name}.md'

    # Load prompt
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Prompt file not found: {file_path}\n"
            f"Agent: {agent_name}\n"
            f"Language: {language}\n"
            f"\n"
            f"Please ensure the prompt file exists.\n"
            f"Available languages: {', '.join(valid_languages)}\n"
            f"Set LANGUAGE environment variable: export LANGUAGE=zh"
        )
```

### A.2 Modified `market_analyst.py` Section

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_stock_data, get_indicators, load_prompt_template
from tradingagents.dataflows.config import get_config


def create_market_analyst(llm):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_stock_data,
            get_indicators,
        ]

        # Load prompt from external file (supports multi-language)
        system_message = load_prompt_template('market_analyst')

        # Rest remains unchanged...
```

---

## Document Metadata

**Version:** 1.0
**Last Updated:** 2026-01-06
**Status:** Draft Specification
**Author:** Claude (with detailed user requirements)
**Review Status:** Pending User Approval

---

**End of Specification**
