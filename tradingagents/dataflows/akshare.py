"""
Akshare data vendor implementation for Chinese stock market data.

This module provides interfaces to Akshare library for retrieving:
- Stock price data (OHLCV)
- Technical indicators
- News data
- Fundamental data (balance sheet, cash flow, income statement)
"""

import logging
import akshare as ak
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================

class AkshareError(Exception):
    """Base exception for Akshare-related errors"""
    pass


class AkshareDataError(AkshareError):
    """Data retrieval or parsing error"""
    pass


class AkshareRateLimitError(AkshareError):
    """API rate limit exceeded (similar to AlphaVantageRateLimitError)"""
    pass


class AkshareCodeError(AkshareError):
    """Invalid stock code or code conversion error"""
    pass


# ============================================================================
# Stock Code Conversion
# ============================================================================

def convert_to_akshare_code(symbol: str) -> str:
    """
    Convert stock symbol to Akshare format.

    Rules:
    - 6xxxxx → shXXXXXX (Shanghai)
    - 0xxxxx, 3xxxxx → szXXXXXX (Shenzhen)
    - 8xxxxx, 4xxxxx → bjXXXXXX (Beijing)
    - Already has prefix → return as-is

    Args:
        symbol: Stock symbol (6-digit code or Akshare format with prefix)

    Returns:
        Akshare-formatted stock symbol

    Examples:
        >>> convert_to_akshare_code("600000")
        'sh600000'
        >>> convert_to_akshare_code("000001")
        'sz000001'
        >>> convert_to_akshare_code("sh600000")
        'sh600000'
    """
    if not symbol:
        raise AkshareCodeError("Stock symbol cannot be empty")

    # If already has prefix, return as-is
    if symbol[:2].lower() in ['sh', 'sz', 'bj', 'hk', 'us']:
        return symbol.lower()

    # Convert 6-digit codes
    if len(symbol) == 6 and symbol.isdigit():
        if symbol.startswith('6'):
            return f"sh{symbol}"
        elif symbol.startswith(('0', '3')):
            return f"sz{symbol}"
        elif symbol.startswith(('8', '4')):
            return f"bj{symbol}"

    # Return original if no conversion rules match
    return symbol


# ============================================================================
# Stock Price Data
# ============================================================================

def get_akshare_stock(
    symbol: str,
    period: str = "daily",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    adjust: str = "qfq"
) -> str:
    """
    Get historical stock price data from Akshare.

    Args:
        symbol: Stock symbol (6-digit code or Akshare format with prefix)
        period: Time period (daily, weekly, monthly)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        adjust: Adjustment type - "qfq" (前复权), "hfq" (后复权), "" (不复权)

    Returns:
        CSV-formatted string with OHLCV data

    Raises:
        AkshareCodeError: If stock code is invalid
        AkshareDataError: If data retrieval fails

    Example:
        >>> get_akshare_stock("000001", "daily", "2023-01-01", "2023-12-31")
        '# Stock data for sz000001 from 2023-01-01 to 2023-12-31...'
    """
    try:
        logger.info(f"Akshare: Fetching stock data for {symbol}, period={period}")

        # Convert symbol to Akshare format
        akshare_symbol = convert_to_akshare_code(symbol)
        logger.debug(f"Converted symbol: {symbol} -> {akshare_symbol}")

        # Convert date format from YYYY-MM-DD to YYYYMMDD for Akshare
        start_date_ak = start_date.replace("-", "") if start_date else "19900101"
        end_date_ak = end_date.replace("-", "") if end_date else datetime.now().strftime("%Y%m%d")

        # Fetch data from Akshare
        data = ak.stock_zh_a_hist(
            symbol=akshare_symbol,
            period=period,
            start_date=start_date_ak,
            end_date=end_date_ak,
            adjust=adjust
        )

        if data is None or data.empty:
            return f"No data found for symbol '{symbol}' between {start_date} and {end_date}"

        # Rename columns to match standard format (English)
        column_mapping = {
            '日期': 'Date',
            '开盘': 'Open',
            '收盘': 'Close',
            '最高': 'High',
            '最低': 'Low',
            '成交量': 'Volume',
            '成交额': 'Amount',
            '振幅': 'Amplitude',
            '涨跌幅': 'ChangePct',
            '涨跌额': 'ChangeAmount',
            '换手率': 'Turnover'
        }
        data.rename(columns=column_mapping, inplace=True)

        # Round numerical values
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            if col in data.columns:
                data[col] = data[col].round(2)

        # Convert to CSV string
        csv_string = data.to_csv()

        # Add header information
        header = f"# Stock data for {akshare_symbol.upper()} from {start_date} to {end_date}\n"
        header += f"# Total records: {len(data)}\n"
        header += f"# Adjustment: {adjust}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        logger.info(f"Akshare: Retrieved {len(data)} records for {symbol}")
        return header + csv_string

    except AkshareCodeError:
        raise
    except Exception as e:
        logger.error(f"Akshare stock data failed for {symbol}: {e}")
        raise AkshareDataError(f"Failed to retrieve stock data: {e}")


