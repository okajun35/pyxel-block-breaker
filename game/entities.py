from dataclasses import dataclass

from game.enums import EnemyType, ItemType


@dataclass
class Ball:
    x: float
    y: float
    vx: float
    vy: float


@dataclass
class FallingItem:
    x: float
    y: float
    type: ItemType


@dataclass
class MovingBlock:
    x: float
    y: float
    vx: float
    hp: int


@dataclass
class Enemy:
    type: EnemyType
    x: float
    y: float
    vx: float
    vy: float
    hp: float
    damage: int
