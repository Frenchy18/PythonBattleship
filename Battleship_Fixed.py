## Program that calculates 2 random points and prompts a user to input coordinates. Scores based on hits or misses based on those coordinates.

#Next updates: Add iterable counter to limit number of shots allowed to ~10 before enemy ship finds us/destroys our ship
#              Add graphical interface that colors in blocks based on whether shots hit or miss to give graphical representation of shots fired
#              Add computer controlled opposition that slowly targets user ship, based on distance from target, randomly choose set of starting points
#                  and adjusts fire position slowly based on distance from user ship. User ship has certain amount of health as well.

#Import modules
import random as rand
import numpy as np
import matplotlib.pyplot as plt
from FriendlyShip import FriendlyShip


# Initialize grid size and channels
GRID_SIZE = 11
CHANNELS = 3

# Global score variables and distance variables
HIGH_SCORE = 33
high_score_dist = 1
GOAL = 99

# Distance shot to trigger AI Enemy
NEAR_TRIGGER_DIST = 3

# Colors
ENEMY_MISS_COLOR = (255,255,0)
PLAYER_HIT_COLOR = (255,0,0)
PLAYER_MISS_COLOR = (255)

# Create a grid using NumPy
grid = np.zeros((GRID_SIZE, GRID_SIZE, CHANNELS),np.uint8)


def instructions():
    """
    Gives the user instructions and instructs them how to continue.
    """

    print("Welcome  to the battlefield, Commander!\n" \
    "Enter target coordinates to fire on an unseeen enemy\n" \
    "Type -1 at any prompt to exit.\n")

def request_coor(axis, target):
    while True:
        user_inp = input(f"Enter {axis} (0..{GRID_SIZE-1}): ").strip().lower()
        if user_inp == "-1":
            raise SystemExit
        if user_inp == "cheat":
            tx, ty = target
            print(f"Cheat activated: Enemy at x={tx}, y={ty}. Cheater...")
            continue
        try:
            val = int(user_inp)
        except ValueError:
            print("Please use an integer.")
            continue

        if 0 <= val < GRID_SIZE:
            return val
        print(f"Value must be between 0 and {GRID_SIZE-1}.")
        
def scorekeepr(current_score):
    if current_score < GOAL:
        print(f"Current score: {current_score} / {GOAL}")
    else:
        print("Congratulations Commander! You defeated the enemy!")

def calculate_distance(user_x, user_y, target_x, target_y):
    """
    Uses distance formula to calculate the distance from the users shot 
    to the enemies ship.

    Returns: Shot distance from enemy
    """
    return ((user_x - target_x)**2 + (user_y - target_y)**2)**0.5

def calculate_score(distance):
    if distance <= high_score_dist:
        print("Bullseye Commander!")
        return HIGH_SCORE,True
    else:
        print("Miss!")
        return 0,False
    
def init_display():
    plt.ion()
    fig, ax = plt.subplots()
    im = ax.imshow(grid, vmin=0, vmax=255)
    ax.set_title("Battlefield")
    ax.set_xlabel("x -> (West)")
    ax.set_ylabel("y -> (North)")
    fig.canvas.draw_idle()
    plt.pause(0.001)
    return fig, ax, im

def update_display(fig, im):
    im.set_data(grid)
    fig.canvas.draw_idle()
    plt.pause(0.001)

def update_grid(user_x, user_y, horm):
    if horm == True:
        grid[user_y,user_x] = (255,0,0)
    else:
        grid[user_y,user_x] = 255

def enemy_init():
    """State: active flag, fired set, and known hit cells on friendly ship"""
    return {"active": False, "fired":set(), "known_hits":set()}

def enemy_neighbors_within1(x,y):
    for delta_x in (-1,0,1):
        for delta_y in (-1,0,1):
            if delta_x == 0 and delta_y == 0:
                continue
            neighbor_x, neighbor_y = x + delta_x, y + delta_y
            if 0 <= neighbor_x < GRID_SIZE and 0 <= neighbor_y < GRID_SIZE:
                yield (neighbor_x,neighbor_y)

def enemy_fire_random(state):
    """Picks a random not yet fired coordinate"""
    available_targets = [
        (x,y)
        for x in range(GRID_SIZE)
        for y in  range(GRID_SIZE)
        if (x,y) not in state["fired"]
    ]

    return rand.choice(available_targets) if available_targets else None

def enemy_pick_target(state):
    """If known hits, pick random neighbor tile otherwise random tile"""
    candidates = set()
    for (hit_x,hit_y) in state["known_hits"]:
        candidates.update(enemy_neighbors_within1(hit_x,hit_y))
    candidates = [c for c in candidates if c not in state["fired"]]
    if candidates:
        return rand.choice(candidates)
    return enemy_fire_random(state)

def enemy_fire(ship: FriendlyShip, state):
    """Enemy takes one shot. Returns (x,y, hit). Enemy misses show as yellow"""
    shot = enemy_pick_target(state) if state["known_hits"] else enemy_fire_random(state)
    if shot is None:
        return None, None, False
    x, y = shot
    state["fired"].add((x,y))

    if ship.register_shot(x,y):
        state["known_hits"].add((x,y))
        return x,y, True
    else:
        grid[y,x] = ENEMY_MISS_COLOR
        return x,y,False

def acquire_rand():
    return rand.randint(0,GRID_SIZE-1),rand.randint(0,GRID_SIZE-1)

def setup_friendly():
    ship = FriendlyShip(grid_size=GRID_SIZE)
    center_x,center_y = FriendlyShip.prompt_friendly(GRID_SIZE)
    ship.place_center(center_x,center_y)
    return ship

def main():
    instructions()
    target = acquire_rand()
    current_score = 0
    ship = setup_friendly()

    enemy = enemy_init()

    fig, ax, im = init_display()
    ship.paint_on_grid(grid)
    update_display(fig, im)

    while current_score < GOAL:
        x = request_coor("x", target)
        y = request_coor("y", target)
        d = calculate_distance(x,y,*target)
        points,horm = calculate_score(d)
        update_grid(x,y,horm)

        ship.paint_on_grid(grid)
        update_display(fig, im)

        current_score += points
        scorekeepr(current_score)

        if not enemy["active"] and (horm or d <= NEAR_TRIGGER_DIST):
            enemy["active"] = True
            print("Enemy has detected your presence!")
        if enemy["active"]:
            ex,ey,e_hit = enemy_fire(ship,enemy)
            if ex is not None:
                print(f"Enemy fires at ({ex},{ey}) - {"HIT!" if e_hit else 'miss.'}")

                ship.paint_on_grid(grid)
                update_display(fig, im)

                if ship.is_sunk():
                    print("Your ship has been sunk!\n" \
                    "You've let us down Commander.\n"
                    "Try again next time!")

    plt.ioff()
    plt.show()

if __name__ == '__main__':
    main()