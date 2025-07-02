# --- START OF FINAL UPGRADED FILE main.py ---

import asyncio
import pygame
from pathlib import Path
import platform

from config import GameConfig, DEFAULT_THEME
from assets import AssetManager
import game
from ui import show_splash_screen, show_main_menu, show_player_select_screen, show_mode_select, show_level_select, play_level, level_editor, show_high_scores

async def main():
    """Main entry point for the Sokoban game."""
    pygame.init()
    config = GameConfig()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Sokoban by Redha & Rooney")

    assets_path = Path(__file__).parent / "assets"
    assets = AssetManager(config, DEFAULT_THEME, assets_path)
    
    game.initialize_game_data()
    
    if pygame.mixer.get_init() and pygame.mixer.music.get_volume() > 0:
        pygame.mixer.music.play(-1, 0.0, 5000)

    game_state = "SPLASH"
    current_mode = 'main'
    current_idx = 0
    current_key = ''
    
    while game_state != "QUIT":
        if game_state == "SPLASH": game_state = await show_splash_screen(screen, assets)
        elif game_state == "MAIN_MENU": game_state = await show_main_menu(screen, assets)
        elif game_state == "PLAYER_SELECT": game_state = await show_player_select_screen(screen, assets)
        elif game_state == "HIGH_SCORES": game_state = await show_high_scores(screen, assets)
        
        elif game_state == "MODE_SELECT":
            current_mode = await show_mode_select(screen, assets)
            if current_mode in ["PLAYER_SELECT", "MAIN_MENU", "QUIT"]:
                game_state = current_mode
            else:
                game_state = "LEVEL_SELECT"

        elif game_state == "LEVEL_SELECT":
            levels_to_show = game.BASE_LEVELS if current_mode == "main" else game.CUSTOM_LEVELS
            next_state, level_idx, level_key = await show_level_select(screen, assets, levels_to_show, current_mode)
            if next_state == "PLAY":
                current_idx, current_key = level_idx, level_key
            game_state = next_state

        elif game_state == "EDITOR":
            game_state = await level_editor(screen, assets)

        elif game_state == "PLAY":
            next_state, new_idx, new_key = await play_level(screen, assets, current_key, current_idx, current_mode)
            if next_state == "PLAY": # For prev/next button clicks
                current_idx, current_key = new_idx, new_key
            else: # If returning to another menu
                game_state = next_state
                if game_state != "QUIT":
                    pygame.mixer.music.play(-1, 0.0, 2000)

        for event in pygame.event.get(pygame.VIDEORESIZE):
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            config.TILE_SIZE = int(64 * min(event.w / config.WINDOW_WIDTH, event.h / config.WINDOW_HEIGHT))
            assets.images = assets.scale_images()

    pygame.quit()

if __name__ == "__main__":
    if platform.system() == "Emscripten": asyncio.ensure_future(main())
    else: asyncio.run(main())