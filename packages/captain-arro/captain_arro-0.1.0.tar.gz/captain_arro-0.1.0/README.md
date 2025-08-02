# Captain Arro ⬅⛵️➡

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Captain Arro** is a Python library for generating animated SVG arrows for web interfaces. Create beautiful, customizable arrow animations with just a few lines of code.

Yes, this package is totally vibe coded. It's useful anyhow!

## Features

- 🎯 **Four arrow types**: Moving flow, spotlight flow, bouncing spread, and spotlight spread
- 🎨 **Fully customizable**: Colors, sizes, speeds, directions, and animations
- 🔧 **Type-safe**: Full TypeScript-style type hints for better development experience
- 📦 **Zero dependencies**: Pure Python implementation
- 🌐 **Web-ready**: Generates clean SVG code for direct HTML embedding

## Installation

```bash
pip install captain-arro
```

## Quick Start

```python
from captain_arro import MovingFlowArrowGenerator

# Create a simple right-pointing arrow
generator = MovingFlowArrowGenerator()
svg_content = generator.generate_svg()

# Save to file
generator.save_to_file("my_arrow.svg")
```

## Arrow Types

### 1. Moving Flow Arrows

Arrows that move continuously in one direction with a flowing animation.

```python
from captain_arro import MovingFlowArrowGenerator

# Blue arrows moving right
generator = MovingFlowArrowGenerator(
    direction="right",
    stroke_width=8,
    color="#3b82f6", 
    num_arrows=6,
    width=150,
    height=100,
    speed_in_px_per_second=25,
    animation="ease-in-out"
)
```

![Moving Flow Right](examples/output/moving_flow_right_blue.svg)

### 2. Spotlight Flow Arrows  

Arrows with a moving spotlight effect that highlights different parts.

```python
from captain_arro import SpotlightFlowArrowGenerator

# Purple spotlight effect
generator = SpotlightFlowArrowGenerator(
        direction="right",
        color="#8b5cf6",
        num_arrows=3,
        width=180,
        height=120,
        speed_in_px_per_second=40.0,
        spotlight_size=0.3,
        dim_opacity=0.5
)
```

![Spotlight Flow Right](examples/output/spotlight_flow_right_purple.svg)

### 3. Bouncing Spread Arrows

Arrows that spread outward from center with a bouncing animation.

```python
from captain_arro import BouncingSpreadArrowGenerator

# Teal arrows spreading horizontally  
generator = BouncingSpreadArrowGenerator(
        direction="horizontal",
        color="#14b8a6",
        num_arrows=4,
        width=250,
        height=100,
        speed_in_px_per_second=15.0,
        animation="ease-in-out",
        center_gap_ratio=0.3,
        stroke_width=10
)
```

![Bouncing Spread Horizontal](examples/output/bouncing_spread_horizontal_teal.svg)

### 4. Spotlight Spread Arrows

Spread arrows with spotlight effects radiating from center.

```python
from captain_arro import SpotlightSpreadArrowGenerator

# Indigo spotlight spreading horizontally
generator = SpotlightSpreadArrowGenerator(
        direction="horizontal",
        color="#6366f1",
        stroke_width=12,
        num_arrows=8,
        width=300,
        height=100,
        speed_in_px_per_second=100.0,
        spotlight_size=0.25,
        dim_opacity=0.5,
        center_gap_ratio=0.3,
)
```

![Spotlight Spread Horizontal](examples/output/spotlight_spread_horizontal_indigo.svg)

## Configuration Options

### Common Parameters

All generators support these base parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `color` | `str` | `"#2563eb"` | Arrow color (hex, rgb, named colors) |
| `stroke_width` | `int` | `10` | Line thickness (min: 2) |
| `width` | `int` | `100` | SVG width in pixels |
| `height` | `int` | `100` | SVG height in pixels |
| `speed` | `float` | `20.0` | Animation speed (pixels per second) |
| `num_arrows` | `int` | `4` | Number of arrows to display |

### Flow Arrow Parameters

| Parameter | Type | Options | Description |
|-----------|------|---------|-------------|
| `direction` | `FLOW_DIRECTIONS` | `"right"`, `"left"`, `"up"`, `"down"` | Arrow movement direction |
| `animation` | `ANIMATION_TYPES` | `"ease-in-out"`, `"linear"`, `"ease"`, etc. | Animation timing function |

