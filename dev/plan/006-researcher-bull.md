# Specification: Bull Researcher - Chinese A-Share Adaptation

## Executive Summary

Adapt the existing `bull_researcher.py` to support Chinese A-share market investment debate by:
1. Extracting and translating the English prompt to Chinese
2. Implementing externalized prompt management using existing infrastructure
3. Providing Chinese bull argument outputs
4. Supporting language switching via existing `LANGUAGE` environment variable

**Key Design Decisions:**
- **Translation Strategy**: Literal translation (直译优先) preserving original structure and professional analysis style
- **Scope**: Only modify `bull_researcher.py` and prompt files (小步快跑, 严格限制范围)
- **Reuse**: Completely follow the pattern established in market_analyst (003), news_analyst (004), and fundamentals_analyst (005)
- **Testing**: File verification only (no automated tests, no manual debate testing)
- **Documentation**: Complete specification document (this file)
- **A-Share Specifics**: No A-share specific considerations needed (pure translation, like fundamentals_analyst)
- **Output Format**: "多头：{中文内容}" (completely Chinese prefix)

---

## 1. Current State Analysis

### 1.1 Existing Code Structure

**File**: `tradingagents/agents/researchers/bull_researcher.py`

**Current Implementation**:
```python
from langchain_core.messages import AIMessage
import time
import json


def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""You are a Bull Analyst advocating for investing in the stock. Your task is to build a strong, evidence-based case emphasizing growth potential, competitive advantages, and positive market indicators. Leverage the provided research and data to address concerns and counter bearish arguments effectively.

Key points to focus on:
- Growth Potential: Highlight the company's market opportunities, revenue projections, and scalability.
- Competitive Advantages: Emphasize factors like unique products, strong branding, or dominant market positioning.
- Positive Indicators: Use financial health, industry trends, and recent positive news as evidence.
- Bear Counterpoints: Critically analyze the bear argument with specific data and sound reasoning, addressing concerns thoroughly and showing why the bull perspective holds stronger merit.
- Engagement: Present your argument in a conversational style, engaging directly with the bear analyst's points and debating effectively rather than just listing data.

Resources available:
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bear argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}
Use this information to deliver a compelling bull argument, refute the bear's concerns, and engage in a dynamic debate that demonstrates the strengths of the bull position. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        response = llm.invoke(prompt)

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
```

**Key Components**:
1. **System Prompt**: Hardcoded English text (~320 words)
2. **Role**: Bull Analyst advocating for stock investment
3. **5 Key Strategy Points**:
   - Growth Potential (增长潜力)
   - Competitive Advantages (竞争优势)
   - Positive Indicators (积极指标)
   - Bear Counterpoints (空头反驳点)
   - Engagement (参与度/辩论互动)
4. **Resources Available**: 5 types of reports + history + memories
5. **Variables**: `{market_research_report}`, `{sentiment_report}`, `{news_report}`, `{fundamentals_report}`, `{history}`, `{current_response}`, `{past_memory_str}`
6. **Output Format**: `f"Bull Analyst: {response.content}"`
7. **Memory System**: Uses `memory.get_memories()` to retrieve past lessons
8. **Debate Context**: Engages in back-and-forth with bear analyst

### 1.2 Infrastructure (Already Exists)

**Function**: `load_prompt_template(agent_name, language)` in `agent_utils.py`

**Features**:
- Loads prompts from `prompts/{language}/{agent_name}.md`
- Supports `LANGUAGE` environment variable (default: 'zh')
- Validates language codes ('zh', 'en')
- Provides clear error messages
- Already used by market_analyst, news_analyst, and fundamentals_analyst

**Directories**:
```
prompts/
├── zh/
│   ├── market_analyst.md      # (already exists)
│   ├── news_analyst.md         # (already exists)
│   └── fundamentals_analyst.md # (already exists)
└── en/
    ├── market_analyst.md      # (already exists)
    ├── news_analyst.md         # (already exists)
    └── fundamentals_analyst.md # (already exists)
```

---

## 2. Target State Specification

### 2.1 Modified Code

**File**: `tradingagents/agents/researchers/bull_researcher.py`

**Changes**:
1. Import `load_prompt_template` from `agent_utils`
2. Replace hardcoded `prompt` with loaded template + variable substitution
3. Change output prefix from "Bull Analyst:" to "多头："
4. Keep all other logic unchanged

**Modified Code**:
```python
from langchain_core.messages import AIMessage
import time
import json
from tradingagents.agents.utils.agent_utils import load_prompt_template


def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # Load prompt from external file (supports multi-language)
        # Note: Uses existing load_prompt_template() infrastructure
        prompt_template = load_prompt_template('bull_researcher')

        # Substitute variables
        prompt = prompt_template.format(
            market_research_report=market_research_report,
            sentiment_report=sentiment_report,
            news_report=news_report,
            fundamentals_report=fundamentals_report,
            history=history,
            current_response=current_response,
            past_memory_str=past_memory_str
        )

        response = llm.invoke(prompt)

        # Chinese output prefix (completely localized)
        argument = f"多头：{response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
```

