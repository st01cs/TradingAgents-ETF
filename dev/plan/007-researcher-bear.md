# Specification: Bear Researcher - Chinese A-Share Adaptation

## Executive Summary

Adapt the existing `bear_researcher.py` to support Chinese A-share market investment debate by:
1. Extracting and translating the English prompt to Chinese
2. Implementing externalized prompt management using existing infrastructure
3. Providing Chinese bear argument outputs
4. Ensuring complete symmetry and consistency with bull_researcher implementation

**Key Design Decisions:**
- **Translation Strategy**: Literal translation (直译优先) preserving original structure and professional analysis style - identical to bull_researcher
- **Scope**: Only modify `bear_researcher.py` and prompt files (小步快跑, 严格限制范围)
- **Symmetry**: Completely mirror bull_researcher (006) implementation pattern
- **Testing**: File verification only (no automated tests, no manual debate testing)
- **Documentation**: Complete specification document (this file)
- **A-Share Specifics**: No A-share specific considerations needed (pure translation, like bull_researcher)
- **Output Format**: "空头：{中文内容}" (completely Chinese prefix, symmetric with "多头：")

---

## 1. Current State Analysis

### 1.1 Existing Code Structure

**File**: `tradingagents/agents/researchers/bear_researcher.py`

**Current Implementation**:
```python
from langchain_core.messages import AIMessage
import time
import json


def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

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

        prompt = f"""You are a Bear Analyst making the case against investing in the stock. Your goal is to present a well-reasoned argument emphasizing risks, challenges, and negative indicators. Leverage the provided research and data to highlight potential downsides and counter bullish arguments effectively.

Key points to focus on:

- Risks and Challenges: Highlight factors like market saturation, financial instability, or macroeconomic threats that could hinder the stock's performance.
- Competitive Weaknesses: Emphasize vulnerabilities such as weaker market positioning, declining innovation, or threats from competitors.
- Negative Indicators: Use evidence from financial data, market trends, or recent adverse news to support your position.
- Bull Counterpoints: Critically analyze the bull argument with specific data and sound reasoning, exposing weaknesses or over-optimistic assumptions.
- Engagement: Present your argument in a conversational style, directly engaging with the bull analyst's points and debating effectively rather than simply listing facts.

Resources available:

Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bull argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}
Use this information to deliver a compelling bear argument, refute the bull's claims, and engage in a dynamic debate that demonstrates the risks and weaknesses of investing in the stock. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        response = llm.invoke(prompt)

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
```

**Key Components**:
1. **System Prompt**: Hardcoded English text (~330 words)
2. **Role**: Bear Analyst making case against stock investment
3. **5 Key Strategy Points**:
   - Risks and Challenges (风险和挑战)
   - Competitive Weaknesses (竞争劣势)
   - Negative Indicators (负面指标)
   - Bull Counterpoints (多头反驳点)
   - Engagement (参与度/辩论互动)
4. **Resources Available**: 5 types of reports + history + memories
5. **Variables**: `{market_research_report}`, `{sentiment_report}`, `{news_report}`, `{fundamentals_report}`, `{history}`, `{current_response}`, `{past_memory_str}`
6. **Output Format**: `f"Bear Analyst: {response.content}"`
7. **Memory System**: Uses `memory.get_memories()` to retrieve past lessons
8. **Debate Context**: Engages in back-and-forth with bull analyst

### 1.2 Infrastructure (Already Exists)

**Function**: `load_prompt_template(agent_name, language)` in `agent_utils.py`

**Features**:
- Loads prompts from `prompts/{language}/{agent_name}.md`
- Supports `LANGUAGE` environment variable (default: 'zh')
- Validates language codes ('zh', 'en')
- Provides clear error messages
- Already used by market_analyst, news_analyst, fundamentals_analyst, and bull_researcher

**Directories**:
```
prompts/
├── zh/
│   ├── market_analyst.md      # (already exists)
│   ├── news_analyst.md         # (already exists)
│   ├── fundamentals_analyst.md # (already exists)
│   └── bull_researcher.md      # (already exists)
└── en/
    ├── market_analyst.md      # (already exists)
    ├── news_analyst.md         # (already exists)
    ├── fundamentals_analyst.md # (already exists)
    └── bull_researcher.md      # (already exists)
```

### 1.3 Bull Researcher Implementation (Reference)

**Completed**: `bull_researcher` implementation (006) serves as template
- Translation: Literal (直译优先)
- Output prefix: "多头："
- All 7 placeholders preserved
- No A-share specific content
- File verification testing only

---

## 2. Target State Specification

### 2.1 Modified Code

**File**: `tradingagents/agents/researchers/bear_researcher.py`

**Changes**:
1. Import `load_prompt_template` from `agent_utils`
2. Replace hardcoded `prompt` with loaded template + variable substitution
3. Change output prefix from "Bear Analyst:" to "空头："
4. Keep all other logic unchanged

**Modified Code**:
```python
from langchain_core.messages import AIMessage
import time
import json
from tradingagents.agents.utils.agent_utils import load_prompt_template


def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

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
        prompt_template = load_prompt_template('bear_researcher')

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
        argument = f"空头：{response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
```

**Lines Modified**: ~10 lines
- Import: Add `load_prompt_template`
- Load prompt: `prompt_template = load_prompt_template('bear_researcher')`
- Variable substitution: Use `.format()` method
- Output prefix: Change to Chinese "空头："
- Add comments explaining changes

