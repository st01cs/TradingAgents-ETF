from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai" 
config["backend_url"] = "https://api.siliconflow.cn/v1"
config["deep_think_llm"] = "deepseek-ai/DeepSeek-V3.2"  # Use a different model
config["quick_think_llm"] = "deepseek-ai/DeepSeek-V3.2"  # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds

# Configure data vendors (default uses yfinance and alpha_vantage)
config["data_vendors"] = {
    "core_stock_apis": "akshare",           # Options: yfinance, alpha_vantage, local
    "technical_indicators": "akshare",      # Options: yfinance, alpha_vantage, local
    "fundamental_data": "akshare",     # Options: openai, alpha_vantage, local
    "news_data": "akshare",            # Options: openai, alpha_vantage, google, local
}

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config, selected_analysts=["market", "news",])

# forward propagate
_, decision = ta.propagate("601939", "2025-05-10")
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
