# Bug Fix #004: Researcher Bull Routing Error

## Problem Statement

### Error Traceback
```
KeyError: 'Bull Researcher'
File "/Users/jbi/Playground/Github/st01cs/TradingAgents-ETF/tradingagents/graph/conditional_logic.py", line 210, in <listcomp>
    r if isinstance(r, Send) else self.ends[r] for r in result
```

### Root Cause Analysis

The error occurs in `conditional_logic.py` at lines 53-55, where the routing logic checks:

```python
if state["investment_debate_state"]["current_response"].startswith("Bull"):
    return "Bear Researcher"
return "Bull Researcher"
```

However, recent changes to `bull_researcher.py` (line 44) now output Chinese prefixes:
```python
argument = f"多头：{response.content}"  # "Bull: {content}" in Chinese
```

Similarly, `bear_researcher.py` (line 44) outputs:
```python
argument = f"空头：{response.content}"  # "Bear: {content}" in Chinese
```

This creates a language mismatch where:
- **Output content** uses Chinese prefixes: "多头" / "空头"
- **Routing logic** expects English prefixes: "Bull" / "Bear"

### Architectural Context

The system has two debate teams:
1. **Investment Debate Team** (Bull/Bear researchers) - NOW BROKEN due to language mismatch
2. **Risk Debate Team** (Risky/Safe/Neutral analysts) - WORKS CORRECTLY

The Risk Debate Team uses a `latest_speaker` field in `RiskDebateState` for routing:
```python
latest_speaker: "Risky" | "Safe" | "Neutral"
```

The Investment Debate Team lacks this field, instead relying on fragile string prefix checking.

## Solution Design

### Approach: Separate State Keys from Output Content

Following the pattern established by the Risk Debate Team, we will:

1. **Add `latest_speaker` field to `InvestDebateState`**
   - Store routing-independent state: `"Bull"` or `"Bear"`
   - Separate from display content (which can be any language)

2. **Update `conditional_logic.py`**
   - Route based on `latest_speaker` instead of string prefix parsing
   - Add detailed error handling for unrecognized values
   - Add debug logging

3. **Update researcher code**
   - Set `latest_speaker` in both `Bull` and `Bear`
   - Keep Chinese output prefixes for display

4. **Initialize state properly**
   - Set initial `latest_speaker = "Bull"` in `propagation.py`

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Separate state and output** | Decouples routing logic from display language, enabling future localization |
| **Follow Risk Team pattern** | Maintains architectural consistency across debate teams |
| **No backward compatibility** | String prefix checking is fundamentally broken; complete replacement is cleaner |
| **Initialize to "Bull"** | Bull Researcher speaks first, so initial state should enable routing to Bear |
| **Throw ValueError on unknown** | Fails fast with clear error message rather than silent misbehavior |
| **Risk team unchanged** | Currently works correctly; no need to modify |

## Implementation Specification

### 1. Update `agent_states.py`

**File**: `tradingagents/agents/utils/agent_states.py`

**Change**: Add `latest_speaker` field to `InvestDebateState` (after line 21)

```python
class InvestDebateState(TypedDict):
    bull_history: Annotated[str, "Bullish Conversation history"]
    bear_history: Annotated[str, "Bearish Conversation history"]
    history: Annotated[str, "Conversation history"]
    current_response: Annotated[str, "Latest response"]
    judge_decision: Annotated[str, "Final judge decision"]
    count: Annotated[int, "Length of the current conversation"]
    latest_speaker: Annotated[str, "Latest speaker in debate ('Bull' or 'Bear')"]
```

### 2. Update `propagation.py`

**File**: `tradingagents/graph/propagation.py`

**Change**: Initialize `latest_speaker` in `create_initial_state` method (line 26-28)

```python
"investment_debate_state": InvestDebateState(
    {
        "history": "",
        "current_response": "",
        "count": 0,
        "latest_speaker": "Bull"  # Initialize to Bull since Bull speaks first
    }
),
```

### 3. Update `conditional_logic.py`

**File**: `tradingagents/graph/conditional_logic.py`

**Changes**:

a) Import logging module (add at top):
```python
import logging

logger = logging.getLogger(__name__)
```

b) Replace `should_continue_debate` method (lines 46-55):

```python
def should_continue_debate(self, state: AgentState) -> str:
    """Determine if debate should continue based on latest_speaker field."""

    if (
        state["investment_debate_state"]["count"] >= 2 * self.max_debate_rounds
    ):  # 2 rounds of back-and-forth between 2 agents
        logger.debug(f"Debate ended: count {state['investment_debate_state']['count']} reached limit")
        return "Research Manager"

    latest_speaker = state["investment_debate_state"]["latest_speaker"]

    # Route based on explicit state field, not string prefix parsing
    if latest_speaker == "Bull":
        logger.debug("Routing: Bull → Bear Researcher")
        return "Bear Researcher"
    elif latest_speaker == "Bear":
        logger.debug("Routing: Bear → Bull Researcher")
        return "Bull Researcher"
    else:
        # Fail fast with clear error message
        raise ValueError(
            f"Invalid latest_speaker value: '{latest_speaker}'. "
            f"Expected 'Bull' or 'Bear'. "
            f"Full investment_debate_state: {state['investment_debate_state']}"
        )
```