### 2.2 Prompt File Specifications

#### 2.2.1 `prompts/en/bear_researcher.md`

**Content**: Extract the original English prompt from current code

**Source Text**:
```markdown
You are a Bear Analyst making the case against investing in the stock. Your goal is to present a well-reasoned argument emphasizing risks, challenges, and negative indicators. Leverage the provided research and data to highlight potential downsides and counter bullish arguments effectively.

Key points to focus on:

- Risks and Challenges: Highlight factors like market saturation, financial instability, or macroeconomic threats that could hinder the stock's performance.
- Competitive Weaknesses: Emphasize vulnerabilities such as weaker market positioning, declining innovation, or threats from competitors.
- Negative Indicators: Use evidence from financial data, market trends, or recent adverse news to support your position.
- Bull Counterpoints: Critically analyze the bull argument with specific data and sound reasoning, exposing weaknesses or over-optimistic assumptions.
- Engagement: Present your argument in a conversational style, directly engaging with the bull analyst's points and debating effectively rather than simply listing facts.

Resources available:

Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bull argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}

Use this information to deliver a compelling bear argument, refute the bull's claims, and engage in a dynamic debate that demonstrates the risks and weaknesses of investing in the stock. You must also address reflections and learn from lessons and mistakes you made in the past.
```

#### 2.2.2 `prompts/zh/bear_researcher.md`

**Translation Strategy**: Literal translation (直译) with minor adjustments for natural Chinese flow - identical to bull_researcher approach

**Content**:
```markdown
你是一位看跌分析师，主张不投资该股票。你的目标是提出合理的论点，强调风险、挑战和负面指标。利用提供的研究和数据来突出潜在的不利因素，有效反驳看涨论点。

需要重点关注的关键点：

- 风险和挑战：突出可能阻碍股票表现的因素，如市场饱和、财务不稳定或宏观经济威胁。
- 竞争劣势：强调弱点，如市场地位较弱、创新下降或来自竞争对手的威胁。
- 负面指标：利用财务数据、市场趋势或近期不利新闻的证据来支持你的立场。
- 多头反驳点：用具体数据和合理推理批判性地分析多头论点，揭露弱点或过度乐观的假设。
- 参与度：采用对话式表达，直接回应多头分析师的观点，进行有效的辩论，而不是简单罗列事实。

可用资源：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新时事新闻：{news_report}
公司基本面报告：{fundamentals_report}
辩论对话历史：{history}
最后的多头论点：{current_response}
类似情况的反思和经验教训：{past_memory_str}

利用这些信息提出令人信服的空头论点，反驳多头的说法，参与动态辩论，展示投资该股票的风险和弱点。你还必须针对反思内容，并从过去的教训和错误中学习。
```

**Translation Notes**:
- "Bear Analyst" → "看跌分析师" (professional, literal translation, symmetric with "看涨分析师")
- "making the case against investing" → "主张不投资" (direct opposite of "主张投资")
- "risks, challenges, and negative indicators" → "风险、挑战和负面指标" (clear and precise)
- "Key points to focus on" → "需要重点关注的关键点" (identical to bull_researcher)
- "Risks and Challenges" → "风险和挑战" (standard financial term)
- "Competitive Weaknesses" → "竞争劣势" (direct opposite of "竞争优势")
- "Negative Indicators" → "负面指标" (direct opposite of "积极指标")
- "Bull Counterpoints" → "多头反驳点" (direct opposite of "空头反驳点")
- "Engagement" → "参与度" (identical to bull_researcher, maintains meaning)
- "conversational style" → "对话式表达" (identical to bull_researcher adjustment)
- "directly engaging" → "直接回应" (identical to bull_researcher adjustment)
- "debating effectively" → "进行有效的辩论" (identical to bull_researcher)
- "exposing weaknesses or over-optimistic assumptions" → "揭露弱点或过度乐观的假设" (literal translation)
- "Resources available" → "可用资源" (identical to bull_researcher)
- "Market research report" → "市场研究报告" (identical to bull_researcher)
- "Social media sentiment report" → "社交媒体情绪报告" (identical to bull_researcher)
- "Latest world affairs news" → "最新时事新闻" (identical to bull_researcher)
- "Company fundamentals report" → "公司基本面报告" (identical to bull_researcher)
- "Conversation history of the debate" → "辩论对话历史" (identical to bull_researcher)
- "Last bull argument" → "最后的多头论点" (direct opposite of "最后的空头论点")
- "Reflections from similar situations and lessons learned" → "类似情况的反思和经验教训" (identical to bull_researcher)
- "compelling bear argument" → "令人信服的空头论点" (natural Chinese)
- "refute the bull's claims" → "反驳多头的说法" (market terminology)
- "risks and weaknesses" → "风险和弱点" (direct translation)
- "learn from lessons and mistakes" → "从过去的教训和错误中学习" (identical to bull_researcher)

**What NOT to Change**:
- All variable placeholders: `{market_research_report}`, `{sentiment_report}`, `{news_report}`, `{fundamentals_report}`, `{history}`, `{current_response}`, `{past_memory_str}`
- Core logical structure of the prompt
- All 5 key strategy points
- Emphasis on risk-based arguments
- Memory and learning requirements
- Debate engagement style

**No A-Share Specific Considerations**:
- Investment debate logic is universal across markets
- No A-share specific guidance needed (like bull_researcher)
- Pure translation, no content adaptation
- Professional analysis style maintained