**Lines Modified**: ~10 lines
- Import: Add `load_prompt_template`
- Load prompt: `prompt_template = load_prompt_template('bull_researcher')`
- Variable substitution: Use `.format()` method
- Output prefix: Change to Chinese "多头："
- Add comments explaining changes

### 2.2 Prompt File Specifications

#### 2.2.1 `prompts/en/bull_researcher.md`

**Content**: Extract the original English prompt from current code

**Source Text**:
```markdown
You are a Bull Analyst advocating for investing in the stock. Your task is to build a strong, evidence-based case emphasizing growth potential, competitive advantages, and positive market indicators. Leverage the provided research and data to address concerns and counter bearish arguments effectively.

Key points to focus on:
- Growth Potential: Highlight the company's market opportunities, revenue projections, and scalability.
- Competitive Advantages: Emphasize factors like unique products, strong branding, or dominant market positioning.
- Positive Indicators: Use financial health, industry trends, and recent positive news as evidence.
- Bear Counterpoints: Critically analyze the bear argument with specific data and sound reasoning, addressing concerns thoroughly and showing why the bull perspective holds stronger merit.
- Engagement: Present your argument in a conversational style, engaging directly with the bear analyst's points and debating effectively rather than just listing data.

Resources available:
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bear argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}

Use this information to deliver a compelling bull argument, refute the bear's concerns, and engage in a dynamic debate that demonstrates the strengths of the bull position. You must also address reflections and learn from lessons and mistakes you made in the past.
```

#### 2.2.2 `prompts/zh/bull_researcher.md`

**Translation Strategy**: Literal translation (直译) with minor adjustments for natural Chinese flow

**Content**:
```markdown
你是一位看涨分析师，主张投资该股票。你的任务是构建一个有力的、基于证据的投资理由，强调增长潜力、竞争优势和积极的市场指标。利用提供的研究和数据来解决疑虑，有效反驳看跌论点。

需要重点关注的关键点：
- 增长潜力：突出公司的市场机会、收入预测和可扩展性。
- 竞争优势：强调独特产品、强大品牌或主导市场地位等因素。
- 积极指标：利用财务健康状况、行业趋势和近期积极新闻作为证据。
- 空头反驳点：用具体数据和合理推理批判性地分析空头论点，全面解决疑虑，说明为什么多头观点更具说服力。
- 参与度：采用对话式表达，直接回应空头分析师的观点，进行有效的辩论，而不是简单罗列数据。

可用资源：
市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新时事新闻：{news_report}
公司基本面报告：{fundamentals_report}
辩论对话历史：{history}
最后的空头论点：{current_response}
类似情况的反思和经验教训：{past_memory_str}

利用这些信息提出令人信服的多头论点，反驳空头的担忧，参与动态辩论，展示多头论点的优势。你还必须针对反思内容，并从过去的教训和错误中学习。
```

**Translation Notes**:
- "Bull Analyst" → "看涨分析师" (professional, literal translation)
- "advocating for investing" → "主张投资" (professional tone)
- "evidence-based case" → "基于证据的投资理由" (clear and precise)
- "Key points to focus on" → "需要重点关注的关键点" (natural Chinese)
- "Growth Potential" → "增长潜力" (standard financial term)
- "Competitive Advantages" → "竞争优势" (standard financial term)
- "Positive Indicators" → "积极指标" (standard financial term)
- "Bear Counterpoints" → "空头反驳点" (market-specific terminology)
- "Engagement" → "参与度" (maintains original meaning while being natural)
- "conversational style" → "对话式表达" (adjusted for Chinese context)
- "engaging directly" → "直接回应" (more natural in Chinese debate context)
- "debating effectively" → "进行有效的辩论" (direct translation)
- "addressing concerns thoroughly" → "全面解决疑虑" (natural Chinese)
- "Resources available" → "可用资源" (direct translation)
- "Market research report" → "市场研究报告" (completely localized)
- "Social media sentiment report" → "社交媒体情绪报告" (completely localized)
- "Latest world affairs news" → "最新时事新闻" (completely localized)
- "Company fundamentals report" → "公司基本面报告" (completely localized)
- "Conversation history of the debate" → "辩论对话历史" (completely localized)
- "Last bear argument" → "最后的空头论点" (completely localized)
- "Reflections from similar situations and lessons learned" → "类似情况的反思和经验教训" (completely localized)
- "compelling bull argument" → "令人信服的多头论点" (natural Chinese)
- "refute the bear's concerns" → "反驳空头的担忧" (market terminology)
- "dynamic debate" → "动态辩论" (direct translation)
- "learn from lessons and mistakes" → "从过去的教训和错误中学习" (natural Chinese)

**What NOT to Change**:
- All variable placeholders: `{market_research_report}`, `{sentiment_report}`, `{news_report}`, `{fundamentals_report}`, `{history}`, `{current_response}`, `{past_memory_str}`
- Core logical structure of the prompt
- All 5 key strategy points
- Emphasis on evidence-based arguments
- Memory and learning requirements
- Debate engagement style

**No A-Share Specific Considerations**:
- Investment debate logic is universal across markets
- No A-share specific guidance needed (like fundamentals_analyst)
- Pure translation, no content adaptation
- Professional analysis style maintained

