from enum import Enum


class ItemType(str, Enum):
    WIDE = "wide"
    SLOW = "slow"
    MULTI = "multi"
    FAST = "fast"


class GameState(str, Enum):
    TITLE = "title"
    TUTORIAL = "tutorial"
    WAITING_START = "waiting_start"
    PLAYING = "playing"
    PAUSED = "paused"
    STAGE_CLEAR = "stage_clear"
    GAME_OVER = "game_over"


class DifficultyMode(str, Enum):
    STORY = "story"
    STANDARD = "standard"
    HARDCORE = "hardcore"


class ProtocolType(str, Enum):
    FUSION = "fusion"
    REFLEX = "reflex"


class EnemyType(str, Enum):
    DRONE = "drone"
    SHIELD_NODE = "shield_node"
    SPLITTER = "splitter"
    SNIPER_ORB = "sniper_orb"
    NULL_CORE_BOSS = "null_core_boss"
