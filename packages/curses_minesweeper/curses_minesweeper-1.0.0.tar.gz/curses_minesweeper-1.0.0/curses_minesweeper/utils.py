import curses

def vector(func):
    def wrapper(self, *args):
        if not isinstance(args[0], Vector2D):
            return NotImplemented
        return func(self, *args)
    return wrapper
    
class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    @property
    def xy(self):
        return (self.x, self.y)
        
    @vector
    def __add__(self, vec):
        return Vector2D(self.x + vec.x, self.y + vec.y)
        
    @vector
    def __sub__(self, vec):
        return Vector2D(self.x - vec.x, self.y - vec.y)
        
    @vector
    def __iadd__(self, vec):
        self.x += vec.x
        self.y += vec.y
        return self
        
    @vector
    def __isub__(self, vec):
        self.x -= vec.x
        self.y -= vec.y
        return self

    @vector
    def __eq__(self, vec):
        return self.x == vec.x and self.y == vec.y 

    @vector
    def __lt__(self, vec):
        return self.x < vec.x and self.y < vec.y
        
    @vector
    def __le__(self, vec):
        return self.x <= vec.x and self.y <= vec.y
        
    @vector
    def __gt__(self, vec):
        return self.x > vec.x and self.y > vec.y
        
    @vector
    def __ge__(self, vec):
        return self.x >= vec.x and self.y >= vec.y
        
    def __hash__(self):
        return hash(self.xy)
            
    def __repr__(self):
        return f"utils.Vector2D(x={self.x}, y={self.y})"
        
    def neighbours(self):
        return {
        Vector2D(x, y)
        for y in range(self.y - 1, self.y + 2)
        for x in range(self.x - 1, self.x + 2)
        if Vector2D(x, y) != self
        }
        
class VectorAccessObjectDict:  # ik, long ass name
    def __init__(self, size, obj = None):
        if obj:
            self._values = {Vector2D(x, y): obj(Vector2D(x, y)) for x in range(size.x) for y in range(size.y)}
        else:
            self._values = {Vector2D(x, y): None for x in range(size.x) for y in range(size.y)}
        self.size = size            
                    
    def keys(self):
        return iter(self._values.keys())
        
    def values(self):
        return iter(self._values.values())
    
    @vector
    def __getitem__(self, vec):
        return self._values[vec]
        
    @vector
    def __setitem__(self, vec, value):
        if vec in self._values:
            self._values[vec] = value
        else:
            raise KeyError(vec)
        
    @vector
    def __delitem__(self, vec):
        self._values[vec] = value
        
class Window:
    def __init__(self, window):
        self.window = window
        y, x = window.getmaxyx()
        self.size = Vector2D(x, y)
        
    def __getattr__(self, name):
        return getattr(self.window, name)
        
    def derwin(self, height, width, begin_y, begin_x):
        return Window(self.window.derwin(width, height, begin_x, begin_y))
        
    def subwin(self, height, width, begin_y, begin_x):
        return Window(self.window.subwin(width, height, begin_x, begin_y))
        
    def add(self, x, y, value, attr=curses.A_NORMAL):  # cope with the changed yx order :3
        value = str(value)
        self.window.addstr(y + 1, x + 1, value, attr)