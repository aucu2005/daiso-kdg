import cv2
import numpy as np
import json
import os

class MapProcessor:
    def __init__(self, image_path: str, grid_size: int = 10):
        self.image_path = image_path
        self.grid_size = grid_size
        self.grid = None
        self.height = 0
        self.width = 0
        self.map_img = None

    def load_and_process(self):
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"Image not found: {self.image_path}")

        # Load image in grayscale
        self.map_img = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
        if self.map_img is None:
            raise ValueError(f"Failed to load image: {self.image_path}")

        self.height, self.width = self.map_img.shape
        print(f"Loaded map: {self.width}x{self.height}")

        # Binarize: Keep white areas as walkable (val=255), black/gray as obstacles (val=0)
        # Assuming white/light gray background is walkable.
        # Threshold: anything lighter than 200 is walkable (255), else obstacle (0).
        # Inverted logic for grid: 0 = walkable, 1 = obstacle.
        
        # Simple thresholding
        _, binary = cv2.threshold(self.map_img, 200, 255, cv2.THRESH_BINARY)
        
        # Create grid
        grid_h = self.height // self.grid_size
        grid_w = self.width // self.grid_size
        
        self.grid = np.zeros((grid_h, grid_w), dtype=int)
        
        for y in range(grid_h):
            for x in range(grid_w):
                # Extract cell
                cell = binary[y*self.grid_size:(y+1)*self.grid_size, 
                              x*self.grid_size:(x+1)*self.grid_size]
                
                # If cell contains significant black pixels, mark as obstacle
                # "Significant" could be > 10% black pixels?
                # Or if *any* pixel is an obstacle? To be safe, maybe > 30%?
                # Obstacle pixel value is 0 (black) in 'binary' image from threshold.
                # Walkable is 255 (white).
                
                # Count non-zero (white pixels)
                white_pixels = cv2.countNonZero(cell)
                total_pixels = cell.shape[0] * cell.shape[1]
                
                # If white ratio is low, it's an obstacle.
                # obstacle if < 90% white? meaning > 10% black.
                if (white_pixels / total_pixels) < 0.9:
                    self.grid[y, x] = 1 # Obstacle
                else:
                    self.grid[y, x] = 0 # Walkable

        print(f"Grid generated: {grid_w}x{grid_h}")
        return self.grid

    def save_grid(self, output_path: str):
        if self.grid is None:
            raise ValueError("Grid not generated. Call load_and_process() first.")
        
        # Save as JSON
        data = {
            "width": self.width,
            "height": self.height,
            "grid_size": self.grid_size,
            "grid_cols": self.grid.shape[1],
            "grid_rows": self.grid.shape[0],
            "grid_data": self.grid.tolist()
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f)
        print(f"Grid saved to {output_path}")

if __name__ == "__main__":
    # Test
    # Adjust path as needed for local testing
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    img_path = os.path.join(base_dir, "frontend", "src", "assets", "images", "map_b1.jpg")
    
    if os.path.exists(img_path):
        processor = MapProcessor(img_path, grid_size=20)
        grid = processor.load_and_process()
        processor.save_grid("grid_b1.json")
    else:
        print(f"Test image not found at {img_path}")
