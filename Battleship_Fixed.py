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

#global score variables and distance variables
high_score = 33
high_score_dist = 1

GOAL = 500

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
        return high_score,True
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

def acquire_rand():
    return rand.randint(0,GRID_SIZE-1),rand.randint(0,GRID_SIZE-1)

def setup_friendly():
    ship = FriendlyShip(grid_size=GRID_SIZE)
    cx,cy = FriendlyShip.prompt_friendly(GRID_SIZE)
    ship.place_center(cx,cy)
    return ship

def main():
    instructions()
    target = acquire_rand()
    current_score = 0
    ship = setup_friendly()

    fig, ax, im = init_display()
    ship.paint_on_grid(grid)
    update_display(fig, im)

    while current_score < GOAL:
        x = request_coor("x", target)
        y = request_coor("y", target)
        d = calculate_distance(x,y,*target)
        s,horm = calculate_score(d)
        update_grid(x,y,horm)

        ship.paint_on_grid(grid)
        update_display(fig, im)

        current_score += s
        scorekeepr(current_score)

        if ship.register_shot(x,y):
            print("You were hit!")
            ship.paint_on_grid(grid)
            update_display(fig,im)
            if ship.is_sunk():
                print("Your ship has been sunk!\n" \
                "You've let us down Commander.\n"
                "Try again next time!")
                raise SystemExit
        ship.paint_on_grid(grid)

    plt.ioff()
    plt.show()

if __name__ == '__main__':
    main()