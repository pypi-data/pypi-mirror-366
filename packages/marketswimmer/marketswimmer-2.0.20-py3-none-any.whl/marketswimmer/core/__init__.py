"""
Core analysis modules for MarketSwimmer.

This module contains the core financial analysis functionality including
the OwnerEarningsCalculator class that implements Warren Buffett's 
Owner Earnings methodology.
"""

from .owner_earnings import OwnerEarningsCalculator

__all__ = ["OwnerEarningsCalculator"]