**Translation Quality Adjustments**:
- "engaging directly" → "直接回应" (slight adjustment for natural Chinese debate flow)
- "conversational style" → "对话式表达" (more natural than literal "对话风格")
- Other phrases: literal translation to preserve original meaning and structure

---

## 3. Implementation Tasks

### Phase 1: Extract English Prompt (Priority: High)
- [ ] Extract current `prompt` from `bull_researcher.py`
- [ ] Save to `prompts/en/bull_researcher.md`
- [ ] Verify file is created correctly
- [ ] Verify all placeholders are preserved

### Phase 2: Translate to Chinese (Priority: High)
- [ ] Translate English prompt to Chinese (literal translation with minor adjustments)
- [ ] Save to `prompts/zh/bull_researcher.md`
- [ ] Verify all placeholders are preserved
- [ ] Verify translation quality (professional analysis style maintained)
- [ ] Ensure no A-share specific content added
- [ ] Verify resource names are completely localized
- [ ] Verify output prefix is "多头："

### Phase 3: Modify Code (Priority: High)
- [ ] Add `load_prompt_template` to imports in `bull_researcher.py`
- [ ] Load prompt template using `load_prompt_template('bull_researcher')`
- [ ] Implement variable substitution using `.format()` method
- [ ] Change output prefix to "多头："
- [ ] Add explanatory comments (in English, consistent with other files)
- [ ] Verify no other code changes needed
- [ ] Verify all 7 variables are substituted correctly
- [ ] Verify memory system logic is unchanged

### Phase 4: Verification (Priority: Medium)
- [ ] Verify prompt files exist in correct locations
- [ ] Verify code compiles without errors
- [ ] Verify `load_prompt_template` works for 'bull_researcher'
- [ ] Check that language switching works via `LANGUAGE` env var
- [ ] Verify default language is Chinese (zh)
- [ ] Verify output prefix is correct
- [ ] Verify all placeholders work correctly

### Phase 5: Documentation (Priority: Low)
- [ ] Update this plan document if needed
- [ ] Add inline comments in code (already done in Phase 3)
- [ ] Document relationship with bear_researcher (future task)
- [ ] Add usage examples if needed

---

## 4. Behavior Specifications

### 4.1 Language Selection

**Mechanism**: Use existing `load_prompt_template()` function

**Logic**:
1. Check `LANGUAGE` environment variable
2. If not set → default to 'zh' (Chinese)
3. Load prompt from: `prompts/{LANGUAGE}/bull_researcher.md`
4. Substitute variables using `.format()` method
5. Invoke LLM with constructed prompt

**Environment Variable Values**:
- `LANGUAGE=zh` → Load Chinese prompt, output "多头：{中文内容}"
- `LANGUAGE=en` → Load English prompt, output "Bull Analyst: {English content}"
- Not set → Default to Chinese prompt

**Default Behavior**: Chinese (zh) - consistent with market_analyst, news_analyst, and fundamentals_analyst

### 4.2 Report Output

**Language**: Fully Chinese argument (when LANGUAGE=zh)

**Output Format**:
```
多头：[中文的看涨论点内容]
```

**Example Output** (hypothetical):
```
多头：根据最新财报显示，该公司在过去季度实现了35%的收入增长，远超行业平均水平。公司在人工智能领域的核心技术优势使其成为市场领导者。虽然空头担心估值过高，但考虑到公司强劲的盈利能力和市场扩张潜力，当前估值是合理的。从历史类似情况来看，具有类似增长潜力的科技公司在该阶段都有显著的上涨空间。
```

**Components**:
1. **Professional Analysis Style** (Chinese)
   - Evidence-based arguments (基于证据的论证)
   - Growth potential emphasis (强调增长潜力)
   - Competitive advantages (竞争优势)
   - Positive indicators (积极指标)

2. **Debate Engagement** (Chinese)
   - Direct response to bear arguments (直接回应空头论点)
   - Conversational style (对话式表达)
   - Effective debating (有效辩论)
   - Not just listing data (不是简单罗列数据)

3. **Learning from History** (Chinese)
   - Address reflections (针对反思内容)
   - Learn from past lessons (从过去的教训中学习)
   - Avoid past mistakes (避免过去的错误)

**Language Consistency**:
- Output prefix: "多头：" (completely Chinese)
- Argument content: Fully Chinese
- Resource references in prompt: Chinese (市场研究报告, etc.)
- Strategy points: Chinese (增长潜力, etc.)

### 4.3 Variable Substitution

**Variables to Substitute** (7 total):
1. `{market_research_report}` - Market research report content
2. `{sentiment_report}` - Social media sentiment report content
3. `{news_report}` - Latest world affairs news content
4. `{fundamentals_report}` - Company fundamentals report content
5. `{history}` - Conversation history of the debate
6. `{current_response}` - Last bear argument
7. `{past_memory_str}` - Reflections from similar situations

**Substitution Method**: Python `.format()` method

**Example**:
```python
prompt_template = load_prompt_template('bull_researcher')
prompt = prompt_template.format(
    market_research_report=market_research_report,
    sentiment_report=sentiment_report,
    news_report=news_report,
    fundamentals_report=fundamentals_report,
    history=history,
    current_response=current_response,
    past_memory_str=past_memory_str
)
```

