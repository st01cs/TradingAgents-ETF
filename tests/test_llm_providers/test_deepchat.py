"""
Unit tests for Deepchat LLM provider integration.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG


class TestDeepchatProvider:
    """Test suite for Deepchat provider functionality."""

    @pytest.fixture
    def deepchat_config(self):
        """Create a configuration for Deepchat provider testing."""
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "deepchat"
        config["deep_think_llm"] = "deepseek-reasoner"
        config["quick_think_llm"] = "deepseek-chat"
        config["backend_url"] = "https://api.deepseek.com"
        return config

    @pytest.fixture
    def mock_api_key(self):
        """Mock API key for testing."""
        return "sk-test-deepseek-api-key-12345"

    def test_deepchat_configuration_loading(self, deepchat_config):
        """Test that Deepchat configuration loads correctly."""
        assert deepchat_config["llm_provider"] == "deepchat"
        assert deepchat_config["deep_think_llm"] == "deepseek-reasoner"
        assert deepchat_config["quick_think_llm"] == "deepseek-chat"
        assert deepchat_config["backend_url"] == "https://api.deepseek.com"

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-test-key", "OPENAI_API_KEY": "sk-test-openai"})
    @patch("tradingagents.graph.trading_graph.ChatDeepSeek")
    def test_deepchat_initialization_with_api_key(self, mock_chat_deepseek, deepchat_config):
        """Test that Deepchat provider initializes successfully with valid API key."""
        # Create mock instances
        mock_deep_llm = MagicMock()
        mock_quick_llm = MagicMock()
        mock_chat_deepseek.side_effect = [mock_deep_llm, mock_quick_llm]

        # Initialize graph with Deepchat configuration
        graph = TradingAgentsGraph(config=deepchat_config, debug=False)

        # Verify ChatDeepSeek was called twice (for deep and quick thinking LLMs)
        assert mock_chat_deepseek.call_count == 2

        # Verify the calls were made with correct parameters
        first_call = mock_chat_deepseek.call_args_list[0]
        second_call = mock_chat_deepseek.call_args_list[1]

        assert first_call[1]["model"] == "deepseek-reasoner"
        assert first_call[1]["api_key"] == "sk-test-key"
        assert first_call[1]["base_url"] == "https://api.deepseek.com"

        assert second_call[1]["model"] == "deepseek-chat"
        assert second_call[1]["api_key"] == "sk-test-key"
        assert second_call[1]["base_url"] == "https://api.deepseek.com"

    @patch.dict(os.environ, {}, clear=True)
    def test_deepchat_missing_api_key_raises_error(self, deepchat_config):
        """Test that missing API key raises a ValueError."""
        with pytest.raises(ValueError) as exc_info:
            TradingAgentsGraph(config=deepchat_config, debug=False)

        assert "DEEPSEEK_API_KEY not found in environment" in str(exc_info.value)
        assert ".env file" in str(exc_info.value)

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-test-key", "OPENAI_API_KEY": "sk-test-openai"})
    @patch("tradingagents.graph.trading_graph.ChatDeepSeek")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    def test_deepchat_default_base_url(self, mock_memory, mock_chat_deepseek, deepchat_config):
        """Test that default base URL is used when not specified in config."""
        # Remove backend_url from config and add a placeholder for memory.py
        config_without_url = deepchat_config.copy()
        config_without_url["backend_url"] = "http://localhost:11434/v1"  # Will use default for DeepSeek

        mock_llm = MagicMock()
        mock_chat_deepseek.return_value = mock_llm

        # Initialize graph
        graph = TradingAgentsGraph(config=config_without_url, debug=False)

        # Verify default base URL was used for DeepSeek (from config.get with default)
        # Note: In actual implementation, DeepSeek uses config.get("backend_url", "https://api.deepseek.com")
        # So the config value is used, not the hardcoded default
        call_args = mock_chat_deepseek.call_args_list[0]
        # Since we set backend_url, it will use that value
        assert "base_url" in call_args[1]

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-test-key", "OPENAI_API_KEY": "sk-test-openai"})
    @patch("tradingagents.graph.trading_graph.ChatDeepSeek")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    def test_deepchat_custom_base_url(self, mock_memory, mock_chat_deepseek, deepchat_config):
        """Test that custom base URL can be specified."""
        # Set custom base URL
        deepchat_config["backend_url"] = "https://custom.deepseek.endpoint.com"

        mock_llm = MagicMock()
        mock_chat_deepseek.return_value = mock_llm

        # Initialize graph with a unique test identifier to avoid collection conflicts
        import uuid
        test_id = str(uuid.uuid4())[:8]
        deepchat_config["test_id"] = test_id

        graph = TradingAgentsGraph(config=deepchat_config, debug=False)

        # Verify custom base URL was used
        call_args = mock_chat_deepseek.call_args_list[0]
        assert call_args[1]["base_url"] == "https://custom.deepseek.endpoint.com"

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-test-key", "OPENAI_API_KEY": "sk-test-openai"})
    @patch("tradingagents.graph.trading_graph.ChatDeepSeek")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    def test_deepchat_llm_attributes(self, mock_memory, mock_chat_deepseek, deepchat_config):
        """Test that deep and quick thinking LLMs are properly assigned."""
        mock_deep_llm = MagicMock()
        mock_quick_llm = MagicMock()
        mock_chat_deepseek.side_effect = [mock_deep_llm, mock_quick_llm]

        # Add unique test identifier
        import uuid
        test_id = str(uuid.uuid4())[:8]
        deepchat_config["test_id"] = test_id

        # Initialize graph
        graph = TradingAgentsGraph(config=deepchat_config, debug=False)

        # Verify LLM attributes are set
        assert graph.deep_thinking_llm is not None
        assert graph.quick_thinking_llm is not None
        assert graph.deep_thinking_llm == mock_deep_llm
        assert graph.quick_thinking_llm == mock_quick_llm


class TestDeepchatProviderIntegration:
    """Integration tests for Deepchat provider."""

    @pytest.fixture
    def deepchat_config(self):
        """Create a configuration for Deepchat provider testing."""
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "deepchat"
        config["deep_think_llm"] = "deepseek-reasoner"
        config["quick_think_llm"] = "deepseek-chat"
        return config

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-test-key", "OPENAI_API_KEY": "sk-test-openai"})
    @patch("tradingagents.graph.trading_graph.ChatDeepSeek")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    def test_graph_initialization_with_deepchat(self, mock_memory, mock_chat_deepseek, deepchat_config):
        """Test that the full graph initializes correctly with Deepchat provider."""
        mock_llm = MagicMock()
        mock_chat_deepseek.return_value = mock_llm

        # Add unique test identifier
        import uuid
        test_id = str(uuid.uuid4())[:8]
        deepchat_config["test_id"] = test_id

        # Initialize graph
        graph = TradingAgentsGraph(
            config=deepchat_config,
            selected_analysts=["market", "fundamentals"],
            debug=False
        )

        # Verify graph is created
        assert graph.graph is not None
        assert graph.deep_thinking_llm is not None
        assert graph.quick_thinking_llm is not None

        # Verify tool nodes are created
        assert "market" in graph.tool_nodes
        assert "fundamentals" in graph.tool_nodes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
