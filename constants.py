from enum import IntEnum

class GameObject(IntEnum):
    """Enumeration of game objects for readability."""
    WALL = -1
    EMPTY = 0
    TARGET = 1
    BOX = 2
    PLAYER = 3