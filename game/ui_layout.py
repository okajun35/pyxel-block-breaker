from dataclasses import dataclass

from game.constants import (
    BOTTOM_HUD_H,
    HEIGHT,
    SAFE_MARGIN,
    START_PANEL_H,
    START_PANEL_W,
    START_PANEL_X,
    START_PANEL_Y,
    TOP_HUD_H,
    WIDTH,
)
from game.enums import GameState


@dataclass(frozen=True)
class UILayout:
    show_hud: bool
    panel_x: int
    panel_y: int
    panel_w: int
    panel_h: int
    top_text_y: int
    top_sub_y: int
    bottom_y: int
    upper_bottom_y: int
    toast_y: int
    balls_x: int
    life_x: int
    rev_x: int
    role_x: int
    stage_x: int


def build_layout(state: GameState) -> UILayout:
    show_hud = state not in (GameState.WAITING_START, GameState.TITLE, GameState.TUTORIAL)
    bottom_y = HEIGHT - SAFE_MARGIN
    upper_bottom_y = HEIGHT - BOTTOM_HUD_H
    return UILayout(
        show_hud=show_hud,
        panel_x=START_PANEL_X,
        panel_y=START_PANEL_Y,
        panel_w=min(START_PANEL_W, WIDTH - SAFE_MARGIN * 2),
        panel_h=min(START_PANEL_H, HEIGHT - SAFE_MARGIN * 2),
        top_text_y=SAFE_MARGIN - 2,
        top_sub_y=TOP_HUD_H - 8,
        bottom_y=bottom_y,
        upper_bottom_y=upper_bottom_y,
        toast_y=HEIGHT - BOTTOM_HUD_H - 12,
        balls_x=4,
        life_x=52,
        rev_x=92,
        role_x=126,
        stage_x=194,
    )
