"""
Unit tests for conditional_logic routing logic.
Tests the investment debate routing based on latest_speaker field.
"""

import pytest
from tradingagents.graph.conditional_logic import ConditionalLogic
from tradingagents.agents.utils.agent_states import InvestDebateState


@pytest.fixture
def conditional_logic():
    """Create a ConditionalLogic instance with default settings."""
    return ConditionalLogic(max_debate_rounds=1, max_risk_discuss_rounds=1)


@pytest.fixture
def investment_debate_state():
    """Create a base investment debate state."""
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
    """Create a full agent state for testing."""
    return {
        "investment_debate_state": investment_debate_state,
        "messages": [],
        "company_of_interest": "601939",
        "trade_date": "2025-05-10",
    }


class TestInvestmentDebateRouting:
    """Test suite for investment debate routing logic."""

    def test_bull_to_bear_routing(self, conditional_logic, agent_state):
        """Test normal routing: Bull → Bear when Bull speaks."""
        agent_state["investment_debate_state"]["latest_speaker"] = "Bull"
        agent_state["investment_debate_state"]["count"] = 0

        result = conditional_logic.should_continue_debate(agent_state)

        assert result == "Bear Researcher", \
            f"Expected 'Bear Researcher' but got '{result}'"

    def test_bear_to_bull_routing(self, conditional_logic, agent_state):
        """Test normal routing: Bear → Bull when Bear speaks."""
        agent_state["investment_debate_state"]["latest_speaker"] = "Bear"
        agent_state["investment_debate_state"]["count"] = 1

        result = conditional_logic.should_continue_debate(agent_state)

        assert result == "Bull Researcher", \
            f"Expected 'Bull Researcher' but got '{result}'"

    def test_debate_end_count_limit(self, conditional_logic, agent_state):
        """Test debate ends when count reaches limit."""
        agent_state["investment_debate_state"]["latest_speaker"] = "Bull"
        agent_state["investment_debate_state"]["count"] = 2  # 2 * max_debate_rounds (1)

        result = conditional_logic.should_continue_debate(agent_state)

        assert result == "Research Manager", \
            f"Expected 'Research Manager' but got '{result}'"

    def test_invalid_latest_speaker(self, conditional_logic, agent_state):
        """Test ValueError raised for invalid latest_speaker."""
        agent_state["investment_debate_state"]["latest_speaker"] = "Invalid"
        agent_state["investment_debate_state"]["count"] = 0

        with pytest.raises(ValueError) as exc_info:
            conditional_logic.should_continue_debate(agent_state)

        error_msg = str(exc_info.value)
        assert "Invalid latest_speaker value" in error_msg
        assert "Invalid" in error_msg
        assert "Expected 'Bull' or 'Bear'" in error_msg

    def test_empty_latest_speaker(self, conditional_logic, agent_state):
        """Test ValueError raised for empty latest_speaker."""
        agent_state["investment_debate_state"]["latest_speaker"] = ""
        agent_state["investment_debate_state"]["count"] = 0

        with pytest.raises(ValueError) as exc_info:
            conditional_logic.should_continue_debate(agent_state)

        error_msg = str(exc_info.value)
        assert "Invalid latest_speaker value" in error_msg

    def test_alternating_routing_cycle(self, conditional_logic, agent_state):
        """Test complete Bull → Bear → Bull routing cycle."""
        # Start with Bull
        agent_state["investment_debate_state"]["latest_speaker"] = "Bull"
        agent_state["investment_debate_state"]["count"] = 0

        # Bull → Bear
        result1 = conditional_logic.should_continue_debate(agent_state)
        assert result1 == "Bear Researcher"

        # Update state to Bear
        agent_state["investment_debate_state"]["latest_speaker"] = "Bear"
        agent_state["investment_debate_state"]["count"] = 1

        # Bear → Bull
        result2 = conditional_logic.should_continue_debate(agent_state)
        assert result2 == "Bull Researcher"

        # Update state back to Bull
        agent_state["investment_debate_state"]["latest_speaker"] = "Bull"
        agent_state["investment_debate_state"]["count"] = 2

        # Count limit reached → Research Manager
        result3 = conditional_logic.should_continue_debate(agent_state)
        assert result3 == "Research Manager"


class TestInvestmentDebateStateStructure:
    """Test suite for InvestDebateState structure."""

    def test_latest_speaker_field_exists(self):
        """Verify latest_speaker field is part of InvestDebateState."""
        state = InvestDebateState(
            history="",
            bull_history="",
            bear_history="",
            current_response="",
            judge_decision="",
            count=0,
            latest_speaker="Bull"
        )

        assert "latest_speaker" in state
        assert state["latest_speaker"] == "Bull"

    def test_latest_speaker_accepts_bull(self):
        """Verify latest_speaker accepts 'Bull'."""
        state = InvestDebateState(
            history="",
            bull_history="",
            bear_history="",
            current_response="",
            judge_decision="",
            count=0,
            latest_speaker="Bull"
        )

        assert state["latest_speaker"] == "Bull"

    def test_latest_speaker_accepts_bear(self):
        """Verify latest_speaker accepts 'Bear'."""
        state = InvestDebateState(
            history="",
            bull_history="",
            bear_history="",
            current_response="",
            judge_decision="",
            count=0,
            latest_speaker="Bear"
        )

        assert state["latest_speaker"] == "Bear"