**Error Handling**: If variable substitution fails, Python will raise `KeyError` with missing variable name

### 4.4 Memory System Integration

**How It Works**:
- `memory.get_memories(curr_situation, n_matches=2)` retrieves past recommendations
- Retrieved memories are concatenated into `past_memory_str`
- `past_memory_str` is substituted into prompt
- LLM is instructed to "address reflections and learn from lessons and mistakes"

**Language Consistency**:
- **No special handling needed** for language mixing
- If past memories are in English and current prompt is in Chinese, LLM will handle automatically
- LLM can understand and integrate multilingual content
- Future memories will be in Chinese (when LANGUAGE=zh)

**Rationale**: System language consistency will emerge naturally over time as all components use Chinese

### 4.5 Historical Context Handling

**Debate History Variables**:
- `{history}` - Full debate conversation history
- `{current_response}` - Last bear argument to respond to

**Language Mixing**:
- **No special handling needed**
- If history contains English arguments and current prompt is Chinese, LLM will:
  - Understand English historical context
  - Generate response in Chinese
  - Reference previous points appropriately

**Future Consistency**:
- Once LANGUAGE=zh is set, all future debate exchanges will be in Chinese
- Output will accumulate in Chinese naturally
- Language consistency emerges without additional logic

---

## 5. Testing Strategy

### 5.1 File Verification Tests

**Test Cases**:
1. **English Prompt File Exists**
   ```bash
   test -f prompts/en/bull_researcher.md
   ```

2. **Chinese Prompt File Exists**
   ```bash
   test -f prompts/zh/bull_researcher.md
   ```

3. **Prompt Loading Works**
   ```python
   from tradingagents.agents.utils.agent_utils import load_prompt_template

   # Test English
   prompt_en = load_prompt_template('bull_researcher', 'en')
   assert 'Bull Analyst' in prompt_en
   assert '{market_research_report}' in prompt_en

   # Test Chinese
   prompt_zh = load_prompt_template('bull_researcher', 'zh')
   assert '看涨分析师' in prompt_zh
   assert '{market_research_report}' in prompt_zh
   assert '多头：' not in prompt_zh  # Prefix is in code, not prompt
   ```

4. **Default Language is Chinese**
   ```python
   import os
   os.environ.pop('LANGUAGE', None)
   prompt = load_prompt_template('bull_researcher')
   assert '看涨分析师' in prompt
   ```

5. **All Placeholders Preserved**
   ```python
   prompt_zh = load_prompt_template('bull_researcher', 'zh')
   placeholders = [
       '{market_research_report}',
       '{sentiment_report}',
       '{news_report}',
       '{fundamentals_report}',
       '{history}',
       '{current_response}',
       '{past_memory_str}'
   ]
   for placeholder in placeholders:
       assert placeholder in prompt_zh
   ```

6. **No A-Share Content Added**
   ```python
   prompt_zh = load_prompt_template('bull_researcher', 'zh')
   assert 'A股' not in prompt_zh
   assert '涨跌停' not in prompt_zh
   assert 'T+1' not in prompt_zh
   ```

7. **Resource Names Localized**
   ```python
   prompt_zh = load_prompt_template('bull_researcher', 'zh')
   assert '市场研究报告：' in prompt_zh
   assert '社交媒体情绪报告：' in prompt_zh
   assert '最新时事新闻：' in prompt_zh
   assert '公司基本面报告：' in prompt_zh
   ```

8. **Variable Substitution Works**
   ```python
   prompt_template = load_prompt_template('bull_researcher', 'zh')
   test_values = {
       'market_research_report': 'TEST_MARKET',
       'sentiment_report': 'TEST_SENTIMENT',
       'news_report': 'TEST_NEWS',
       'fundamentals_report': 'TEST_FUNDAMENTALS',
       'history': 'TEST_HISTORY',
       'current_response': 'TEST_CURRENT',
       'past_memory_str': 'TEST_MEMORY'
   }
   prompt = prompt_template.format(**test_values)
   assert 'TEST_MARKET' in prompt
   assert 'TEST_SENTIMENT' in prompt
   assert '看涨分析师' in prompt
   ```

### 5.2 Code Verification

**Checks**:
1. Import statement added correctly
2. No syntax errors
3. All placeholders preserved in code
4. Function signature unchanged (still accepts `llm` and `memory`)
5. Memory system logic unchanged
6. All 7 variables substituted correctly
7. Output prefix changed to "多头："
8. Comments are in English (consistent with codebase)

### 5.3 No Automated Testing

**Scope Limitation**:
- No unit tests for bull_researcher debate functionality
- No integration tests with bear_researcher
- No manual debate testing
- Only file verification to ensure basic correctness

**Rationale**:
- Follows "小步快跑" (small steps, fast iteration) principle
- Consistent with news_analyst (004) and fundamentals_analyst (005) approach
- Infrastructure change is minimal
- Reuses existing tested components
- Fast iteration, validate later if needed

---

