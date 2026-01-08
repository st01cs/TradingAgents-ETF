import functools
import time
import json
from tradingagents.agents.utils.agent_utils import load_prompt_template


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        # Load prompt from external file (supports multi-language)
        # Note: Uses existing load_prompt_template() infrastructure
        prompt_template = load_prompt_template('trader')

        # Substitute variables
        prompt = prompt_template.format(
            investment_plan=investment_plan,
            past_memory_str=past_memory_str
        )

        result = llm.invoke(prompt)

        # Chinese output prefix (trader role)
        trading_decision = f"交易员：{result.content}"

        return {
            "messages": [result],
            "trader_investment_plan": trading_decision,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