**Translation Quality Adjustments**:
- "directly engaging" → "直接回应" (identical to bull_researcher adjustment)
- "conversational style" → "对话式表达" (identical to bull_researcher adjustment)
- Other phrases: literal translation to preserve original meaning and structure

---

## 3. Implementation Tasks

### Phase 1: Extract English Prompt (Priority: High)
- [ ] Extract current `prompt` from `bear_researcher.py`
- [ ] Save to `prompts/en/bear_researcher.md`
- [ ] Verify file is created correctly
- [ ] Verify all placeholders are preserved

### Phase 2: Translate to Chinese (Priority: High)
- [ ] Translate English prompt to Chinese (literal translation with minor adjustments)
- [ ] Save to `prompts/zh/bear_researcher.md`
- [ ] Verify all placeholders are preserved
- [ ] Verify translation quality (professional analysis style maintained)
- [ ] Ensure no A-share specific content added
- [ ] Verify resource names are identical to bull_researcher
- [ ] Verify output prefix is "空头："
- [ ] Verify translation symmetry with bull_researcher

### Phase 3: Modify Code (Priority: High)
- [ ] Add `load_prompt_template` to imports in `bear_researcher.py`
- [ ] Load prompt template using `load_prompt_template('bear_researcher')`
- [ ] Implement variable substitution using `.format()` method
- [ ] Change output prefix to "空头："
- [ ] Add explanatory comments (in English, consistent with other files)
- [ ] Verify no other code changes needed
- [ ] Verify all 7 variables are substituted correctly
- [ ] Verify memory system logic is unchanged

### Phase 4: Verification (Priority: High)
- [ ] Verify prompt files exist in correct locations
- [ ] Verify code compiles without errors
- [ ] Verify `load_prompt_template` works for 'bear_researcher'
- [ ] Check that language switching works via `LANGUAGE` env var
- [ ] Verify default language is Chinese (zh)
- [ ] Verify output prefix is correct
- [ ] Verify all placeholders work correctly
- [ ] Verify symmetry with bull_researcher

### Phase 5: Documentation (Priority: High)
- [ ] Update this plan document if needed
- [ ] Add inline comments in code (already done in Phase 3)
- [ ] Document symmetry with bull_researcher
- [ ] Add usage examples if needed

---

## 4. Behavior Specifications

### 4.1 Language Selection

**Mechanism**: Use existing `load_prompt_template()` function

**Logic**:
1. Check `LANGUAGE` environment variable
2. If not set → default to 'zh' (Chinese)
3. Load prompt from: `prompts/{LANGUAGE}/bear_researcher.md`
4. Substitute variables using `.format()` method
5. Invoke LLM with constructed prompt

**Environment Variable Values**:
- `LANGUAGE=zh` → Load Chinese prompt, output "空头：{中文内容}"
- `LANGUAGE=en` → Load English prompt, output "Bear Analyst: {English content}"
- Not set → Default to Chinese prompt

**Default Behavior**: Chinese (zh) - consistent with bull_researcher and all other analysts

### 4.2 Report Output

**Language**: Fully Chinese argument (when LANGUAGE=zh)

**Output Format**:
```
空头：[中文的看跌论点内容]
```

**Example Output** (hypothetical):
```
空头：尽管该公司近期表现良好，但必须警惕几个关键风险。首先，行业竞争日趋激烈，新进入者正在侵蚀市场份额，公司的创新速度明显放缓。其次，财务数据显示利润率连续三个季度下滑，现金流状况恶化。虽然多头强调增长潜力，但这种增长是建立在高负债基础上的，一旦利率上升，偿债压力将严重影响盈利能力。从历史类似情况来看，过度扩张的公司往往在面临行业拐点时出现断崖式下跌。
```

**Components**:
1. **Professional Analysis Style** (Chinese)
   - Risk-based arguments (基于风险的论证)
   - Challenges emphasis (强调挑战)
   - Competitive weaknesses (竞争劣势)
   - Negative indicators (负面指标)

2. **Debate Engagement** (Chinese)
   - Direct response to bull arguments (直接回应多头论点)
   - Conversational style (对话式表达)
   - Effective debating (有效辩论)
   - Not just listing facts (不是简单罗列事实)

3. **Learning from History** (Chinese)
   - Address reflections (针对反思内容)
   - Learn from past lessons (从过去的教训中学习)
   - Avoid past mistakes (避免过去的错误)

**Language Consistency**:
- Output prefix: "空头：" (completely Chinese, symmetric with "多头：")
- Argument content: Fully Chinese
- Resource references in prompt: Chinese (市场研究报告, etc.)
- Strategy points: Chinese (风险和挑战, etc.)

### 4.3 Variable Substitution

**Variables to Substitute** (7 total - identical to bull_researcher):
1. `{market_research_report}` - Market research report content
2. `{sentiment_report}` - Social media sentiment report content
3. `{news_report}` - Latest world affairs news content
4. `{fundamentals_report}` - Company fundamentals report content
5. `{history}` - Conversation history of the debate
6. `{current_response}` - Last bull argument
7. `{past_memory_str}` - Reflections from similar situations

**Substitution Method**: Python `.format()` method

