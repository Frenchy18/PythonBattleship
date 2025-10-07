## Program that calculates 2 random points and prompts a user to input coordinates. Scores based on hits or misses based on those coordinates.

#Next updates: Add iterable counter to limit number of shots allowed to ~10 before enemy ship finds us/destroys our ship
#              Add graphical interface that colors in blocks based on whether shots hit or miss to give graphical representation of shots fired
#              Add computer controlled opposition that slowly targets user ship, based on distance from target, randomly choose set of starting points
#                  and adjusts fire position slowly based on distance from user ship. User ship has certain amount of health as well.

#Import modules
import random as rand
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.widgets import TextBox
from FriendlyShip import FriendlyShip


# Initialize grid size and channels
GRID_SIZE = 11
CHANNELS = 3

# Global score variables and distance variables
HIGH_SCORE = 33
HIGH_SCORE_DIST = 1
GOAL = 99

# Distance shot to trigger AI Enemy
NEAR_TRIGGER_DIST = 3

# Color-Blind friendly Colors
CBF_BLUE = (0,114,178)
CBF_ORANGE = (230, 159, 0)
CBF_SKY = (86, 180, 233)
CBF_GREEN = (0, 158, 115)
CBF_YELLOW = (240, 228, 66)
CBF_VERMILLION = (213, 94, 0)
CBF_PURPLE = (204, 121, 167)
CBF_BLACK = (0,0,0)
CBF_GRAY = (200, 200, 200)


ENEMY_MISS_COLOR = CBF_ORANGE
PLAYER_HIT_COLOR = CBF_VERMILLION
PLAYER_MISS_COLOR = CBF_GRAY
FRIENDLY_ALIVE = CBF_BLUE
FRIENDLY_HIT = CBF_PURPLE
FRIENDLY_SUNK = CBF_BLACK


# Create a grid using NumPy
grid = np.zeros((GRID_SIZE, GRID_SIZE, CHANNELS),np.uint8)


def instructions():
    """
    Gives the user instructions and instructs them how to continue.
    """
    max_col = chr(ord('A') + GRID_SIZE-1)

    print(
        "\n=== How to Play === \n"
        f"* Enter grid coordinates in Battleship style, e.g., B7 or K{GRID_SIZE}.\n"
        f"* Columns:  A..{max_col} Rows: 1..{GRID_SIZE}\n"
        "* Type 'help' anytime to re-show these instructions. \n"
        "* Type 'quit' or -1 to exit. \n"
    )

def _col_letter_to_index(letter):
    letter = letter.upper()
    col = ord(letter) - ord('A')
    if 0 <= col < GRID_SIZE:
        return col
    raise ValueError("Column out of bounds")

def _to_battleship_string(x,y):
    return f"{chr(ord('A') + x)}{y+1}"

def parse_battleship_coord(token):
    token = token.strip().replace(" ","").replace(",","")
    if not token:
        raise ValueError("Empty coordinate")
    
    col_char = token[0]
    row_str = token[1:]
    if not col_char.isalpha() or not row_str.isdigit():
        raise ValueError("Use format like B7 or K11")
    
    x = _col_letter_to_index(col_char)
    row = int(row_str)
    if not (1 <= row <= GRID_SIZE):
        raise ValueError("Row out of bounds")
    y = row - 1
    return x,y

def request_coor(target):
    max_col = chr(ord('A') + GRID_SIZE-1)

    while True:
        user_inp = input(
            f"Enter coordinate (A1..{max_col}{GRID_SIZE}) "
            "[help/quit]: "
        ).strip().lower()

        if user_inp in ('-1','quit','exit'):
            raise SystemExit
        if user_inp in ('help','h','?'):
            instructions()
            continue
        if user_inp == "cheat":
            tx, ty = target
            print(f"Cheat activated: Enemy at {_to_battleship_string(tx,ty)}. Cheater...")
            continue
        try:
           return parse_battleship_coord(user_inp)
        except ValueError as e:
            print(f"Invalid coordinate: {e}. Try B7 or {max_col}{GRID_SIZE}")
        
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
    if distance <= HIGH_SCORE_DIST:
        print("Bullseye Commander!")
        return HIGH_SCORE,True
    else:
        print("Miss!")
        return 0,False
    
#----------- Display -----------------
def apply_axis_styling(ax):
    ax.set_xticks(np.arange(GRID_SIZE))
    ax.set_yticks(np.arange(GRID_SIZE))
    ax.set_xticklabels([chr(ord('A')+i) for i in range(GRID_SIZE)])
    ax.set_yticklabels([str(i+1) for i in range(GRID_SIZE)])
    ax.set_xticks(np.arange(-0.5,GRID_SIZE,1), minor=True)
    ax.set_yticks(np.arange(-0.5,GRID_SIZE,1), minor=True)
    ax.grid(which='minor',color=(120/255,120/255,120/255),linestyle='-', linewidth=0.5)
    ax.tick_params(which='both',length=0)

def set_titles(fig,ax,score):
    title = f"Battlefield - Score: {score}/{GOAL}"
    ax.set_title(title)
    try:
        fig.canvas.manager.set_window_title(title)
    except Exception:
        pass

