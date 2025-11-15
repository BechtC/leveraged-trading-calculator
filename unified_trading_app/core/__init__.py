"""
Core Business Logic

Exports:
- UnifiedPositionCalculator
- TradeManager
- Trade
- CalculationResult
"""

from .calculator import UnifiedPositionCalculator, CalculationResult
from .trade_manager import TradeManager, Trade

__all__ = [
    'UnifiedPositionCalculator',
    'CalculationResult',
    'TradeManager',
    'Trade'
]
