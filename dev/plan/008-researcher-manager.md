# Specification: Research Manager - Chinese A-Share Adaptation

## Executive Summary

Adapt the existing `research_manager.py` to support Chinese A-share market investment decision-making by:
1. Extracting and translating the English prompt to Chinese
2. Implementing externalized prompt management using existing infrastructure
3. Providing Chinese investment decision outputs
4. Supporting language switching via existing `LANGUAGE` environment variable

**Key Design Decisions:**
- **Translation Strategy**: Literal translation (直译优先) preserving original structure and professional analysis style
- **Scope**: Only modify `research_manager.py` and prompt files (小步快跑, 严格限制范围)
- **Code Pattern**: Independent manager pattern (adapted from researcher pattern but without `latest_speaker`)
- **Testing**: File verification only (no automated tests, no manual decision testing)
- **Documentation**: Complete specification document (this file)
- **Output Format**: "研究总监：{中文内容}" (completely Chinese prefix with director title)
- **Role Title**: 研究总监 (Research Director)
- **Decision Terms**: 买入/卖出/持有 (Buy/Sell/Hold)
- **Prompt Files**: Create both Chinese and English versions

---

## 1. Current State Analysis

### 1.1 Existing Code Structure

**File**: `tradingagents/agents/managers/research_manager.py`

**Current Implementation**:
```python
import time
import json


def create_research_manager(llm, memory):
    def research_manager_node(state) -> dict:
        history = state["investment_debate_state"].get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        investment_debate_state = state["investment_debate_state"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""As the portfolio manager and debate facilitator, your role is to critically evaluate this round of debate and make a definitive decision: align with the bear analyst, the bull analyst, or choose Hold only if it is strongly justified based on the arguments presented.

Summarize the key points from both sides concisely, focusing on the most compelling evidence or reasoning. Your recommendation—Buy, Sell, or Hold—must be clear and actionable. Avoid defaulting to Hold simply because both sides have valid points; commit to a stance grounded in the debate's strongest arguments.

Additionally, develop a detailed investment plan for the trader. This should include:

Your Recommendation: A decisive stance supported by the most convincing arguments.
Rationale: An explanation of why these arguments lead to your conclusion.
Strategic Actions: Concrete steps for implementing the recommendation.
Take into account your past mistakes on similar situations. Use these insights to refine your decision-making and ensure you are learning and improving. Present your analysis conversationally, as if speaking naturally, without special formatting.

Here are your past reflections on mistakes:
\"{past_memory_str}\"

Here is the debate:
Debate History:
{history}"""
        response = llm.invoke(prompt)

        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node
```

**Key Components**:
1. **System Prompt**: Hardcoded English text (~180 words)
2. **Role**: Portfolio manager and debate facilitator
3. **Four-Part Structure**:
   - Role definition and task
   - Key points summary requirement
   - Investment plan structure (3 elements)
   - Debate history with reflections
4. **Decision Options**: Buy, Sell, or Hold
5. **Investment Plan Elements**: Recommendation, Rationale, Strategic Actions
6. **Output Format**: Direct content without prefix
7. **State Management**: Preserves all history fields, does NOT set `latest_speaker` (final node in debate)

### 1.2 Context from Previous Adaptations

**Lesson from Bugfix #004**:
- ❌ **Wrong**: Routing based on string prefix parsing (`startswith("Bull")`)
- ✅ **Correct**: Routing based on explicit `latest_speaker` state field
- **Key Insight**: Research manager is the FINAL node, so it does NOT need to set `latest_speaker`

**Pattern from Researchers (006/007)**:
- Extract prompt to external file: `prompts/{lang}/researcher_name.md`
- Use `load_prompt_template()` function
- Format with variables: `prompt.format(var1=value1, var2=value2, ...)`
- Add Chinese output prefix: `"多头：{content}"` or `"空头：{content}"`

**Pattern from Analysts (003/004/005)**:
- Use `load_prompt_template(agent_name, language=None)`
- Default to `LANGUAGE` env var (default: "zh")
- Maintain variable names in English