# ============================================================================
# Technical Indicators
# ============================================================================

def get_akshare_indicators(
    symbol: str,
    period: str = "daily",
    indicator_names: str = "macd,rsi"
) -> str:
    """
    Get technical indicators using hybrid approach.

    Strategy: Try Akshare's built-in indicators first, fallback to stockstats calculation.

    Args:
        symbol: Stock symbol
        period: Time period
        indicator_names: Comma-separated list of indicator names

    Returns:
        Text summary of technical indicators

    Raises:
        AkshareDataError: If indicator calculation fails
    """
    try:
        logger.info(f"Akshare: Fetching indicators for {symbol}: {indicator_names}")

        akshare_symbol = convert_to_akshare_code(symbol)

        # Try to get stock data with spot data (includes some indicators)
        # Note: This is a placeholder. Full implementation would use stockstats
        # for comprehensive indicator calculation.

        # For now, return a message indicating indicators would be calculated
        return (
            f"# Technical Indicators for {akshare_symbol}\n"
            f"# Requested indicators: {indicator_names}\n"
            f"# Note: Full indicator calculation implementation pending\n"
            f"# This will use stockstats library for calculation\n"
        )

    except Exception as e:
        logger.error(f"Akshare indicators failed for {symbol}: {e}")
        raise AkshareDataError(f"Failed to retrieve indicators: {e}")


# ============================================================================
# News Data
# ============================================================================

