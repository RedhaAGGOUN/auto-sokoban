# --- START OF CORRECTED FILE assets.py ---

import pygame
from typing import Dict
from pathlib import Path
from config import GameConfig
from constants import GameObject

class AssetManager:
    """Manages loading and scaling of all game assets."""
    def __init__(self, config: GameConfig, theme: Dict, assets_path: Path):
        pygame.mixer.init()
        self.config = config
        self.theme = theme
        self.assets_path = assets_path
        
        self.font_title = pygame.font.SysFont(config.FONT_NAME, 96, bold=True)
        self.font_large = pygame.font.SysFont(config.FONT_NAME, 48, bold=True)
        self.font_medium = pygame.font.SysFont(config.FONT_NAME, 28, bold=True)
        self.font_small = pygame.font.SysFont(config.FONT_NAME, 18)

        self.original_images = self._load_original_images()
        self.images = self.scale_images()
        self.sounds = self._load_sounds()

    def scale_images(self) -> Dict[str, pygame.Surface]:
        """Scales the original sprites to the current TILE_SIZE and window size."""
        scaled = {}
        tile_size = (self.config.TILE_SIZE, self.config.TILE_SIZE)
        for name, surf in self.original_images.items():
            if name == 'background':
                 scaled[name] = pygame.transform.scale(surf, (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
            else:
                scaled[name] = pygame.transform.scale(surf, tile_size)
        return scaled

    def _load_original_images(self) -> Dict[str, pygame.Surface]:
        """Loads each game asset from its own image file, matching the user's screenshot exactly."""
        images = {}
        image_files = {
            'player_front': 'player_front.png',
            'player_back':  'player_back.png',
            'player_left':  'player_left.png',
            'player_right': 'player_right.png',
            'player_face':  'playerFace.png', 
            'wall':         'block.png',
            'box':          'box.png',
            'floor':        'ground.png',
            'background':   'ground.png',
            'target':       'target1.png', 
        }
        print("--- Loading Images ---")
        for name, filename in image_files.items():
            path = self.assets_path / filename
            try:
                if name == 'player_front': images['player'] = pygame.image.load(path).convert_alpha()
                images[name] = pygame.image.load(path).convert_alpha()
                print(f"OK: Loaded image '{filename}' as '{name}'")
            except pygame.error as e:
                print(f"!! FATAL ERROR: Could not load image '{path}': {e}"); raise SystemExit(e)
        images['box_on_target'] = images['box']
        print("----------------------")
        return images

    def _load_sounds(self) -> Dict[str, pygame.mixer.Sound]:
        """Load sound effects, matching the user's screenshot exactly."""
        sounds = {}
        sound_files = ["button.wav", "move.wav", "place_box.wav", "undo.wav", "win.wav"]
        print("--- Loading Sounds ---")
        for f in sound_files:
            name = f.split('.')[0]
            try:
                sounds[name] = pygame.mixer.Sound(str(self.assets_path / f))
                print(f"OK: Loaded sound '{f}' as sounds['{name}']")
            except pygame.error:
                print(f"!! WARNING: Could not load sound '{f}'.")
                sounds[name] = type('DummySound', (), {'play': lambda: None})()
        print("----------------------")
        return sounds

# --- END OF CORRECTED FILE assets.py ---