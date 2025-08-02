"""
Tests for MovingFlowArrowGenerator.
"""

import pytest
from captain_arro.generators.flow.moving_flow_arrow_generator import MovingFlowArrowGenerator


class TestMovingFlowArrowGenerator:
    """Test cases for MovingFlowArrowGenerator."""

    def test_init_default_values(self):
        """Test generator initialization with default values."""
        generator = MovingFlowArrowGenerator()
        
        assert generator.color == "#2563eb"
        assert generator.stroke_width == 15
        assert generator.width == 100
        assert generator.height == 100
        assert generator.speed_in_px_per_second == 20.0
        assert generator.direction == "right"
        assert generator.num_arrows == 4
        assert generator.animation == "ease-in-out"

    def test_init_custom_values(self):
        """Test generator initialization with custom values."""
        generator = MovingFlowArrowGenerator(
            color="#ff0000",
            stroke_width=20,
            width=200,
            height=150,
            speed_in_px_per_second=30.0,
            direction="up",
            num_arrows=6,
            animation="linear"
        )
        
        assert generator.color == "#ff0000"
        assert generator.stroke_width == 20
        assert generator.width == 200
        assert generator.height == 150
        assert generator.speed_in_px_per_second == 30.0
        assert generator.direction == "up"
        assert generator.num_arrows == 6
        assert generator.animation == "linear"

    def test_num_arrows_validation(self):
        """Test that num_arrows is validated to minimum 1."""
        generator = MovingFlowArrowGenerator(num_arrows=0)
        assert generator.num_arrows == 1
        
        generator = MovingFlowArrowGenerator(num_arrows=-5)
        assert generator.num_arrows == 1

    def test_stroke_width_validation(self):
        """Test that stroke_width is validated to minimum 2."""
        generator = MovingFlowArrowGenerator(stroke_width=1)
        assert generator.stroke_width == 2
        
        generator = MovingFlowArrowGenerator(stroke_width=-10)
        assert generator.stroke_width == 2

    def test_direction_normalization(self):
        """Test that direction is normalized to lowercase."""
        generator = MovingFlowArrowGenerator(direction="UP")
        assert generator.direction == "up"
        
        generator = MovingFlowArrowGenerator(direction="LEFT")
        assert generator.direction == "left"

    def test_generate_svg_returns_string(self):
        """Test that generate_svg returns a string."""
        generator = MovingFlowArrowGenerator()
        svg = generator.generate_svg()
        
        assert isinstance(svg, str)
        assert len(svg) > 0

    def test_svg_contains_required_elements(self):
        """Test that generated SVG contains required elements."""
        generator = MovingFlowArrowGenerator()
        svg = generator.generate_svg()
        
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "clipPath" in svg
        assert "polyline" in svg
        assert "animation" in svg

    def test_svg_contains_custom_attributes(self):
        """Test that generated SVG contains custom attributes."""
        generator = MovingFlowArrowGenerator(
            color="#ff0000",
            width=200,
            height=150
        )
        svg = generator.generate_svg()
        
        assert 'width="200"' in svg
        assert 'height="150"' in svg
        assert "#ff0000" in svg

    def test_calculate_animation_duration(self):
        """Test animation duration calculation."""
        generator = MovingFlowArrowGenerator(speed_in_px_per_second=20.0, width=100, height=100)
        duration = generator._calculate_animation_duration()
        
        assert isinstance(duration, float)
        assert duration > 0

    def test_get_arrow_points_all_directions(self):
        """Test arrow points generation for all directions."""
        generator = MovingFlowArrowGenerator()
        
        for direction in ["right", "left", "up", "down"]:
            generator.direction = direction
            points = generator._get_arrow_points()
            
            assert isinstance(points, str)
            assert len(points) > 0
            assert "," in points  # Should contain coordinates

    def test_invalid_direction_raises_error(self):
        """Test that invalid direction raises ValueError."""
        generator = MovingFlowArrowGenerator(direction="invalid")
        
        with pytest.raises(ValueError):
            generator._get_arrow_points()

    def test_save_to_file(self, tmp_path):
        """Test saving SVG to file."""
        generator = MovingFlowArrowGenerator()
        file_path = tmp_path / "test_arrow.svg"
        
        generator.save_to_file(str(file_path))
        
        assert file_path.exists()
        content = file_path.read_text()
        assert "<svg" in content
        assert "</svg>" in content