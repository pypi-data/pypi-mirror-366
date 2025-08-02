from captain_arro.generators.base import AnimatedArrowGeneratorBase
from captain_arro.constants import SPREAD_DIRECTIONS
from typing import Union
import uuid


class SpotlightSpreadArrowGenerator(AnimatedArrowGeneratorBase):
    def __init__(
            self,
            color: str = "#2563eb",
            stroke_width: int = 10,
            width: int = 100,
            height: int = 100,
            speed_in_px_per_second: float = 20.0,
            speed_in_duration_seconds: float = None,
            direction: SPREAD_DIRECTIONS = "horizontal",
            num_arrows: int = 4,
            spotlight_size: float = 0.3,
            spotlight_path_extension_factor: float = 0.5,
            dim_opacity: float = 0.2,
            center_gap_ratio: float = 0.2,
    ):
        super().__init__(
            color=color,
            stroke_width=stroke_width,
            width=width,
            height=height,
            speed_in_px_per_second=speed_in_px_per_second,
            speed_in_duration_seconds=speed_in_duration_seconds,
            num_arrows=max(2, num_arrows),
        )
        self.direction = direction.lower()
        self.spotlight_size = max(0.1, min(1.0, spotlight_size))
        self.dim_opacity = max(0.0, min(1.0, dim_opacity))
        self.spotlight_path_extension_factor = spotlight_path_extension_factor
        self.center_gap_ratio = max(0.1, min(0.4, center_gap_ratio))

    def generate_svg(self, unique_id: Union[bool, str] = True) -> str:
        """Override to customize arrow styles with directional gradients."""
        
        clip_bounds = self._get_clip_bounds()
        animations = self._generate_animations()
        arrow_elements = self._generate_arrow_elements()
        gradient_defs = self._generate_gradient_defs()

        svg = f"""
        <svg width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <clipPath id="arrowClip">
              <rect x="{clip_bounds['x']}" y="{clip_bounds['y']}" width="{clip_bounds['width']}" height="{clip_bounds['height']}"/>
            </clipPath>
            {gradient_defs}
          </defs>

          <style>
            .arrow-left {{
              stroke: url(#spotlightGradientLeft);
              stroke-width: {self.stroke_width};
              stroke-linecap: round;
              stroke-linejoin: round;
              fill: none;
            }}

            .arrow-right {{
              stroke: url(#spotlightGradientRight);
              stroke-width: {self.stroke_width};
              stroke-linecap: round;
              stroke-linejoin: round;
              fill: none;
            }}

            .arrow-top {{
              stroke: url(#spotlightGradientTop);
              stroke-width: {self.stroke_width};
              stroke-linecap: round;
              stroke-linejoin: round;
              fill: none;
            }}

            .arrow-bottom {{
              stroke: url(#spotlightGradientBottom);
              stroke-width: {self.stroke_width};
              stroke-linecap: round;
              stroke-linejoin: round;
              fill: none;
            }}
            
            {animations}
          </style>

          <g clip-path="url(#arrowClip)">
            {arrow_elements}
          </g>
        </svg>
        """
        
        # Apply unique suffixes if requested
        if unique_id is not False:
            if unique_id is True:
                # Generate random suffix
                suffix = uuid.uuid4().hex[:6]
            else:
                # Use provided suffix
                suffix = str(unique_id)
            
            # Get the list of IDs that need to be made unique
            id_keys = self._get_unique_id_keys()
            svg = self._apply_unique_suffix(svg, suffix, id_keys)
        
        return svg

    def _generate_gradient_defs(self) -> str:
        duration = self.speed_in_duration_seconds
        spotlight_percent = self.spotlight_size * 100
        dim_before = (100 - spotlight_percent) / 2
        dim_after = dim_before + spotlight_percent

        if self.direction == "horizontal":
            center_x = self.width // 2
            left_gradient = f"""
        <linearGradient id="spotlightGradientLeft" x1="0" y1="0" x2="{self.width}" y2="0" gradientUnits="userSpaceOnUse">
          <animateTransform
            attributeName="gradientTransform"
            type="translate"
            values="{center_x} 0; -{self.width} 0"
            dur="{duration:.2f}s"
            repeatCount="indefinite"/>
          <stop offset="0%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
          <stop offset="{dim_before:.1f}%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
          <stop offset="50%" stop-color="{self.color}" stop-opacity="1"/>
          <stop offset="{dim_after:.1f}%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
          <stop offset="100%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
        </linearGradient>"""

            right_gradient = f"""
        <linearGradient id="spotlightGradientRight" x1="-{self.width}" y1="0" x2="0" y2="0" gradientUnits="userSpaceOnUse">
          <animateTransform
            attributeName="gradientTransform"
            type="translate"
            values="-{center_x} 0; {self.width} 0"
            dur="{duration:.2f}s"
            repeatCount="indefinite"/>
          <stop offset="0%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
          <stop offset="{dim_before:.1f}%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
          <stop offset="50%" stop-color="{self.color}" stop-opacity="1"/>
          <stop offset="{dim_after:.1f}%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
          <stop offset="100%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
        </linearGradient>"""

            return left_gradient + "\n" + right_gradient

        else:
            center_y = self.height // 2
            top_gradient = f"""
        <linearGradient id="spotlightGradientTop" x1="0" y1="0" x2="0" y2="{self.height}" gradientUnits="userSpaceOnUse">
          <animateTransform
            attributeName="gradientTransform"
            type="translate"
            values="0 {center_y}; 0 -{self.height}"
            dur="{duration:.2f}s"
            repeatCount="indefinite"/>
          <stop offset="0%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
          <stop offset="{dim_before:.1f}%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
          <stop offset="50%" stop-color="{self.color}" stop-opacity="1"/>
          <stop offset="{dim_after:.1f}%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
          <stop offset="100%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
        </linearGradient>"""

            bottom_gradient = f"""
        <linearGradient id="spotlightGradientBottom" x1="0" y1="-{self.height}" x2="0" y2="0" gradientUnits="userSpaceOnUse">
          <animateTransform
            attributeName="gradientTransform"
            type="translate"
            values="0 -{center_y}; 0 {self.height}"
            dur="{duration:.2f}s"
            repeatCount="indefinite"/>
          <stop offset="0%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
          <stop offset="{dim_before:.1f}%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
          <stop offset="50%" stop-color="{self.color}" stop-opacity="1"/>
          <stop offset="{dim_after:.1f}%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
          <stop offset="100%" stop-color="{self.color}" stop-opacity="{self.dim_opacity}"/>
        </linearGradient>"""

            return top_gradient + "\n" + bottom_gradient

    def _generate_arrow_elements(self) -> str:
        elements = []

        if self.direction == "horizontal":
            left_positions = self._get_left_arrow_positions()
            right_positions = self._get_right_arrow_positions()

            for pos in left_positions:
                arrow_points = self._get_left_arrow_points()
                elements.append(
                    f'    <g class="arrow-left" style="transform: translate({pos["x"]}px, {pos["y"]}px)">\n      <polyline points="{arrow_points}"/>\n    </g>')

            for pos in right_positions:
                arrow_points = self._get_right_arrow_points()
                elements.append(
                    f'    <g class="arrow-right" style="transform: translate({pos["x"]}px, {pos["y"]}px)">\n      <polyline points="{arrow_points}"/>\n    </g>')

        else:
            top_positions = self._get_top_arrow_positions()
            bottom_positions = self._get_bottom_arrow_positions()

            for pos in top_positions:
                arrow_points = self._get_up_arrow_points()
                elements.append(
                    f'    <g class="arrow-top" style="transform: translate({pos["x"]}px, {pos["y"]}px)">\n      <polyline points="{arrow_points}"/>\n    </g>')

            for pos in bottom_positions:
                arrow_points = self._get_down_arrow_points()
                elements.append(
                    f'    <g class="arrow-bottom" style="transform: translate({pos["x"]}px, {pos["y"]}px)">\n      <polyline points="{arrow_points}"/>\n    </g>')

        return "\n    \n".join(elements)

    def _calculate_arrow_layout(self):
        """SIMPLE constraint-based layout - work backwards from constraints"""
        arrows_per_side = self.num_arrows // 2
        
        if self.direction == "horizontal":
            # 1. Arrow size: use most of perpendicular space (height)
            arrow_height = int(self.height * 0.8)  # 80% of height
            
            # 2. Center gap: fixed ratio 
            center_gap = int(self.width * self.center_gap_ratio)
            
            # 3. Available space per side
            available_width_per_side = (self.width - center_gap) // 2
            
            # 4. Arrow width: constrained by space per arrow
            arrow_width = available_width_per_side // max(arrows_per_side, 1)
            
            return {
                "arrow_width": arrow_width,
                "arrow_height": arrow_height,
                "center_gap": center_gap,
                "available_width_per_side": available_width_per_side
            }
        else:
            # 1. Arrow size: use most of perpendicular space (width)
            arrow_width = int(self.width * 0.8)  # 80% of width
            
            # 2. Center gap: fixed ratio 
            center_gap = int(self.height * self.center_gap_ratio)
            
            # 3. Available space per side
            available_height_per_side = (self.height - center_gap) // 2
            
            # 4. Arrow height: constrained by space per arrow
            arrow_height = available_height_per_side // max(arrows_per_side, 1)
            
            return {
                "arrow_width": arrow_width,
                "arrow_height": arrow_height,
                "center_gap": center_gap,
                "available_height_per_side": available_height_per_side
            }

    def _get_left_arrow_positions(self) -> list[dict[str, int]]:
        arrows_per_side = self.num_arrows // 2
        positions = []

        if self.direction == "horizontal":
            layout = self._calculate_arrow_layout()
            
            center_x = self.width // 2
            left_edge = center_x - layout["center_gap"] // 2
            
            for i in range(arrows_per_side):
                # Outermost arrow tip exactly at edge, work backwards
                # Account for stroke width so stroke edge stays within bounds
                arrow_center = left_edge - (layout["arrow_width"] // 2) + (self.stroke_width // 2) - i * layout["arrow_width"]
                positions.append({"x": int(arrow_center), "y": self.height // 2})

        return positions

    def _get_right_arrow_positions(self) -> list[dict[str, int]]:
        arrows_per_side = self.num_arrows // 2
        positions = []

        if self.direction == "horizontal":
            layout = self._calculate_arrow_layout()
            
            center_x = self.width // 2
            right_edge = center_x + layout["center_gap"] // 2
            
            for i in range(arrows_per_side):
                # Outermost arrow tip exactly at edge, work backwards
                # Account for stroke width so stroke edge stays within bounds
                arrow_center = right_edge + (layout["arrow_width"] // 2) - (self.stroke_width // 2) + i * layout["arrow_width"]
                positions.append({"x": int(arrow_center), "y": self.height // 2})

        return positions

    def _get_top_arrow_positions(self) -> list[dict[str, int]]:
        arrows_per_side = self.num_arrows // 2
        positions = []

        if self.direction == "vertical":
            layout = self._calculate_arrow_layout()
            
            center_y = self.height // 2
            top_edge = center_y - layout["center_gap"] // 2
            
            for i in range(arrows_per_side):
                # Outermost arrow tip exactly at edge, work backwards
                # Account for stroke width so stroke edge stays within bounds
                arrow_center = top_edge - (layout["arrow_height"] // 2) + (self.stroke_width // 2) - i * layout["arrow_height"]
                positions.append({"x": self.width // 2, "y": int(arrow_center)})

        return positions

    def _get_bottom_arrow_positions(self) -> list[dict[str, int]]:
        arrows_per_side = self.num_arrows // 2
        positions = []

        if self.direction == "vertical":
            layout = self._calculate_arrow_layout()
            
            center_y = self.height // 2
            bottom_edge = center_y + layout["center_gap"] // 2
            
            for i in range(arrows_per_side):
                # Outermost arrow tip exactly at edge, work backwards
                # Account for stroke width so stroke edge stays within bounds
                arrow_center = bottom_edge + (layout["arrow_height"] // 2) - (self.stroke_width // 2) + i * layout["arrow_height"]
                positions.append({"x": self.width // 2, "y": int(arrow_center)})

        return positions

    def _get_clip_bounds(self) -> dict[str, int]:
        # Use full canvas area - no margins
        return {
            "x": 0,
            "y": 0,
            "width": self.width,
            "height": self.height
        }

    def _get_left_arrow_points(self) -> str:
        layout = self._calculate_arrow_layout()
        offset_x = layout["arrow_width"] // 2
        offset_y = layout["arrow_height"] // 2
        return f"{offset_x},{-offset_y} {-offset_x},0 {offset_x},{offset_y}"

    def _get_right_arrow_points(self) -> str:
        layout = self._calculate_arrow_layout()
        offset_x = layout["arrow_width"] // 2
        offset_y = layout["arrow_height"] // 2
        return f"{-offset_x},{-offset_y} {offset_x},0 {-offset_x},{offset_y}"

    def _get_up_arrow_points(self) -> str:
        layout = self._calculate_arrow_layout()
        offset_x = layout["arrow_width"] // 2
        offset_y = layout["arrow_height"] // 2
        return f"{-offset_x},{offset_y} 0,{-offset_y} {offset_x},{offset_y}"

    def _get_down_arrow_points(self) -> str:
        layout = self._calculate_arrow_layout()
        offset_x = layout["arrow_width"] // 2
        offset_y = layout["arrow_height"] // 2
        return f"{-offset_x},{-offset_y} 0,{offset_y} {offset_x},{-offset_y}"

    def _get_transform_distance(self) -> float:
        if self.direction == "vertical":
            return float(self.height)
        else:
            return float(self.width)

    def _generate_animations(self) -> str:
        """Return empty string since animations are handled by gradient transforms."""
        return ""

    def _get_unique_id_keys(self) -> list[str]:
        """Get the list of ID keys that need to be made unique for this generator."""
        return [
            "arrowClip",
            "spotlightGradientLeft",
            "spotlightGradientRight", 
            "spotlightGradientTop",
            "spotlightGradientBottom",
            "arrow-left",
            "arrow-right",
            "arrow-top", 
            "arrow-bottom"
        ]


if __name__ == "__main__":
    generator = SpotlightSpreadArrowGenerator()

    print("Generated default spotlight spread arrow:")
    print(generator.generate_svg())
    generator.save_to_file("_tmp/spotlight_spread_arrow_default.svg")

    configurations = [
        {"direction": "horizontal", "color": "#3b82f6", "num_arrows": 6, "width": 200, "height": 80,
         "speed": 80.0, "spotlight_size": 0.4},
        {"direction": "vertical", "color": "#ef4444", "num_arrows": 4, "width": 100, "height": 150,
         "speed": 60.0, "spotlight_size": 0.3, "dim_opacity": 0.1},
        {"direction": "horizontal", "color": "#10b981", "num_arrows": 8, "width": 180, "height": 60,
         "speed": 100.0, "spotlight_size": 0.25, "center_gap_ratio": 0.3},
        {"direction": "vertical", "color": "#f59e0b", "num_arrows": 6, "width": 100, "height": 200,
         "speed": 90.0, "spotlight_size": 0.35, "dim_opacity": 0.15}
    ]

    for config in configurations:
        gen = SpotlightSpreadArrowGenerator(**config)
        file = f"_tmp/spotlight_spread_arrow_{config['direction']}_{config['num_arrows']}.svg"
        gen.save_to_file(file)
        print(f"Created {file} with {config}")