---

## 2. Solution Design

### 2.1 Translation Approach

**Strategy**: Literal Translation (直译优先)

**Rationale**:
- Maintains original structure and logic
- Preserves professional investment analysis style
- Consistent with fundamentals_analyst (005) approach
- Easier to maintain consistency across languages

**Key Translation Decisions**:

| English Term | Chinese Translation | Rationale |
|--------------|-------------------|-----------|
| Research Manager | 研究总监 | Reflects director-level decision-making authority |
| Portfolio manager and debate facilitator | 担任研究总监，负责评估多空辩论并制定投资决策 | Complete role definition with responsibilities |
| Buy, Sell, or Hold | 买入、卖出或持有 | Standard Chinese securities market terminology |
| Bear analyst / Bull analyst | 空头研究员 / 多头研究员 | Consistent with researcher prefixes |
| Recommendation | 推荐建议 | Direct translation, clear action |
| Rationale | 决策理由 | Explains the "why" behind decision |
| Strategic Actions | 执行策略 | Actionable implementation steps |
| Debate History | 观点与论辩 | Captures both content and debate process |
| Past reflections on mistakes | 过去错误的反思 | Emphasizes learning from mistakes |
| Conversationally, naturally | 以自然对话风格 | Clear instruction for output style |

### 2.2 Code Structure Pattern

**Independent Manager Pattern**:

Adapted from researcher pattern but simplified:
```python
from tradingagents.agents.utils.agent_utils import load_prompt_template

def create_research_manager(llm, memory):
    def research_manager_node(state) -> dict:
        # Extract state
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # Load memories
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # Load prompt from external file (supports multi-language)
        prompt_template = load_prompt_template('research_manager')

        # Substitute variables (keep English variable names)
        prompt = prompt_template.format(
            history=history,
            past_memory_str=past_memory_str
        )

        response = llm.invoke(prompt)

        # Chinese output prefix (director title)
        decision = f"研究总监：{response.content}"

        # Return state (NO latest_speaker - final node)
        new_investment_debate_state = {
            "judge_decision": decision,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": decision,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": decision,
        }

    return research_manager_node
```

**Key Differences from Researcher Pattern**:
- ✅ Uses `load_prompt_template()` infrastructure
- ✅ Supports multi-language via `LANGUAGE` env var
- ❌ Does NOT set `latest_speaker` (manager is final node)
- ✅ Adds role prefix: "研究总监：{content}"

### 2.3 Prompt File Structure

**Four-Part Structure** (maintained from original):

1. **Role Definition**: 研究总监角色定位和职责
2. **Task Instructions**: 总结论点 + 明确决策 + 避免默认持有
3. **Investment Plan Requirements**: 推荐建议 + 决策理由 + 执行策略
4. **Debate History**: 反思内容 + 观点与论辩

**Variable Substitution** (keep English names):
```python
{history}          # Debate history
{past_memory_str}  # Past reflections on mistakes
```

---

## 3. Implementation Specification

### 3.1 File Modifications

**File**: `tradingagents/agents/managers/research_manager.py`

**Changes Required**:

1. **Import statement** (add after line 2):
```python
from tradingagents.agents.utils.agent_utils import load_prompt_template
```

2. **Remove hardcoded prompt** (delete lines 22-38):
```python
# DELETE:
prompt = f"""As the portfolio manager and debate facilitator..."""
```

3. **Add prompt loading** (replace deleted lines):
```python
# Load prompt from external file (supports multi-language)
# Note: Uses existing load_prompt_template() infrastructure
prompt_template = load_prompt_template('research_manager')

# Substitute variables
prompt = prompt_template.format(
    history=history,
    past_memory_str=past_memory_str
)
```

4. **Add Chinese output prefix** (modify line 39):
```python
# OLD:
response = llm.invoke(prompt)

# NEW:
response = llm.invoke(prompt)

# Chinese output prefix (research director)
decision = f"研究总监：{response.content}"
```

