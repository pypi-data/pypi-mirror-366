"""
Spread arrow generators.

Generates arrows that spread from center (horizontal or vertical).
"""

from .bouncing_spread_arrow_generator import BouncingSpreadArrowGenerator
from .spotlight_spread_arrow_generator import SpotlightSpreadArrowGenerator

__all__ = [
    "BouncingSpreadArrowGenerator",
    "SpotlightSpreadArrowGenerator",
]