### 4. Update `bull_researcher.py`

**File**: `tradingagents/agents/researchers/bull_researcher.py`

**Change**: Add `latest_speaker` to `new_investment_debate_state` (line 46-52)

```python
new_investment_debate_state = {
    "history": history + "\n" + argument,
    "bull_history": bull_history + "\n" + argument,
    "bear_history": investment_debate_state.get("bear_history", ""),
    "current_response": argument,
    "count": investment_debate_state["count"] + 1,
    "latest_speaker": "Bull",  # Set routing state
}
```

### 5. Update `bear_researcher.py`

**File**: `tradingagents/agents/researchers/bear_researcher.py`

**Change**: Add `latest_speaker` to `new_investment_debate_state` (line 46-52)

```python
new_investment_debate_state = {
    "history": history + "\n" + argument,
    "bear_history": bear_history + "\n" + argument,
    "bull_history": investment_debate_state.get("bull_history", ""),
    "current_response": argument,
    "count": investment_debate_state["count"] + 1,
    "latest_speaker": "Bear",  # Set routing state
}
```

## Testing Strategy

### Unit Tests

**File**: `tests/graph/test_conditional_logic.py` (NEW)

**Framework**: pytest with fixtures

**Test Cases**:

1. **Normal Routing: Bull → Bear → Bull**
   - Setup: latest_speaker = "Bull", count < max
   - Expect: Routes to "Bear Researcher"
   - Verify: latest_speaker updated to "Bear"

2. **Normal Routing: Bear → Bull**
   - Setup: latest_speaker = "Bear", count < max
   - Expect: Routes to "Bull Researcher"
   - Verify: latest_speaker updated to "Bull"

3. **Debate End: Count Limit Reached**
   - Setup: count >= 2 * max_debate_rounds
   - Expect: Routes to "Research Manager" regardless of latest_speaker

4. **Error Handling: Invalid latest_speaker**
   - Setup: latest_speaker = "Invalid"
   - Expect: Raises ValueError with detailed message

**Fixture Example**:
```python
@pytest.fixture
def investment_debate_state():
    return {
        "history": "",
        "bull_history": "",
        "bear_history": "",
        "current_response": "",
        "judge_decision": "",
        "count": 0,
        "latest_speaker": "Bull"
    }

@pytest.fixture
def agent_state(investment_debate_state):
    return {
        "investment_debate_state": investment_debate_state,
        # ... other required fields
    }
```

### Integration Tests

**File**: `tests/integration/test_investment_debate_flow.py` (NEW)

**Test Scenario**: Full trading graph execution

1. Run complete trading graph for sample stock (601939, 2025-05-10)
2. Verify Bull → Bear → Bull → Research Manager routing
3. Verify no KeyError occurs
4. Verify Chinese output preserved in history

## Verification Checklist

- [ ] `InvestDebateState` includes `latest_speaker` field with type annotation
- [ ] `propagation.py` initializes `latest_speaker = "Bull"`
- [ ] `bull_researcher.py` sets `latest_speaker = "Bull"`
- [ ] `bear_researcher.py` sets `latest_speaker = "Bear"`
- [ ] `conditional_logic.py` routes based on `latest_speaker`, not string prefix
- [ ] Debug logging added to routing logic
- [ ] ValueError raised for invalid `latest_speaker` values
- [ ] Unit tests created in `tests/graph/test_conditional_logic.py`
- [ ] Integration test created in `tests/integration/test_investment_debate_flow.py`
- [ ] All tests pass (`pytest tests/`)
- [ ] Manual test with original failing case (`main.py` with 601939, 2025-05-10)
- [ ] Risk debate team unchanged (verifies no regression)
- [ ] Code comments added explaining `latest_speaker` purpose

## Notes

- **Prompt files unchanged**: No changes needed to `prompts/zh/*.md` files
- **Risk team unchanged**: Risk debate team continues using existing `latest_speaker` pattern
- **No backward compatibility**: Old string prefix checking completely removed
- **Language flexibility**: Output content can now be any language; routing remains independent
- **Performance**: No performance impact; state field access is O(1)

## References

- Error trace: `main.py:29` → `trading_graph.py:197` → `conditional_logic.py:210`
- Related files:
  - `tradingagents/agents/researchers/bull_researcher.py:44`
  - `tradingagents/agents/researchers/bear_researcher.py:44`
  - `tradingagents/graph/conditional_logic.py:53-55`
  - `tradingagents/graph/setup.py:156-171`
- Pattern source: `RiskDebateState` in `agent_states.py:36`