## 6. Risk Assessment

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Translation quality issues | Medium | Literal translation strategy, preserve all technical details; provide full translation in spec for review |
| Placeholder corruption | Medium | Careful review of all placeholders during translation; automated verification tests |
| Variable substitution errors | Medium | Use Python `.format()` method which provides clear error messages; comprehensive verification tests |
| LangChain integration issues | Low | Keep existing code structure, only swap prompt source; LLM invocation unchanged |
| File path resolution | Low | Reuse existing `load_prompt_template()` function which has proven reliability |
| Language mixing in history | Low | LLM can handle multilingual context; natural consistency emerges over time |
| Memory system compatibility | Very Low | Memory system is language-agnostic; stores recommendations as-is |

### Operational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing A-share considerations | Very Low | Investment debate logic is universal; not market-specific like news analysis |
| Debate style too formal for Chinese context | Low | Literal translation preserves professional analysis style; minor adjustments for natural flow |
| Output prefix "多头：" unfamiliar to users | Low | Standard Chinese market terminology; consistent with financial industry usage |
| Language switching issues | Low | Reuse existing tested infrastructure from market_analyst, news_analyst, fundamentals_analyst |
| Inconsistent behavior with bear_researcher | Low | Document in spec that bear_researcher should follow same pattern in future implementation |
| Users unaware of LANGUAGE variable | Medium | Consistent with existing analysts; already documented in .env.example from previous work |

### Translation Quality Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| "engaging directly" translation too literal | Low | Adjusted to "直接回应" for natural Chinese debate flow |
| "conversational style" translation awkward | Low | Adjusted to "对话式表达" for natural Chinese |
| Resource names inconsistent with other analysts | Low | Completely localized resource names (市场研究报告, etc.) |
| Professional analysis style lost in translation | Low | Maintain literal translation of all strategy points and professional terminology |

---

## 7. Design Rationale

### 7.1 Why Literal Translation?

**Reasoning**:
- Preserves original analysis framework and debate logic
- Ensures consistent behavior between languages
- Reduces risk of introducing errors
- Validated approach from market_analyst, news_analyst, and fundamentals_analyst
- Investment debate principles are universal
- Professional analysis style transcends language boundaries

### 7.2 Why "多头：" as Output Prefix?

**Reasoning**:
- User explicitly chose "多头：" during interview
- Standard Chinese market terminology
- Concise and widely understood
- More natural than "看涨分析师：" in debate context
- Consistent with professional Chinese trading discourse

### 7.3 Why Minor Adjustments for Natural Flow?

**Reasoning**:
- "engaging directly" → "直接回应" is more natural in Chinese debate context
- "conversational style" → "对话式表达" avoids awkwardness
- Preserves core meaning while fitting Chinese linguistic patterns
- User approved "微调表达，更符合中文习惯" during interview
- Professional analysis style maintained

### 7.4 Why No A-Share Specific Considerations?

**Reasoning**:
- Investment debate logic is universal across markets
- Bull/bear arguments work the same way globally
- No market-specific debate mechanics needed
- Keeps prompt simpler and more focused
- Consistent with fundamentals_analyst (005) approach
- User explicitly requested "不添加任何 A 股特定内容"

### 7.5 Why No Special Handling for Language Mixing?

**Reasoning**:
- LLMs (especially GPT-4) handle multilingual context well
- Language consistency will emerge naturally over time
- No need for complex language detection/conversion logic
- Reduces system complexity
- Past memories (even if English) provide value regardless of language
- Future debates will be consistent in Chinese once LANGUAGE=zh is set

### 7.6 Why Only File Verification Testing?

**Reasoning**:
- Follows "小步快跑" principle
- Consistent with news_analyst (004) and fundamentals_analyst (005) approach
- Infrastructure change is minimal (reuses existing components)
- Debate testing is complex and time-consuming
- Fast iteration, validate later if needed
- Focus on prompt translation quality rather than functional testing

### 7.7 Why Complete Specification Document?

**Reasoning**:
- User explicitly requested "完整详细 spec (003 风格)" during interview
- Provides comprehensive documentation
- Useful for future reference
- Consistent with market_analyst (003) approach
- Facilitates bear_researcher implementation (future task)

### 7.8 Why Comply with Previous Patterns?

**Reasoning**:
- Consistent approach across all analysts and researchers
- Proven to work successfully three times already
- Reduces development time
- Easier maintenance and understanding
- Established pattern in codebase
- User explicitly requested to "参考 @dev/plan/003-analyst-market.md 和 dev/plan/005-analyst-fundamentals.md 的做法"

---

## 8. Comparison with Previous Implementations

### 8.1 Similarities

| Aspect | market_analyst (003) | news_analyst (004) | fundamentals_analyst (005) | bull_researcher (006) |
|--------|----------------------|---------------------|----------------------------|------------------------|
| Use `load_prompt_template()` | ✅ | ✅ | ✅ | ✅ |
| External prompt files | ✅ | ✅ | ✅ | ✅ |
| LANGUAGE environment variable | ✅ | ✅ | ✅ | ✅ |
| Default to Chinese | ✅ | ✅ | ✅ | ✅ |
| Literal translation | ✅ | ✅ | ✅ | ✅ |
| File verification testing | Unit + manual | File only | File only | File only |
| Code comments language | English | English | English | English |
| Markdown requirement | ✅ | ✅ | ✅ | ❌ (debate format) |

### 8.2 Differences

