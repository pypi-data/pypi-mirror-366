"""
Tests for constants module.
"""

from typing import get_args
from captain_arro.constants import ANIMATION_TYPES, FLOW_DIRECTIONS, SPREAD_DIRECTIONS


class TestConstants:
    """Test cases for constants."""

    def test_animation_types(self):
        """Test ANIMATION_TYPES literal values."""
        expected_animations = {"linear", "ease", "ease-in", "ease-out", "ease-in-out"}
        actual_animations = set(get_args(ANIMATION_TYPES))
        
        assert actual_animations == expected_animations

    def test_flow_directions(self):
        """Test FLOW_DIRECTIONS literal values."""
        expected_directions = {"right", "left", "up", "down"}
        actual_directions = set(get_args(FLOW_DIRECTIONS))
        
        assert actual_directions == expected_directions

    def test_spread_directions(self):
        """Test SPREAD_DIRECTIONS literal values."""
        expected_directions = {"horizontal", "vertical"}
        actual_directions = set(get_args(SPREAD_DIRECTIONS))
        
        assert actual_directions == expected_directions

    def test_constants_are_literals(self):
        """Test that constants are proper Literal types."""
        # This test ensures the constants can be used for type checking
        from typing import Literal
        
        # These should not raise any type errors
        animation: ANIMATION_TYPES = "linear"
        flow_dir: FLOW_DIRECTIONS = "up"
        spread_dir: SPREAD_DIRECTIONS = "horizontal"
        
        assert animation == "linear"
        assert flow_dir == "up"
        assert spread_dir == "horizontal"