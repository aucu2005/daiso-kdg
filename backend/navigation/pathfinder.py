import heapq
import math
from typing import List, Tuple, Optional, Dict

class MapNavigator:
    def __init__(self):
        self.grids: Dict[str, List[List[int]]] = {} # floor -> grid
        self.width: Dict[str, int] = {}
        self.height: Dict[str, int] = {}

    def load_grid(self, floor: str, grid_data: List[List[int]]):
        """Loads a grid for a specific floor. 0=walkable, 1=obstacle."""
        self.grids[floor] = grid_data
        self.height[floor] = len(grid_data)
        self.width[floor] = len(grid_data[0]) if grid_data else 0
        print(f"Loaded grid for {floor}: {self.width[floor]}x{self.height[floor]}")

    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        # Manhattan distance
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
        # Euclidean: return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def get_neighbors(self, node: Tuple[int, int], floor: str) -> List[Tuple[int, int]]:
        x, y = node
        neighbors = []
        # 8-connected movement (including diagonals)
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0), # Straight
            (1, 1), (1, -1), (-1, 1), (-1, -1) # Diagonal
        ]
        
        grid = self.grids.get(floor)
        if not grid:
            return []

        h, w = self.height[floor], self.width[floor]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            # Check bounds
            if 0 <= nx < w and 0 <= ny < h:
                # Check obstacle (0=walkable, 1=obstacle)
                if grid[ny][nx] == 0:
                    neighbors.append((nx, ny))
                    
        return neighbors

    def find_path(self, floor: str, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Finds path from start (x, y) to end (x, y) on the given floor using A*.
        Returns list of (x, y) coordinates.
        """
        if floor not in self.grids:
            raise ValueError(f"Grid for floor {floor} not loaded.")
            
        start_node = tuple(start)
        end_node = tuple(end)
        
        # Priority queue: (f_score, node)
        open_set = []
        heapq.heappush(open_set, (0, start_node))
        
        came_from = {}
        
        # g_score[node] is cost from start to node
        g_score = {start_node: 0}
        
        # f_score[node] is g_score + heuristic
        f_score = {start_node: self.heuristic(start_node, end_node)}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == end_node:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_node)
                path.reverse()
                return path
            
            for neighbor in self.get_neighbors(current, floor):
                # Distance calculation
                # Straight move cost = 10, Diagonal = 14
                dx = abs(neighbor[0] - current[0])
                dy = abs(neighbor[1] - current[1])
                move_cost = 14 if (dx + dy) == 2 else 10
                
                tentative_g_score = g_score[current] + move_cost
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f = tentative_g_score + self.heuristic(neighbor, end_node) * 10 # Scale heuristic validation
                    f_score[neighbor] = f
                    heapq.heappush(open_set, (f, neighbor))
                    
        return None # No path found

