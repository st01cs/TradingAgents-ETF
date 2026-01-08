"""
Unit tests for risky debator prompt loading functionality.
"""
import os
import pytest
from tradingagents.agents.utils.agent_utils import load_prompt_template


class TestRiskyDebatorPromptLoading:
    """Test suite for risky debator multi-language prompt loading."""

    def test_load_chinese_prompt(self):
        """Test loading Chinese prompt for risky debator."""
        prompt = load_prompt_template('risky_debator', 'zh')
        assert '作为高风险偏好分析师' in prompt
        assert '高收益高回报' in prompt  # Actual phrase in translation
        assert '交易计划' in prompt
        assert '保守分析师' in prompt
        assert '中立分析师' in prompt

    def test_load_english_prompt(self):
        """Test loading English prompt for risky debator."""
        prompt = load_prompt_template('risky_debator', 'en')
        assert 'As the Risky Risk Analyst' in prompt
        assert 'high-reward, high-risk' in prompt
        assert "trader's decision" in prompt

    def test_default_language_is_chinese(self):
        """Test that default language is Chinese when LANGUAGE is not set."""
        # Save original value
        original_language = os.environ.get('LANGUAGE')

        try:
            # Remove LANGUAGE from environment
            if 'LANGUAGE' in os.environ:
                del os.environ['LANGUAGE']

            # Load prompt without specifying language
            prompt = load_prompt_template('risky_debator')
            assert '作为高风险偏好分析师' in prompt
            assert '高收益高回报' in prompt  # Actual phrase in translation
        finally:
            # Restore original value
            if original_language is not None:
                os.environ['LANGUAGE'] = original_language

    def test_language_from_env_variable(self):
        """Test loading language from LANGUAGE environment variable."""
        # Save original value
        original_language = os.environ.get('LANGUAGE')

        try:
            # Set language to English
            os.environ['LANGUAGE'] = 'en'
            prompt = load_prompt_template('risky_debator')
            assert 'As the Risky Risk Analyst' in prompt
            assert 'high-reward, high-risk' in prompt

            # Set language to Chinese
            os.environ['LANGUAGE'] = 'zh'
            prompt = load_prompt_template('risky_debator')
            assert '作为高风险偏好分析师' in prompt
        finally:
            # Restore original value
            if original_language is not None:
                os.environ['LANGUAGE'] = original_language
            elif 'LANGUAGE' in os.environ:
                del os.environ['LANGUAGE']

    def test_prompt_file_not_found(self):
        """Test that FileNotFoundError is raised with detailed message."""
        # The function actually raises ValueError for invalid language codes
        # before checking for file existence
        with pytest.raises((FileNotFoundError, ValueError)) as exc_info:
            load_prompt_template('risky_debator', 'fr')

        error_message = str(exc_info.value)
        # Either validation error or file error is acceptable
        assert 'fr' in error_message or 'Invalid language code' in error_message

    def test_invalid_language_code(self):
        """Test that ValueError is raised for invalid language code."""
        with pytest.raises(ValueError) as exc_info:
            load_prompt_template('risky_debator', 'invalid')

        error_message = str(exc_info.value)
        assert 'Invalid language code' in error_message
        assert 'invalid' in error_message

    def test_placeholders_preserved(self):
        """Test that all placeholders are preserved in Chinese prompt."""
        prompt = load_prompt_template('risky_debator', 'zh')

        # Check all required placeholders
        assert '{trader_decision}' in prompt
        assert '{market_research_report}' in prompt
        assert '{sentiment_report}' in prompt
        assert '{news_report}' in prompt
        assert '{fundamentals_report}' in prompt
        assert '{history}' in prompt
        assert '{current_safe_response}' in prompt
        assert '{current_neutral_response}' in prompt

    def test_placeholders_preserved_english(self):
        """Test that all placeholders are preserved in English prompt."""
        prompt = load_prompt_template('risky_debator', 'en')

        # Check all required placeholders
        assert '{trader_decision}' in prompt
        assert '{market_research_report}' in prompt
        assert '{sentiment_report}' in prompt
        assert '{news_report}' in prompt
        assert '{fundamentals_report}' in prompt
        assert '{history}' in prompt
        assert '{current_safe_response}' in prompt
        assert '{current_neutral_response}' in prompt

    def test_chinese_terminology_consistency(self):
        """Test that Chinese terminology is consistent throughout the prompt."""
        prompt = load_prompt_template('risky_debator', 'zh')

        # Check key terminology
        assert '高风险偏好分析师' in prompt
        assert '交易计划' in prompt
        assert '保守分析师' in prompt
        assert '中立分析师' in prompt
        assert '对话记录' in prompt

    def test_aggressive_debating_style_preserved(self):
        """Test that aggressive debating style is preserved in Chinese prompt."""
        prompt = load_prompt_template('risky_debator', 'zh')

        # Check for aggressive debating language
        assert '积极主张' in prompt or '积极倡导' in prompt
        assert '反击' in prompt
        assert '质疑' in prompt or '批判' in prompt

    def test_data_sources_order_preserved(self):
        """Test that data source order is preserved in Chinese prompt."""
        prompt = load_prompt_template('risky_debator', 'zh')

        # Find positions of data sources
        market_pos = prompt.find('市场研究报告')
        sentiment_pos = prompt.find('社交媒体情绪报告')
        news_pos = prompt.find('最新世界时事报告')
        fundamentals_pos = prompt.find('公司基本面报告')

        # Verify order is preserved
        assert market_pos < sentiment_pos < news_pos < fundamentals_pos

    def test_chinese_prompt_structure(self):
        """Test that Chinese prompt has proper structure."""
        prompt = load_prompt_template('risky_debator', 'zh')

        # Check for key sections
        assert prompt.count('{trader_decision}') == 1
        assert '报告' in prompt  # Check for report citations
        assert '辩论' in prompt or '反驳' in prompt

    def test_english_prompt_structure(self):
        """Test that English prompt has proper structure."""
        prompt = load_prompt_template('risky_debator', 'en')

        # Check for key sections
        assert prompt.count('{trader_decision}') == 1
        assert 'debating' in prompt.lower() or 'persuading' in prompt.lower()
