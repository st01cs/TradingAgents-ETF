"""Unit tests for risk_manager multi-language prompt loading."""

import os
import pytest
from tradingagents.agents.utils.agent_utils import load_prompt_template


class TestRiskManagerPromptLoading:
    """Test suite for risk_manager prompt loading functionality."""

    def test_load_chinese_prompt(self):
        """Verify Chinese prompt loads correctly."""
        # Ensure default language is Chinese
        if 'LANGUAGE' in os.environ:
            del os.environ['LANGUAGE']

        prompt = load_prompt_template('risk_manager')

        # Verify key Chinese phrases are present
        assert '裁判与协调员' in prompt, "Should contain '裁判与协调员' (Judge and Coordinator)"
        assert '总结关键论点' in prompt, "Should contain '总结关键论点' (Summarize Key Arguments)"
        assert '提供决策依据' in prompt, "Should contain '提供决策依据' (Provide Rationale)"
        assert '优化交易计划' in prompt, "Should contain '优化交易计划' (Refine Plan)"
        assert '从历史记录学习' in prompt, "Should contain '从历史记录学习' (Learn from History)"

    def test_load_english_prompt(self):
        """Verify English prompt loads correctly."""
        os.environ['LANGUAGE'] = 'en'
        prompt = load_prompt_template('risk_manager')

        # Verify key English phrases are present
        assert 'Judge and Debate Facilitator' in prompt, "Should contain 'Judge and Debate Facilitator'"
        assert 'Summarize Key Arguments' in prompt, "Should contain 'Summarize Key Arguments'"
        assert 'Provide Rationale' in prompt, "Should contain 'Provide Rationale'"
        assert "Refine the Trader's Plan" in prompt, "Should contain \"Refine the Trader's Plan\""
        assert 'Learn from Past Mistakes' in prompt, "Should contain 'Learn from Past Mistakes'"

    def test_default_language_is_chinese(self):
        """Confirm default language is Chinese when LANGUAGE not set."""
        if 'LANGUAGE' in os.environ:
            del os.environ['LANGUAGE']

        prompt = load_prompt_template('risk_manager')
        assert '裁判与协调员' in prompt, "Default should be Chinese"

    def test_language_from_env_variable(self):
        """Test LANGUAGE environment variable controls prompt language."""
        # Test Chinese
        os.environ['LANGUAGE'] = 'zh'
        prompt_zh = load_prompt_template('risk_manager')
        assert '裁判与协调员' in prompt_zh, "LANGUAGE=zh should load Chinese"

        # Test English
        os.environ['LANGUAGE'] = 'en'
        prompt_en = load_prompt_template('risk_manager')
        assert 'Judge and Debate Facilitator' in prompt_en, "LANGUAGE=en should load English"

    def test_prompt_file_not_found(self):
        """Validate error handling for missing prompt files."""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_prompt_template('nonexistent_agent')
        assert 'Prompt file not found' in str(exc_info.value)

    def test_invalid_language_code(self):
        """Test validation of invalid language codes."""
        os.environ['LANGUAGE'] = 'invalid'
        with pytest.raises(ValueError) as exc_info:
            load_prompt_template('risk_manager')
        assert 'Invalid language code' in str(exc_info.value)

    def test_placeholders_preserved(self):
        """Ensure all placeholders preserved in Chinese prompt."""
        if 'LANGUAGE' in os.environ:
            del os.environ['LANGUAGE']

        prompt = load_prompt_template('risk_manager')

        # Test all three placeholders
        assert '{trader_plan}' in prompt, "Should preserve {trader_plan} placeholder"
        assert '{past_memory_str}' in prompt, "Should preserve {past_memory_str} placeholder"
        assert '{history}' in prompt, "Should preserve {history} placeholder"

    def test_placeholders_preserved_english(self):
        """Ensure all placeholders preserved in English prompt."""
        os.environ['LANGUAGE'] = 'en'
        prompt = load_prompt_template('risk_manager')

        # Test all three placeholders
        assert '{trader_plan}' in prompt, "Should preserve {trader_plan} placeholder"
        assert '{past_memory_str}' in prompt, "Should preserve {past_memory_str} placeholder"
        assert '{history}' in prompt, "Should preserve {history} placeholder"

    def test_four_guidelines_sections_present(self):
        """Verify all 4 guideline sections present in Chinese."""
        if 'LANGUAGE' in os.environ:
            del os.environ['LANGUAGE']

        prompt = load_prompt_template('risk_manager')

        # Verify all 4 sections
        assert '总结关键论点' in prompt, "Should have section 1: 总结关键论点"
        assert '提供决策依据' in prompt, "Should have section 2: 提供决策依据"
        assert '优化交易计划' in prompt, "Should have section 3: 优化交易计划"
        assert '从历史记录学习' in prompt, "Should have section 4: 从历史记录学习"

    def test_four_guidelines_sections_present_english(self):
        """Verify all 4 guideline sections present in English."""
        os.environ['LANGUAGE'] = 'en'
        prompt = load_prompt_template('risk_manager')

        # Verify all 4 sections
        assert 'Summarize Key Arguments' in prompt, "Should have section 1: Summarize Key Arguments"
        assert 'Provide Rationale' in prompt, "Should have section 2: Provide Rationale"
        assert "Refine the Trader's Plan" in prompt, "Should have section 3: Refine the Trader's Plan"
        assert 'Learn from Past Mistakes' in prompt, "Should have section 4: Learn from Past Mistakes"

    def test_terminology_consistency(self):
        """Validate Chinese terminology matches debators."""
        if 'LANGUAGE' in os.environ:
            del os.environ['LANGUAGE']

        prompt = load_prompt_template('risk_manager')

        # Verify three analyst names match debator terminology
        assert '风险分析师' in prompt, "Should use '风险分析师' (Risky Analyst)"
        assert '中立分析师' in prompt, "Should use '中立分析师' (Neutral Analyst)"
        assert '稳健分析师' in prompt, "Should use '稳健分析师' (Conservative Analyst)"

    def test_decision_terms_present(self):
        """Verify decision terms in Chinese."""
        if 'LANGUAGE' in os.environ:
            del os.environ['LANGUAGE']

        prompt = load_prompt_template('risk_manager')

        # Verify Buy/Sell/Hold terms
        assert '买入' in prompt, "Should contain '买入' (Buy)"
        assert '卖出' in prompt, "Should contain '卖出' (Sell)"
        assert '持有' in prompt, "Should contain '持有' (Hold)"

    def test_citation_format_consistency(self):
        """Verify citation format matches debator implementations."""
        if 'LANGUAGE' in os.environ:
            del os.environ['LANGUAGE']

        prompt = load_prompt_template('risk_manager')

        # Check for citation format in instructions
        assert '引用' in prompt or '根据' in prompt, "Should include citation format"

    def test_judge_role_description(self):
        """Tests role description is accurate."""
        if 'LANGUAGE' in os.environ:
            del os.environ['LANGUAGE']

        prompt = load_prompt_template('risk_manager')

        # Verify role description
        assert '裁判与协调员' in prompt, "Should describe role as '裁判与协调员'"
        assert '评估' in prompt, "Should mention '评估' (evaluate)"
        assert '辩论' in prompt, "Should mention '辩论' (debate)"

    def test_decisive_style_preserved(self):
        """Tests decisive tone is maintained."""
        if 'LANGUAGE' in os.environ:
            del os.environ['LANGUAGE']

        prompt = load_prompt_template('risk_manager')

        # Verify decisive style
        assert '明确果断' in prompt, "Should emphasize '明确果断' (clear and decisive)"
        assert '力求' in prompt, "Should contain '力求' (strive for)"

    def test_deliverables_section_present(self):
        """Tests deliverables section present."""
        if 'LANGUAGE' in os.environ:
            del os.environ['LANGUAGE']

        prompt = load_prompt_template('risk_manager')

        # Verify deliverables section
        assert '交付成果' in prompt, "Should have '交付成果' (Deliverables) section"
        assert '买入、卖出或持有' in prompt, "Should specify the three decisions"

    def test_memory_reference_present(self):
        """Tests memory system reference in Chinese."""
        if 'LANGUAGE' in os.environ:
            del os.environ['LANGUAGE']

        prompt = load_prompt_template('risk_manager')

        # Verify memory reference
        assert '历史记录' in prompt, "Should reference '历史记录' (historical records)"
        assert '误判' in prompt or '教训' in prompt, "Should mention learning from mistakes"
