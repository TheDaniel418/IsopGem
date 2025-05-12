#!/usr/bin/env python3
"""
Create a Golden Ratio icon for the Golden Mean Explorer
"""

import math
import os

from PIL import Image, ImageDraw

# Make sure the directory exists
os.makedirs("/home/daniel/Desktop/IsopGem/assets/geometry", exist_ok=True)

# Create a new image with a white background
size = (256, 256)
img = Image.new("RGBA", size, (255, 255, 255, 0))  # Transparent background
draw = ImageDraw.Draw(img)

# Calculate the golden ratio
phi = (1 + math.sqrt(5)) / 2

# Define the center of the image
center_x, center_y = size[0] // 2, size[1] // 2

# Define colors
gold_color = (255, 215, 0, 255)  # Gold color
border_color = (139, 69, 19, 255)  # Brown color

# Create the golden rectangle
width = 180
height = width / phi
rect_x = center_x - width / 2
rect_y = center_y - height / 2

# Draw the golden rectangle with thick borders
border_width = 3
draw.rectangle(
    (rect_x, rect_y, rect_x + width, rect_y + height),
    outline=border_color,
    width=border_width,
)

# Draw the square within the rectangle
square_size = height
draw.rectangle(
    (rect_x, rect_y, rect_x + square_size, rect_y + square_size),
    outline=border_color,
    width=border_width,
)

# Draw the remaining rectangle
draw.rectangle(
    (rect_x + square_size, rect_y, rect_x + width, rect_y + square_size),
    outline=border_color,
    width=border_width,
)

# Draw the golden spiral using arcs
spiral_x, spiral_y = rect_x + square_size, rect_y + square_size
spiral_size = square_size

# First arc (largest)
bbox = (rect_x, rect_y, rect_x + square_size, rect_y + square_size)
draw.arc(bbox, 180, 270, fill=gold_color, width=border_width)

# Second arc
spiral_size = width - square_size
bbox = (
    rect_x + square_size - spiral_size,
    rect_y + square_size,
    rect_x + square_size,
    rect_y + square_size + spiral_size,
)
draw.arc(bbox, 270, 360, fill=gold_color, width=border_width)

# Third arc (smaller)
spiral_size = square_size - (width - square_size)
bbox = (
    rect_x + square_size - spiral_size,
    rect_y + square_size,
    rect_x + square_size,
    rect_y + square_size + spiral_size,
)
draw.arc(bbox, 0, 90, fill=gold_color, width=border_width)

# Fourth arc (smallest)
spiral_size = width - square_size - (square_size - (width - square_size))
bbox = (
    rect_x + square_size - spiral_size,
    rect_y + square_size - spiral_size,
    rect_x + square_size,
    rect_y + square_size,
)
draw.arc(bbox, 90, 180, fill=gold_color, width=border_width)

# Save the image with verbose output
output_path = "/home/daniel/Desktop/IsopGem/assets/geometry/golden_ratio.png"
try:
    img.save(output_path)
    print(f"Golden ratio icon created at {output_path}")
    print(f"File exists check: {os.path.exists(output_path)}")
except Exception as e:
    print(f"Error saving image: {e}")
    # Try an alternative location
    try:
        img.save("golden_ratio.png")
        print("Saved to current directory instead")
    except Exception as e:
        print(f"Error saving to current directory: {e}")
