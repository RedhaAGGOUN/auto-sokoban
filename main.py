# --- START OF CORRECTED AND FINAL FILE main.py ---

import asyncio
import pygame
from pathlib import Path
import platform

from config import GameConfig, DEFAULT_THEME
from assets import AssetManager
# Import the entire game module to access its live data, not a snapshot.
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
    
    # This function populates the lists inside the 'game' module.
    game.initialize_game_data() 

    game_state = "SPLASH"
    level_to_edit_idx = None
    level_to_edit_data = None
    
    while game_state != "QUIT":
        if game_state == "SPLASH":
            game_state = await show_splash_screen(screen, assets)
        elif game_state == "MAIN_MENU":
            game_state = await show_main_menu(screen, assets)
        elif game_state == "PLAYER_SELECT":
            game_state = await show_player_select_screen(screen, assets)
        elif game_state == "HIGH_SCORES":
            game_state = await show_high_scores(screen, assets)
        
        elif game_state == "MODE_SELECT":
            mode = await show_mode_select(screen, assets)
            if mode == "PLAYER_SELECT":
                game_state = "PLAYER_SELECT"
                continue
            
            # CORRECTED: Access the level lists through the 'game' module
            # to get the live, populated data.
            levels_to_show = game.BASE_LEVELS if mode == "main" else game.CUSTOM_LEVELS
            next_state, level_idx, level_key = await show_level_select(screen, assets, levels_to_show, mode)
            
            game_state = next_state
            if next_state == "PLAY":
                from ui import current_level_idx, current_level_key, current_level_mode
                current_level_idx = level_idx
                current_level_key = level_key
                current_level_mode = mode 
        
        elif game_state == "EDITOR":
            game_state = await level_editor(screen, assets, level_to_edit_idx, level_to_edit_data)
            level_to_edit_idx, level_to_edit_data = None, None

        elif game_state == "PLAY":
            game_state = await play_level(screen, assets)
        
        for event in pygame.event.get(pygame.VIDEORESIZE):
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            config.TILE_SIZE = int(64 * min(event.w / config.WINDOW_WIDTH, event.h / config.WINDOW_HEIGHT))
            assets.images = assets.scale_images()

    pygame.quit()

if __name__ == "__main__":
    if platform.system() == "Emscripten":
        asyncio.ensure_future(main())
    else:
        asyncio.run(main())

# --- END OF CORRECTED AND FINAL FILE main.py ---