def apply_legend(fig, ax):
    prev = ax.get_legend()
    if prev is not None:
        prev.remove()
    handles = [
        Patch(facecolor=np.array(PLAYER_HIT_COLOR)/255.0, edgecolor='none',label='Player Hit'),
        Patch(facecolor=np.array(PLAYER_MISS_COLOR)/255.0, edgecolor='none',label='Player Miss'),
        Patch(facecolor=np.array(ENEMY_MISS_COLOR)/255.0, edgecolor='none',label='Enemy Miss'),
        Patch(facecolor=np.array(FRIENDLY_ALIVE)/255.0, edgecolor='none',label='Friendly Alive'),
        Patch(facecolor=np.array(FRIENDLY_HIT)/255.0, edgecolor='none', label='Friendly Hit'),
        Patch(facecolor=np.array(FRIENDLY_SUNK)/255.0, edgecolor='none', label='Friendly Sunk'),
    ]
    ax.legend(
        handles=handles, 
        loc="center left",
        bbox_to_anchor=(1.02,0.5),
        borderaxespad=0.0,
        framealpha=0.9,
        fontsize=9,
    )

def init_display():
    plt.ion()
    fig, ax = plt.subplots()
    fig.subplots_adjust(right=0.8)

    im = ax.imshow(grid, vmin=0, vmax=255)

    apply_axis_styling(ax)
    apply_legend(fig, ax)
    set_titles(fig,ax,0)

    enable_mouse_input(fig)
    create_command_box(fig)
    
    fig.canvas.draw_idle()
    plt.pause(0.001)
    return fig, ax, im

_click_queue = []
_command_queue = []
_textbox = None

def on_click(event):
    """Capture mouse clicks on the grid and queues integer cells"""
    if not event.inaxes:
        return
    try:
        x = int(round(event.xdata))
        y= int(round(event.ydata))
    except (TypeError, ValueError):
        return
    if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
        _click_queue.append((x,y))

def enable_mouse_input(fig):
    fig.canvas.mpl_connect('button_press_event',on_click)

def on_command_submit(text):
    """Textbox callback: push lowercased commands onto the queue and then clears"""
    global _textbox
    cmd = (text or "").strip()
    if not cmd:
        return
    _command_queue.append(cmd.lower())

    if _textbox is not None:
        _textbox.set_val('')

def create_command_box(fig):
    """Creates a textbox on the right side of the figure for commands."""
    global _textbox

    axbox = fig.add_axes([0.82, 0.08, 0.16, 0.05])
    _textbox = TextBox(axbox, "Command:", initial="")
    _textbox.on_submit(on_command_submit)
    return _textbox

def request_coord_mouse(fig, ax, target):
    '''Block until user clicks a valid cell; returns (x,y)'''

    ax.set_xlabel("Click a cell (or type 'help' in console).")
    while _command_queue:
        cmd = _command_queue.pop(0)
        if cmd in ('quit', 'exit', '-1'):
            raise SystemExit
        elif cmd in ("help", "h", "?"):
            instructions()
        elif cmd == "cheat":
            tx, ty = enemy_target_xy
            print(f"Enemy at {_to_battleship_string(tx,ty)}. Cheater...")
        else:
            print(f"Unknown Command: {cmd}. (Try help/quit).")

    if _click_queue:
        return _click_queue.pop(0)
    
    plt.pause(0.05)

def update_display(fig, ax, im, score):
    im.set_data(grid)
    set_titles(fig,ax,score)
    apply_legend(fig, ax)
    fig.canvas.draw_idle()
    plt.pause(0.001)

def update_grid(user_x, user_y, horm):
    grid[user_y,user_x] = PLAYER_HIT_COLOR if horm else PLAYER_MISS_COLOR

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

def acquire_rand(excluded_cells):
    """Return a random (x,y) not in excluded_cells (Friendly Ships)"""
    while True:
        x,y = rand.randint(0,GRID_SIZE-1),rand.randint(0,GRID_SIZE-1)

        if (x,y) not in excluded_cells:
            return x,y
        
def setup_friendly():
    ship = FriendlyShip(grid_size=GRID_SIZE)
    center_x,center_y = FriendlyShip.prompt_friendly(GRID_SIZE)
    ship.place_center(center_x,center_y)
    return ship

def main():
    instructions()
    current_score = 0
    ship = setup_friendly()
    target = acquire_rand(ship.cells)
    enemy = enemy_init()

    fig, ax, im = init_display()
    enable_mouse_input(fig)
    ship.paint_on_grid(grid, color_alive=FRIENDLY_ALIVE, color_hit=FRIENDLY_HIT, color_sunk=FRIENDLY_SUNK)
    update_display(fig, ax, im, current_score)

    while current_score < GOAL:
        #x,y = request_coor(target)
        x,y = request_coord_mouse(fig, ax, target)
        d = calculate_distance(x,y,*target)
        points,horm = calculate_score(d)
        update_grid(x,y,horm)

        ship.paint_on_grid(grid, color_alive=FRIENDLY_ALIVE, color_hit=FRIENDLY_HIT, color_sunk=FRIENDLY_SUNK)
        current_score += points
        scorekeepr(current_score)
        update_display(fig, ax, im, current_score)

        if current_score >= GOAL:
            break

        if not enemy["active"] and (horm or d <= NEAR_TRIGGER_DIST):
            enemy["active"] = True
            print("Enemy has detected your presence!")
        if enemy["active"]:
            ex,ey,e_hit = enemy_fire(ship,enemy)
            if ex is not None:
                print(f"Enemy fires at {_to_battleship_string(ex,ey)} - {"HIT!" if e_hit else 'miss.'}")

                ship.paint_on_grid(grid,color_alive=FRIENDLY_ALIVE,color_hit=FRIENDLY_HIT,color_sunk=FRIENDLY_SUNK)
                update_display(fig, ax, im, current_score)

                if ship.is_sunk():
                    print("Your ship has been sunk!\n" \
                    "You've let us down Commander.\n"
                    "Try again next time!")
                    break

    plt.ioff()
    plt.show()

if __name__ == '__main__':
    main()