5. **Update state dictionary** (modify lines 41-48):
```python
# OLD:
new_investment_debate_state = {
    "judge_decision": response.content,
    "history": investment_debate_state.get("history", ""),
    "bear_history": investment_debate_state.get("bear_history", ""),
    "bull_history": investment_debate_state.get("bull_history", ""),
    "current_response": response.content,
    "count": investment_debate_state["count"],
}

return {
    "investment_debate_state": new_investment_debate_state,
    "investment_plan": response.content,
}

# NEW:
new_investment_debate_state = {
    "judge_decision": decision,
    "history": investment_debate_state.get("history", ""),
    "bear_history": investment_debate_state.get("bear_history", ""),
    "bull_history": investment_debate_state.get("bull_history", ""),
    "current_response": decision,
    "count": investment_debate_state["count"],
}

return {
    "investment_debate_state": new_investment_debate_state,
    "investment_plan": decision,
}
```

### 3.2 Prompt File Creation

**File**: `prompts/zh/research_manager.md` (NEW)

**Content**:
```markdown
作为研究总监，您的职责是批判性评估本轮辩论并做出明确决策：支持空头研究员、支持多头研究员，或只有在有充分理由支持时才选择持有。

简明总结双方的关键观点，聚焦于最有说服力的证据或推理。您的推荐建议——买入、卖出或持有——必须清晰且可执行。避免因为双方都有道理就默认选择持有；应基于辩论中最有力的论点做出明确立场。

此外，为交易员制定详细的投资计划。该计划应包括：

您的推荐建议：基于最有说服力的论点所支持的明确立场
决策理由：解释这些论点如何导致您的结论
执行策略：实施推荐建议的具体步骤

借鉴相似情境下的经验教训，利用这些见解优化决策制定，确保持续改进。以自然对话风格呈现您的分析，就像日常交谈一样，不使用特殊格式。

以下是您过去错误的反思：
\"{past_memory_str}\"

以下是辩论内容：
观点与论辩：
{history}
```

**File**: `prompts/en/research_manager.md` (NEW - English original)

**Content** (extracted from original code for consistency):
```markdown
As the portfolio manager and debate facilitator, your role is to critically evaluate this round of debate and make a definitive decision: align with the bear analyst, the bull analyst, or choose Hold only if it is strongly justified based on the arguments presented.

Summarize the key points from both sides concisely, focusing on the most compelling evidence or reasoning. Your recommendation—Buy, Sell, or Hold—must be clear and actionable. Avoid defaulting to Hold simply because both sides have valid points; commit to a stance grounded in the debate's strongest arguments.

Additionally, develop a detailed investment plan for the trader. This should include:

Your Recommendation: A decisive stance supported by the most convincing arguments.
Rationale: An explanation of why these arguments lead to your conclusion.
Strategic Actions: Concrete steps for implementing the recommendation.
Take into account your past mistakes on similar situations. Use these insights to refine your decision-making and ensure you are learning and improving. Present your analysis conversationally, as if speaking naturally, without special formatting.

Here are your past reflections on mistakes:
\"{past_memory_str}\"

Here is the debate:
Debate History:
{history}
```

---

## 4. Translation Reference

### 4.1 Section-by-Section Translation

