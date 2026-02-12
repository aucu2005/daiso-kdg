import sys
import os
import unittest

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.navigation.pathfinder import MapNavigator

class TestMapNavigator(unittest.TestCase):
    def setUp(self):
        self.navigator = MapNavigator()
        # Create a simple 5x5 grid
        # 0 0 0 0 0
        # 0 1 1 1 0
        # 0 0 0 1 0
        # 0 1 0 0 0
        # 0 0 0 0 0
        self.grid = [
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        self.navigator.load_grid("test_floor", self.grid)

    def test_simple_path(self):
        start = (0, 0)
        end = (4, 4)
        path = self.navigator.find_path("test_floor", start, end)
        self.assertIsNotNone(path)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], end)
        print(f"Path found: {path}")

    def test_obstacle_avoidance(self):
        start = (0, 2)
        end = (2, 2) 
        # Direct path (1, 2) is blocked by (1, 2) being 0... wait row 2 col 1 is 0.
        # row 2: 0 0 0 1 0
        # index: 0 1 2 3 4
        # (0, 2) -> (1, 2) -> (2, 2) all 0. 
        
        # Let's test going through obstacle
        # Start (2, 0), End (2, 4)
        # Blocked by row 1 col 2 (value 1)
        # Path should go around.
        
        start = (2, 0)
        end = (2, 3) # (2, 4) is 0. (2, 3) is 0.
        # But (2, 1) is 1.
        
        path = self.navigator.find_path("test_floor", start, end)
        self.assertIsNotNone(path)
        
        # Verify no obstacles in path
        for x, y in path:
            self.assertEqual(self.grid[y][x], 0, f"Path goes through obstacle at {x},{y}")

if __name__ == '__main__':
    unittest.main()
