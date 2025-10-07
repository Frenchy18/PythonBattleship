from dataclasses import dataclass, field
from typing import Set, Tuple

Coord = Tuple[int, int]

class FriendlyShip:

    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.cells: Set[Coord] = set()
        self.hits: Set[Coord] = set()

    def place_center(self, x, y):
        if not (0 <= x < self.grid_size):
            raise ValueError(f"x must be in [0, {self.grid_size}]")
        
        if not (1 <= y <= self.grid_size -2):
            raise ValueError(f"y must be in [1, {self.grid_size}]")
        
        self.cells = {(x,y-1),(x,y),(x,y+1)}
        self.hits.clear()

    def register_shot(self,x,y):
        shot = (x,y)
        if shot in self.cells:
            self.hits.add(shot)
            return True
        return False
    
    def is_sunk(self):
        return len(self.hits) == 3
    
    def remaining_cells(self):
        return self.cells - self.hits
    
    def paint_on_grid(
            self,
            grid,
            color_alive=(0,255,255),
            color_hit=(255,165,0),
            color_sunk=(128,0,128),
    ):
        if not self.cells:
            return
        if self.is_sunk():
            for (x,y) in self.cells:
                grid[y,x] = color_sunk
        else:
            for (x,y) in self.cells:
                grid[y,x] = color_alive
            for (x,y) in self.hits:
                grid[y,x] = color_hit

    def prompt_friendly(grid_size):
        while True:
            inp_x = input(f"Choose ship center X (0..{grid_size-1}): ").strip()
            inp_y = input(f"Choose ship center Y (0..{grid_size-1}: ").strip()
            if inp_x == "-1" or inp_y == "-1":
                raise SystemExit
            
            try:
                x = int(inp_x); y=int(inp_y)
            except ValueError:
                print("Please enter integers.")
                continue
            if 0 <= x < grid_size and 1 <= y <= grid_size -2:
                return x,y
            print("Center to close to edge and is out of bounds. Try again.")
