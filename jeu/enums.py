from enum import Enum

class GameState(Enum):
    MENU = 1
    GAME = 2
    DIALOGUE = 3
    VICTORY = 4
    GAME_OVER = 5

class Element(Enum):
    NONE = 0
    EAU = 1
    TERRE = 2
    AIR = 3
    FEU = 4

class Direction(Enum):
    DOWN = 0
    UP = 1
    LEFT = 2
    RIGHT = 3