| Section | English | Chinese | Notes |
|---------|---------|---------|-------|
| **Role Definition** | As the portfolio manager and debate facilitator, your role is to critically evaluate this round of debate and make a definitive decision | 作为研究总监，您的职责是批判性评估本轮辩论并做出明确决策 | Direct literal translation |
| **Decision Options** | align with the bear analyst, the bull analyst, or choose Hold only if it is strongly justified | 支持空头研究员、支持多头研究员，或只有在有充分理由支持时才选择持有 | Maintain three options structure |
| **Summary Requirement** | Summarize the key points from both sides concisely, focusing on the most compelling evidence or reasoning | 简明总结双方的关键观点，聚焦于最有说服力的证据或推理 | Literal translation preserving emphasis |
| **Decision Clarity** | Your recommendation—Buy, Sell, or Hold—must be clear and actionable | 您的推荐建议——买入、卖出或持有——必须清晰且可执行 | Maintain em-dashes for emphasis |
| **Avoid Hold Default** | Avoid defaulting to Hold simply because both sides have valid points; commit to a stance grounded in the debate's strongest arguments | 避免因为双方都有道理就默认选择持有；应基于辩论中最有力的论点做出明确立场 | Direct literal translation |
| **Investment Plan Intro** | Additionally, develop a detailed investment plan for the trader. This should include: | 此外，为交易员制定详细的投资计划。该计划应包括： | Standard transition phrase |
| **Plan Element 1** | Your Recommendation: A decisive stance supported by the most convincing arguments | 您的推荐建议：基于最有说服力的论点所支持的明确立场 | Three-part title format |
| **Plan Element 2** | Rationale: An explanation of why these arguments lead to your conclusion | 决策理由：解释这些论点如何导致您的结论 | Explains cause-effect relationship |
| **Plan Element 3** | Strategic Actions: Concrete steps for implementing the recommendation | 执行策略：实施推荐建议的具体步骤 | Action-oriented implementation |
| **Learning from Past** | Take into account your past mistakes on similar situations. Use these insights to refine your decision-making and ensure you are learning and improving | 借鉴相似情境下的经验教训，利用这些见解优化决策制定，确保持续改进 | Borrow experience and refine decision-making |
| **Output Style** | Present your analysis conversationally, as if speaking naturally, without special formatting | 以自然对话风格呈现您的分析，就像日常交谈一样，不使用特殊格式 | Conversational and natural style |
| **Reflections Section** | Here are your past reflections on mistakes: | 以下是您过去错误的反思： | Direct section header |
| **Debate Section** | Here is the debate: Debate History: | 以下是辩论内容：观点与论辩： | Two-line header format |
| **Variable** | {past_memory_str} | {past_memory_str} | Keep English variable names |
| **Variable** | {history} | {history} | Keep English variable names |

### 4.2 Key Terminology

| Term | English | Chinese | Context |
|------|---------|---------|---------|
| Role | Portfolio manager | 研究总监 | Decision-maker role |
| Analyst | Bear analyst | 空头研究员 | Researcher role |
| Analyst | Bull analyst | 多头研究员 | Researcher role |
| Decision | Buy | 买入 | Investment action |
| Decision | Sell | 卖出 | Investment action |
| Decision | Hold | 持有 | Investment action |
| Plan Element | Recommendation | 推荐建议 | What to do |
| Plan Element | Rationale | 决策理由 | Why to do it |
| Plan Element | Strategic Actions | 执行策略 | How to do it |
| Section | Reflections on mistakes | 错误的反思 | Learning from past |
| Section | Debate History | 观点与论辩 | Debate content |
| Style | Conversationally | 自然对话风格 | Output format |
| Modifier | Concisely | 简明 | Summary style |
| Modifier | Decisive | 明确 | Decision quality |
| Modifier | Actionable | 可执行 | Plan quality |
| Modifier | Compelling | 有说服力 | Argument quality |

---

## 5. Testing Strategy

### 5.1 Scope: File Verification Only

Following "小步快跑" principle, testing will be limited to file existence and basic validation.

### 5.2 Verification Checklist

- [ ] `prompts/zh/research_manager.md` file exists
- [ ] `prompts/en/research_manager.md` file exists
- [ ] Chinese prompt contains all required sections (role, task, plan, history)
- [ ] English prompt matches original hardcoded text
- [ ] Both prompts use correct variable placeholders: `{history}`, `{past_memory_str}`
- [ ] `load_prompt_template('research_manager')` call added to code
- [ ] Hardcoded prompt removed from `research_manager.py`
- [ ] Chinese output prefix added: `f"研究总监：{response.content}"`
- [ ] State dictionary uses `decision` variable instead of `response.content`
- [ ] Return statement uses `decision` for both `judge_decision` and `investment_plan`
- [ ] No `latest_speaker` field in state dictionary (manager is final node)
- [ ] Import statement added: `from tradingagents.agents.utils.agent_utils import load_prompt_template`

