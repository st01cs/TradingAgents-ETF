from tradingagents.agents.utils.agent_utils import load_prompt_template


def create_risk_manager(llm, memory):
    """Create risk manager node with multi-language prompt support.

    The risk manager acts as a judge and debate facilitator, evaluating
    arguments from three risk analysts (Risky/Neutral/Safe) and making
    final Buy/Sell/Hold decisions. Supports Chinese and English prompts
    via external template files.

    Args:
        llm: Language model instance for invoking the risk manager
        memory: Memory system for learning from past decisions

    Returns:
        risk_manager_node: Function that processes risk debate state
            and returns final trading decision with rationale
    """
    def risk_manager_node(state) -> dict:
        # Extract state variables
        company_name = state["company_of_interest"]
        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["news_report"]
        sentiment_report = state["sentiment_report"]
        trader_plan = state["investment_plan"]

        # Compile current situation for memory retrieval
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        # Format past memories for prompt
        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # Load prompt from external file (supports multi-language)
        prompt_template = load_prompt_template('risk_manager')

        # Format prompt with variables
        prompt = prompt_template.format(
            trader_plan=trader_plan,
            past_memory_str=past_memory_str,
            history=history
        )

        # Invoke LLM with formatted prompt
        response = llm.invoke(prompt)

        # Preserve all debate state and add judge decision
        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return risk_manager_node
