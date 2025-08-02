from captain_arro.generators.base import AnimatedArrowGeneratorBase
from captain_arro.constants import ANIMATION_TYPES, SPREAD_DIRECTIONS
from typing import Union
import uuid


class BouncingSpreadArrowGenerator(AnimatedArrowGeneratorBase):
    def __init__(
            self,
            color: str = "#2563eb",
            stroke_width: int = 2,
            width: int = 300,
            height: int = 150,
            speed_in_px_per_second: float = 10.0,
            speed_in_duration_seconds: float = None,
            direction: SPREAD_DIRECTIONS = "vertical",
            num_arrows: int = 6,
            animation: ANIMATION_TYPES = "ease-in-out",
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
        self.animation = animation
        self.center_gap_ratio = max(0.1, min(0.4, center_gap_ratio))

    def generate_svg(self, unique_id: Union[bool, str] = True) -> str:
        """Override to customize the arrow groups and animations."""
        
        clip_bounds = self._get_clip_bounds()
        animations = self._generate_animations()
        arrow_elements = self._generate_arrow_elements()

        svg = f"""
        <svg width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <clipPath id="arrowClip">
              <rect x="{clip_bounds['x']}" y="{clip_bounds['y']}" width="{clip_bounds['width']}" height="{clip_bounds['height']}"/>
            </clipPath>
          </defs>

          <style>
            .arrow {{
              stroke: {self.color};
              stroke-width: {self.stroke_width};
              stroke-linecap: round;
              stroke-linejoin: round;
              fill: none;
            }}

            .group-left {{
              animation: moveLeft {self.speed_in_duration_seconds:.2f}s {self.animation} infinite alternate;
            }}

            .group-right {{
              animation: moveRight {self.speed_in_duration_seconds:.2f}s {self.animation} infinite alternate;
            }}

            .group-top {{
              animation: moveTop {self.speed_in_duration_seconds:.2f}s {self.animation} infinite alternate;
            }}

            .group-bottom {{
              animation: moveBottom {self.speed_in_duration_seconds:.2f}s {self.animation} infinite alternate;
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

    def _generate_arrow_elements(self) -> str:
        arrows_per_side = self.num_arrows // 2
        elements = []

        left_arrows = []
        right_arrows = []
        top_arrows = []
        bottom_arrows = []

        if self.direction == "horizontal":
            left_positions = self._get_left_arrow_positions()
            right_positions = self._get_right_arrow_positions()

            for i, pos in enumerate(left_positions):
                arrow_points = self._get_left_arrow_points()
                left_arrows.append(
                    f'      <g style="transform: translate({pos["x"]}px, {pos["y"]}px)">\n        <polyline points="{arrow_points}"/>\n      </g>')

            for i, pos in enumerate(right_positions):
                arrow_points = self._get_right_arrow_points()
                right_arrows.append(
                    f'      <g style="transform: translate({pos["x"]}px, {pos["y"]}px)">\n        <polyline points="{arrow_points}"/>\n      </g>')

            if left_arrows:
                elements.append(f'    <g class="arrow group-left">\n{chr(10).join(left_arrows)}\n    </g>')
            if right_arrows:
                elements.append(f'    <g class="arrow group-right">\n{chr(10).join(right_arrows)}\n    </g>')

        else:
            top_positions = self._get_top_arrow_positions()
            bottom_positions = self._get_bottom_arrow_positions()

            for i, pos in enumerate(top_positions):
                arrow_points = self._get_up_arrow_points()
                top_arrows.append(
                    f'      <g style="transform: translate({pos["x"]}px, {pos["y"]}px)">\n        <polyline points="{arrow_points}"/>\n      </g>')

            for i, pos in enumerate(bottom_positions):
                arrow_points = self._get_down_arrow_points()
                bottom_arrows.append(
                    f'      <g style="transform: translate({pos["x"]}px, {pos["y"]}px)">\n        <polyline points="{arrow_points}"/>\n      </g>')

            if top_arrows:
                elements.append(f'    <g class="arrow group-top">\n{chr(10).join(top_arrows)}\n    </g>')
            if bottom_arrows:
                elements.append(f'    <g class="arrow group-bottom">\n{chr(10).join(bottom_arrows)}\n    </g>')

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
            available_space = self.height - 2 * (self.height // 8)
            return float(available_space * 0.15)
        else:
            available_space = self.width - 2 * (self.width // 8)
            return float(available_space * 0.15)


    def _generate_animations(self) -> str:
        distance = self._get_transform_distance()

        if self.direction == "horizontal":
            return f"""
        @keyframes moveLeft {{
          0% {{ transform: translateX(0px); }}
          100% {{ transform: translateX({distance}px); }}
        }}

        @keyframes moveRight {{
          0% {{ transform: translateX(0px); }}
          100% {{ transform: translateX(-{distance}px); }}
        }}"""
        else:
            return f"""
        @keyframes moveTop {{
          0% {{ transform: translateY(0px); }}
          100% {{ transform: translateY({distance}px); }}
        }}

        @keyframes moveBottom {{
          0% {{ transform: translateY(0px); }}
          100% {{ transform: translateY(-{distance}px); }}
        }}"""

    def _get_unique_id_keys(self) -> list[str]:
        """Get the list of ID keys that need to be made unique for this generator."""
        return [
            "arrowClip", 
            "arrow", 
            "group-left", 
            "group-right", 
            "group-top", 
            "group-bottom",
            "moveLeft",
            "moveRight", 
            "moveTop", 
            "moveBottom"
        ]


if __name__ == "__main__":
    generator = BouncingSpreadArrowGenerator()

    print("Generated default bouncing spread arrow:")
    print(generator.generate_svg())
    generator.save_to_file("_tmp/bouncing_spread_arrow_default.svg")

    configurations = [
        {"direction": "horizontal", "color": "#3b82f6", "num_arrows": 1, "width": 300, "height": 300,
         "animation": "ease-in-out"},
        {"direction": "vertical", "color": "#ef4444", "num_arrows": 4, "width": 80, "height": 150,
         "animation": "ease-in"},
        {"direction": "horizontal", "color": "#10b981", "num_arrows": 8, "stroke_width": 12, "width": 180, "height": 60,
         "center_gap_ratio": 0.3},
        {"direction": "vertical", "color": "#f59e0b", "num_arrows": 6, "stroke_width": 8, "speed": 25.0, "width": 100,
         "height": 200}
    ]

    for config in configurations:
        gen = BouncingSpreadArrowGenerator(**config)
        file = f"_tmp/bouncing_spread_arrow_{config['direction']}_{config['num_arrows']}.svg"
        gen.save_to_file(file)
        print(f"Created {file} with {config}")
