#!/usr/bin/env python3
"""
Basic usage examples for captain_arro package.

This script demonstrates the basic functionality of all arrow generators
and creates sample SVG files for documentation.
"""

import os
import sys

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from captain_arro import (
    MovingFlowArrowGenerator,
    SpotlightFlowArrowGenerator,
    BouncingSpreadArrowGenerator,
    SpotlightSpreadArrowGenerator
)


def create_output_dir():
    """Create output directory if it doesn't exist."""
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def generate_moving_flow_examples(output_dir):
    """Generate moving flow arrow examples."""
    print("Generating moving flow arrow examples...")
    
    # Basic example
    generator = MovingFlowArrowGenerator()
    generator.save_to_file(os.path.join(output_dir, "moving_flow_basic.svg"))
    
    # Custom examples
    examples = [
        {
            "name": "moving_flow_right_blue",
            "params": {
                "direction": "right",
                "stroke_width": 8,
                "color": "#3b82f6",
                "num_arrows": 6,
                "width": 150,
                "height": 100,
                "speed_in_px_per_second": 25.0,
                "animation": "ease-in-out"
            }
        },
        {
            "name": "moving_flow_up_red",
            "params": {
                "direction": "up",
                "color": "#ef4444",
                "num_arrows": 4,
                "width": 80,
                "height": 120,
                "speed_in_px_per_second": 15.0,
                "animation": "linear"
            }
        },
        {
            "name": "moving_flow_left_green",
            "params": {
                "direction": "left",
                "color": "#10b981",
                "num_arrows": 2,
                "width": 200,
                "height": 50,
                "stroke_width": 8,
                "speed_in_px_per_second": 30.0
            }
        }
    ]
    
    for example in examples:
        gen = MovingFlowArrowGenerator(**example["params"])
        gen.save_to_file(os.path.join(output_dir, f"{example['name']}.svg"))
        print(f"  Created {example['name']}.svg")


def generate_spotlight_flow_examples(output_dir):
    """Generate spotlight flow arrow examples."""
    print("Generating spotlight flow arrow examples...")
    
    # Basic example
    generator = SpotlightFlowArrowGenerator()
    generator.save_to_file(os.path.join(output_dir, "spotlight_flow_basic.svg"))
    
    # Custom examples
    examples = [
        {
            "name": "spotlight_flow_right_purple",
            "params": {
                "direction": "right",
                "color": "#8b5cf6",
                "num_arrows": 3,
                "width": 180,
                "height": 120,
                "speed_in_px_per_second": 40.0,
                "spotlight_size": 0.3,
                "dim_opacity": 0.5,
            }
        },
        {
            "name": "spotlight_flow_down_orange",
            "params": {
                "direction": "down",
                "color": "#f59e0b",
                "num_arrows": 2,
                "width": 60,
                "height": 150,
                "speed_in_px_per_second": 20.0,
                "spotlight_size": 0.5,
                "dim_opacity": 0.1
            }
        }
    ]
    
    for example in examples:
        gen = SpotlightFlowArrowGenerator(**example["params"])
        gen.save_to_file(os.path.join(output_dir, f"{example['name']}.svg"))
        print(f"  Created {example['name']}.svg")


def generate_bouncing_spread_examples(output_dir):
    """Generate bouncing spread arrow examples."""
    print("Generating bouncing spread arrow examples...")
    
    # Basic example
    generator = BouncingSpreadArrowGenerator()
    generator.save_to_file(os.path.join(output_dir, "bouncing_spread_basic.svg"))
    
    # Custom examples
    examples = [
        {
            "name": "bouncing_spread_horizontal_teal",
            "params": {
                "direction": "horizontal",
                "color": "#14b8a6",
                "num_arrows": 4,
                "width": 250,
                "height": 100,
                "speed_in_px_per_second": 15.0,
                "animation": "ease-in-out",
                "center_gap_ratio": 0.3,
                "stroke_width": 10
            }
        },
        {
            "name": "bouncing_spread_vertical_pink",
            "params": {
                "direction": "vertical",
                "color": "#ec4899",
                "num_arrows": 4,
                "width": 100,
                "height": 200,
                "speed_in_px_per_second": 20.0,
                "animation": "ease",
                "stroke_width": 4
            },
        },
        {
            "name": "bouncing_spread_horizontal_red",
            "params": {
                "direction": "horizontal",
                "color": "red",
                "num_arrows": 8,
                "width": 400,
                "height": 200,
                "speed_in_px_per_second": 20.0,
                "animation": "ease",
                "stroke_width": 8,
                "center_gap_ratio": 1.5,
            }
        },
    ]
    
    for example in examples:
        gen = BouncingSpreadArrowGenerator(**example["params"])
        gen.save_to_file(os.path.join(output_dir, f"{example['name']}.svg"))
        print(f"  Created {example['name']}.svg")


def generate_spotlight_spread_examples(output_dir):
    """Generate spotlight spread arrow examples."""
    print("Generating spotlight spread arrow examples...")
    
    # Basic example
    generator = SpotlightSpreadArrowGenerator()
    generator.save_to_file(os.path.join(output_dir, "spotlight_spread_basic.svg"))
    
    # Custom examples
    examples = [
        {
            "name": "spotlight_spread_horizontal_indigo",
            "params": {
                "direction": "horizontal",
                "color": "#6366f1",
                "stroke_width": 12,
                "num_arrows": 8,
                "width": 300,
                "height": 100,
                "speed_in_px_per_second": 100.0,
                "spotlight_size": 0.25,
                "dim_opacity": 0.5,
                "center_gap_ratio": 0.3,
            }
        },
        {
            "name": "spotlight_spread_vertical_emerald",
            "params": {
                "direction": "vertical",
                "color": "#059669",
                "num_arrows": 6,
                "width": 80,
                "height": 250,
                "speed_in_px_per_second": 35.0,
                "spotlight_size": 0.35,
                "dim_opacity": 0.1
            }
        }
    ]
    
    for example in examples:
        gen = SpotlightSpreadArrowGenerator(**example["params"])
        gen.save_to_file(os.path.join(output_dir, f"{example['name']}.svg"))
        print(f"  Created {example['name']}.svg")


def main():
    """Generate all example SVGs."""
    print("Captain Arro - Generating example SVGs")
    print("=" * 40)
    
    output_dir = create_output_dir()
    print(f"Output directory: {output_dir}")
    print()
    
    generate_moving_flow_examples(output_dir)
    print()
    
    generate_spotlight_flow_examples(output_dir)
    print()
    
    generate_bouncing_spread_examples(output_dir)
    print()
    
    generate_spotlight_spread_examples(output_dir)
    print()
    
    print("All examples generated successfully!")
    print(f"Check the '{output_dir}' directory for SVG files.")


if __name__ == "__main__":
    main()