**Example**:
```python
prompt_template = load_prompt_template('bear_researcher')
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
- **No special handling needed** for language mixing (identical to bull_researcher)
- If past memories are in English and current prompt is in Chinese, LLM will handle automatically
- LLM can understand and integrate multilingual content
- Future memories will be in Chinese (when LANGUAGE=zh)

**Rationale**: System language consistency will emerge naturally over time as all components use Chinese

### 4.5 Historical Context Handling

**Debate History Variables**:
- `{history}` - Full debate conversation history
- `{current_response}` - Last bull argument to respond to

**Language Mixing**:
- **No special handling needed** (identical to bull_researcher)
- If history contains English arguments and current prompt is in Chinese, LLM will:
  - Understand English historical context
  - Generate response in Chinese
  - Reference previous points appropriately

**Future Consistency**:
- Once LANGUAGE=zh is set, all future debate exchanges will be in Chinese
- Output will accumulate in Chinese naturally
- Language consistency emerges without additional logic

### 4.6 Symmetry with Bull Researcher

**Structural Symmetry**:
- Identical code structure and modifications
- Same variable substitution method
- Same memory system integration
- Same output format (except prefix)

**Translation Symmetry**:
- Output prefixes: "多头：" ↔ "空头："
- Strategy points: Direct opposites
- Resource names: Identical
- Translation approach: Identical

**Functional Symmetry**:
- Both use 7 variables
- Both reference same reports
- Both use memory system
- Both engage in debate

---

## 5. Testing Strategy

### 5.1 File Verification Tests

**Test Cases** (identical to bull_researcher):
1. **English Prompt File Exists**
   ```bash
   test -f prompts/en/bear_researcher.md
   ```

2. **Chinese Prompt File Exists**
   ```bash
   test -f prompts/zh/bear_researcher.md
   ```

3. **Prompt Loading Works**
   ```python
   from tradingagents.agents.utils.agent_utils import load_prompt_template

   # Test English
   prompt_en = load_prompt_template('bear_researcher', 'en')
   assert 'Bear Analyst' in prompt_en
   assert '{market_research_report}' in prompt_en

   # Test Chinese
   prompt_zh = load_prompt_template('bear_researcher', 'zh')
   assert '看跌分析师' in prompt_zh
   assert '{market_research_report}' in prompt_zh
   assert '空头：' not in prompt_zh  # Prefix is in code, not prompt
   ```

4. **Default Language is Chinese**
   ```python
   import os
   os.environ.pop('LANGUAGE', None)
   prompt = load_prompt_template('bear_researcher')
   assert '看跌分析师' in prompt
   ```

5. **All Placeholders Preserved**
   ```python
   prompt_zh = load_prompt_template('bear_researcher', 'zh')
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
   prompt_zh = load_prompt_template('bear_researcher', 'zh')
   assert 'A股' not in prompt_zh
   assert '涨跌停' not in prompt_zh
   assert 'T+1' not in prompt_zh
   ```

7. **Resource Names Localized**
   ```python
   prompt_zh = load_prompt_template('bear_researcher', 'zh')
   assert '市场研究报告：' in prompt_zh
   assert '社交媒体情绪报告：' in prompt_zh
   assert '最新时事新闻：' in prompt_zh
   assert '公司基本面报告：' in prompt_zh
   ```

8. **Variable Substitution Works**
   ```python
   prompt_template = load_prompt_template('bear_researcher', 'zh')
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
   assert '看跌分析师' in prompt
   ```

9. **Symmetry with Bull Researcher**
   ```python
   # Verify resource names are identical
   bull_prompt = load_prompt_template('bull_researcher', 'zh')
   bear_prompt = load_prompt_template('bear_researcher', 'zh')
   assert '市场研究报告：' in bull_prompt and '市场研究报告：' in bear_prompt
   ```

10. **Code Verification**
    ```python
    import ast
    with open('tradingagents/agents/researchers/bear_researcher.py', 'r') as f:
        code = f.read()
        # Verify no syntax errors
        ast.parse(code)
        # Verify import
        assert 'load_prompt_template' in code
        # Verify output prefix
        assert '空头：' in code
        # Verify .format() method
        assert '.format(' in code
    ```

### 5.2 Code Verification

**Checks**:
1. Import statement added correctly
2. No syntax errors
3. All placeholders preserved in code
4. Function signature unchanged (still accepts `llm` and `memory`)
5. Memory system logic unchanged
6. All 7 variables substituted correctly
7. Output prefix changed to "空头："
8. Comments are in English (consistent with codebase)
9. Code structure identical to bull_researcher

### 5.3 No Automated Testing

**Scope Limitation**:
- No unit tests for bear_researcher debate functionality
- No integration tests with bull_researcher
- No manual debate testing
- Only file verification to ensure basic correctness

**Rationale**:
- Follows "小步快跑" (small steps, fast iteration) principle
- Consistent with bull_researcher (006), news_analyst (004), and fundamentals_analyst (005) approach
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
| Asymmetry with bull_researcher | Low | Reference bull_researcher implementation; verify translation symmetry |

### Operational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing A-share considerations | Very Low | Investment debate logic is universal; not market-specific like news analysis |
| Debate style too formal for Chinese context | Low | Literal translation preserves professional analysis style; minor adjustments for natural flow |
| Output prefix "空头：" unfamiliar to users | Low | Standard Chinese market terminology; symmetric with "多头：" |
| Language switching issues | Low | Reuse existing tested infrastructure from all previous implementations |
| Inconsistent behavior with bull_researcher | Low | Use identical implementation pattern; verify symmetry |
| Users unaware of LANGUAGE variable | Medium | Consistent with existing analysts; already documented in .env.example from previous work |

### Translation Quality Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| "exposing weaknesses" translation too literal | Low | Use "揭露弱点" which is natural in Chinese debate context |
| "over-optimistic assumptions" translation awkward | Low | Use "过度乐观的假设" which is clear and precise |
| Resource names inconsistent with bull_researcher | Low | Use identical resource names from bull_researcher |
| Professional analysis style lost in translation | Low | Maintain literal translation of all strategy points and professional terminology |

### Symmetry Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Strategy points not symmetric with bull_researcher | Medium | Ensure direct opposites in translation; verify in spec |
| Output format inconsistent | Low | Use symmetric output prefix "空头：" |
| Variable substitution different | Very Low | Use identical code structure from bull_researcher |
| Debate flow breaks | Low | Maintain identical logic and state management |

---

## 7. Design Rationale

### 7.1 Why Complete Symmetry with Bull Researcher?

**Reasoning**:
- Ensures consistent debate flow between bull and bear arguments
- Reduces cognitive load for developers maintaining code
- Makes system behavior predictable and understandable
- Facilitates future enhancements to debate system
- Validated approach from bull_researcher implementation
- User explicitly requested consistency during interview

### 7.2 Why "空头：" as Output Prefix?

**Reasoning**:
- User explicitly chose "空头：" during interview
- Direct symmetric opposite to "多头："
- Standard Chinese market terminology
- Concise and widely understood
- Consistent with professional Chinese trading discourse
- Maintains debate clarity

### 7.3 Why Literal Translation?

**Reasoning**:
- Identical to bull_researcher approach
- Preserves original analysis framework and debate logic
- Ensures consistent behavior between languages
- Reduces risk of introducing errors
- Validated approach from all previous analyst implementations
- Investment debate principles are universal
- Professional analysis style transcends language boundaries

### 7.4 Why Minor Adjustments for Natural Flow?

**Reasoning**:
- "directly engaging" → "直接回应" is more natural in Chinese debate context
- "conversational style" → "对话式表达" avoids awkwardness
- Preserves core meaning while fitting Chinese linguistic patterns
- User approved "微调表达，更符合中文习惯" during interview
- Identical to bull_researcher adjustments
- Professional analysis style maintained

### 7.5 Why No A-Share Specific Considerations?

**Reasoning**:
- Investment debate logic is universal across markets
- Bull/bear arguments work the same way globally
- No market-specific debate mechanics needed
- Keeps prompt simpler and more focused
- Consistent with bull_researcher (006) and fundamentals_analyst (005) approach
- User explicitly requested "不添加任何 A 股特定内容"

### 7.6 Why No Special Handling for Language Mixing?

**Reasoning**:
- LLMs (especially GPT-4) handle multilingual context well
- Language consistency will emerge naturally over time
- No need for complex language detection/conversion logic
- Reduces system complexity
- Past memories (even if English) provide value regardless of language
- Future debates will be consistent in Chinese once LANGUAGE=zh is set
- Identical to bull_researcher approach

### 7.7 Why Only File Verification Testing?

**Reasoning**:
- Follows "小步快跑" principle
- Consistent with bull_researcher (006), news_analyst (004), and fundamentals_analyst (005) approach
- Infrastructure change is minimal (reuses existing components)
- Debate testing is complex and time-consuming
- Fast iteration, validate later if needed
- Focus on prompt translation quality rather than functional testing

### 7.8 Why Complete Specification Document?

**Reasoning**:
- User explicitly requested "完整详细 spec（006 风格）" during interview
- Provides comprehensive documentation
- Useful for future reference
- Consistent with bull_researcher (006) and market_analyst (003) approach
- Facilitates understanding of bull-bear symmetry
- Documents relationship with bull_researcher

### 7.9 Why Comply with Previous Patterns?

**Reasoning**:
- Consistent approach across all analysts and researchers
- Proven to work successfully four times already
- Reduces development time
- Easier maintenance and understanding
- Established pattern in codebase
- User explicitly requested to "参考 @dev/plan/006-researcher-bull.md 的做法，保持风格一致"

### 7.10 Why Implement Independently but Reference Bull Researcher?

**Reasoning**:
- Bear researcher should be able to function independently
- However, bull_researcher provides proven template
- Reduces development time and risk
- Ensures symmetry and consistency
- User chose "参考但独立" during interview
- Best balance between independence and efficiency

---

## 8. Comparison with Bull Researcher

### 8.1 Structural Similarities

| Aspect | bull_researcher (006) | bear_researcher (007) |
|--------|------------------------|------------------------|
| Use `load_prompt_template()` | ✅ | ✅ |
| External prompt files | ✅ | ✅ |
| LANGUAGE environment variable | ✅ | ✅ |
| Default to Chinese | ✅ | ✅ |
| Literal translation | ✅ | ✅ |
| File verification testing | File only | File only |
| Code comments language | English | English |
| 7 variables | ✅ | ✅ |
| Memory system integration | ✅ | ✅ |
| Variable substitution with `.format()` | ✅ | ✅ |

### 8.2 Functional Symmetries

| Aspect | bull_researcher (006) | bear_researcher (007) |
|--------|------------------------|------------------------|
| Role | Advocate for investing | Make case against investing |
| Emphasis | Growth, advantages, positives | Risks, weaknesses, negatives |
| Output prefix | "多头：" | "空头：" |
| Strategy points | 5 points | 5 points (direct opposites) |
| Resources used | 5 types + history + memories | 5 types + history + memories |
| Debate context | Engages with bear | Engages with bull |
| Learning from past | ✅ | ✅ |

### 8.3 Translation Symmetries

| English | bull_researcher | bear_researcher | Relationship |
|---------|----------------|-----------------|--------------|
| Role name | 看涨分析师 | 看跌分析师 | Direct opposites |
| Output prefix | 多头： | 空头： | Direct opposites |
| Strategy point 1 | 增长潜力 | 风险和挑战 | Direct opposites |
| Strategy point 2 | 竞争优势 | 竞争劣势 | Direct opposites |
| Strategy point 3 | 积极指标 | 负面指标 | Direct opposites |
| Strategy point 4 | 空头反驳点 | 多头反驳点 | Direct opposites |
| Strategy point 5 | 参与度 | 参与度 | Identical |
| Resource 1 | 市场研究报告 | 市场研究报告 | Identical |
| Resource 2 | 社交媒体情绪报告 | 社交媒体情绪报告 | Identical |
| Resource 3 | 最新时事新闻 | 最新时事新闻 | Identical |
| Resource 4 | 公司基本面报告 | 公司基本面报告 | Identical |
| History reference | 辩论对话历史 | 辩论对话历史 | Identical |
| Last argument | 最后的空头论点 | 最后的多头论点 | Direct opposites |
| Memories | 类似情况的反思和经验教训 | 类似情况的反思和经验教训 | Identical |

### 8.4 Unique Characteristics

Despite high symmetry, each has unique role:
- **bull_researcher**: Emphasizes opportunities, growth potential, competitive advantages
- **bear_researcher**: Emphasizes risks, challenges, competitive weaknesses

Both maintain:
- Professional analysis style
- Evidence-based arguments
- Debate engagement
- Learning from past mistakes

---

## 9. Implementation Details

### 9.1 File Creation Checklist

**prompts/en/bear_researcher.md**:
- [ ] Extracted from current code
- [ ] All text preserved verbatim
- [ ] All 7 placeholders preserved: `{market_research_report}`, `{sentiment_report}`, `{news_report}`, `{fundamentals_report}`, `{history}`, `{current_response}`, `{past_memory_str}`
- [ ] UTF-8 encoding
- [ ] Contains all 5 strategy points
- [ ] Contains resource descriptions
- [ ] Contains learning and reflection requirements

**prompts/zh/bear_researcher.md**:
- [ ] Translated from English version (literal translation with minor adjustments)
- [ ] No A-share considerations added
- [ ] All 7 placeholders preserved
- [ ] Professional analysis style maintained
- [ ] All 5 strategy points translated
- [ ] Resource names identical to bull_researcher
- [ ] UTF-8 encoding
- [ ] Markdown formatting correct
- [ ] Natural Chinese flow for "directly engaging" and "conversational style"
- [ ] Symmetry with bull_researcher verified

### 9.2 Code Modification Checklist

**bear_researcher.py**:
- [ ] Import added: `load_prompt_template`
- [ ] Prompt loaded from file using `load_prompt_template('bear_researcher')`
- [ ] Variable substitution implemented using `.format()` method
- [ ] All 7 variables substituted correctly
- [ ] Output prefix changed to "空头："
- [ ] Comments added explaining changes (in English)
- [ ] Memory system logic unchanged
- [ ] LLM invocation unchanged
- [ ] State management unchanged
- [ ] No syntax errors
- [ ] Function signature unchanged (`llm`, `memory`)
- [ ] Code structure identical to bull_researcher

### 9.3 Variable Substitution Implementation

**Before** (original code):
```python
prompt = f"""You are a Bear Analyst...
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
...
"""
```

**After** (new code):
```python
# Load prompt from external file (supports multi-language)
# Note: Uses existing load_prompt_template() infrastructure
prompt_template = load_prompt_template('bear_researcher')

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
- Identical to bull_researcher implementation

