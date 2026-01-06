# Specification: Configurable Embedding Interface for Memory System

## Overview
Refactor the memory mechanism's embedding interface to support configurable embedding providers, replacing the current hardcoded logic that determines the embedding model based on `backend_url`.

## Current State Analysis

### Current Implementation (`tradingagents/agents/utils/memory.py:8-21`)
```python
def __init__(self, name, config):
    if config["backend_url"] == "http://localhost:11434/v1":
        self.embedding = "nomic-embed-text"
    else:
        self.embedding = "text-embedding-3-small"
    self.client = OpenAI(base_url=config["backend_url"])
```

### Problems Identified
1. **Hardcoded model selection**: Model name determined by URL string matching
2. **Shared LLM configuration**: Embedding provider reuses LLM's `backend_url`
3. **Tight coupling**: No independent configuration for embedding
4. **Limited extensibility**: Difficult to add new embedding providers

### Usage Context
- 5 independent memory instances in `trading_graph.py:111-115`:
  - `bull_memory`
  - `bear_memory`
  - `trader_memory`
  - `invest_judge_memory`
  - `risk_manager_memory`

## Requirements

### 1. Configuration Design

#### Configuration Structure
**Format**: Simple nested dictionary
```python
config = {
    # ... other config ...
    "embedding": {
        "endpoint": "https://api.openai.com/v1",  # Required: Complete URL
        "model": "text-embedding-3-small",         # Required: Model name
        "api_key": "sk-..."                        # Required: API key
    }
}
```

#### Field Requirements
- **Required fields** (all must be non-empty strings):
  - `endpoint`: Complete API endpoint URL (e.g., `https://api.openai.com/v1`)
  - `model`: Embedding model name (e.g., `text-embedding-3-small`)
  - `api_key`: Authentication token

#### URL Handling
- User must provide **complete URL** including `/v1` suffix
- No automatic URL modification or suffix addition

#### API Key Handling
- **Required field**: Must be provided even for local providers
- No environment variable fallback
- If `None` or empty string, treat as configuration error

### 2. Functional Requirements

#### Provider Support
- **OpenAI-compatible APIs only**
- Use OpenAI SDK with configurable `base_url`
- Support: OpenAI, DeepSeek, Ollama (OpenAI-compatible mode)

#### Scope
- **Global sharing**: All 5 memory instances use the same embedding configuration
- No per-instance embedding configuration override

#### Error Handling
- **Fast failure**: No automatic retry or fallback on API failures
- **Configuration validation**: Validate in `__init__`, fail fast if misconfigured
- **Exception type**: Use `ValueError` for all configuration errors
- **Validation checks**:
  - `config` is a dict
  - `config["embedding"]` exists
  - `config["embedding"]` contains `endpoint`, `model`, `api_key` keys
  - All values are non-empty strings

#### Performance
- **No performance optimizations**: No caching, no batch API calls
- Keep implementation simple

### 3. Backward Compatibility

**Breaking Change**: No backward compatibility
- Remove hardcoded `backend_url` logic
- Require explicit embedding configuration
- No automatic fallback to old behavior
- No migration support needed

### 4. Code Organization

**Approach**: In-place modification
- Modify existing `FinancialSituationMemory` class
- Update `__init__` and `get_embedding` methods
- No new classes or modules
- Maintain existing API surface

### 5. Testing Strategy

**Test Coverage**: Unit tests focused on normal flow
- Test correct embedding configuration initializes successfully
- Test embedding API calls work as expected
- Focus on happy path validation
- Existing tests should continue to work

### 6. Documentation

#### README Documentation
- Add embedding configuration to existing configuration section
- Provide examples for common providers:
  - OpenAI
  - DeepSeek
  - Ollama

#### Code Documentation
- Add detailed docstrings to `FinancialSituationMemory.__init__`
- Document configuration format
- Document required fields and their meanings

### 7. Logging

**Log Level**: INFO
- Log embedding configuration on initialization:
  - Endpoint
  - Model name
- No DEBUG level logging for API calls
- No additional logging overhead

### 8. Non-Requirements

Explicitly **NOT** included:
- ❌ Multi-provider support (only one active embedding provider)
- ❌ Provider fallback mechanism
- ❌ Automatic retry on API failures
- ❌ Embedding caching
- ❌ Batch embedding API calls
- ❌ Dimension validation or checking
- ❌ Connectivity testing in `__init__`
- ❌ CLI validation tools
- ❌ Environment variable configuration
- ❌ Per-instance embedding configuration override

## Implementation Plan

### Phase 1: Modify FinancialSituationMemory Class

**File**: `tradingagents/agents/utils/memory.py`

#### Changes to `__init__` method:
1. Remove hardcoded `backend_url` checking logic
2. Add embedding configuration extraction
3. Validate embedding configuration
4. Initialize OpenAI client with embedding-specific config
5. Add INFO logging

