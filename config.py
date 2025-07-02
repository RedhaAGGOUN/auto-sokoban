from dataclasses import dataclass

@dataclass
class GameConfig:
    """Configuration settings for the Sokoban game."""
    FPS: int = 60
    TILE_SIZE: int = 64
    FONT_NAME: str = 'Arial'
    HEADER_HEIGHT: int = 90
    WINDOW_WIDTH: int = 1280
    WINDOW_HEIGHT: int = 720

DEFAULT_THEME = {
    'BG':(70,80,90),'TEXT':(240,240,240),'WIN':(140,240,140),'STAR':(255,223,0),
    'UI_BTN':(210,210,220),'UI_BTN_SHADOW':(150,150,160),'UI_BTN_HOVER':(255,255,255),
    'UI_BTN_TEXT':(55,66,82),'UI_BTN_TOGGLE_ON':(255,202,58),
    'EDITOR_PALETTE_BG':(60,70,80),'EDITOR_PALETTE_SELECTED':(255,202,58),'EDITOR_TEXT':(200,200,200),
    'EDITOR_MSG_BAD': (255,100,100),
}