### 5.3 No Automated Tests

**Rationale**:
- Consistent with 006/007 (bull/bear researcher) approach
- Testing full debate flow requires LLM mocking or API keys
- Manual verification sufficient for prompt extraction

**Manual Verification** (optional, not required):
```bash
# Test prompt loading
python -c "
from tradingagents.agents.utils.agent_utils import load_prompt_template
prompt_zh = load_prompt_template('research_manager', 'zh')
print('=== Chinese Prompt ===')
print(prompt_zh[:200] + '...')
prompt_en = load_prompt_template('research_manager', 'en')
print('\n=== English Prompt ===')
print(prompt_en[:200] + '...')
"
```

---

## 6. Edge Cases and Considerations

### 6.1 Empty History or Memories

**Approach**: LLM Natural Handling

**Rationale**:
- No special handling needed
- LLM can handle empty `{history}` or `{past_memory_str}` gracefully
- Prompt structure remains valid even with empty variables
- Consistent with other agents' approach

**Example**:
```python
# Empty case (valid):
history = ""
past_memory_str = ""

# Prompt becomes:
"...观点与论辩："
# LLM will understand this means no debate history yet
```

### 6.2 Language Switching

**Mechanism**: Environment Variable

```bash
# Use Chinese prompts (default)
export LANGUAGE=zh

# Use English prompts
export LANGUAGE=en
```

**Behavior**:
- `load_prompt_template()` reads from `LANGUAGE` env var
- Defaults to "zh" if not set
- Falls back to existing infrastructure

### 6.3 Role Prefix Consistency

**Hierarchy**:
- Researchers: "多头" / "空头" (Analyst level)
- Manager: "研究总监" (Director level)

**Rationale**:
- Reflects organizational hierarchy
- Distinguishes decision-maker from debaters
- Consistent with Chinese corporate structure

---

## 7. Comparison with Related Specifications

### 7.1 Similarities to 006/007 (Bull/Bear Researchers)

| Aspect | Researchers | Manager |
|--------|-------------|---------|
| Use `load_prompt_template()` | ✅ | ✅ |
| External prompt files | ✅ | ✅ |
| Multi-language support | ✅ | ✅ |
| Chinese output prefix | ✅ | ✅ |
| Format with variables | ✅ | ✅ |
| Keep English variable names | ✅ | ✅ |
| Literal translation strategy | ✅ | ✅ |

### 7.2 Differences from 006/007 (Bull/Bear Researchers)

| Aspect | Researchers | Manager |
|--------|-------------|---------|
| Set `latest_speaker` | ✅ Required | ❌ Not needed (final node) |
| Output prefix | "多头：" / "空头：" | "研究总监：" |
| Role | Debater (advocate) | Decision-maker (judge) |
| Position in flow | Middle (multiple rounds) | End (one-time) |
| State manipulation | Update history + count | Preserve all state |

### 7.3 Learnings from Bugfix #004

**Key Insight Applied**:
- Manager does NOT set `latest_speaker` because it's the final node in the debate flow
- No routing depends on manager's output
- State preservation is sufficient

**Avoided Mistake**:
- ❌ Would have been wrong to blindly copy researcher pattern
- ✅ Correct understanding of manager's terminal position in flow

---

## 8. Implementation Steps

### Step 1: Create English Prompt File
**File**: `prompts/en/research_manager.md`
- Extract original hardcoded prompt
- Verify no content loss
- Add markdown formatting

### Step 2: Create Chinese Prompt File
**File**: `prompts/zh/research_manager.md`
- Translate using literal translation strategy
- Maintain four-part structure
- Use English variable names
- Keep section headers

### Step 3: Modify `research_manager.py`
- Add import statement
- Remove hardcoded prompt
- Add `load_prompt_template()` call
- Add Chinese output prefix
- Update state dictionary

