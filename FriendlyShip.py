from dataclasses import dataclass, field
from typing import Iterable, List, Set, Tuple
import random as rand

Coord = Tuple[int, int]

class Ship:

    def __init__(self, grid_size):
        if grid_size < 3:
            raise ValueError("grid_size must be at least 3.")
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

    def random_valid_center(grid_size):
        x,y = rand.randint(0,grid_size-1),rand.randint(1,grid_size-2)

        return x,y
    
    def spawn_no_overlap(
            cls,
            grid_size: int,
            forbidden: Iterable[Coord] = (),
            max_tries: int = 10000,
    ):
        blocked = set(forbidden)
        for _ in range(max_tries):
            x,y = cls.random_valid_center(grid_size)
            candidate = {(x,y-1),(x,y),(x,y+1)}
            if candidate.isdisjoint(blocked):
                ship = cls(grid_size)
                ship.place_center(x,y)
                return ship
            
        raise RuntimeError("Could not place ship without overlap after max tries")
    
    def place_many_no_overlap(
            cls,
            grid_size,
            count: int,
            forbidden: Iterable[Coord] = (),
            max_tries: int = 10000,
    ):
        ships: List[Ship] = []
        blocked: Set[Coord] = set(forbidden)

        for _ in range(count):
            ship = cls.spawn_no_overlap(grid_size,blocked,max_tries)
            ships.append(ship)
            blocked |= ship.cells

        return ships
    
EnemyShip = Ship