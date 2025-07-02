# --- START OF FINAL UPGRADED FILE assets.py ---

import pygame
from typing import Dict
from pathlib import Path
from config import GameConfig

class AssetManager:
    """Manages loading and scaling of all game assets."""
    def __init__(self, config: GameConfig, theme: Dict, assets_path: Path):
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"!! WARNING: Failed to initialize pygame.mixer: {e}")

        self.config = config; self.theme = theme; self.assets_path = assets_path
        
        self.font_title = pygame.font.SysFont(config.FONT_NAME, 96, bold=True)
        self.font_large = pygame.font.SysFont(config.FONT_NAME, 48, bold=True)
        self.font_medium = pygame.font.SysFont(config.FONT_NAME, 28, bold=True)
        self.font_small = pygame.font.SysFont(config.FONT_NAME, 18, bold=True)
        self.font_tiny = pygame.font.SysFont(config.FONT_NAME, 14, bold=True) 

        self.original_images = self._load_original_images()
        self.images = self.scale_images()
        self.sounds = self._load_sounds()
        
        # Safely load background music
        try:
            pygame.mixer.music.load(assets_path / "menu_music.wav")
            print("OK: Loaded background music 'menu_music.wav'")
        except pygame.error as e:
            print(f"!! WARNING: Could not load background music 'menu_music.wav'. Game will continue without it. Error: {e}")

    def scale_images(self) -> Dict[str, pygame.Surface]:
        scaled = {}; tile_size = (self.config.TILE_SIZE, self.config.TILE_SIZE)
        for name, surf in self.original_images.items():
            if surf is None: continue # Skip if an optional image failed to load
            if name == 'background': scaled[name] = pygame.transform.scale(surf, (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
            elif name == 'logo': scaled[name] = surf 
            else: scaled[name] = pygame.transform.scale(surf, tile_size)
        
        if 'logo' in self.original_images and self.original_images['logo'] is not None:
            logo_surf = self.original_images['logo']
            original_width, original_height = logo_surf.get_size()
            new_width = original_width // 2
            new_height = original_height // 2
            scaled['logo_small'] = pygame.transform.smoothscale(logo_surf, (new_width, new_height))
            
        return scaled

    def _load_original_images(self) -> Dict[str, pygame.Surface]:
        images = {}
        # Define which files are essential and which are optional
        required_files = {
            'player_front':'player_front.png','player_back':'player_back.png','player_left':'player_left.png',
            'player_right':'player_right.png','player_face':'playerFace.png','wall':'block.png',
            'box':'box.png','floor':'ground.png','background':'ground.png','target':'target1.png',
        }
        optional_files = {
            'logo': 'logo.png'
        }
        
        print("--- Loading Images ---")
        # Load required files, crash if they are missing
        for name, filename in required_files.items():
            path = self.assets_path / filename
            try:
                images[name] = pygame.image.load(path).convert_alpha()
                print(f"OK: Loaded image '{filename}' as '{name}'")
            except (pygame.error, FileNotFoundError) as e:
                print(f"!! FATAL ERROR: Could not load required image '{path}'. Please ensure this file exists.")
                raise SystemExit(e)

        # Load optional files, warn but don't crash if they are missing
        for name, filename in optional_files.items():
            path = self.assets_path / filename
            try:
                images[name] = pygame.image.load(path).convert_alpha()
                print(f"OK: Loaded optional image '{filename}' as '{name}'")
            except (pygame.error, FileNotFoundError):
                print(f"!! WARNING: Optional image '{filename}' not found. Game will continue without it.")
                images[name] = None
        
        images['player'] = images['player_front']
        images['box_on_target'] = images['box']
        print("----------------------")
        return images

    def _load_sounds(self) -> Dict[str, pygame.mixer.Sound]:
        sounds = {}
        sound_files = ["button.wav","move.wav","place_box.wav","undo.wav","win.wav", "new_highscore.wav"]
        print("--- Loading Sounds ---")
        for f in sound_files:
            name = f.split('.')[0]
            try:
                sounds[name] = pygame.mixer.Sound(str(self.assets_path / f))
                print(f"OK: Loaded sound '{f}' as sounds['{name}']")
            except (pygame.error, FileNotFoundError):
                print(f"!! WARNING: Could not load sound '{f}'.")
                sounds[name] = type('DummySound',(),{'play':lambda:None})()
        print("----------------------")
        return sounds

# --- END OF FINAL UPGRADED FILE assets.py ---