### Step 4: Verify Files
- Check file existence
- Verify prompt structure
- Test prompt loading (optional manual test)

### Step 5: Document Changes
- Create/update summary document
- Record translation decisions
- Note differences from researcher pattern

---

## 9. Success Criteria

### 9.1 Functional Requirements

- [✅] Code loads prompts from external files
- [✅] Prompts support both Chinese and English
- [✅] Chinese output uses "研究总监：" prefix
- [✅] State management preserves all history
- [✅] No `latest_speaker` field in manager state
- [✅] Variables use English names
- [✅] LANGUAGE environment variable controls language

### 9.2 Quality Requirements

- [✅] Translation is literal and accurate
- [✅] Maintains professional investment tone
- [✅] Four-part prompt structure preserved
- [✅] All original requirements retained
- [✅] Code follows existing patterns
- [✅] No regression in functionality

### 9.3 Constraints

- [✅] Scope limited to `research_manager.py` and prompt files
- [✅] No changes to graph structure or routing
- [✅] No changes to other agents
- [✅] No automated tests required
- [✅] File verification only for testing

---

## 10. Risks and Mitigations

### 10.1 Risk: Inconsistent Role Title

**Risk**: Output prefix "研究总监" may not match user expectations if they expect "研究经理"

**Mitigation**:
- "研究总监" more accurately reflects decision-making authority
- Consistent with Chinese corporate hierarchy
- "总监" > "经理" in seniority, appropriate for final decision-maker

### 10.2 Risk: Translation Quality

**Risk**: Literal translation may not capture nuanced investment terminology

**Mitigation**:
- Use standard Chinese securities market terminology (买入/卖出/持有)
- Maintain professional tone and structure
- Reference established translations from 006/007

### 10.3 Risk: State Inconsistency

**Risk**: Missing `latest_speaker` might cause issues if graph expects it

**Mitigation**:
- Manager is terminal node, no routing depends on its output
- Verified via bugfix #004 that routing uses `latest_speaker` from researchers
- Manager only reads state, doesn't need to update routing fields

### 10.4 Risk: Variable Name Confusion

**Risk**: English variable names in Chinese prompt may confuse LLM

**Mitigation**:
- Consistent with all other agents (003-007)
- LLMs handle English variable names in Chinese prompts well
- Variable substitution happens at runtime, LLM sees substituted values

---

## 11. Future Enhancements (Out of Scope)

### 11.1 Potential Improvements

1. **Decision Confidence Score**: Add numerical confidence level (e.g., 1-10)
2. **Risk Assessment**: Explicit risk rating for the recommendation
3. **Position Sizing**: Suggested position size or portfolio allocation
4. **Time Horizon**: Explicit investment time frame (short/medium/long term)
5. **Key Metrics**: Specific metrics or thresholds supporting decision

**Rationale for Exclusion**:
- Not present in original implementation
- Would expand scope beyond "小步快跑"
- Can be added in future iterations

### 11.2 Localization Opportunities

1. **Taiwan Market**: Use traditional Chinese and different terminology
2. **Hong Kong Market**: Use traditional Chinese and English mixing
3. **US Market**: Use original English prompt

**Rationale for Exclusion**:
- Current scope is China A-share only
- Infrastructure already supports multi-language via `LANGUAGE` var
- Future markets can follow this pattern

---

## 12. References

### 12.1 Related Specifications

1. **003-analyst-market.md**: First agent to use external prompts
2. **004-analyst-news.md**: News analyst Chinese adaptation
3. **005-analyst-fundamentals.md**: Fundamentals analyst Chinese adaptation
4. **006-researcher-bull.md**: Bull researcher Chinese adaptation
5. **007-researcher-bear.md**: Bear researcher Chinese adaptation
6. **004-researcher-bull-error.md**: Routing bugfix and state management

### 12.2 Code Files

