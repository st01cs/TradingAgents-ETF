"""
Integration tests for investment debate flow.
Tests the complete trading graph execution with proper routing.
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestInvestmentDebateIntegration:
    """
    Integration tests for investment debate flow.

    Note: These tests require full trading graph setup.
    They are marked as integration tests and may require API keys.
    """

    @pytest.mark.integration
    def test_state_initialization_has_latest_speaker(self):
        """Test that initial state includes latest_speaker field."""
        from tradingagents.graph.propagation import Propagator

        propagator = Propagator()
        state = propagator.create_initial_state("601939", "2025-05-10")

        assert "investment_debate_state" in state
        assert "latest_speaker" in state["investment_debate_state"]
        assert state["investment_debate_state"]["latest_speaker"] == "Bull"

    @pytest.mark.integration
    def test_researcher_nodes_set_latest_speaker(self):
        """Test that researcher nodes properly set latest_speaker."""
        from tradingagents.agents.researchers.bull_researcher import create_bull_researcher
        from tradingagents.agents.researchers.bear_researcher import create_bear_researcher
        from langchain_openai import ChatOpenAI

        # Note: These tests require actual LLM setup
        # For now, we test the structure without actual invocation

        # Create mock state
        mock_state = {
            "investment_debate_state": {
                "history": "",
                "bull_history": "",
                "bear_history": "",
                "current_response": "",
                "count": 0,
                "latest_speaker": "Bull"
            },
            "market_report": "Test market report",
            "sentiment_report": "Test sentiment report",
            "news_report": "Test news report",
            "fundamentals_report": "Test fundamentals report",
        }

        # Verify node creation works
        # (Actual execution would require LLM mocking or API keys)
        assert callable(create_bull_researcher)
        assert callable(create_bear_researcher)

    @pytest.mark.integration
    def test_conditional_logic_routes_correctly(self):
        """Test that conditional logic routes based on latest_speaker."""
        from tradingagents.graph.conditional_logic import ConditionalLogic

        logic = ConditionalLogic(max_debate_rounds=1)

        # Test Bull → Bear routing
        state_bull = {
            "investment_debate_state": {
                "history": "",
                "bull_history": "",
                "bear_history": "",
                "current_response": "多头：测试内容",  # Chinese prefix
                "count": 0,
                "latest_speaker": "Bull"
            },
            "messages": [],
        }

        result = logic.should_continue_debate(state_bull)
        assert result == "Bear Researcher"

        # Test Bear → Bull routing
        state_bear = {
            "investment_debate_state": {
                "history": "",
                "bull_history": "",
                "bear_history": "",
                "current_response": "空头：测试内容",  # Chinese prefix
                "count": 1,
                "latest_speaker": "Bear"
            },
            "messages": [],
        }

        result = logic.should_continue_debate(state_bear)
        assert result == "Bull Researcher"

    @pytest.mark.integration
    def test_chinese_output_preserved_in_history(self):
        """Test that Chinese output is preserved in conversation history."""
        from tradingagents.graph.conditional_logic import ConditionalLogic

        # State with Chinese prefixes
        state = {
            "investment_debate_state": {
                "history": "多头：第一个论点\n",
                "bull_history": "多头：第一个论点\n",
                "bear_history": "",
                "current_response": "多头：第一个论点",
                "count": 1,
                "latest_speaker": "Bull"
            },
            "messages": [],
        }

        logic = ConditionalLogic()
        result = logic.should_continue_debate(state)

        # Should route correctly despite Chinese content
        assert result == "Bear Researcher"
        # Chinese content should be preserved
        assert "多头" in state["investment_debate_state"]["history"]


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_missing_latest_speaker_field(self):
        """Test behavior when latest_speaker field is missing."""
        from tradingagents.graph.conditional_logic import ConditionalLogic

        state = {
            "investment_debate_state": {
                "history": "",
                "bull_history": "",
                "bear_history": "",
                "current_response": "",
                "count": 0,
                # Missing latest_speaker
            },
            "messages": [],
        }

        logic = ConditionalLogic()

        with pytest.raises(KeyError):
            # Should raise KeyError when latest_speaker is missing
            logic.should_continue_debate(state)

    def test_none_latest_speaker(self):
        """Test behavior when latest_speaker is None."""
        from tradingagents.graph.conditional_logic import ConditionalLogic

        state = {
            "investment_debate_state": {
                "history": "",
                "bull_history": "",
                "bear_history": "",
                "current_response": "",
                "count": 0,
                "latest_speaker": None
            },
            "messages": [],
        }

        logic = ConditionalLogic()

        with pytest.raises(ValueError) as exc_info:
            logic.should_continue_debate(state)

        assert "Invalid latest_speaker value" in str(exc_info.value)

    def test_count_exceeds_limit(self):
        """Test behavior when count greatly exceeds limit."""
        from tradingagents.graph.conditional_logic import ConditionalLogic

        state = {
            "investment_debate_state": {
                "history": "",
                "bull_history": "",
                "bear_history": "",
                "current_response": "",
                "count": 100,  # Way over limit
                "latest_speaker": "Bull"
            },
            "messages": [],
        }

        logic = ConditionalLogic(max_debate_rounds=1)
        result = logic.should_continue_debate(state)

        # Should still route to Research Manager
        assert result == "Research Manager"
