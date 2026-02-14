from enum import Enum


class ItemType(str, Enum):
    WIDE = "wide"
    SLOW = "slow"
    MULTI = "multi"
    FAST = "fast"


class GameState(str, Enum):
    WAITING_START = "waiting_start"
    PLAYING = "playing"
    STAGE_CLEAR = "stage_clear"
    GAME_OVER = "game_over"
