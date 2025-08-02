from captain_arro.generators.base import AnimatedArrowGeneratorBase
from captain_arro.constants import ANIMATION_TYPES, FLOW_DIRECTIONS


class MovingFlowArrowGenerator(AnimatedArrowGeneratorBase):
    def __init__(
            self,
            color: str = "#2563eb",
            stroke_width: int = 15,
            width: int = 100,
            height: int = 100,
            speed_in_px_per_second: float = 20.0,
            speed_in_duration_seconds: float = None,
            direction: FLOW_DIRECTIONS = "right",
            num_arrows: int = 4,
            animation: ANIMATION_TYPES = "ease-in-out",
    ):
        super().__init__(
            color=color,
            stroke_width=stroke_width,
            width=width,
            height=height,
            speed_in_px_per_second=speed_in_px_per_second,
            speed_in_duration_seconds=speed_in_duration_seconds,
            num_arrows=num_arrows,
        )
        self.direction = direction.lower()
        self.animation = animation

    def _generate_arrow_classes(self) -> str:
        duration = self.speed_in_duration_seconds
        classes = []
        for i in range(1, self.num_arrows + 1):
            classes.append(
                f"    .arrow{i} {{\n      animation: flow{i} {duration:.2f}s {self.animation} infinite;\n    }}")
        return "\n    \n".join(classes)

    def _generate_arrow_elements(self) -> str:
        arrow_points = self._get_arrow_points()
        duration = self.speed_in_duration_seconds
        elements = []

        for i in range(1, self.num_arrows + 1):
            if i == 1:
                delay = ""
            else:
                delay_value = -((i - 1) * duration / self.num_arrows)
                delay = f' style="animation-delay: {delay_value:.2f}s;"'

            elements.append(
                f'    <g class="arrow arrow{i}"{delay}>\n      <polyline points="{arrow_points}"/>\n    </g>')

        return "\n    \n".join(elements)

    def _get_clip_bounds(self) -> dict[str, int]:
        # Use full canvas area - no margins
        return {
            "x": 0,
            "y": 0,
            "width": self.width,
            "height": self.height
        }

    def _get_arrow_points(self) -> str:
        center_x = self.width // 2
        center_y = self.height // 2
        offset_x = self.width // 4
        offset_y = self.height // 4

        if self.direction == "down":
            return f"{center_x - offset_x},{center_y - offset_y // 2} {center_x},{center_y + offset_y // 2} {center_x + offset_x},{center_y - offset_y // 2}"
        elif self.direction == "up":
            return f"{center_x - offset_x},{center_y + offset_y // 2} {center_x},{center_y - offset_y // 2} {center_x + offset_x},{center_y + offset_y // 2}"
        elif self.direction == "right":
            return f"{center_x - offset_x // 2},{center_y - offset_y} {center_x + offset_x // 2},{center_y} {center_x - offset_x // 2},{center_y + offset_y}"
        elif self.direction == "left":
            return f"{center_x + offset_x // 2},{center_y - offset_y} {center_x - offset_x // 2},{center_y} {center_x + offset_x // 2},{center_y + offset_y}"
        else:
            raise ValueError(f"Invalid direction: {self.direction}. Use 'up', 'down', 'left', or 'right'.")

    def _get_transform_distance(self) -> float:
        if self.direction in ["up", "down"]:
            return float(self.height // 2 * 2)  # Total distance for moving flow
        else:
            return float(self.width // 2 * 2)  # Total distance for moving flow

    def _generate_animations(self) -> str:
        distance = self._get_transform_distance() // 2  # Half distance for start/end positions

        if self.direction == "down":
            start_transform = f"translateY(-{distance}px)"
            end_transform = f"translateY({distance}px)"
        elif self.direction == "up":
            start_transform = f"translateY({distance}px)"
            end_transform = f"translateY(-{distance}px)"
        elif self.direction == "right":
            start_transform = f"translateX(-{distance}px)"
            end_transform = f"translateX({distance}px)"
        elif self.direction == "left":
            start_transform = f"translateX({distance}px)"
            end_transform = f"translateX(-{distance}px)"
        else:
            raise ValueError(f"Direction {self.direction} not accepted")

        animation_template = """
        @keyframes {animation_name} {{
          0% {{
            transform: {start_transform};
            opacity: 0;
          }}
          20% {{
            opacity: 1;
          }}
          80% {{
            opacity: 1;
          }}
          100% {{
            transform: {end_transform};
            opacity: 0;
          }}
        }}
        """

        animations = []
        for i in range(1, self.num_arrows + 1):
            animations.append(animation_template.format(
                animation_name=f"flow{i}",
                start_transform=start_transform,
                end_transform=end_transform
            ))

        return "\n    ".join(animations)

    def _get_unique_id_keys(self) -> list[str]:
        """Get the list of ID keys that need to be made unique for this generator."""
        # Base IDs that are always present
        id_keys = ["arrowClip", "arrow"]
        
        # Add dynamic arrow class IDs based on num_arrows
        for i in range(1, self.num_arrows + 1):
            id_keys.extend([f"arrow{i}", f"flow{i}"])
        
        return id_keys


if __name__ == "__main__":
    generator = MovingFlowArrowGenerator()

    print("Generated default moving flow arrow:")
    print(generator.generate_svg())
    generator.save_to_file("_tmp/moving_flow_arrow_default.svg")

    configurations = [
        {"direction": "down", "color": "#3b82f6", "num_arrows": 3, "width": 60, "height": 120, "animation": "linear"},
        {"direction": "up", "color": "#ef4444", "num_arrows": 4, "width": 80, "height": 80, "animation": "ease-in"},
        {"direction": "left", "color": "#10b981", "num_arrows": 2, "stroke_width": 15, "width": 150, "height": 60},
        {"direction": "right", "color": "#f59e0b", "num_arrows": 6, "stroke_width": 5, "speed": 15.0, "width": 120, "height": 40}
    ]

    for config in configurations:
        gen = MovingFlowArrowGenerator(**config)
        file = f"_tmp/moving_flow_arrow_{config['direction']}_{config['num_arrows']}.svg"
        gen.save_to_file(file)
        print(f"Created {file} with {config}")
