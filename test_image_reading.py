from PIL import Image
import os
import numpy as np

img_path = r"c:\Users\301\finalProject\daiso-category-search-dev-kdg\frontend\src\assets\images\map_b1.jpg"

if not os.path.exists(img_path):
    print(f"Image not found: {img_path}")
    exit()

try:
    print(f"Opening image: {img_path}")
    img = Image.open(img_path).convert('L') # Grayscale
    width, height = img.size
    print(f"Image loaded: {width}x{height}")
    
    # Convert to numpy array to simulate processing
    arr = np.array(img)
    print(f"Mean pixel value: {np.mean(arr)}")
    
    # Threshold check
    binary = arr > 200 # Walkable
    walkable_ratio = np.sum(binary) / binary.size
    print(f"Walkable area ratio: {walkable_ratio:.2f}")

except Exception as e:
    print(f"Error: {e}")