---

## 10. Success Criteria

The implementation is considered complete when:

1. ✅ English prompt file exists at `prompts/en/bear_researcher.md`
2. ✅ Chinese prompt file exists at `prompts/zh/bear_researcher.md`
3. ✅ `bear_researcher.py` loads prompts from external files
4. ✅ `LANGUAGE` environment variable controls language selection
5. ✅ Default language is Chinese when `LANGUAGE` is not set
6. ✅ All 7 placeholders preserved in both language versions
7. ✅ Code compiles and runs without errors
8. ✅ File verification tests pass (all 10 tests)
9. ✅ No A-share specific content added
10. ✅ Resource names identical to bull_researcher
11. ✅ Output prefix changed to "空头："
12. ✅ Variable substitution works correctly
13. ✅ Memory system logic unchanged
14. ✅ Professional analysis style maintained in translation
15. ✅ All 5 strategy points preserved
16. ✅ Debate engagement requirements preserved
17. ✅ Learning from past requirements preserved
18. ✅ Comments are in English
19. ✅ No syntax errors
20. ✅ Function signature unchanged
21. ✅ Complete symmetry with bull_researcher
22. ✅ Translation forms mirror opposites with bull_researcher

---

## 11. Future Enhancements (Out of Scope)

### 11.1 Bull-Bear Debate System Optimization