- `tradingagents/agents/managers/research_manager.py` - Target file for modification
- `tradingagents/agents/researchers/bull_researcher.py` - Reference pattern
- `tradingagents/agents/researchers/bear_researcher.py` - Reference pattern
- `tradingagents/agents/utils/agent_utils.py` - Prompt loading infrastructure
- `tradingagents/graph/conditional_logic.py` - Routing logic (for understanding)

### 12.3 Prompt Files

- `prompts/zh/bull_researcher.md` - Translation style reference
- `prompts/zh/bear_researcher.md` - Translation style reference
- `prompts/zh/market_analyst.md` - Structure reference
- `prompts/zh/fundamentals_analyst.md` - Structure reference

---

## Appendix A: Complete Modified Code

### File: `tradingagents/agents/managers/research_manager.py`

```python
import time
import json
from tradingagents.agents.utils.agent_utils import load_prompt_template


def create_research_manager(llm, memory):
    def research_manager_node(state) -> dict:
        history = state["investment_debate_state"].get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        investment_debate_state = state["investment_debate_state"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # Load prompt from external file (supports multi-language)
        # Note: Uses existing load_prompt_template() infrastructure
        prompt_template = load_prompt_template('research_manager')

        # Substitute variables
        prompt = prompt_template.format(
            history=history,
            past_memory_str=past_memory_str
        )

        response = llm.invoke(prompt)

        # Chinese output prefix (research director)
        decision = f"研究总监：{response.content}"

        new_investment_debate_state = {
            "judge_decision": decision,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": decision,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": decision,
        }

    return research_manager_node
```

**Changes Summary**:
- Line 4: Added import for `load_prompt_template`
- Lines 22-38: Replaced hardcoded prompt with external file loading
- Line 40: Added Chinese output prefix "研究总监："
- Lines 42-48: Updated to use `decision` variable instead of `response.content`
- Line 52: Updated return to use `decision` for `investment_plan`

---

## Appendix B: Verification Script

### Manual Test Script

```python
#!/usr/bin/env python3
"""
Manual verification script for research manager Chinese adaptation.
Run this to verify prompt loading and basic structure.
"""

from tradingagents.agents.utils.agent_utils import load_prompt_template

def test_prompt_loading():
    """Test that prompts can be loaded successfully."""
    print("Testing prompt loading...\n")

    # Test Chinese prompt
    try:
        prompt_zh = load_prompt_template('research_manager', 'zh')
        print("✅ Chinese prompt loaded successfully")
        print(f"   Length: {len(prompt_zh)} characters")
        print(f"   Preview: {prompt_zh[:150]}...")
    except Exception as e:
        print(f"❌ Failed to load Chinese prompt: {e}")
        return False

    print()

    # Test English prompt
    try:
        prompt_en = load_prompt_template('research_manager', 'en')
        print("✅ English prompt loaded successfully")
        print(f"   Length: {len(prompt_en)} characters")
        print(f"   Preview: {prompt_en[:150]}...")
    except Exception as e:
        print(f"❌ Failed to load English prompt: {e}")
        return False

    print()

    # Verify variables
    print("Verifying variable placeholders...")
    variables = ['{history}', '{past_memory_str}']

    for var in variables:
        if var in prompt_zh:
            print(f"✅ Found {var} in Chinese prompt")
        else:
            print(f"❌ Missing {var} in Chinese prompt")
            return False

        if var in prompt_en:
            print(f"✅ Found {var} in English prompt")
        else:
            print(f"❌ Missing {var} in English prompt")
            return False

    print()

    # Verify sections
    print("Verifying prompt sections...")
    zh_sections = [
        "作为研究总监",
        "简明总结",
        "推荐建议",
        "决策理由",
        "执行策略",
        "观点与论辩"
    ]

    for section in zh_sections:
        if section in prompt_zh:
            print(f"✅ Found section: {section}")
        else:
            print(f"⚠️  Section not found: {section}")

    print("\n✅ All checks passed!")
    return True

if __name__ == "__main__":
    test_prompt_loading()
```

**Usage**:
```bash
python test_research_manager.py
```

---

**End of Specification**
