from pathlib import Path
import os
from langchain_core.messages import HumanMessage, RemoveMessage

# Import tools from separate utility files
from tradingagents.agents.utils.core_stock_tools import (
    get_stock_data
)
from tradingagents.agents.utils.technical_indicators_tools import (
    get_indicators
)
from tradingagents.agents.utils.fundamental_data_tools import (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement
)
from tradingagents.agents.utils.news_data_tools import (
    get_news,
    get_insider_sentiment,
    get_insider_transactions,
    get_global_news
)

def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]

        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]

        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")

        return {"messages": removal_operations + [placeholder]}

    return delete_messages


def load_prompt_template(agent_name: str, language: str = None) -> str:
    """
    Load prompt template from external markdown file.

    Args:
        agent_name: Name of the agent (e.g., 'market_analyst')
        language: Language code ('zh' or 'en'). If None, reads from LANGUAGE
                  environment variable with default 'zh'.

    Returns:
        Prompt content as string

    Raises:
        FileNotFoundError: With detailed error message including configuration guidance
        ValueError: If language code is invalid

    Example:
        >>> prompt = load_prompt_template('market_analyst', 'zh')
        >>> prompt_en = load_prompt_template('market_analyst', 'en')
    """
    # Determine language
    if language is None:
        language = os.environ.get('LANGUAGE', 'zh')

    # Validate language
    valid_languages = ['zh', 'en']
    if language not in valid_languages:
        raise ValueError(
            f"Invalid language code: '{language}'. "
            f"Valid options: {', '.join(valid_languages)}"
        )

    # Build file path (relative to this file)
    # Navigate from agents/utils/ up to project root, then to prompts/
    base_path = Path(__file__).parent.parent.parent.parent / 'prompts'
    file_path = base_path / language / f'{agent_name}.md'

    # Load prompt
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Prompt file not found: {file_path}\n"
            f"Agent: {agent_name}\n"
            f"Language: {language}\n"
            f"\n"
            f"Please ensure the prompt file exists.\n"
            f"Available languages: {', '.join(valid_languages)}\n"
            f"Set LANGUAGE environment variable: export LANGUAGE=zh"
        )
