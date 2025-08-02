"""
Base class for arrow generators.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
import re
import uuid


class AnimatedArrowGeneratorBase(ABC):
    """
    Abstract base class for all animated arrow generators.
    
    Provides common functionality and interface for arrow generation.
    """
    
    def __init__(
        self,
        color: str = "#2563eb",
        stroke_width: int = 10,
        width: int = 100,
        height: int = 100,
        speed_in_px_per_second: float = None,
        speed_in_duration_seconds: float = None,
        num_arrows: int = 4,
    ):
        self.color = color
        self.width = width
        self.height = height
        self.num_arrows = max(1, num_arrows)
        self.stroke_width = max(2, stroke_width)
        
        if (speed_in_px_per_second is None) and (speed_in_duration_seconds is None):
            raise ValueError("One speed option must be defined: speed_in_px_per_second or speed_in_duration_seconds")
        if (speed_in_px_per_second is not None) and (speed_in_duration_seconds is not None):
            raise ValueError("Only one speed option can be defined: speed_in_px_per_second or speed_in_duration_seconds")

        self.speed_in_px_per_second = speed_in_px_per_second
        self._speed_in_duration_seconds = speed_in_duration_seconds

    @property
    def speed_in_duration_seconds(self) -> float:
        """Get the speed in duration seconds, calculating it if needed."""
        if self._speed_in_duration_seconds is not None:
            return self._speed_in_duration_seconds
        else:
            # Calculate from speed_in_px_per_second
            transform_distance = self._get_transform_distance()
            return transform_distance / self.speed_in_px_per_second

    @abstractmethod
    def _generate_arrow_elements(self) -> str:
        """Generate the arrow elements for the SVG."""
        pass
    
    @abstractmethod
    def _generate_animations(self) -> str:
        """Generate the CSS animations for the SVG."""
        pass
    
    @abstractmethod
    def _get_transform_distance(self) -> float:
        """Get the transform distance for animation calculations."""
        pass
    
    @abstractmethod
    def _get_unique_id_keys(self) -> list[str]:
        """Get the list of ID keys that need to be made unique for this generator."""
        pass
    
    def _calculate_animation_duration(self) -> float:
        """Calculate the appropriate animation duration based on speed options."""
        return self.speed_in_duration_seconds
    
    def _apply_unique_suffix(self, svg: str, suffix: str, id_keys: list[str]) -> str:
        """
        Apply a unique suffix to SVG IDs, classes, and references to avoid collisions.
        
        Args:
            svg: The SVG string to process
            suffix: The suffix to append to identifiers  
            id_keys: List of base identifiers to make unique
            
        Returns:
            Modified SVG string with unique identifiers
        """
        modified_svg = svg
        
        for base_id in id_keys:
            unique_id = f"{base_id}-{suffix}"
            
            # Replace ID definitions: id="baseId" -> id="baseId-suffix"
            modified_svg = re.sub(
                rf'id="{re.escape(base_id)}"',
                f'id="{unique_id}"',
                modified_svg
            )
            
            # Replace URL references: url(#baseId) -> url(#baseId-suffix)
            modified_svg = re.sub(
                rf'url\(#{re.escape(base_id)}\)',
                f'url(#{unique_id})',
                modified_svg
            )
            
            # Replace CSS class definitions: .baseId -> .baseId-suffix
            modified_svg = re.sub(
                rf'\.{re.escape(base_id)}(?=\s*\{{)',
                f'.{unique_id}',
                modified_svg
            )
            
            # Replace CSS class usage in HTML: class="baseId" -> class="baseId-suffix"
            # Handle both single class and multiple classes in class attribute
            modified_svg = re.sub(
                rf'class="([^"]*?)(\b{re.escape(base_id)}\b)([^"]*?)"',
                rf'class="\1{unique_id}\3"',
                modified_svg
            )
            
            # Replace @keyframes names: @keyframes baseId -> @keyframes baseId-suffix
            modified_svg = re.sub(
                rf'@keyframes\s+{re.escape(base_id)}(?=\s*\{{)',
                f'@keyframes {unique_id}',
                modified_svg
            )
            
            # Replace animation property references: animation: baseId -> animation: baseId-suffix
            modified_svg = re.sub(
                rf'animation:\s+{re.escape(base_id)}(?=\s)',
                f'animation: {unique_id}',
                modified_svg
            )
        
        return modified_svg
    
    def generate_svg(self, unique_id: Union[bool, str] = True) -> str:
        """
        Generate the complete SVG string.
        
        Args:
            unique_id: Controls ID uniqueness behavior:
                - False: Use default IDs (may cause collisions)
                - True: Generate random suffix for unique IDs
                - str: Use provided string as suffix for IDs
                
        Returns:
            SVG string with optionally unique identifiers
        """
        clip_bounds = self._get_clip_bounds()
        animations = self._generate_animations()
        arrow_elements = self._generate_arrow_elements()
        
        svg = f"""
        <svg width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <clipPath id="arrowClip">
              <rect x="{clip_bounds['x']}" y="{clip_bounds['y']}" width="{clip_bounds['width']}" height="{clip_bounds['height']}"/>
            </clipPath>
            {self._generate_gradient_defs() if hasattr(self, '_generate_gradient_defs') else ''}
          </defs>
        
          <style>
            .arrow {{
              stroke: {self.color};
              stroke-width: {self.stroke_width};
              stroke-linecap: round;
              stroke-linejoin: round;
              fill: none;
            }}
            
            {self._generate_arrow_classes() if hasattr(self, '_generate_arrow_classes') else ''}
            
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
    
    def _get_clip_bounds(self) -> Dict[str, int]:
        """Get the clipping bounds for the SVG."""
        # Use full canvas area - no margins
        return {
            "x": 0,
            "y": 0,
            "width": self.width,
            "height": self.height
        }
    
    def save_to_file(self, file_path: str, unique_id: Union[bool, str] = True) -> None:
        """Save the generated SVG to a file."""
        svg_content = self.generate_svg(unique_id=unique_id)
        with open(file_path, 'w') as file:
            file.write(svg_content)