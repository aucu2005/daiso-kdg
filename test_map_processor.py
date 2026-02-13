import cv2
import numpy as np
import os

# Adjust path to your local image
img_path = r"c:\Users\301\finalProject\daiso-category-search-dev-kdg\frontend\src\assets\images\map_b1.jpg"

if not os.path.exists(img_path):
    print(f"Image not found: {img_path}")
    exit()

img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
grid_size = 10

height, width = img.shape
grid_h = height // grid_size
grid_w = width // grid_size

print(f"Original: {width}x{height}, Grid: {grid_w}x{grid_h}")

# Threshold
_, binary = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
cv2.imwrite("debug_binary.jpg", binary) # Save to check what is white

# Create grid
grid = np.zeros((grid_h, grid_w), dtype=int)

for y in range(grid_h):
    row_str = ""
    for x in range(grid_w):
        cell = binary[y*grid_size:(y+1)*grid_size, x*grid_size:(x+1)*grid_size]
        white_pixels = cv2.countNonZero(cell)
        total_pixels = cell.shape[0] * cell.shape[1]
        
        # If < 90% white, obstacle
        if (white_pixels / total_pixels) < 0.9:
            grid[y, x] = 1
            row_str += "#"
        else:
            grid[y, x] = 0
            row_str += "."
    # print(row_str) # Too large to print all
    
# Check specific area (Digital Zone)
# User path went through center-bottom roughly.
# Let's sample a region.
print("Sampling center region:")
mid_y = grid_h // 2
mid_x = grid_w // 2
for y in range(mid_y - 10, mid_y + 10):
    row_str = ""
    for x in range(mid_x - 10, mid_x + 10):
        row_str += "#" if grid[y, x] == 1 else "."
    print(row_str)