**Primary Future Task**: Optimize the interaction between bull_researcher and bear_researcher

**Key Considerations**:
- Ensure smooth debate flow
- Balance argument strengths
- Prevent repetitive arguments
- Add debate stage awareness
- Implement debate scoring mechanisms

### 11.2 Enhanced Debate Features

**Possible Future Enhancements**:
- Add debate stage awareness (opening, rebuttal, closing)
- Implement structured argument scoring
- Add debate moderator agent
- Multi-round debate history summarization
- Debate outcome prediction
- Sentiment-aware argument generation

### 11.3 A-Share Specific Debate Considerations

**Possible Future Enhancements**:
- Add A-share market-specific debate points (policy impact, etc.)
- Incorporate price limit effects into bull/bear arguments
- Add retail vs institutional investor perspectives
- Consider T+1 trading rule implications
- Add sector rotation analysis

### 11.4 Testing and Validation

**Possible Future Enhancements**:
- Add unit tests for bear_researcher functionality
- Add integration tests with bull_researcher
- Manual debate testing with real stocks
- Automated debate quality metrics
- Debate outcome accuracy validation

**Note**: These are explicitly out of scope for current implementation. Current task is limited to bear_researcher only, following "小步快跑" principle.

---

## 12. Timeline & Dependencies

**Dependencies**:
- None (infrastructure already exists from previous implementations, including bull_researcher)

