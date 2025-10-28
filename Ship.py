from typing import Iterable, List, Set, Tuple, Literal, Optional
import random as rand

Coord = Tuple[int, int]
Orientation = Literal["V","H"]

class Ship:
    """
    3-cell ship with orientation either "V" (Vertical) or "H" (Horizontal)
    Sinks after 3 hits, Usable for friendly or enemy ships.
    """

    def __init__(self, grid_size:int, length: int=3, orientation: Orientation = "V"):
        if length != 3:
            raise ValueError("Requires a minimum length of 3.")
        if grid_size < 3:
            raise ValueError("grid_size must be at least 3.")
        self.grid_size = grid_size
        self.length = length
        self.orientation: Orientation = orientation
        self.cells: Set[Coord] = set()
        self.hits: Set[Coord] = set()

    def _cells_from_center(self, x: int, y: int, orientation: Orientation):
        if orientation == "V":
            if not (0 <= x < self.grid_size and 1 <= y <= self.grid_size -2):
                raise ValueError(f"For vertical placement, y must be in [1, {self.grid_size -2}].")
            return {(x,y-1),(x,y),(x,y+1)}
        else:
            if not (1 <= x <= self.grid_size -2 and 0 <= y < self.grid_size):
                raise ValueError(f"Center x must be in [1, {self.grid_size -2}] for horizontal ships.")
            return {(x-1,y),(x,y),(x+1,y)}

    def place_center(self, x, y, orientation: Optional[Orientation] = None):
        ori = orientation or self.orientation
        cells = self._cells_from_center(x,y,ori)
        self.orientation = ori
        self.cells = cells
        self.hits.clear()

    def register_shot(self,x,y):
        shot = (x,y)
        if shot in self.cells:
            self.hits.add(shot)
            return True
        return False
    
    def is_sunk(self):
        return len(self.hits) == self.length
    
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

    def _normalize_orientation(text):
        t = (text or "").strip().lower()
        if t in ("v", "vert", "vertical"):
            return "V"
        if t in ("h","horiz","horizontal"):
            return "H"
        raise ValueError("Please enter V or H (Vertical/Horizontal)")

    def prompt_friendly(grid_size):
        """
        Prompt for vertical ship center
        y must be 1 to grid_size -2 so ship fits vertically
        """
        while True:
            ori_inp = input("Choose orientation[V/H]: ").strip()
            try:
                ori = Ship._normalize_orientation(ori_inp)
                break
            except ValueError as e:
                print(e)

        if ori == "V":
            prompt_x = f"Choose ship center X (0..{grid_size-1}): "
            prompt_y = f"Choose ship center Y (1..{grid_size-2}): "
            x_ok = lambda x: 0 <= x <= grid_size -1
            y_ok = lambda y: 1 <= y <= grid_size -2
        else:
            prompt_x = f"Choose ship center X (1..{grid_size-2}): "
            prompt_y = f"Choose ship center Y (0..{grid_size-1}): "
            x_ok = lambda x: 1 <= x <= grid_size -2
            y_ok = lambda y: 0 <= y <= grid_size -1

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
            if x_ok(x) and y_ok(y):
                return x,y, ori
            print("Center to close to edge and is out of bounds. Try again.")

    def random_valid_center(grid_size, orientation: Orientation):
        if orientation == "V":
            return rand.randint(0,grid_size-1),rand.randint(1,grid_size-2)
        else:
            return rand.randint(1,grid_size-2),rand.randint(0,grid_size -1)
    
    @classmethod
    def spawn_no_overlap(
            cls,
            grid_size: int,
            forbidden: Iterable[Coord] = (),
            orientations: Iterable[Orientation] = ("V","H"),
            max_tries: int = 10000,
    ):
        blocked = set(forbidden)
        for _ in range(max_tries):
            ori = rand.choice(tuple(orientations))
            cx,cy = cls.random_valid_center(grid_size,ori)
            try:
                cells = cls(grid_size,orientation=ori)._cells_from_center(cx,cy,ori)
            except ValueError:
                continue
            if cells.isdisjoint(blocked):
                s = cls(grid_size,orientation=ori)
                s.place_center(cx,cy,ori)
                return s
            
        raise RuntimeError("Could not place ship without overlap after max tries")
    
    @classmethod
    def place_many_no_overlap(
            cls,
            grid_size,
            count: int,
            forbidden: Iterable[Coord] = (),
            orientations: Iterable[Orientation] = ("V","H"),
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