#### New validation logic:
```python
def __init__(self, name, config):
    # Validate embedding configuration
    if "embedding" not in config:
        raise ValueError("Missing 'embedding' configuration")

    embedding_config = config["embedding"]

    required_fields = ["endpoint", "model", "api_key"]
    for field in required_fields:
        if field not in embedding_config:
            raise ValueError(f"Missing required field '{field}' in embedding configuration")
        if not embedding_config[field] or not isinstance(embedding_config[field], str):
            raise ValueError(f"Field '{field}' must be a non-empty string")

    self.embedding = embedding_config["model"]
    self.client = OpenAI(
        base_url=embedding_config["endpoint"],
        api_key=embedding_config["api_key"]
    )

    # Rest of initialization remains the same
    self.chroma_client = chromadb.Client(Settings(allow_reset=True))
    self.situation_collection = self.chroma_client.create_collection(name=name)

    # Log configuration
    logger.info(f"Initialized memory '{name}' with embedding: "
                f"endpoint={embedding_config['endpoint']}, "
                f"model={embedding_config['model']}")
```

#### Changes to `get_embedding` method:
- No changes needed (already uses `self.embedding` and `self.client`)

### Phase 2: Update Documentation

#### README updates:
- Add "Embedding Configuration" subsection to existing configuration section
- Provide configuration examples:
  ```yaml
  # config.yaml
  embedding:
    endpoint: https://api.openai.com/v1
    model: text-embedding-3-small
    api_key: sk-your-api-key-here
  ```

#### Code documentation:
- Update class docstring with configuration format
- Add parameter documentation for `config` argument

### Phase 3: Update Tests

**File**: New test file or add to existing test suite

```python
def test_embedding_configuration_success():
    """Test that valid embedding configuration initializes correctly"""
    config = {
        "embedding": {
            "endpoint": "https://api.openai.com/v1",
            "model": "text-embedding-3-small",
            "api_key": "sk-test-key"
        }
    }
    memory = FinancialSituationMemory("test", config)
    assert memory.embedding == "text-embedding-3-small"

def test_embedding_configuration_missing_field():
    """Test that missing required fields raise ValueError"""
    config = {
        "embedding": {
            "endpoint": "https://api.openai.com/v1",
            # Missing 'model' and 'api_key'
        }
    }
    with pytest.raises(ValueError, match="Missing required field"):
        FinancialSituationMemory("test", config)
```

### Phase 4: Update Default Configuration

**File**: `tradingagents/default_config.py`

Add embedding configuration to `DEFAULT_CONFIG`:
```python
DEFAULT_CONFIG = {
    # ... existing config ...
    "embedding": {
        "endpoint": "https://api.openai.com/v1",
        "model": "text-embedding-3-small",
        "api_key": None  # Users must override this
    }
}
```

## Configuration Examples

### Example 1: OpenAI
```python
config = {
    "embedding": {
        "endpoint": "https://api.openai.com/v1",
        "model": "text-embedding-3-small",
        "api_key": "sk-proj-..."
    }
}
```

### Example 2: DeepSeek
```python
config = {
    "embedding": {
        "endpoint": "https://api.deepseek.com/v1",  # Adjust if different
        "model": "deepseek-embedding",  # Use actual model name
        "api_key": "sk-..."
    }
}
```

### Example 3: Ollama (Local)
```python
config = {
    "embedding": {
        "endpoint": "http://localhost:11434/v1",
        "model": "nomic-embed-text",
        "api_key": "dummy-key"  # Required even for local
    }
}
```

## Success Criteria

1. ✅ Embedding provider is independently configurable
2. ✅ Configuration validation prevents misconfiguration
3. ✅ All 5 memory instances work with new configuration
4. ✅ Unit tests pass for normal flow
5. ✅ README documents configuration format
6. ✅ Code is well-documented with docstrings
7. ✅ Breaking change is clearly communicated
8. ✅ No backward compatibility remains

## Migration Guide for Users

### Before (Old Configuration)
```python
config = {
    "backend_url": "https://api.openai.com/v1",
    # Memory automatically uses text-embedding-3-small
}
```

### After (New Configuration)
```python
config = {
    "backend_url": "https://api.openai.com/v1",  # For LLM
    "embedding": {
        "endpoint": "https://api.openai.com/v1",  # For embeddings
        "model": "text-embedding-3-small",
        "api_key": "sk-..."
    }
}
```

### Action Required
Users must add `embedding` configuration to their config files with all three required fields.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking change disrupts existing users | High | Clear documentation and error messages guide users to add required config |
| Incorrect API keys cause silent failures | Medium | Validate all required fields in `__init__` |
| Different embedding dimensions cause issues | Low | Not handling dimension validation; trusting provider returns correct dimensions |

## Future Considerations

Out of scope for this implementation but may be considered later:
1. Multi-provider support with routing
2. Embedding caching for performance
3. Batch API calls for efficiency
4. Dimension validation and checking
5. Provider-specific optimizations
6. Alternative embedding providers (Cohere, Sentence Transformers, etc.)

## Appendix

### Current Code Locations
- Memory implementation: `tradingagents/agents/utils/memory.py`
- Memory usage: `tradingagents/graph/trading_graph.py:111-115`
- Tests: `tests/test_llm_providers/test_deepchat.py`

### Related Issues/PRs
- None tracked yet

### References
- OpenAI Embeddings API: https://platform.openai.com/docs/guides/embeddings
- ChromaDB Documentation: https://docs.trychroma.com/