**Estimated Complexity**: Low-Medium
- Extract English prompt: 10 minutes
- Translate to Chinese: 2-3 hours (careful translation of all 5 strategy points and debate-specific language)
- Modify code: 30 minutes (variable substitution logic, identical to bull_researcher)
- Verification: 30 minutes (7 placeholders to verify, symmetry checks)
- Documentation: 2 hours (complete spec as requested)

**Total Estimated Effort**: 6-9 hours

**Complexity Breakdown**:
- Identical to bull_researcher (006) in terms of documentation detail
- More complex translation than fundamentals_analyst (005) due to debate-specific terminology
- More complex variable substitution (7 variables vs 4 in analysts)
- Simpler than market_analyst in terms of testing (file verification only)
- Faster than bull_researcher due to established template

**Parallel Work Opportunities**:
- Translation can be done in parallel with code modification
- File verification can be done in parallel with documentation

---

## 13. Acceptance Criteria

The implementation is accepted when:

1. ✅ Both prompt files are created and contain correct content
2. ✅ Code modification follows the pattern from bull_researcher
3. ✅ All 7 placeholders are preserved and work correctly
4. ✅ No A-share specific content added
5. ✅ Files are in correct locations
6. ✅ Code compiles and runs without errors
7. ✅ Language switching works as expected
8. ✅ Default language is Chinese
9. ✅ Output prefix is "空头："
10. ✅ Professional analysis style maintained
11. ✅ All 5 strategy points preserved
12. ✅ Resource names identical to bull_researcher
13. ✅ Memory system unchanged
14. ✅ File verification tests pass (all 10 tests)
15. ✅ Comments are in English
16. ✅ Function signature unchanged
17. ✅ No regression in existing functionality
18. ✅ Documentation is complete (this spec)
19. ✅ Symmetry with bull_researcher verified
20. ✅ Translation forms mirror opposites with bull_researcher
21. ✅ Ready for integrated debate testing (future)
22. ✅ Code structure identical to bull_researcher

---

## 14. Key Translation Decisions Reference

### 14.1 Strategy Points Translation (Symmetric with Bull Researcher)

| English (Bull) | Chinese (Bull) | English (Bear) | Chinese (Bear) | Relationship |
|----------------|----------------|----------------|-----------------|--------------|
| Growth Potential | 增长潜力 | Risks and Challenges | 风险和挑战 | Direct opposites |
| Competitive Advantages | 竞争优势 | Competitive Weaknesses | 竞争劣势 | Direct opposites |
| Positive Indicators | 积极指标 | Negative Indicators | 负面指标 | Direct opposites |
| Bear Counterpoints | 空头反驳点 | Bull Counterpoints | 多头反驳点 | Direct opposites |
| Engagement | 参与度 | Engagement | 参与度 | Identical |

### 14.2 Resource Names Translation (Identical to Bull Researcher)

| English | Chinese (Both) | Rationale |
|---------|----------------|-----------|
| Market research report | 市场研究报告 | Complete localization, identical |
| Social media sentiment report | 社交媒体情绪报告 | Complete localization, identical |
| Latest world affairs news | 最新时事新闻 | Complete localization, identical |
| Company fundamentals report | 公司基本面报告 | Complete localization, identical |
| Conversation history of the debate | 辩论对话历史 | Complete localization, identical |
| Last [bull/bear] argument | 最后的[多头/空头]论点 | Context-dependent, symmetric |
| Reflections from similar situations and lessons learned | 类似情况的反思和经验教训 | Complete localization, identical |

### 14.3 Key Phrase Translations with Adjustments (Identical to Bull Researcher)

| English | Literal | Adjusted Chinese | Rationale |
|---------|----------|------------------|-----------|
| directly engaging | 直接参与 | 直接回应 | More natural in Chinese debate context |
| conversational style | 对话风格 | 对话式表达 | Avoids awkwardness in Chinese |
| addressing concerns | 解决担忧 | 解决疑虑/揭露弱点 | Context-dependent |
| sound reasoning | 合理推理 | 合理推理 | Direct translation (natural) |
| debating effectively | 有效辩论 | 进行有效的辩论 | Slight adjustment for grammar |
| exposing weaknesses | 揭露弱点 | 揭露弱点 | Direct translation (natural) |
| over-optimistic assumptions | 过度乐观的假设 | 过度乐观的假设 | Direct translation (clear) |