### Spotlight Parameters

| Parameter                         | Type | Default | Description                                           |
|-----------------------------------|------|---------|-------------------------------------------------------|
| `spotlight_size`                  | `float` | `0.3`   | Size of spotlight effect (0.1-1.0)                    |
| `spotlight_path_extension_factor` | `float` | `1.0`   | Factor by which the path of the spotlight is extended |
| `dim_opacity`                     | `float` | `0.2`   | Opacity of dimmed areas (0.0-1.0)                     |

### Spread Arrow Parameters  

| Parameter | Type | Options | Description |
|-----------|------|---------|-------------|
| `direction` | `SPREAD_DIRECTIONS` | `"horizontal"`, `"vertical"` | Spread orientation |
| `center_gap_ratio` | `float` | `0.2` | Gap size in center (0.1-0.4) |

## Advanced Usage

### Custom Animations

```python
from captain_arro import MovingFlowArrowGenerator

# Fast linear animation upward
generator = MovingFlowArrowGenerator(
    direction="up",
    speed_in_px_per_second=50.0,
    animation="linear",
    num_arrows=6
)
```

### Responsive Sizing

```python
# Large arrow for desktop
desktop_arrow = MovingFlowArrowGenerator(width=300, height=120)

# Small arrow for mobile  
mobile_arrow = MovingFlowArrowGenerator(width=150, height=60)
```

### Color Theming

```python
# Dark theme
dark_arrow = SpotlightFlowArrowGenerator(
    color="#ffffff",
    dim_opacity=0.1
)

# Brand colors
brand_arrow = BouncingSpreadArrowGenerator(
    color="#your-brand-color"
)
```

## HTML Integration

Embed generated SVGs directly in your HTML:

```html
<!-- Option 1: Inline SVG -->
<div class="arrow-container">
    <!-- Paste SVG content here -->
</div>

<!-- Option 2: External file -->
<img src="path/to/arrow.svg" alt="Animated arrow" />

<!-- Option 3: CSS background -->
<div style="background-image: url('path/to/arrow.svg')"></div>
```

## Type Safety

Captain Arro includes full type annotations for excellent IDE support:

```python
from captain_arro import FLOW_DIRECTIONS, ANIMATION_TYPES

# TypeScript-style literal types
direction: FLOW_DIRECTIONS = "right"  # ✅ Valid
direction: FLOW_DIRECTIONS = "invalid"  # ❌ Type error

animation: ANIMATION_TYPES = "ease-in-out"  # ✅ Valid  
animation: ANIMATION_TYPES = "bounce"  # ❌ Type error
```

## Examples

The `examples/` directory contains comprehensive usage examples:

```bash
# Generate all example SVGs
python examples/basic_usage.py

# View examples
ls examples/output/
```

See [`examples/README.md`](examples/README.md) for detailed descriptions of each example.

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=captain_arro
```

### Code Quality

```bash
# Format code
black captain_arro tests examples

# Sort imports  
isort captain_arro tests examples

# Type checking
mypy captain_arro

# Linting
flake8 captain_arro tests examples
```

## API Reference

### Base Classes

- `AnimatedArrowGeneratorBase` - Abstract base class for all generators

### Generator Classes

- `MovingFlowArrowGenerator` - Moving flow arrows
- `SpotlightFlowArrowGenerator` - Spotlight flow arrows  
- `BouncingSpreadArrowGenerator` - Bouncing spread arrows
- `SpotlightSpreadArrowGenerator` - Spotlight spread arrows

### Type Definitions

- `ANIMATION_TYPES` - Valid animation timing functions
- `FLOW_DIRECTIONS` - Valid flow directions  
- `SPREAD_DIRECTIONS` - Valid spread directions

## Browser Compatibility

Generated SVGs work in all modern browsers that support:
- SVG animations (`animateTransform`)
- CSS animations (`@keyframes`)
- Linear gradients


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0

- Initial release
- Four arrow generator types
- Full type safety
- Comprehensive test suite
- Documentation and examples

---

Made with ❤️ and good vibes