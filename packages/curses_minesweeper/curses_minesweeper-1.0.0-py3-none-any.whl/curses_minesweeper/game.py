"""
Launch the Minesweeper game.

Basic usage:
    from minesweeper import launch
    launch()

Args:
    scheme (int, optional): Control scheme to use.
        - 1 (default): Arrow keys
        - 2: WASD
        - 3: Numpad
    width (int, optional): Width of the minefield. 
        If width * height < 12, defaults to a max-sized grid.
    height (int, optional): Height of the minefield. 
        If width * height < 12, defaults to a max-sized grid.
    seed (int, optional): Random seed. Must be a 7-digit number 
        (i.e. 1000000 <= seed < 10000000).

Example:
    from minesweeper import launch
    launch(2, 20, 10, 1234567)
"""
import curses
from time import perf_counter
import random
from sys import exit
from argparse import ArgumentParser
from .utils import Vector2D, VectorAccessObjectDict, Window
from collections import deque

class Minefield:
    class Tile:
        def __init__(self, vec, mine=False):
            self.vec = vec
            self.mine = mine
            self.seen = False
            self.flag = False 
            self.grid = 10 + ((self.vec.x % 2) ^ (self.vec.y % 2))
            
        def __repr__(self):
            return f"Minefield.Tile(vec={self.vec}, mine={self.mine}, seen={self.seen}, flag={self.flag})"

    def __init__(self, size, stdscr, contr, seed):
        _, x = stdscr.getmaxyx()
        gridvec = Vector2D(size.x * 2 + 2, size.y + 2)
        self.contr = contr
        self.seed = seed
        self.initialized = False
        self.grid = VectorAccessObjectDict(size, self.Tile)
        self.ui = stdscr.derwin(x, 6, 0, 0)
        self.gr = stdscr.derwin(gridvec.x, gridvec.y, (x - gridvec.x) // 2, 6)
        self.color = lambda n: curses.color_pair(n)
            
    def get_neighbours(self, tile):
        return {
        self.grid[vec]
        for vec in tile.vec.neighbours()
        if Vector2D(0, 0) <= vec < self.grid.size
        }
        
    def count(self, tile, attr):
        if tile.mine:
            return 9  # valid for mines and the function is never called for flags
        return sum(getattr(tile, attr) for tile in self.get_neighbours(tile))
    
    def sumup(self, attr):
        return sum((tile.mine and tile.flag if attr == "correct" else getattr(tile, attr)) for tile in self.grid.values())
    
    def flood(self, tile):
        queue = deque([tile])
        while queue:
            tile = queue.popleft()
            if tile.seen:
                continue
            tile.seen = True
            tile.flag = False
            if not self.count(tile, "mine"):
                for neighbour in self.get_neighbours(tile):
                    queue.append(neighbour)
            
    def reveal(self, cur):
        tile = self.grid[cur]
        if tile.flag:
            return
        if tile.mine:
            self.end(victory = False)
        self.flood(tile)
        
    def flag(self, cur):
        tile = self.grid[cur]
        if not tile.seen:
            tile.flag = tile.flag ^ True
        if tile.seen:
            flags = self.count(tile, "flag")
            mines = self.count(tile, "mine")
            if flags == mines:
                for neighbour in self.get_neighbours(tile):
                    if not neighbour.flag:
                        self.reveal(neighbour.vec)
        if self.sumup("correct") == self.sumup("flag") == self.sumup("mine"):
            self.end(victory = True)
            
    def initialize(self, cur):
        tile = self.grid[cur]
        random.seed(self.seed)
        safe = {t.vec for t in self.get_neighbours(tile) | {tile}}
        for vec in self.grid.keys():
            if vec in safe:
                continue
            self.grid[vec] = self.Tile(vec, random.random() < 0.2)
        self.reveal(tile.vec)
        self.initialized = True
        self.start = perf_counter()        
        
    def timestamp(self):
        elapsed = perf_counter() - self.start
        m, s = divmod(int(elapsed), 60)
        return f" {m:02}:{s:02} "
            
    def ui_render(self, title = None, contr1 = None, contr2 = None):
        title = title or "===MINESWEEPER==="
        contr1 = contr1 or f"< press {self.contr.dig_name} to dig, {self.contr.flag_name} to flag >"
        contr2 = contr2 or f"< {self.contr.keys_name} to move, Q to exit >"
        
        self.ui.add(0, 0, title.center(self.ui.size.x))
        self.ui.add(0, 1, contr1.center(self.ui.size.x))
        self.ui.add(0, 2, contr2.center(self.ui.size.x))
        if self.initialized:
            stamp = self.timestamp()
            mines = self.sumup("mine")
            flags = self.sumup("flag")
            seed = self.seed
        else:
            stamp = " --:-- "
            mines = "---"
            flags = "---"
            seed = "-------"
        self.ui.add(0, 1, f"TIME : [{stamp}]")
        self.ui.add(0, 2, f"MINES: [{str(flags).rjust(3, "0")}/{str(mines).rjust(3, "0")}]")
        self.ui.add(0, 3, f"SEED : [{seed}]")
        self.ui.box()
        self.ui.refresh()
        
    def render(self, cur):
        self.gr.box()
        for tile in self.grid.values():
            screen = Vector2D(tile.vec.x * 2, tile.vec.y)
            c = ">" if cur == tile.vec else " "
            if tile.seen:
                n = self.count(tile, "mine")
                val = " " if (n >= 9 or not n) else str(n)
                self.gr.add(screen.x, screen.y, c, self.color(6))
            else:
                n = tile.grid
                val = "#" if tile.flag else " "
                self.gr.add(screen.x, screen.y, c, self.color(n))
            self.gr.add(screen.x + 1, screen.y, val, self.color(n))
            self.gr.refresh()
        
    def end(self, victory):
        for tile in self.grid.values():
            tile.seen = True
        
        for _ in range(3):
            curses.beep()
            curses.flash()
            curses.napms(200)
        
        self.render(Vector2D(-1, -1))
        
        title = "=== VICTORY ===" if victory else "=== GAME OVER ==="
        contr1 = "< press Q to exit >"
        
        self.ui_render(title, contr1, " ")
        
        while True:
            ch = self.ui.getch()
            if (curses.keyname(ch) if ch != -1 else None) == b"q":
                exit(1)
                
class Cursor:
    def __init__(self, size, stdscr, contr, seed):
        self.minefield = Minefield(size, stdscr, contr, seed)
        self.pos = Vector2D(0, 0)
        vecs = [Vector2D(0, -1), Vector2D(0, 1), Vector2D(-1, 0), Vector2D(1, 0), Vector2D(0, 0)]
        self.direction_vecs = {
        key: vec for key, vec in zip(contr.keys + [None], vecs)
        }
        
    def render(self):
        self.minefield.render(self.pos)
        self.minefield.ui_render()        
    
    def move(self, key):
        self.pos += self.direction_vecs[key]
        if not Vector2D(0, 0) <= self.pos < self.minefield.grid.size:
            self.pos -= self.direction_vecs[key]
        
    def dig(self):
        if not self.minefield.initialized:
            self.minefield.initialize(self.pos)
        else:
            self.minefield.reveal(self.pos)
        self.move(None)            
        
    def flag(self):
        if not self.minefield.initialized:
            return
        self.minefield.flag(self.pos)
        self.move(None)
        
class Controls:
    def __init__(self, keys, dig, flag):
        self.keys = keys[0]
        self.keys_name = keys[1]
        self.dig = dig[0]
        self.dig_name = dig[1]
        self.flag = flag[0]
        self.flag_name = flag[1]
        
def main(stdscr):
    global args
    
    def getmax():
        _y, _x = stdscr.getmaxyx()
        maxx, maxy = int(_x // 2 - 1), _y - 8
        if args.width * args.height <= 12:
            return Vector2D(maxx, maxy)
        else:
            return Vector2D(min(maxx, args.width), min(maxy, args.height))
        
    def getkey():
        ch = stdscr.getch()
        return curses.keyname(ch) if ch != -1 else None
        
    schemes = {
    1: Controls(([b"KEY_UP", b"KEY_DOWN", b"KEY_LEFT", b"KEY_RIGHT"], "ARROW KEYS"), (b"^J", "ENTER"), (b" ", "SPACE")),
    2: Controls(([b"w", b"s", b"a", b"d"], "WASD"), (b"^J", "ENTER"), (b" ", "SPACE")),
    3: Controls(([b"2", b"8", b"4", b"6"], "2468"), (b"^J", "ENTER"), (b"5", "5"))
    }        
    
    contr = schemes[args.scheme]
    
    curses.start_color()
    curses.init_pair(1, 159, 0)
    curses.init_pair(2, 33, 0)
    curses.init_pair(3, 118, 0)
    curses.init_pair(4, 226, 0)
    curses.init_pair(5, 208, 0)
    curses.init_pair(6, 196, 0)
    curses.init_pair(7, 207, 0)
    curses.init_pair(8, 93, 0)
    curses.init_pair(9, 0, 196)
    curses.init_pair(10, 196, 76)
    curses.init_pair(11, 196, 34)
    
    curses.curs_set(0)
    curses.noecho()
    
    stdscr = Window(stdscr)
    stdscr.nodelay(True)
    stdscr.clear()
    
    c = Cursor(getmax(), stdscr, contr, args.seed)
    
    while True:
        key = getkey()
        if key in contr.keys:
            c.move(key)
        if key == contr.dig:
            c.dig()
        if key == contr.flag:
            c.flag()
        if key == b"q":
            break
        c.render()

def launch(scheme = None, width = None, height = None, seed = None):
    global args
    parser = ArgumentParser()
    
    parser.add_argument("--scheme", default=1, type=int, help="control scheme to use, 1 (default) for arrow keys, 2 for WASD, 3 for NUMPAD")
    parser.add_argument("--width", default=3, type=int, help="set the width of the minefield, WARNING: grids smaller than 12 tiles (width * height) get changed into default, max-sized ones")
    parser.add_argument("--height", default=3, type=int, help="set the height of the minefield, WARNING: grids smaller than 12 tiles (width * height) get changed into default, max-sized ones")
    parser.add_argument("--seed", default=random.randint(10**6, 10**7), type=int, help="seed for the random module, must be 7 digit long (10 ** 6 <= seed < 10 ** 7)")
    
    args = parser.parse_args()
    
    args.scheme = int(scheme or args.scheme)
    if args.scheme not in {1, 2, 3}:
        raise ValueError("'scheme' must be in range [1 ; 3]")
    args.width = int(width or args.width)
    args.height = int(height or args.height)
    args.seed = int(seed or args.seed)
    if not (10**6 <= args.seed < 10**7):
        raise ValueError("'seed' must be in range [10 ** 6 ; 10 ** 7)")
    
    curses.wrapper(main)