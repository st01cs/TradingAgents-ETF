"""
Technical indicator calculation module for Chinese stock market.

This module provides indicator calculation functionality using the stockstats library
as a fallback when akshare built-in indicators are not available.
"""

from .calculator import IndicatorCalculator

__all__ = ['IndicatorCalculator']
