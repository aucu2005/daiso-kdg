import heapq
import math
from typing import List, Tuple, Optional, Dict

class MapNavigator:
    def __init__(self):
        self.grids: Dict[str, List[List[int]]] = {} # floor -> grid
        self.width: Dict[str, int] = {}
        self.width: Dict[str, int] = {}
        self.height: Dict[str, int] = {}
        self.distance_grids: Dict[str, List[List[float]]] = {} # floor -> distance map

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

    def get_neighbors(self, node: Tuple[int, int], floor: str, allow_diagonal: bool = True) -> List[Tuple[int, int]]:
        x, y = node
        neighbors = []
        
        # Directions
        if allow_diagonal:
            # 8-connected movement
            directions = [
                (0, 1), (0, -1), (1, 0), (-1, 0), # Straight
                (1, 1), (1, -1), (-1, 1), (-1, -1) # Diagonal
            ]
        else:
            # 4-connected (Manhattan)
            directions = [
                (0, 1), (0, -1), (1, 0), (-1, 0)
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

    def update_obstacles(self, floor: str, zones: List[Dict]):
        """
        Updates the grid with obstacles from zone definitions.
        Only considers zones with type='zone' (shelves/structures).
        Inflates obstacles slightly to separate path from walls.
        """
        if floor not in self.grids:
            print(f"⚠️ Grid for floor {floor} not loaded, cannot update obstacles.")
            return

        grid = self.grids[floor]
        h, w = self.height[floor], self.width[floor]
        
        # Inflation radius (in grid cells). 1 cell approx 10-20cm depending on scale.
        # grid_size=10 means 1px on grid = 10px on map. 
        # If map is 2000px wide, grid is 200.
        padding = 1 

        count = 0
        for zone in zones:
            if zone.get('type') != 'zone':
                continue
            
            try:
                # Parse rect: "left: 10%, top: 20%, width: 5%, height: 10%"
                # Format from DB might be JSON string or dict. 
                # In api.py it uses string replace.
                rect_str = zone['rect']
                # If it's a dict
                if isinstance(rect_str, dict):
                     r = rect_str
                else:
                    # Simple parsing if it's the specific format
                    import json
                    try:
                        r = json.loads(rect_str)
                    except:
                        # Fallback manual parsing
                        parts = rect_str.split(',')
                        r = {}
                        for p in parts:
                            k, v = p.split(':')
                            r[k.strip()] = v.strip()

                l_pct = float(str(r['left']).replace('%', ''))
                t_pct = float(str(r['top']).replace('%', ''))
                w_pct = float(str(r['width']).replace('%', ''))
                h_pct = float(str(r['height']).replace('%', ''))

                # Convert to grid coords
                x1 = int(l_pct / 100 * w)
                y1 = int(t_pct / 100 * h)
                x2 = int((l_pct + w_pct) / 100 * w)
                y2 = int((t_pct + h_pct) / 100 * h)

                # Clamp
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(w, x2 + padding)
                y2 = min(h, y2 + padding)

                # Mark as obstacle
                for y in range(y1, y2):
                    for x in range(x1, x2):
                        grid[y][x] = 1
                count += 1
            except Exception as e:
                print(f"⚠️ Failed to process zone {zone.get('name')}: {e}")
        
        # Calculate distance transform (Distance Map) for centering
        # BFS from all obstacles to find distance to nearest obstacle
        dist_grid = [[float('inf')] * w for _ in range(h)]
        queue = []
        
        # Initialize queue with all obstacles
        for y in range(h):
            for x in range(w):
                if grid[y][x] == 1:
                    dist_grid[y][x] = 0
                    queue.append((x, y))
        
        # BFS
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        head = 0
        while head < len(queue):
            cx, cy = queue[head]
            head += 1
            
            curr_dist = dist_grid[cy][cx]
            
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if dist_grid[ny][nx] == float('inf'):
                        dist_grid[ny][nx] = curr_dist + 1
                        queue.append((nx, ny))
                        
        self.distance_grids[floor] = dist_grid
        print(f"✅ Updated grid for {floor} with {count} obstacles and distance map")

    def get_nearest_walkable(self, floor: str, node: Tuple[int, int], max_radius: int = 30) -> Optional[Tuple[int, int]]:
        """Finds the nearest walkable node using BFS"""
        grid = self.grids.get(floor)
        if not grid: return None
        
        h, w = self.height[floor], self.width[floor]
        x, y = node
        
        # If valid and walkable, return itself
        if 0 <= x < w and 0 <= y < h and grid[y][x] == 0:
            return node
            
        # BFS
        queue = [(x, y)]
        visited = set([(x, y)])
        
        # Directions: Start with cardinal, then diagonal
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        while queue:
            cx, cy = queue.pop(0)
            
            # Check if this node is walkable
            if 0 <= cx < w and 0 <= cy < h and grid[cy][cx] == 0:
                print(f"DEBUG: Moved node {node} -> {(cx, cy)} (nearest walkable)")
                return (cx, cy)
            
            # Limit radius roughly
            if abs(cx - x) > max_radius or abs(cy - y) > max_radius:
                continue

            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        
        return None

    def find_path(self, floor: str, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Finds path from start (x, y) to end (x, y) on the given floor using A*.
        Returns list of (x, y) coordinates.
        """
        if floor not in self.grids:
            print(f"DEBUG: Grid for {floor} missing")
            raise ValueError(f"Grid for floor {floor} not loaded.")
            
        # Ensure start/end are walkable
        start_node = self.get_nearest_walkable(floor, start)
        end_node = self.get_nearest_walkable(floor, end)
        
        if not start_node:
            print("DEBUG: Start node is in obstacle and no walkable neighbor found")
            return None
        if not end_node:
            print("DEBUG: End node is in obstacle and no walkable neighbor found")
            return None
        
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
            
            # Use allow_diagonal=False for straighter paths
            for neighbor in self.get_neighbors(current, floor, allow_diagonal=False):
                # Distance calculation
                # Straight move cost = 10, Diagonal = 14
                dx = abs(neighbor[0] - current[0])
                dy = abs(neighbor[1] - current[1])
                move_cost = 14 if (dx + dy) == 2 else 10
                
                tentative_g_score = g_score[current] + move_cost
                
                # Add penalty for being close to obstacles (Centering)
                if floor in self.distance_grids:
                    dist = self.distance_grids[floor][neighbor[1]][neighbor[0]]
                    # Max distance heuristic: e.g. 20. 
                    # If dist is small (close to wall), penalty is high.
                    # If dist is large (center), penalty is low.
                    # Penalty = (Max - dist) * weight
                    # We want to encourage high dist. 
                    # Let's say max useful dist is 10.
                    max_d = 10.0
                    capped_dist = min(dist, max_d)
                    penalty = (max_d - capped_dist) * 2.0 # Weight 2.0
                    tentative_g_score += penalty

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f = tentative_g_score + self.heuristic(neighbor, end_node) * 10
                    f_score[neighbor] = f
                    heapq.heappush(open_set, (f, neighbor))
                    
        return None # No path found

