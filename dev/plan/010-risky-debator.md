# Specification: Risky Debator - Chinese A-Share Adaptation

## Executive Summary

Adapt the existing `aggresive_debator.py` to support Chinese A-share market risk debating by:
1. Translating the English prompt to Chinese while maintaining all debating logic and aggressive style
2. Implementing externalized prompt management with multi-language support
3. Providing fully-featured Chinese debating responses (maintaining technical accuracy)
4. Supporting language switching via environment variable configuration

**Key Design Decisions:**
- **Translation Strategy**: Literal translation (直译优先) preserving original structure and debating logic
- **Debating Style**: Maintain aggressive/confrontational style (保持对抗性风格) with professional financial tone
- **Terminology**: "High-risk, high-reward" → "高收益高风险", "Trader's decision" → "交易计划"
- **Prompt Organization**: External Markdown files in `prompts/{lang}/` directory
- **Language Control**: `LANGUAGE` environment variable (zh/en)
- **Default Language**: Chinese (zh)
- **Testing**: Unit tests for prompt loading functionality
- **Scope**: Focus on risky_debator only (小步快跑，只修改 risky debator)

---

## Technical Architecture

### 1. Directory Structure

```
TradingAgents-ETF/
├── prompts/
│   ├── zh/
│   │   └── risky_debator.md       # Chinese prompt template
│   └── en/
│       └── risky_debator.md       # English prompt template (original)
├── tradingagents/
│   ├── agents/
│   │   └── risk_mgmt/
│   │       └── aggresive_debator.py  # Modified to use external prompts
│   └── utils/
│       └── agent_utils.py         # Add prompt loading function
├── .env.example                   # Add LANGUAGE variable documentation
└── ...
```

### 2. File Changes

#### 2.1 `tradingagents/agents/utils/agent_utils.py`

**Action:** Reuse existing `load_prompt_template()` function from plan #003

No modifications needed - the existing implementation already supports:
- Multi-language loading (zh/en)
- Environment variable control (`LANGUAGE`)
- Default language: Chinese (zh)
- Comprehensive error handling

**Function Signature:**
```python
def load_prompt_template(agent_name: str, language: str = None) -> str:
    """
    Load prompt template from external markdown file.

    Args:
        agent_name: Name of the agent (e.g., 'risky_debator')
        language: Language code ('zh' or 'en'). If None, reads from LANGUAGE
                  environment variable with default 'zh'.

    Returns:
        Prompt content as string

    Raises:
        FileNotFoundError: With detailed error message including:
            - File path that was not found
            - How to set LANGUAGE environment variable
            - Available language options
    """
```

#### 2.2 `tradingagents/agents/risk_mgmt/aggresive_debator.py`

**Modifications:**
1. Import `load_prompt_template` from `agent_utils`
2. In `create_risky_debator()` function:
   - Load prompt using: `prompt_content = load_prompt_template('risky_debator')`
   - Replace hardcoded prompt string with loaded content
   - Keep all existing logic (state management, response handling, etc.)

**Code Changes:**
```python
import time
import json
from tradingagents.agents.utils.agent_utils import load_prompt_template

def create_risky_debator(llm):
    """
    Create risky debator node with multi-language prompt support.

    The risky debator actively champions high-reward, high-risk opportunities,
    emphasizing bold strategies and competitive advantages.

    Args:
        llm: Language model instance

    Returns:
        risky_node: Function that processes state and generates risky arguments
    """
    def risky_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        risky_history = risk_debate_state.get("risky_history", "")

        current_safe_response = risk_debate_state.get("current_safe_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        # Load prompt from external file (supports multi-language)
        prompt_template = load_prompt_template('risky_debator')

        # Format prompt with variables
        prompt = prompt_template.format(
            trader_decision=trader_decision,
            market_research_report=market_research_report,
            sentiment_report=sentiment_report,
            news_report=news_report,
            fundamentals_report=fundamentals_report,
            history=history,
            current_safe_response=current_safe_response,
            current_neutral_response=current_neutral_response
        )

        response = llm.invoke(prompt)

        argument = f"Risky Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Risky",
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return risky_node
```

**Key Changes:**
- Import `load_prompt_template`
- Add docstring explaining the function
- Load prompt template from external file
- Use `str.format()` instead of f-string to load external template
- Maintain all existing state management logic

#### 2.3 `.env.example`

