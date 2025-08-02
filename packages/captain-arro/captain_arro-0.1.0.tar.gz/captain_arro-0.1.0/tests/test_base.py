"""
Tests for AnimatedArrowGeneratorBase.
"""

import pytest
from abc import ABC
from captain_arro.generators.base import AnimatedArrowGeneratorBase


class ConcreteArrowGenerator(AnimatedArrowGeneratorBase):
    """Concrete implementation for testing."""
    
    def _generate_arrow_elements(self) -> str:
        return '<polyline points="0,0 10,10 20,0"/>'
    
    def _generate_animations(self) -> str:
        return '@keyframes test { 0% { opacity: 0; } 100% { opacity: 1; } }'
    
    def _get_transform_distance(self) -> float:
        return 100.0
    
    def _get_unique_id_keys(self) -> list[str]:
        return ["arrowClip", "test"]


class TestAnimatedArrowGeneratorBase:
    """Test cases for AnimatedArrowGeneratorBase."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that abstract base class cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AnimatedArrowGeneratorBase()

    def test_concrete_implementation_can_be_instantiated(self):
        """Test that concrete implementation can be instantiated."""
        generator = ConcreteArrowGenerator()
        
        assert isinstance(generator, AnimatedArrowGeneratorBase)
        assert generator.color == "#2563eb"
        assert generator.width == 100
        assert generator.height == 100

    def test_init_default_values(self):
        """Test base class initialization with default values."""
        generator = ConcreteArrowGenerator()
        
        assert generator.color == "#2563eb"
        assert generator.stroke_width == 10
        assert generator.width == 100
        assert generator.height == 100
        assert generator.speed_in_px_per_second == 20.0
        assert generator.num_arrows == 4

    def test_init_custom_values(self):
        """Test base class initialization with custom values."""
        generator = ConcreteArrowGenerator(
            color="#ff0000",
            stroke_width=15,
            width=200,
            height=150,
            speed_in_px_per_second=30.0,
            num_arrows=6
        )
        
        assert generator.color == "#ff0000"
        assert generator.stroke_width == 15
        assert generator.width == 200
        assert generator.height == 150
        assert generator.speed_in_px_per_second == 30.0
        assert generator.num_arrows == 6

    def test_num_arrows_validation(self):
        """Test that num_arrows is validated to minimum 1."""
        generator = ConcreteArrowGenerator(num_arrows=0)
        assert generator.num_arrows == 1
        
        generator = ConcreteArrowGenerator(num_arrows=-5)
        assert generator.num_arrows == 1

    def test_stroke_width_validation(self):
        """Test that stroke_width is validated to minimum 2."""
        generator = ConcreteArrowGenerator(stroke_width=1)
        assert generator.stroke_width == 2
        
        generator = ConcreteArrowGenerator(stroke_width=-10)
        assert generator.stroke_width == 2

    def test_generate_svg_template_method(self):
        """Test that generate_svg template method works."""
        generator = ConcreteArrowGenerator()
        svg = generator.generate_svg()
        
        assert isinstance(svg, str)
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "clipPath" in svg
        assert "polyline" in svg

    def test_get_clip_bounds_default(self):
        """Test default clip bounds calculation."""
        generator = ConcreteArrowGenerator(width=100, height=200)
        bounds = generator._get_clip_bounds()
        
        assert bounds["x"] == 0  # no margin
        assert bounds["y"] == 0  # no margin
        assert bounds["width"] == 100  # full width
        assert bounds["height"] == 200  # full height

    def test_save_to_file(self, tmp_path):
        """Test saving SVG to file."""
        generator = ConcreteArrowGenerator()
        file_path = tmp_path / "test_base.svg"
        
        generator.save_to_file(str(file_path))
        
        assert file_path.exists()
        content = file_path.read_text()
        assert "<svg" in content
        assert "</svg>" in content

    def test_abstract_methods_required(self):
        """Test that abstract methods must be implemented."""
        
        class IncompleteGenerator(AnimatedArrowGeneratorBase):
            def _generate_arrow_elements(self) -> str:
                return ""
            # Missing _generate_animations
        
        class AnotherIncompleteGenerator(AnimatedArrowGeneratorBase):
            def _generate_animations(self) -> str:
                return ""
            # Missing _generate_arrow_elements
        
        with pytest.raises(TypeError):
            IncompleteGenerator()
        
        with pytest.raises(TypeError):
            AnotherIncompleteGenerator()