def get_akshare_news(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """
    Get news data from multiple Chinese sources.

    Aggregates news from:
    - East Money (东方财富) - Primary
    - Sina Finance (新浪财经) - Secondary
    - Xueqiu (雪球) - Tertiary

    Args:
        symbol: Stock symbol
        start_date: Start date
        end_date: End date

    Returns:
        Aggregated news from all sources

    Raises:
        AkshareDataError: If all news sources fail
    """
    try:
        logger.info(f"Akshare: Fetching news for {symbol}")

        akshare_symbol = convert_to_akshare_code(symbol)
        all_news = []

        # Try East Money news (primary)
        try:
            eastmoney_news = ak.stock_news_em(symbol=akshare_symbol)
            if eastmoney_news is not None and not eastmoney_news.empty:
                all_news.append("# East Money News (东方财富)")
                all_news.append(eastmoney_news.to_csv())
                logger.debug(f"Retrieved {len(eastmoney_news)} news items from East Money")
        except Exception as e:
            logger.warning(f"East Money news failed: {e}")

        # Try Sina Finance news (secondary)
        try:
            sina_news = ak.stock_news_sina(symbol=akshare_symbol)
            if sina_news is not None and not sina_news.empty:
                all_news.append("\n# Sina Finance News (新浪财经)")
                all_news.append(sina_news.to_csv())
                logger.debug(f"Retrieved {len(sina_news)} news items from Sina Finance")
        except Exception as e:
            logger.warning(f"Sina Finance news failed: {e}")

        if not all_news:
            return f"No news found for symbol '{symbol}'"

        result = "\n".join(all_news)
        logger.info(f"Akshare: Retrieved news from {len([n for n in all_news if n.startswith('# ')])} source(s)")
        return result

    except Exception as e:
        logger.error(f"Akshare news failed for {symbol}: {e}")
        raise AkshareDataError(f"Failed to retrieve news: {e}")


def get_akshare_global_news(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """
    Get global market news.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Global market news summary

    Raises:
        AkshareDataError: If retrieval fails
    """
    try:
        logger.info("Akshare: Fetching global market news")

        # Get global market news from East Money
        try:
            news_data = ak.stock_global_news_em()
        except Exception:
            # Fallback: return message if function not available
            return "# Global Market News\n\nGlobal news feature is currently limited. Please use get_akshare_news for individual stock news."

        if news_data is None or news_data.empty:
            return "No global market news found"

        result = f"# Global Market News\n{news_data.to_csv()}"
        logger.info(f"Akshare: Retrieved {len(news_data)} global news items")
        return result

    except Exception as e:
        logger.error(f"Akshare global news failed: {e}")
        raise AkshareDataError(f"Failed to retrieve global news: {e}")


# ============================================================================
# Fundamental Data
# ============================================================================

def get_akshare_fundamentals(
    symbol: str,
    curr_date: Optional[str] = None
) -> str:
    """
    Get comprehensive fundamental analysis for a Chinese stock.

    Args:
        symbol: Stock symbol (6-digit or Akshare format)
        curr_date: Current date for reference

    Returns:
        Text summary including company overview, key ratios, and highlights

    Raises:
        AkshareCodeError: If stock code is invalid
        AkshareDataError: If data retrieval fails
    """
    try:
        logger.info(f"Akshare: Fetching fundamentals for {symbol}")

        akshare_symbol = convert_to_akshare_code(symbol)

        # Get company info
        company_info = ak.stock_individual_info_em(symbol=akshare_symbol)

        # Get financial indicators
        indicators = ak.stock_financial_analysis_indicator(symbol=akshare_symbol)

        # Build summary
        summary_parts = [
            f"# Fundamental Analysis for {akshare_symbol.upper()}",
            f"# Analysis Date: {curr_date or datetime.now().strftime('%Y-%m-%d')}",
            ""
        ]

        if company_info is not None and not company_info.empty:
            summary_parts.append("## Company Information")
            summary_parts.append(company_info.to_csv())
            summary_parts.append("")

        if indicators is not None and not indicators.empty:
            summary_parts.append("## Financial Indicators")
            summary_parts.append(indicators.head(10).to_csv())  # Show most recent data
            summary_parts.append("")

        result = "\n".join(summary_parts)
        logger.info(f"Akshare: Retrieved fundamentals for {symbol}")
        return result

    except AkshareCodeError:
        raise
    except Exception as e:
        logger.error(f"Akshare fundamentals failed for {symbol}: {e}")
        raise AkshareDataError(f"Failed to retrieve fundamentals: {e}")


def get_akshare_balance_sheet(
    symbol: str,
    freq: str = "quarterly",
    curr_date: Optional[str] = None
) -> str:
    """
    Get balance sheet data from Akshare.

    Args:
        symbol: Stock symbol
        freq: Reporting frequency - "annual" or "quarterly" (default)
        curr_date: Current date for reference

    Returns:
        Balance sheet data as text

    Raises:
        AkshareDataError: If retrieval fails
    """
    try:
        logger.info(f"Akshare: Fetching balance sheet for {symbol}, freq={freq}")

        akshare_symbol = convert_to_akshare_code(symbol)

        # Fetch balance sheet data
        if freq == "annual":
            data = ak.stock_balance_sheet_by_yearly_em(symbol=akshare_symbol)
        else:  # quarterly (default)
            data = ak.stock_balance_sheet_by_quarterly_em(symbol=akshare_symbol)

        if data is None or data.empty:
            return f"No balance sheet data found for {symbol}"

        result = f"# Balance Sheet for {akshare_symbol.upper()} ({freq})\n{data.to_csv()}"
        logger.info(f"Akshare: Retrieved balance sheet for {symbol}")
        return result

    except Exception as e:
        logger.error(f"Akshare balance sheet failed for {symbol}: {e}")
        raise AkshareDataError(f"Failed to retrieve balance sheet: {e}")


def get_akshare_cashflow(
    symbol: str,
    freq: str = "quarterly",
    curr_date: Optional[str] = None
) -> str:
    """
    Get cash flow statement data from Akshare.

    Args:
        symbol: Stock symbol
        freq: Reporting frequency - "annual" or "quarterly" (default)
        curr_date: Current date for reference

    Returns:
        Cash flow statement data as text

    Raises:
        AkshareDataError: If retrieval fails
    """
    try:
        logger.info(f"Akshare: Fetching cash flow statement for {symbol}, freq={freq}")

        akshare_symbol = convert_to_akshare_code(symbol)

        # Fetch cash flow data
        if freq == "annual":
            data = ak.stock_cash_flow_sheet_by_yearly_em(symbol=akshare_symbol)
        else:  # quarterly (default)
            data = ak.stock_cash_flow_sheet_by_quarterly_em(symbol=akshare_symbol)

        if data is None or data.empty:
            return f"No cash flow statement data found for {symbol}"

        result = f"# Cash Flow Statement for {akshare_symbol.upper()} ({freq})\n{data.to_csv()}"
        logger.info(f"Akshare: Retrieved cash flow statement for {symbol}")
        return result

    except Exception as e:
        logger.error(f"Akshare cash flow statement failed for {symbol}: {e}")
        raise AkshareDataError(f"Failed to retrieve cash flow statement: {e}")


def get_akshare_income_statement(
    symbol: str,
    freq: str = "quarterly",
    curr_date: Optional[str] = None
) -> str:
    """
    Get income statement data from Akshare.

    Args:
        symbol: Stock symbol
        freq: Reporting frequency - "annual" or "quarterly" (default)
        curr_date: Current date for reference

    Returns:
        Income statement data as text

    Raises:
        AkshareDataError: If retrieval fails
    """
    try:
        logger.info(f"Akshare: Fetching income statement for {symbol}, freq={freq}")

        akshare_symbol = convert_to_akshare_code(symbol)

        # Fetch income statement data
        if freq == "annual":
            data = ak.stock_profit_sheet_by_yearly_em(symbol=akshare_symbol)
        else:  # quarterly (default)
            data = ak.stock_profit_sheet_by_quarterly_em(symbol=akshare_symbol)

        if data is None or data.empty:
            return f"No income statement data found for {symbol}"

        result = f"# Income Statement for {akshare_symbol.upper()} ({freq})\n{data.to_csv()}"
        logger.info(f"Akshare: Retrieved income statement for {symbol}")
        return result

    except Exception as e:
        logger.error(f"Akshare income statement failed for {symbol}: {e}")
        raise AkshareDataError(f"Failed to retrieve income statement: {e}")