**Action:** Verify `LANGUAGE` variable is documented (from plan #003)

If not present, add:
```bash
# Language configuration for agent prompts
# Options: zh (Chinese), en (English)
# Default: zh
LANGUAGE=zh
```

---

## 3. Prompt File Specifications

### 3.1 `prompts/zh/risky_debator.md`

**Content Requirements:**
- **Translation Strategy**: Literal translation (直译优先)
- **Language**: Professional Chinese (中文专业版) with financial terminology
- **Tone**: Aggressive/confrontational debating style (保持对抗性风格)
- **Terminology Consistency**:
  - "Risky Risk Analyst" → "高风险偏好分析师"
  - "high-reward, high-risk opportunities" → "高收益高风险机会"
  - "trader's decision/plan" → "交易计划"
  - "conservative/neutral analysts" → "保守分析师/中立分析师"
  - "conversation history" → "对话记录"
  - "current_safe_response" → "保守分析师的上一次论点"
  - "current_neutral_response" → "中立分析师的上一次论点"

**Key Sections to Translate:**

1. **Role Definition**:
   ```
   作为高风险偏好分析师，你的角色是积极主张高收益高回报的投资机会，重点强调进取型策略和竞争性优势。
   ```

2. **Evaluation Focus**:
   ```
   在评估交易计划时，应密切关注其潜在的上行空间、增长潜力和创新性优势——即使这些伴随较高风险。
   ```

3. **Data Usage**:
   ```
   利用提供的市场数据和情绪分析来加强你的论点，并反驳对立观点。
   ```

4. **Direct Response Requirement**:
   ```
   具体来说，针对保守分析师和中立分析师提出的每一点，用数据驱动的反驳和有说服力的论证进行反击。
   ```

5. **Highlighting Opportunities**:
   ```
   指出他们的谨慎可能错过的关键机会，或者他们的假设可能过于保守的地方。
   ```

6. **Data Source Integration**:
   ```
   将以下来源的洞察整合到你的论证中：
   - 市场研究报告
   - 社交媒体情绪报告
   - 最新世界时事报告
   - 公司基本面报告
   ```

7. **Argument Structure**:
   ```
   当前对话记录：{history}
   保守分析师的上一次论点：{current_safe_response}
   中立分析师的上一次论点：{current_neutral_response}
   如果没有其他观点的回应，请勿编造，仅阐述己方立场。
   ```

8. **Active Engagement**:
   ```
   通过积极参与对话、解决具体关切、反驳对方逻辑漏洞、强调风险承担能超越市场常规水平来积极辩论。
   ```

9. **Focus on Debating**:
   ```
   针对每一个反驳点进行挑战，以突显为什么高风险策略是最优的。保持专注于辩论和说服，而不仅仅是呈现数据。
   ```

10. **Output Format**:
    ```
    请以对话的方式输出，像说话一样自然，不使用任何特殊格式。
    ```

**Placeholders (Keep Unchanged):**
- `{trader_decision}`
- `{market_research_report}`
- `{sentiment_report}`
- `{news_report}`
- `{fundamentals_report}`
- `{history}`
- `{current_safe_response}`
- `{current_neutral_response}`

**Debating Style Requirements:**
- Maintain aggressive/confrontational tone: "错误" (wrong), "忽略了" (ignored), "低估了" (underestimated)
- Emphasize high-reward potential: "强调收益潜力"
- Point out specific problems in opposing arguments: "指出具体问题"
- Use data-driven rebuttals: "引用具体数据点"
- Quote data sources using standard format: "根据市场研究报告", "社交媒体情绪显示"
- Professional financial language throughout
- Direct argumentation without lengthy opening statements

**What NOT to Change:**
- All variable placeholders: `{trader_decision}`, `{market_research_report}`, etc.
- Data source order: market research, social media, news, fundamentals
- Core logic: respond to each point, use data-driven rebuttals, active engagement
- Conversational output format (no special formatting)

**Complete Chinese Prompt Structure:**
```markdown
作为高风险偏好分析师，你的角色是积极主张高收益高回报的投资机会，重点强调进取型策略和竞争性优势。在评估交易计划时，应密切关注其潜在的上行空间、增长潜力和创新性优势——即使这些伴随较高风险。利用提供的市场数据和情绪分析来加强你的论点，并反驳对立观点。

具体来说，针对保守分析师和中立分析师提出的每一点，用数据驱动的反驳和有说服力的论证进行反击。指出他们的谨慎可能错过的关键机会，或者他们的假设可能过于保守的地方。

以下是交易者的计划：
{trader_decision}

你的任务是通过质疑和批判保守和中立分析师的立场，为交易者的计划创建一个令人信服的案例，以展示为什么你的高收益视角提供了最佳的前进路径。

将以下来源的洞察整合到你的论证中：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新世界时事报告：{news_report}
公司基本面报告：{fundamentals_report}

当前对话记录：{history}
保守分析师的上一次论点：{current_safe_response}
中立分析师的上一次论点：{current_neutral_response}

如果没有其他观点的回应，请勿编造，仅阐述己方立场。

通过积极参与对话、解决具体关切、反驳对方逻辑漏洞、强调风险承担能超越市场常规水平来积极辩论。针对每一个反驳点进行挑战，以突显为什么高风险策略是最优的。保持专注于辩论和说服，而不仅仅是呈现数据。

请以对话的方式输出，像说话一样自然，不使用任何特殊格式。
```

### 3.2 `prompts/en/risky_debator.md`

**Content:** Extract the original English prompt from current code (lines 21-33 in aggresive_debator.py) and save as markdown file.

```markdown
As the Risky Risk Analyst, your role is to actively champion high-reward, high-risk opportunities, emphasizing bold strategies and competitive advantages. When evaluating the trader's decision or plan, focus intently on the potential upside, growth potential, and innovative benefits—even when these come with elevated risk. Use the provided market data and sentiment analysis to strengthen your arguments and challenge the opposing views. Specifically, respond directly to each point made by the conservative and neutral analysts, countering with data-driven rebuttals and persuasive reasoning. Highlight where their caution might miss critical opportunities or where their assumptions may be overly conservative. Here is the trader's decision:

{trader_decision}

Your task is to create a compelling case for the trader's decision by questioning and critiquing the conservative and neutral stances to demonstrate why your high-reward perspective offers the best path forward. Incorporate insights from the following sources into your arguments:

Market Research Report: {market_research_report}
Social Media Sentiment Report: {sentiment_report}
Latest World Affairs Report: {news_report}
Company Fundamentals Report: {fundamentals_report}
Here is the current conversation history: {history} Here are the last arguments from the conservative analyst: {current_safe_response} Here are the last arguments from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

Engage actively by addressing any specific concerns raised, refuting the weaknesses in their logic, and asserting the benefits of risk-taking to outpace market norms. Maintain a focus on debating and persuading, not just presenting data. Challenge each counterpoint to underscore why a high-risk approach is optimal. Output conversationally as if you are speaking without any special formatting.
```

---

## 4. Behavior Specifications

### 4.1 Language Selection Logic

```
1. Check LANGUAGE environment variable
2. If not set → default to 'zh' (Chinese)
3. Load prompt from: prompts/{LANGUAGE}/risky_debator.md
4. If file not found → raise FileNotFoundError with detailed message
```

**Environment Variable Values:**
- `LANGUAGE=zh` → Load Chinese prompt
- `LANGUAGE=en` → Load English prompt
- Not set → Default to Chinese prompt

### 4.2 Debating Response Output

**Language:** Fully Chinese response

**Tone and Style:**
- Professional financial language
- Aggressive/confrontational debating style
- Strong negation words: "错误", "忽略了", "低估了"
- Emphasis on high-reward potential
- Data-driven rebuttals with specific data points
- Standard citation format: "根据市场研究报告", "社交媒体情绪显示"

**Response Components:**
1. **Direct Challenge** (no lengthy opening)
   - Immediately start arguing
   - No fixed opening statement

2. **Data-Driven Rebuttals**
   - Quote specific data points from reports
   - Use standard citation format for data sources

3. **Specific Challenges**
   - Point out specific problems in opposing arguments
   - Challenge assumptions and logic weaknesses

4. **Conversational Style**
   - Natural speaking style
   - No special formatting (no bold, headers, etc.)

**Example Response Structure:**
```
保守分析师的观点存在问题。根据市场研究报告，[具体数据]，这表明[反驳内容]。社交媒体情绪显示[具体数据]，进一步证明了...

保守方过于关注[某风险]，但忽略了[关键机会]。从公司基本面来看，[具体数据]支持高风险策略的可行性...

中立分析师认为[观点]，但这是错误的。数据显示[反驳内容]...
```

### 4.3 Error Handling

**File Not Found Exception:**
(Reused from agent_utils.py - consistent with plan #003)

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

**Test File:** `tests/agents/test_risky_debator_prompt.py`

**Test Cases:**

1. **Multi-language Loading**
   ```python
   def test_load_chinese_prompt():
       prompt = load_prompt_template('risky_debator', 'zh')
       assert '作为高风险偏好分析师' in prompt
       assert '高收益高风险' in prompt

   def test_load_english_prompt():
       prompt = load_prompt_template('risky_debator', 'en')
       assert 'As the Risky Risk Analyst' in prompt
       assert 'high-reward, high-risk' in prompt
   ```

2. **Default Language**
   ```python
   def test_default_language_is_chinese():
       os.environ.pop('LANGUAGE', None)
       prompt = load_prompt_template('risky_debator')
       assert '作为高风险偏好分析师' in prompt
   ```

3. **Environment Variable**
   ```python
   def test_language_from_env_variable():
       os.environ['LANGUAGE'] = 'en'
       prompt = load_prompt_template('risky_debator')
       assert 'As the Risky Risk Analyst' in prompt
   ```

4. **File Not Found**
   ```python
   def test_prompt_file_not_found():
       with pytest.raises(FileNotFoundError) as exc_info:
           load_prompt_template('risky_debator', 'fr')
       assert 'Prompt file not found' in str(exc_info.value)
   ```

5. **Placeholder Preservation**
   ```python
   def test_placeholders_preserved():
       prompt = load_prompt_template('risky_debator', 'zh')
       assert '{trader_decision}' in prompt
       assert '{market_research_report}' in prompt
       assert '{sentiment_report}' in prompt
       assert '{news_report}' in prompt
       assert '{fundamentals_report}' in prompt
       assert '{history}' in prompt
       assert '{current_safe_response}' in prompt
       assert '{current_neutral_response}' in prompt
   ```

6. **Terminology Consistency**
   ```python
   def test_chinese_terminology_consistency():
       prompt = load_prompt_template('risky_debator', 'zh')
       assert '高风险偏好分析师' in prompt
       assert '交易计划' in prompt
       assert '保守分析师' in prompt
       assert '中立分析师' in prompt
       assert '对话记录' in prompt
   ```

### 5.2 Integration Testing

**Test Objective:** Verify that the modified `aggresive_debator.py` works correctly with external prompts

**Test Approach:**
- Manual testing with real trading scenarios
- Verify language switching functionality
- Validate debating response quality

---

## 6. Implementation Tasks

### Phase 1: Infrastructure (Priority: High)
- [ ] Extract original English prompt from `aggresive_debator.py` to `prompts/en/risky_debator.md`
- [ ] Create `prompts/zh/risky_debator.md` with Chinese translation
- [ ] Verify `load_prompt_template()` function exists in `agent_utils.py` (from plan #003)
- [ ] Add unit tests for prompt loading

### Phase 2: Integration (Priority: High)
- [ ] Modify `aggresive_debator.py` to use external prompts
- [ ] Add import statement for `load_prompt_template`
- [ ] Replace hardcoded prompt with loaded template
- [ ] Add function docstring
- [ ] Use `str.format()` for variable substitution
- [ ] Verify `.env.example` contains LANGUAGE variable documentation

### Phase 3: Testing & Validation (Priority: High)
- [ ] Run unit tests
- [ ] Test with both languages (zh/en)
- [ ] Verify default language is Chinese
- [ ] Manual testing with real trading scenarios
- [ ] Fix any issues

### Phase 4: Documentation (Priority: Medium)
- [ ] Update plan #010 document with implementation details
- [ ] Add design rationale section

---

## 7. Design Rationale

### 7.1 Why Maintain Aggressive Debating Style?
- **Role Preservation**: The "Risky Risk Analyst" role is designed to advocate for high-risk strategies
- **Counterbalance**: Needed to balance conservative and neutral viewpoints in the debate
- **Authenticity**: Direct confrontation creates more persuasive arguments than polite suggestions
- **Decision Quality**: Strong challenge reveals weaknesses in conservative assumptions

### 7.2 Why Use "高风险偏好分析师" Instead of "激进风险分析师"?
- **Professional Tone**: "高风险偏好" (high-risk preference) is more formal and professional
- **Clarity**: Clearly describes the role's risk attitude without negative connotation
- **Accuracy**: Better reflects the role of advocating risk-taking strategies
- **Market Conventions**: Aligns with Chinese financial industry terminology

### 7.3 Why "交易计划" for "Trader's Decision/Plan"?
- **Business Context**: More accurately reflects the output of the trader agent
- **Natural Language**: More natural Chinese expression than "交易者决策"
- **Consistency**: Maintain consistent terminology throughout the prompt

### 7.4 Why "对话记录" Instead of "对话历史"?
- **Clarity**: "记录" (record) is clearer for historical debate tracking
- **Context**: Better reflects the debate scenario context
- **Professional**: More professional terminology for debate documentation

### 7.5 Why "请勿编造，仅阐述己方立场" for "Do Not Hallucinate"?
- **Natural Expression**: More natural and professional Chinese phrasing
- **Clarity**: Clearer instruction for AI behavior
- **Formal Tone**: Aligns with professional financial context

### 7.6 Why Keep Confrontational Tone (Strong Negation)?
- **Role Requirements**: The risky analyst's job is to challenge, not to be polite
- **Debate Effectiveness**: Direct challenges create more persuasive arguments
- **Decision Quality**: Strong negation reveals hidden assumptions and weaknesses
- **Balance**: Counterbalances the conservative analyst's caution

### 7.7 Why "以对话的方式输出" Adjustment?
- **Natural Chinese**: More natural phrasing than literal translation
- **Clarity**: Clearer instruction for conversational output
- **Context**: Better conveys the "speaking naturally" requirement

### 7.8 Why Maintain Original Data Source Order?
- **Logic Flow**: Original order (market → sentiment → news → fundamentals) has logical flow
- **Consistency**: Maintains consistency with English version
- **Testing**: Reduces risk of introducing bugs through reordering

### 7.9 Why Standard Citation Format ("根据...报告")?
- **Professionalism**: Standard format for professional financial analysis
- **Clarity**: Clear attribution of data sources
- **Credibility**: Enhances argument credibility with proper citations

### 7.10 Why Focus Only on risky_debator?
- **Incremental Approach**: Small steps, fast iterations (小步快跑)
- **Validation**: Validate approach before extending to other debators
- **Risk Control**: Limited scope reduces risk of breaking changes
- **Learning**: Learn from this implementation to improve future adaptations

### 7.11 Why No A-Share Specific Additions?
- **Scope Limitation**: This plan focuses on translation, not market adaptation
- **Role Universality**: Risk analysis principles are similar across markets
- **Simplicity**: Keep changes minimal to reduce risk
- **Future Enhancement**: Can add market-specific features in future iterations

---

## 8. Risk Assessment

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Translation quality issues | Medium | Literal translation strategy, preserve original structure |
| str.format() compatibility issues | Low | Test all placeholders work correctly |
| LangChain integration issues | Low | Keep existing code structure, only swap prompt |
| Prompt loading failures | Medium | Clear error messages with setup instructions |

### Operational Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Debating style changes during translation | Medium | Explicitly maintain aggressive tone in translation requirements |
| Inconsistent terminology | Low | Define terminology mapping and verify consistency |
| Testing gaps | Low | Unit tests cover key functionality |
| Language switching issues | Low | Reuse tested load_prompt_template function |

---

## 9. Dependencies

**External Dependencies:**
- None (no new packages required)

**Internal Dependencies:**
- `load_prompt_template()` function from `agent_utils.py` (implemented in plan #003)
- Existing state management structure in `risk_debate_state`
- Existing report formats (market_report, sentiment_report, etc.)

**Prerequisites:**
- Plan #003 must be completed (provides load_prompt_template function)
- LANGUAGE environment variable documentation in `.env.example`

---

## 10. Acceptance Criteria

The implementation is considered complete when:

1. ✅ Chinese and English prompt files exist in `prompts/zh/` and `prompts/en/` directories
2. ✅ Chinese prompt contains accurate translation with aggressive debating style
3. ✅ English prompt is extracted from original code and saved
4. ✅ All placeholders (`{trader_decision}`, `{market_research_report}`, etc.) are preserved
5. ✅ Terminology is consistent ("高风险偏好分析师", "交易计划", "保守分析师", "中立分析师")
6. ✅ `aggresive_debator.py` loads prompts from external files
7. ✅ Code includes import statement and docstring
8. ✅ `LANGUAGE` environment variable controls language selection
9. ✅ Default language is Chinese when `LANGUAGE` is not set
10. ✅ Unit tests pass for all scenarios
11. ✅ Manual testing confirms proper Chinese debating responses
12. ✅ Error message is clear when prompt file is missing
13. ✅ Code style is consistent with other analysts (market_analyst, etc.)

---

## 11. Future Enhancements (Out of Scope)

### 11.1 Extending to Other Debators
- Apply same pattern to `conservative_debator.py`
- Apply same pattern to `neutral_debator.py`
- Create unified prompt management for all debators

### 11.2 A-Share Specific Features
- Add A-share market risk considerations (price limits, T+1, etc.)
- Incorporate A-share specific data sources (北向资金, 换手率)
- Adjust debating style for Chinese market context

### 11.3 Advanced Prompt Features
- Dynamic prompt adjustment based on market conditions
- Multi-language response generation (bilingual output)
- Prompt versioning and A/B testing

### 11.4 Architecture Improvements
- Generic debator prompt manager
- Template engine for complex prompts
- Configuration file based prompt selection

---

## Document Metadata

**Version:** 1.0
**Last Updated:** 2026-01-08
**Status:** Complete Specification
**Author:** Claude (with detailed user requirements from in-depth interview)
**Review Status:** Ready for Implementation

---

**End of Specification**
