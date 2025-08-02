"""
Captain Arro - Animated SVG Arrow Generators

A Python library for generating animated SVG arrows for web interfaces.
Provides flow and spread arrow generators with various animation styles.
"""

from .generators.flow.moving_flow_arrow_generator import MovingFlowArrowGenerator
from .generators.flow.spotlight_flow_arrow_generator import SpotlightFlowArrowGenerator
from .generators.spread.bouncing_spread_arrow_generator import BouncingSpreadArrowGenerator
from .generators.spread.spotlight_spread_arrow_generator import SpotlightSpreadArrowGenerator
from .generators.base import AnimatedArrowGeneratorBase
from .constants import ANIMATION_TYPES, FLOW_DIRECTIONS, SPREAD_DIRECTIONS

__version__ = "0.1.0"
__author__ = "Helge Esch"

__all__ = [
    "MovingFlowArrowGenerator",
    "SpotlightFlowArrowGenerator", 
    "BouncingSpreadArrowGenerator",
    "SpotlightSpreadArrowGenerator",
    "AnimatedArrowGeneratorBase",
    "ANIMATION_TYPES",
    "FLOW_DIRECTIONS", 
    "SPREAD_DIRECTIONS",
]