| Aspect | market_analyst (003) | news_analyst (004) | fundamentals_analyst (005) | bull_researcher (006) |
|--------|----------------------|---------------------|----------------------------|------------------------|
| Domain | Technical analysis | News analysis | Financial analysis | Investment debate |
| Output format | Markdown report | Markdown report | Markdown report | Debate argument |
| A-share content | Technical indicators | News categories | None | None |
| Tools used | 2 tools | 2 tools | 4 tools | 0 tools |
| Time scope | No scope | Past week | Past week | No scope |
| Memory system | No | No | No | Yes |
| Output prefix | None | None | None | "多头：" |
| Variable count | 4 | 4 | 4 | 7 |
| Context | Standalone analysis | Standalone analysis | Standalone analysis | Debate interaction |

### 8.3 Unique Characteristics of bull_researcher

1. **Memory System Integration**: First agent to use `memory.get_memories()` for learning from past situations
2. **Debate Context**: Engages in back-and-forth with bear_researcher, not standalone analysis
3. **7 Variables**: Most complex variable substitution (vs 4 in analysts)
4. **Output Prefix**: Uses localized prefix "多头：" to identify speaker in debate
5. **Conversational Style**: Emphasizes debate engagement over report generation
6. **Historical Context**: References full debate history and last bear argument
7. **Paired Design**: Designed to work with bear_researcher (future implementation)

---

## 9. Implementation Details

### 9.1 File Creation Checklist

**prompts/en/bull_researcher.md**:
- [ ] Extracted from current code
- [ ] All text preserved verbatim
- [ ] All 7 placeholders preserved: `{market_research_report}`, `{sentiment_report}`, `{news_report}`, `{fundamentals_report}`, `{history}`, `{current_response}`, `{past_memory_str}`
- [ ] UTF-8 encoding
- [ ] Contains all 5 strategy points
- [ ] Contains resource descriptions
- [ ] Contains learning and reflection requirements

**prompts/zh/bull_researcher.md**:
- [ ] Translated from English version (literal translation with minor adjustments)
- [ ] No A-share considerations added
- [ ] All 7 placeholders preserved
- [ ] Professional analysis style maintained
- [ ] All 5 strategy points translated
- [ ] Resource names completely localized (市场研究报告, etc.)
- [ ] UTF-8 encoding
- [ ] Markdown formatting correct
- [ ] Natural Chinese flow for "engaging directly" and "conversational style"

### 9.2 Code Modification Checklist

**bull_researcher.py**:
- [ ] Import added: `load_prompt_template`
- [ ] Prompt loaded from file using `load_prompt_template('bull_researcher')`
- [ ] Variable substitution implemented using `.format()` method
- [ ] All 7 variables substituted correctly
- [ ] Output prefix changed to "多头："
- [ ] Comments added explaining changes (in English)
- [ ] Memory system logic unchanged
- [ ] LLM invocation unchanged
- [ ] State management unchanged
- [ ] No syntax errors
- [ ] Function signature unchanged (`llm`, `memory`)

### 9.3 Variable Substitution Implementation

**Before** (original code):
```python
prompt = f"""You are a Bull Analyst...
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
...
"""
```

**After** (new code):
```python
# Load prompt from external file (supports multi-language)
# Note: Uses existing load_prompt_template() infrastructure
prompt_template = load_prompt_template('bull_researcher')

# Substitute variables
prompt = prompt_template.format(
    market_research_report=market_research_report,
    sentiment_report=sentiment_report,
    news_report=news_report,
    fundamentals_report=fundamentals_report,
    history=history,
    current_response=current_response,
    past_memory_str=past_memory_str
)
```

**Benefits**:
- Clear separation of template and variables
- Easier to maintain and update prompts
- Supports multi-language without code duplication
- Type-safe (Python `.format()` validates variable names)

---

## 10. Success Criteria

The implementation is considered complete when:

1. ✅ English prompt file exists at `prompts/en/bull_researcher.md`
2. ✅ Chinese prompt file exists at `prompts/zh/bull_researcher.md`
3. ✅ `bull_researcher.py` loads prompts from external files
4. ✅ `LANGUAGE` environment variable controls language selection
5. ✅ Default language is Chinese when `LANGUAGE` is not set
6. ✅ All 7 placeholders preserved in both language versions
7. ✅ Code compiles and runs without errors
8. ✅ File verification tests pass
9. ✅ No A-share specific content added
10. ✅ Resource names completely localized in Chinese version
11. ✅ Output prefix changed to "多头："
12. ✅ Variable substitution works correctly
13. ✅ Memory system logic unchanged
14. ✅ Professional analysis style maintained in translation
15. ✅ All 5 strategy points preserved
16. ✅ Debate engagement requirements preserved
17. ✅ Learning from past requirements preserved
18. ✅ Comments are in English
19. ✅ No syntax errors
20. ✅ Function signature unchanged

---

## 11. Future Enhancements (Out of Scope)

### 11.1 Bear Researcher Implementation

**Highest Priority Future Task**: Implement `bear_researcher` following the same pattern

**Key Considerations**:
- Use identical translation strategy (literal translation with minor adjustments)
- Output prefix should be "空头：" (parallel to "多头：")
- Mirror the 5 strategy points from bear perspective
- Use same memory system integration
- Ensure debate flow consistency
- Reference this spec as template