### 14.4 Role and Prefix Terminology (Symmetric)

| Context | English | Chinese (Bull) | Chinese (Bear) | Relationship |
|---------|---------|----------------|-----------------|--------------|
| Prompt description | Bull Analyst | 看涨分析师 | - | Professional, literal |
| Prompt description | Bear Analyst | - | 看跌分析师 | Professional, literal |
| Output prefix | Bull Analyst: | 多头： | - | User choice, concise |
| Output prefix | Bear Analyst: | - | 空头： | Symmetric with bull |

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
FileNotFoundError: Prompt file not found: prompts/zh/bear_researcher.md
```
**Solution**: Ensure prompt files exist in correct locations; verify directory structure

**Issue 3: Language not switching**
**Symptom**: Prompt always loads in English regardless of LANGUAGE variable
**Solution**: Verify LANGUAGE environment variable is set before calling `load_prompt_template()`

**Issue 4: Output prefix still in English**
**Symptom**: Output shows "Bear Analyst:" instead of "空头："
**Solution**: Verify line `argument = f"空头：{response.content}"` is correct in code

**Issue 5: Memory not retrieved**
**Symptom**: `past_memory_str` is empty
**Solution**: This is expected if no similar situations exist in memory; not an error

**Issue 6: Poor translation quality**
**Symptom**: Generated arguments don't sound natural in Chinese
**Solution**: Review prompt translation; ensure strategy points are clear; may need iteration

**Issue 7: Asymmetry with bull_researcher**
**Symptom**: Debate flow seems inconsistent or output format differs
**Solution**: Verify translation mirrors bull_researcher; check resource names and strategy points

### 15.2 Debugging Tips

**Verify Prompt Loading**:
```python
from tradingagents.agents.utils.agent_utils import load_prompt_template
prompt = load_prompt_template('bear_researcher', 'zh')
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

**Verify Symmetry with Bull Researcher**:
```python
bull_prompt = load_prompt_template('bull_researcher', 'zh')
bear_prompt = load_prompt_template('bear_researcher', 'zh')
# Check resource names are identical
assert '市场研究报告：' in bull_prompt and '市场研究报告：' in bear_prompt
# Check output prefixes are symmetric
# (This is in code, not in prompts)
```

---

## 16. Relationship with Other Components

### 16.1 Dependency Diagram

```
bear_researcher.py
    ├── load_prompt_template() [from agent_utils.py]
    │   └── prompts/{LANGUAGE}/bear_researcher.md
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

Symmetric Relationship:
    └── bull_researcher.py
        ├── Identical structure
        ├── Mirror opposite strategy points
        └── Same resources and variables
```

### 16.2 Interaction with Bull Researcher

**Current State**: bull_researcher already implemented (006)

**Debate Flow** (current and future):
```
Debate Flow:
1. bull_researcher generates initial argument
2. State stores in investment_debate_state.current_response
3. bear_researcher reads current_response and generates rebuttal
4. State updates with bear argument
5. Repeat for specified rounds
```

**Symmetry Requirements** (Current):
- Both use `load_prompt_template()` infrastructure ✅
- Both use LANGUAGE environment variable ✅
- Both use localized prefixes ("多头：" and "空头：") ✅
- Both use same memory system ✅
- Both reference same reports (market, sentiment, news, fundamentals) ✅
- Parallel structure in prompts (mirror strategies) ✅
- Both have 7 variables ✅
- Both use `.format()` for substitution ✅

### 16.3 Integration with Main System

**How bear_researcher is Called**:
```python
# In main graph or orchestrator
bear_researcher = create_bear_researcher(llm, memory)
state = {
    "investment_debate_state": {...},
    "market_report": "...",
    "sentiment_report": "...",
    "news_report": "...",
    "fundamentals_report": "..."
}
result = bear_researcher(state)
```

**Output**:
```python
{
    "investment_debate_state": {
        "history": "...",
        "bull_history": "...",
        "bear_history": "...",
        "current_response": "空头：[argument]",
        "count": N
    }
}
```

---

## Document Metadata

**Version**: 1.0
**Date**: 2026-01-08
**Status**: Implementation Specification
**Scope**: bear_researcher only (小步快跑)
**Pattern**: Mirror bull_researcher (006), follow news_analyst (004), fundamentals_analyst (005)
**Testing**: File verification only
**Documentation**: Complete specification (006 style)
**A-Share Specifics**: None (investment debate is universal)
**Interview Language**: Chinese (中文)
**Specification Language**: English (英文)
**Output Language**: Chinese (中文)

**Related Documents**:
- dev/plan/003-analyst-market.md (market_analyst specification)
- dev/plan/004-analyst-news-summary.md (news_analyst implementation summary)
- dev/plan/005-analyst-fundamentals.md (fundamentals_analyst specification)
- dev/plan/006-researcher-bull.md (bull_researcher specification) - PRIMARY REFERENCE

**Future Tasks**:
- Optimize bull-bear debate system interaction
- Add A-share specific debate enhancements
- Add debate testing and validation

---

**End of Specification**
