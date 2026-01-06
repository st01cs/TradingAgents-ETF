"""
Technical indicator calculator for Chinese stock market.

Uses stockstats library for local calculation when akshare built-in
indicators are not available.
"""

import pandas as pd
from stockstats import StockDataFrame
from typing import List
import logging

logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """Calculate technical indicators from OHLCV data."""

    # Indicator name mappings (market_analyst names → stockstats names)
    INDICATOR_MAP = {
        # Moving Averages
        'close_50_sma': 'close_50_sma',
        'close_200_sma': 'close_200_sma',
        'close_10_ema': 'close_10_ema',

        # MACD
        'macd': 'macd',
        'macds': 'macds',
        'macdh': 'macdh',

        # Momentum
        'rsi': 'rsi_14',  # Default 14-period RSI

        # Bollinger Bands
        'boll': 'boll',
        'boll_ub': 'boll_ub',
        'boll_lb': 'boll_lb',

        # Volatility
        'atr': 'atr_14',  # Default 14-period ATR

        # Volume
        'vwma': 'vwma_20'  # Default 20-period VWMA
    }

    @staticmethod
    def parse_indicator_list(indicator_str: str) -> List[str]:
        """
        Parse comma-separated indicator string into list.

        Handles:
        - Single indicator: "rsi"
        - Multiple indicators: "rsi,macd,atr"
        - Spacing: "rsi, macd , atr"

        Args:
            indicator_str: Comma-separated indicator names

        Returns:
            List of normalized indicator names
        """
        if not indicator_str:
            return []

        # Split by comma, strip whitespace, filter empty
        indicators = [ind.strip() for ind in indicator_str.split(',')]
        return [ind for ind in indicators if ind]

    @staticmethod
    def calculate(
        df: pd.DataFrame,
        indicators: List[str]
    ) -> pd.DataFrame:
        """
        Calculate technical indicators using stockstats.

        Args:
            df: DataFrame with OHLCV data (columns: Date, Open, High, Low, Close, Volume)
            indicators: List of indicator names to calculate

        Returns:
            DataFrame with calculated indicators added as columns

        Raises:
            ValueError: If required columns missing from DataFrame
        """
        # Validate required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Stockstats requires lowercase column names
        df_renamed = df.copy()
        column_mapping = {
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }
        df_renamed.rename(columns=column_mapping, inplace=True)

        # Convert to StockDataFrame
        stock = StockDataFrame(df_renamed)

        # Calculate each indicator
        calculated_indicators = {}
        for indicator in indicators:
            try:
                # Map indicator name to stockstats format
                stockstats_name = IndicatorCalculator.INDICATOR_MAP.get(indicator)

                if not stockstats_name:
                    logger.warning(f"Indicator '{indicator}' not in mapping, skipping")
                    continue

                # Calculate indicator using stockstats
                indicator_value = stock[stockstats_name]

                # Store the last (most recent) value
                if not indicator_value.empty:
                    calculated_indicators[indicator] = indicator_value.iloc[-1]
                    logger.debug(f"Calculated {indicator}: {indicator_value.iloc[-1]}")

            except Exception as e:
                logger.error(f"Failed to calculate {indicator}: {e}")
                continue

        # Create summary DataFrame
        summary_df = pd.DataFrame([calculated_indicators])

        return summary_df

    @staticmethod
    def format_as_text(
        symbol: str,
        summary_df: pd.DataFrame,
        curr_date: str,
        look_back_days: int
    ) -> str:
        """
        Format indicator summary as text with CSV data.

        Args:
            symbol: Stock symbol
            summary_df: DataFrame with calculated indicators
            curr_date: Current date
            look_back_days: Lookback period

        Returns:
            Formatted text with CSV data
        """
        lines = [
            f"# Technical Indicators for {symbol}",
            f"# Date: {curr_date}",
            f"# Lookback Period: {look_back_days} days",
            f"# Total Indicators: {len(summary_df.columns)}",
            ""
        ]

        # Add CSV data
        csv_data = summary_df.to_csv(index=False)
        lines.append(csv_data)

        return "\n".join(lines)
