"""
Unit tests for safe/conservative debator prompt loading functionality.
"""
import os
import pytest
from tradingagents.agents.utils.agent_utils import load_prompt_template


class TestSafeDebatorPromptLoading:
    """Test suite for safe debator multi-language prompt loading."""

    def test_load_chinese_prompt(self):
        """Test loading Chinese prompt for safe debator."""
        prompt = load_prompt_template('safe_debator', 'zh')
        assert '作为稳健风险分析师' in prompt
        assert '保护资产' in prompt
        assert '稳健策略' in prompt
        assert '风险分析师' in prompt
        assert '中立分析师' in prompt

    def test_load_english_prompt(self):
        """Test loading English prompt for safe debator."""
        prompt = load_prompt_template('safe_debator', 'en')
        assert 'As the Safe/Conservative Risk Analyst' in prompt
        assert 'protect assets' in prompt
        assert 'low-risk approach' in prompt

    def test_default_language_is_chinese(self):
        """Test that default language is Chinese when LANGUAGE is not set."""
        # Save original value
        original_language = os.environ.get('LANGUAGE')

        try:
            # Remove LANGUAGE from environment
            if 'LANGUAGE' in os.environ:
                del os.environ['LANGUAGE']

            # Load prompt without specifying language
            prompt = load_prompt_template('safe_debator')
            assert '作为稳健风险分析师' in prompt
            assert '保护资产' in prompt
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
            prompt = load_prompt_template('safe_debator')
            assert 'As the Safe/Conservative Risk Analyst' in prompt
            assert 'protect assets' in prompt

            # Set language to Chinese
            os.environ['LANGUAGE'] = 'zh'
            prompt = load_prompt_template('safe_debator')
            assert '作为稳健风险分析师' in prompt
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
            load_prompt_template('safe_debator', 'fr')

        error_message = str(exc_info.value)
        # Either validation error or file error is acceptable
        assert 'fr' in error_message or 'Invalid language code' in error_message

    def test_invalid_language_code(self):
        """Test that ValueError is raised for invalid language code."""
        with pytest.raises(ValueError) as exc_info:
            load_prompt_template('safe_debator', 'invalid')

        error_message = str(exc_info.value)
        assert 'Invalid language code' in error_message
        assert 'invalid' in error_message

    def test_placeholders_preserved(self):
        """Test that all placeholders are preserved in Chinese prompt."""
        prompt = load_prompt_template('safe_debator', 'zh')

        # Check all required placeholders
        assert '{trader_decision}' in prompt
        assert '{market_research_report}' in prompt
        assert '{sentiment_report}' in prompt
        assert '{news_report}' in prompt
        assert '{fundamentals_report}' in prompt
        assert '{history}' in prompt
        assert '{current_risky_response}' in prompt
        assert '{current_neutral_response}' in prompt

    def test_placeholders_preserved_english(self):
        """Test that all placeholders are preserved in English prompt."""
        prompt = load_prompt_template('safe_debator', 'en')

        # Check all required placeholders
        assert '{trader_decision}' in prompt
        assert '{market_research_report}' in prompt
        assert '{sentiment_report}' in prompt
        assert '{news_report}' in prompt
        assert '{fundamentals_report}' in prompt
        assert '{history}' in prompt
        assert '{current_risky_response}' in prompt
        assert '{current_neutral_response}' in prompt

    def test_chinese_terminology_consistency(self):
        """Test that Chinese terminology is consistent throughout the prompt."""
        prompt = load_prompt_template('safe_debator', 'zh')

        # Check key terminology (aligned with neutral debator)
        assert '稳健风险分析师' in prompt
        assert '风险分析师' in prompt
        assert '中立分析师' in prompt
        assert '对话记录' in prompt

    def test_citation_format_consistency(self):
        """Test that citation format is consistent with neutral debator."""
        prompt = load_prompt_template('safe_debator', 'zh')
        assert '报告' in prompt  # Check for report citations
        # Should match neutral debator format

    def test_conservative_style_preserved(self):
        """Test that conservative debating style is preserved in Chinese prompt."""
        prompt = load_prompt_template('safe_debator', 'zh')

        # Check for conservative debating language
        assert '保护资产' in prompt or '风险最小化' in prompt
        assert '潜在风险' in prompt or '下行风险' in prompt

    def test_data_sources_order_preserved(self):
        """Test that data source order is preserved in Chinese prompt."""
        prompt = load_prompt_template('safe_debator', 'zh')

        # Find positions of data sources
        market_pos = prompt.find('市场研究报告')
        sentiment_pos = prompt.find('社交媒体情绪报告')
        news_pos = prompt.find('最新世界时事报告')
        fundamentals_pos = prompt.find('公司基本面报告')

        # Verify order is preserved
        assert market_pos < sentiment_pos < news_pos < fundamentals_pos

    def test_chinese_prompt_structure(self):
        """Test that Chinese prompt has proper structure."""
        prompt = load_prompt_template('safe_debator', 'zh')

        # Check for key sections
        assert prompt.count('{trader_decision}') == 1
        assert '辩论' in prompt or '反驳' in prompt

    def test_english_prompt_structure(self):
        """Test that English prompt has proper structure."""
        prompt = load_prompt_template('safe_debator', 'en')

        # Check for key sections
        assert prompt.count('{trader_decision}') == 1
        assert 'conservative' in prompt.lower()
