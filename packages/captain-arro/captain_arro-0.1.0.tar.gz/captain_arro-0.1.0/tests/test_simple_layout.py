#!/usr/bin/env python3
"""Test the correct constraint-based layout logic"""

def calculate_layout(canvas_width, canvas_height, num_arrows, center_gap_ratio, direction):
    """SIMPLE constraint-based layout - work backwards from constraints"""
    arrows_per_side = num_arrows // 2
    
    if direction == "horizontal":
        # 1. Arrow size: use most of perpendicular space (height)
        arrow_height = int(canvas_height * 0.8)  # 80% of height
        
        # 2. Center gap: fixed ratio 
        center_gap = int(canvas_width * center_gap_ratio)
        
        # 3. Available space per side
        available_width_per_side = (canvas_width - center_gap) // 2
        
        # 4. Arrow width: constrained by space per arrow
        arrow_width = available_width_per_side // max(arrows_per_side, 1)
        
        # 5. Positions: outermost arrow tip exactly at edge
        positions = []
        center_x = canvas_width // 2
        left_edge = center_x - center_gap // 2
        
        for i in range(arrows_per_side):
            # Outermost arrow (i=arrows_per_side-1) has its right tip at left_edge
            # So its center is at left_edge - arrow_width//2
            arrow_center = left_edge - (arrow_width // 2) - i * arrow_width
            positions.append(arrow_center)
            
        return {
            "arrow_width": arrow_width,
            "arrow_height": arrow_height,
            "left_positions": positions,
            "bounds_check": f"Leftmost tip: {min(positions) - arrow_width//2}, rightmost: {max(positions) + arrow_width//2}"
        }
    
# Test cases
test_cases = [
    (300, 150, 6, 0.2, "horizontal"),  # Basic case
    (250, 200, 4, 0.2, "horizontal"),  # Teal case  
    (100, 200, 4, 0.2, "vertical"),   # Pink case
]

for width, height, arrows, gap_ratio, direction in test_cases:
    print(f"\nCanvas: {width}x{height}, {arrows} arrows, {direction}")
    layout = calculate_layout(width, height, arrows, gap_ratio, direction)
    print(f"Arrow size: {layout['arrow_width']}x{layout['arrow_height']}")
    print(f"Positions: {layout['left_positions']}")
    print(f"Bounds: {layout['bounds_check']}")