**Implementation Plan** (Future):
1. Extract `bear_researcher.py` prompt
2. Create `prompts/en/bear_researcher.md`
3. Translate to `prompts/zh/bear_researcher.md`
4. Modify `bear_researcher.py` to use `load_prompt_template()`
5. Change output prefix to "空头："
6. Verify consistency with bull_researcher

### 11.2 Enhanced Debate Features

**Possible Future Enhancements**:
- Add debate stage awareness (opening, rebuttal, closing)
- Implement structured argument scoring
- Add debate moderator agent
- Multi-round debate history summarization
- Debate outcome prediction

### 11.3 Advanced Prompt Features

**Possible Future Enhancements**:
- Dynamic prompt adjustment based on debate stage
- Multi-language report generation (bilingual debate)
- Prompt A/B testing for debate effectiveness
- Sentiment-aware argument generation
- Role-specific debate personas

### 11.4 A-Share Specific Debate Considerations

**Possible Future Enhancements**:
- Add A-share market-specific debate points (policy impact, etc.)
- Incorporate price limit effects into bull/bear arguments
- Add retail vs institutional investor perspectives
- Consider T+1 trading rule implications
- Add sector rotation analysis

### 11.5 Testing and Validation

**Possible Future Enhancements**:
- Add unit tests for bull_researcher functionality
- Add integration tests with bear_researcher
- Manual debate testing with real stocks
- Automated debate quality metrics
- Debate outcome accuracy validation

**Note**: These are explicitly out of scope for current implementation. Current task is limited to bull_researcher only, following "小步快跑" principle.

---

## 12. Timeline & Dependencies

**Dependencies**:
- None (infrastructure already exists from previous implementations)

**Estimated Complexity**: Low-Medium
- Extract English prompt: 10 minutes
- Translate to Chinese: 2-3 hours (careful translation of all 5 strategy points and debate-specific language)
- Modify code: 30 minutes (variable substitution logic)
- Verification: 30 minutes (7 placeholders to verify)
- Documentation: 2 hours (complete spec as requested)

**Total Estimated Effort**: 6-9 hours

**Complexity Breakdown**:
- Similar to market_analyst (003) in terms of documentation detail
- More complex translation than fundamentals_analyst (005) due to debate-specific terminology
- More complex variable substitution (7 variables vs 4 in analysts)
- Simpler than market_analyst in terms of testing (file verification only)

**Parallel Work Opportunities**:
- Translation can be done in parallel with code modification
- File verification can be done in parallel with documentation

---

## 13. Acceptance Criteria

The implementation is accepted when:

1. ✅ Both prompt files are created and contain correct content
2. ✅ Code modification follows the pattern from previous analysts
3. ✅ All 7 placeholders are preserved and work correctly
4. ✅ No A-share specific content added
5. ✅ Files are in correct locations
6. ✅ Code compiles and runs without errors
7. ✅ Language switching works as expected
8. ✅ Default language is Chinese
9. ✅ Output prefix is "多头："
10. ✅ Professional analysis style maintained
11. ✅ All 5 strategy points preserved
12. ✅ Resource names completely localized
13. ✅ Memory system unchanged
14. ✅ File verification tests pass
15. ✅ Comments are in English
16. ✅ Function signature unchanged
17. ✅ No regression in existing functionality
18. ✅ Documentation is complete (this spec)
19. ✅ Bear researcher relationship documented
20. ✅ Ready for bear_researcher implementation (future)

---

## 14. Key Translation Decisions Reference

### 14.1 Strategy Points Translation

| English | Chinese | Rationale |
|---------|---------|-----------|
| Growth Potential | 增长潜力 | Standard financial term |
| Competitive Advantages | 竞争优势 | Standard financial term |
| Positive Indicators | 积极指标 | Standard financial term |
| Bear Counterpoints | 空头反驳点 | Market-specific terminology |
| Engagement | 参与度 | Maintains original meaning |

### 14.2 Resource Names Translation

| English | Chinese | Rationale |
|---------|---------|-----------|
| Market research report | 市场研究报告 | Complete localization |
| Social media sentiment report | 社交媒体情绪报告 | Complete localization |
| Latest world affairs news | 最新时事新闻 | Complete localization |
| Company fundamentals report | 公司基本面报告 | Complete localization |
| Conversation history of the debate | 辩论对话历史 | Complete localization |
| Last bear argument | 最后的空头论点 | Complete localization |
| Reflections from similar situations and lessons learned | 类似情况的反思和经验教训 | Complete localization |

### 14.3 Key Phrase Translations with Adjustments

| English | Literal | Adjusted Chinese | Rationale |
|---------|----------|------------------|-----------|
| engaging directly | 直接参与 | 直接回应 | More natural in Chinese debate context |
| conversational style | 对话风格 | 对话式表达 | Avoids awkwardness in Chinese |
| addressing concerns thoroughly | 彻底解决担忧 | 全面解决疑虑 | More natural Chinese |
| sound reasoning | 合理推理 | 合理推理 | Direct translation (natural) |
| debating effectively | 有效辩论 | 进行有效的辩论 | Slight adjustment for grammar |

