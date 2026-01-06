"""
Unit tests for market_analyst prompt loading functionality.

Tests the load_prompt_template function to ensure:
- Multi-language loading (Chinese and English)
- Default language behavior
- Environment variable configuration
- Error handling for missing files
"""

import os
import pytest
from tradingagents.agents.utils.agent_utils import load_prompt_template


class TestMultiLanguageLoading:
    """Test loading prompts in different languages."""

    def test_load_chinese_prompt(self):
        """Test loading Chinese prompt template."""
        prompt = load_prompt_template('market_analyst', 'zh')
        assert prompt is not None
        assert len(prompt) > 0
        assert '你是一位负责分析金融市场的交易助手' in prompt
        assert '(Moving Averages)' in prompt or 'Moving Averages' in prompt  # Technical terms kept in English
        assert 'MACD' in prompt

    def test_load_english_prompt(self):
        """Test loading English prompt template."""
        prompt = load_prompt_template('market_analyst', 'en')
        assert prompt is not None
        assert len(prompt) > 0
        assert 'You are a trading assistant tasked with analyzing financial markets' in prompt


class TestDefaultLanguage:
    """Test default language behavior."""

    def test_default_language_is_chinese(self):
        """Test that default language is Chinese when LANGUAGE is not set."""
        # Remove LANGUAGE from environment
        language_backup = os.environ.get('LANGUAGE')
        os.environ.pop('LANGUAGE', None)

        try:
            prompt = load_prompt_template('market_analyst')
            assert prompt is not None
            assert '你是一位负责分析金融市场的交易助手' in prompt
        finally:
            # Restore LANGUAGE if it was set
            if language_backup:
                os.environ['LANGUAGE'] = language_backup


class TestEnvironmentVariable:
    """Test LANGUAGE environment variable configuration."""

    def test_language_from_env_variable_chinese(self):
        """Test loading Chinese prompt via LANGUAGE environment variable."""
        os.environ['LANGUAGE'] = 'zh'
        prompt = load_prompt_template('market_analyst')
        assert prompt is not None
        assert '你是一位负责分析金融市场的交易助手' in prompt

    def test_language_from_env_variable_english(self):
        """Test loading English prompt via LANGUAGE environment variable."""
        os.environ['LANGUAGE'] = 'en'
        prompt = load_prompt_template('market_analyst')
        assert prompt is not None
        assert 'You are a trading assistant tasked with analyzing financial markets' in prompt

    def test_explicit_language_overrides_env_variable(self):
        """Test that explicit language parameter overrides environment variable."""
        os.environ['LANGUAGE'] = 'en'
        # Explicit 'zh' should override 'en' from environment
        prompt = load_prompt_template('market_analyst', 'zh')
        assert prompt is not None
        assert '你是一位负责分析金融市场的交易助手' in prompt


class TestErrorHandling:
    """Test error handling for invalid inputs."""

    def test_prompt_file_not_found(self):
        """Test ValueError when using invalid language code."""
        # Invalid language codes are validated before file access
        with pytest.raises(ValueError) as exc_info:
            load_prompt_template('market_analyst', 'fr')

        error_message = str(exc_info.value)
        assert 'Invalid language code' in error_message
        assert 'fr' in error_message
        assert 'Valid options' in error_message

    def test_invalid_language_code(self):
        """Test ValueError for invalid language code."""
        with pytest.raises(ValueError) as exc_info:
            load_prompt_template('market_analyst', 'invalid')

        error_message = str(exc_info.value)
        assert 'Invalid language code' in error_message
        assert 'invalid' in error_message
        assert 'Valid options' in error_message

    def test_nonexistent_agent(self):
        """Test FileNotFoundError when agent doesn't exist."""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_prompt_template('nonexistent_agent', 'zh')

        error_message = str(exc_info.value)
        assert 'Prompt file not found' in error_message
        assert 'nonexistent_agent' in error_message


class TestPromptContent:
    """Test that loaded prompts contain expected content."""

    def test_chinese_prompt_contains_key_sections(self):
        """Test that Chinese prompt contains all required sections."""
        prompt = load_prompt_template('market_analyst', 'zh')

        # Check for main sections
        assert '## 移动平均线' in prompt or 'Moving Averages' in prompt
        assert 'MACD相关指标' in prompt or 'MACD' in prompt
        assert '动量指标' in prompt or 'Momentum' in prompt

        # Check for A-share notes
        assert 'A股市场注意事项' in prompt or 'A-share' in prompt or '涨跌停' in prompt

        # Check for report requirements
        assert 'Markdown表格' in prompt or 'Markdown table' in prompt
        assert '关键价格点位' in prompt or 'Key Price Points' in prompt

    def test_english_prompt_contains_key_sections(self):
        """Test that English prompt contains all required sections."""
        prompt = load_prompt_template('market_analyst', 'en')

        # Check for main sections
        assert 'Moving Averages' in prompt
        assert 'MACD Related' in prompt
        assert 'Momentum Indicators' in prompt

        # Check for report requirements
        assert 'Markdown table' in prompt

    def test_chinese_prompt_preserves_technical_terms(self):
        """Test that Chinese prompt preserves technical indicator names in English."""
        prompt = load_prompt_template('market_analyst', 'zh')

        # Check that technical terms are kept in English
        assert 'close_50_sma' in prompt
        assert 'close_200_sma' in prompt
        assert 'close_10_ema' in prompt
        assert 'macd' in prompt
        assert 'rsi' in prompt
        assert 'boll' in prompt
        assert 'atr' in prompt
        assert 'vwma' in prompt

    def test_both_prompts_have_tools_instruction(self):
        """Test that both prompts include tool usage instructions."""
        zh_prompt = load_prompt_template('market_analyst', 'zh')
        en_prompt = load_prompt_template('market_analyst', 'en')

        # Check for get_stock_data and get_indicators instructions
        assert 'get_stock_data' in zh_prompt
        assert 'get_indicators' in zh_prompt
        assert 'get_stock_data' in en_prompt
        assert 'get_indicators' in en_prompt
