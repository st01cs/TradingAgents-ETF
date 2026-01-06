"""Unit tests for FinancialSituationMemory embedding configuration."""

import os
import pytest
from tradingagents.agents.utils.memory import FinancialSituationMemory


class TestEmbeddingConfiguration:
    """Test suite for embedding configuration validation and initialization."""

    def test_embedding_configuration_success(self):
        """Test that valid embedding configuration initializes correctly."""
        config = {
            "embedding": {
                "endpoint": "https://api.openai.com/v1",
                "model": "text-embedding-3-small",
                "api_key": "sk-test-key"
            }
        }
        memory = FinancialSituationMemory("test", config)

        assert memory.embedding == "text-embedding-3-small"
        assert memory.client is not None
        assert memory.situation_collection is not None

    def test_embedding_configuration_missing_embedding_key(self):
        """Test that missing 'embedding' configuration raises ValueError."""
        config = {}
        with pytest.raises(ValueError, match="Missing 'embedding' configuration"):
            FinancialSituationMemory("test", config)

    def test_embedding_configuration_missing_endpoint(self):
        """Test that missing 'endpoint' field raises ValueError."""
        config = {
            "embedding": {
                "model": "text-embedding-3-small",
                "api_key": "sk-test-key"
            }
        }
        with pytest.raises(ValueError, match="Missing required field 'endpoint'"):
            FinancialSituationMemory("test", config)

    def test_embedding_configuration_missing_model(self):
        """Test that missing 'model' field raises ValueError."""
        config = {
            "embedding": {
                "endpoint": "https://api.openai.com/v1",
                "api_key": "sk-test-key"
            }
        }
        with pytest.raises(ValueError, match="Missing required field 'model'"):
            FinancialSituationMemory("test", config)

    def test_embedding_configuration_missing_api_key(self):
        """Test that missing 'api_key' field without env var raises ValueError."""
        # Ensure environment variable is not set
        if "EMBEDDING_API_KEY" in os.environ:
            del os.environ["EMBEDDING_API_KEY"]

        config = {
            "embedding": {
                "endpoint": "https://api.openai.com/v1",
                "model": "text-embedding-3-small"
            }
        }
        with pytest.raises(ValueError, match="API key must be provided either in config"):
            FinancialSituationMemory("test", config)

    def test_embedding_configuration_empty_endpoint(self):
        """Test that empty 'endpoint' field raises ValueError."""
        config = {
            "embedding": {
                "endpoint": "",
                "model": "text-embedding-3-small",
                "api_key": "sk-test-key"
            }
        }
        with pytest.raises(ValueError, match="Field 'endpoint' must be a non-empty string"):
            FinancialSituationMemory("test", config)

    def test_embedding_configuration_empty_model(self):
        """Test that empty 'model' field raises ValueError."""
        config = {
            "embedding": {
                "endpoint": "https://api.openai.com/v1",
                "model": "",
                "api_key": "sk-test-key"
            }
        }
        with pytest.raises(ValueError, match="Field 'model' must be a non-empty string"):
            FinancialSituationMemory("test", config)

    def test_embedding_configuration_empty_api_key(self):
        """Test that empty 'api_key' field without env var raises ValueError."""
        # Ensure environment variable is not set
        if "EMBEDDING_API_KEY" in os.environ:
            del os.environ["EMBEDDING_API_KEY"]

        config = {
            "embedding": {
                "endpoint": "https://api.openai.com/v1",
                "model": "text-embedding-3-small",
                "api_key": ""
            }
        }
        with pytest.raises(ValueError, match="API key must be provided either in config"):
            FinancialSituationMemory("test", config)

    def test_embedding_configuration_non_string_endpoint(self):
        """Test that non-string 'endpoint' field raises ValueError."""
        config = {
            "embedding": {
                "endpoint": 123,
                "model": "text-embedding-3-small",
                "api_key": "sk-test-key"
            }
        }
        with pytest.raises(ValueError, match="Field 'endpoint' must be a non-empty string"):
            FinancialSituationMemory("test", config)

    def test_embedding_configuration_non_string_model(self):
        """Test that non-string 'model' field raises ValueError."""
        config = {
            "embedding": {
                "endpoint": "https://api.openai.com/v1",
                "model": None,
                "api_key": "sk-test-key"
            }
        }
        with pytest.raises(ValueError, match="Field 'model' must be a non-empty string"):
            FinancialSituationMemory("test", config)

    def test_embedding_configuration_ollama(self):
        """Test that Ollama configuration initializes correctly."""
        config = {
            "embedding": {
                "endpoint": "http://localhost:11434/v1",
                "model": "nomic-embed-text",
                "api_key": "dummy-key"
            }
        }
        memory = FinancialSituationMemory("test_ollama", config)

        assert memory.embedding == "nomic-embed-text"
        assert memory.client is not None
        assert memory.situation_collection is not None

    def test_embedding_configuration_deepseek(self):
        """Test that DeepSeek configuration initializes correctly."""
        config = {
            "embedding": {
                "endpoint": "https://api.deepseek.com/v1",
                "model": "deepseek-embedding",
                "api_key": "sk-deepseek-key"
            }
        }
        memory = FinancialSituationMemory("test_deepseek", config)

        assert memory.embedding == "deepseek-embedding"
        assert memory.client is not None
        assert memory.situation_collection is not None

    def test_multiple_memory_instances(self):
        """Test that multiple memory instances can be created with the same config."""
        config = {
            "embedding": {
                "endpoint": "https://api.openai.com/v1",
                "model": "text-embedding-3-small",
                "api_key": "sk-test-key"
            }
        }

        bull_memory = FinancialSituationMemory("bull_memory", config)
        bear_memory = FinancialSituationMemory("bear_memory", config)
        trader_memory = FinancialSituationMemory("trader_memory", config)

        assert bull_memory.embedding == "text-embedding-3-small"
        assert bear_memory.embedding == "text-embedding-3-small"
        assert trader_memory.embedding == "text-embedding-3-small"

        # Each should have its own collection
        assert bull_memory.situation_collection.name != bear_memory.situation_collection.name
        assert bear_memory.situation_collection.name != trader_memory.situation_collection.name

    def test_api_key_from_environment_variable(self, monkeypatch):
        """Test that api_key can be read from EMBEDDING_API_KEY environment variable."""
        # Set environment variable
        monkeypatch.setenv("EMBEDDING_API_KEY", "sk-env-key")

        config = {
            "embedding": {
                "endpoint": "https://api.openai.com/v1",
                "model": "text-embedding-3-small"
                # No api_key in config
            }
        }
        memory = FinancialSituationMemory("test_env_var", config)

        assert memory.embedding == "text-embedding-3-small"
        assert memory.client is not None

    def test_api_key_config_takes_precedence_over_env(self, monkeypatch):
        """Test that api_key in config takes precedence over environment variable."""
        # Set environment variable
        monkeypatch.setenv("EMBEDDING_API_KEY", "sk-env-key")

        config = {
            "embedding": {
                "endpoint": "https://api.openai.com/v1",
                "model": "text-embedding-3-small",
                "api_key": "sk-config-key"  # This should be used
            }
        }
        memory = FinancialSituationMemory("test_precedence", config)

        assert memory.embedding == "text-embedding-3-small"
        assert memory.client is not None

    def test_api_key_empty_string_uses_env(self, monkeypatch):
        """Test that empty string api_key falls back to environment variable."""
        # Set environment variable
        monkeypatch.setenv("EMBEDDING_API_KEY", "sk-env-key")

        config = {
            "embedding": {
                "endpoint": "https://api.openai.com/v1",
                "model": "text-embedding-3-small",
                "api_key": ""  # Empty string should use env var
            }
        }
        memory = FinancialSituationMemory("test_empty_string", config)

        assert memory.embedding == "text-embedding-3-small"
        assert memory.client is not None

    def test_api_key_none_uses_env(self, monkeypatch):
        """Test that None api_key falls back to environment variable."""
        # Set environment variable
        monkeypatch.setenv("EMBEDDING_API_KEY", "sk-env-key")

        config = {
            "embedding": {
                "endpoint": "https://api.openai.com/v1",
                "model": "text-embedding-3-small",
                "api_key": None  # None should use env var
            }
        }
        memory = FinancialSituationMemory("test_none", config)

        assert memory.embedding == "text-embedding-3-small"
        assert memory.client is not None