### 14.4 Role and Prefix Terminology

| Context | English | Chinese | Rationale |
|---------|---------|---------|-----------|
| Prompt description | Bull Analyst | 看涨分析师 | Professional, literal |
| Output prefix | Bull Analyst: | 多头： | User choice, concise, market-standard |
| Bear counterpart | Bear Analyst | 空头分析师 | Parallel terminology |

---

## 15. Troubleshooting Guide

### 15.1 Common Issues and Solutions

**Issue 1: KeyError during variable substitution**
```
KeyError: 'market_research_report'
```
**Solution**: Verify all 7 variables are passed to `.format()` method with exact names

**Issue 2: Prompt file not found**
```
FileNotFoundError: Prompt file not found: prompts/zh/bull_researcher.md
```
**Solution**: Ensure prompt files exist in correct locations; verify directory structure

**Issue 3: Language not switching**
**Symptom**: Prompt always loads in English regardless of LANGUAGE variable
**Solution**: Verify LANGUAGE environment variable is set before calling `load_prompt_template()`

**Issue 4: Output prefix still in English**
**Symptom**: Output shows "Bull Analyst:" instead of "多头："
**Solution**: Verify line `argument = f"多头：{response.content}"` is correct in code

**Issue 5: Memory not retrieved**
**Symptom**: `past_memory_str` is empty
**Solution**: This is expected if no similar situations exist in memory; not an error

**Issue 6: Poor translation quality**
**Symptom**: Generated arguments don't sound natural in Chinese
**Solution**: Review prompt translation; ensure strategy points are clear; may need iteration

### 15.2 Debugging Tips

**Verify Prompt Loading**:
```python
from tradingagents.agents.utils.agent_utils import load_prompt_template
prompt = load_prompt_template('bull_researcher', 'zh')
print(prompt)  # Should show Chinese prompt with placeholders
```

**Verify Variable Substitution**:
```python
# Check if placeholders exist
assert '{market_research_report}' in prompt
# Try substitution
test_prompt = prompt.format(market_research_report='TEST')
assert 'TEST' in test_prompt
```

**Verify Language Setting**:
```python
import os
print(f"LANGUAGE={os.environ.get('LANGUAGE', 'not set')}")
```

---

## 16. Relationship with Other Components

### 16.1 Dependency Diagram

```
bull_researcher.py
    ├── load_prompt_template() [from agent_utils.py]
    │   └── prompts/{LANGUAGE}/bull_researcher.md
    ├── memory.get_memories() [provided by caller]
    └── llm.invoke() [provided by caller]

State Flow:
    └── investment_debate_state
        ├── history (accumulates all arguments)
        ├── bull_history (bull arguments only)
        ├── bear_history (bear arguments only)
        ├── current_response (latest argument)
        └── count (debate round number)

Reports Used (from state):
    ├── market_report [from market_analyst]
    ├── sentiment_report [from sentiment_analyst]
    ├── news_report [from news_analyst]
    └── fundamentals_report [from fundamentals_analyst]
```

### 16.2 Interaction with Bear Researcher

**Current State**: bear_researcher not yet implemented

**Future State** (after bear_researcher implementation):
```
Debate Flow:
1. bull_researcher generates initial argument
2. State stores in investment_debate_state.current_response
3. bear_researcher reads current_response and generates rebuttal
4. State updates with bear argument
5. Repeat for specified rounds
```

**Consistency Requirements** (Future):
- Both use `load_prompt_template()` infrastructure
- Both use LANGUAGE environment variable
- Both use localized prefixes ("多头：" and "空头：")
- Both use same memory system
- Both reference same reports (market, sentiment, news, fundamentals)
- Parallel structure in prompts (mirror strategies)

### 16.3 Integration with Main System

**How bull_researcher is Called**:
```python
# In main graph or orchestrator
bull_researcher = create_bull_researcher(llm, memory)
state = {
    "investment_debate_state": {...},
    "market_report": "...",
    "sentiment_report": "...",
    "news_report": "...",
    "fundamentals_report": "..."
}
result = bull_researcher(state)
```

**Output**:
```python
{
    "investment_debate_state": {
        "history": "...",
        "bull_history": "...",
        "bear_history": "...",
        "current_response": "多头：[argument]",
        "count": N
    }
}
```

---

## Document Metadata

**Version**: 1.0
**Date**: 2026-01-08
**Status**: Implementation Specification
**Scope**: bull_researcher only (小步快跑)
**Pattern**: Reuse market_analyst (003), news_analyst (004), fundamentals_analyst (005)
**Testing**: File verification only
**Documentation**: Complete specification (003 style)
**A-Share Specifics**: None (investment debate is universal)
**Interview Language**: Chinese (中文)
**Specification Language**: English (英文)
**Output Language**: Chinese (中文)

**Related Documents**:
- dev/plan/003-analyst-market.md (market_analyst specification)
- dev/plan/004-analyst-news-summary.md (news_analyst implementation summary)
- dev/plan/005-analyst-fundamentals.md (fundamentals_analyst specification)

**Future Tasks**:
- Implement bear_researcher using identical pattern
- Consider A-share specific debate enhancements
- Add debate testing and validation

---

**End of Specification**
