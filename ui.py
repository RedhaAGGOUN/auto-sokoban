# --- START OF CORRECTED AND FINAL ui.py ---

import asyncio
import pygame
import numpy as np
import time
from typing import Tuple, Optional, List
from pathlib import Path
import random

from config import GameConfig, DEFAULT_THEME as THEME
from assets import AssetManager
import game
from core import get_initial_board
from save_load import save_data, load_data

current_level_idx = 0
current_level_key = ''
current_level_mode = 'main'
player_animator = None

# --- UI Helper Classes and Functions ---
class AnimatedPlayer:
    def __init__(self, initial_sprite: pygame.Surface):
        self.original_sprite = initial_sprite; self.sprite = initial_sprite
        self.y_offset = 0; self.breath_timer = 0; self.move_timer = 0; self.squash = 1.0
    def set_sprite(self, new_sprite: pygame.Surface): self.original_sprite = new_sprite
    def update(self):
        self.breath_timer += 0.1; self.y_offset = np.sin(self.breath_timer) * 2
        if self.move_timer > 0:
            self.move_timer -= 1; progress = (10 - self.move_timer) / 10; self.squash = 1.0 + 0.3 * np.sin(progress * np.pi)
        else: self.squash = 1.0
        w, h = self.original_sprite.get_size(); squash_h = int(h * (1/self.squash)); squash_w = int(w * self.squash)
        self.sprite = pygame.transform.scale(self.original_sprite, (squash_w, squash_h))
    def trigger_move(self): self.move_timer = 10

class FloatingBox:
    def __init__(self, W, H, assets):
        self.W, self.H = W, H; self.x = random.randint(0, W); self.y = random.randint(0, H)
        self.speed = random.uniform(0.5, 1.5); self.size = random.randint(40, 80)
        self.sprite = pygame.transform.scale(assets.images['box'], (self.size, self.size))
    def update(self):
        self.y -= self.speed
        if self.y < -self.size: self.y = self.H; self.x = random.randint(0, self.W)

def draw_board_and_objects(screen, board, assets, offset=(0,0), is_editor=False, target_mask=None, player_direction=(1,0)):
    h, w = board.shape; start_x, start_y = offset
    bg_tile = assets.images['floor']
    for i in range(h):
        for j in range(w):
            rect = pygame.Rect(start_x + j * assets.config.TILE_SIZE, start_y + i * assets.config.TILE_SIZE, assets.config.TILE_SIZE, assets.config.TILE_SIZE)
            cell = board[i, j]; is_target_location = False
            if target_mask is not None and i < target_mask.shape[0] and j < target_mask.shape[1]: is_target_location = target_mask[i, j]
            elif is_editor and cell == game.GameObject.TARGET.value: is_target_location = True
            screen.blit(bg_tile, rect.topleft)
            if is_target_location: screen.blit(assets.images['target'], rect.topleft)
            if cell == game.GameObject.WALL.value: screen.blit(assets.images['wall'], rect.topleft)
            elif cell == game.GameObject.BOX.value: screen.blit(assets.images['box'], rect.topleft)
            elif cell == game.GameObject.PLAYER.value:
                sprite_key = 'player_front'
                if player_direction == (-1, 0): sprite_key = 'player_back'
                elif player_direction == (0, -1): sprite_key = 'player_left'
                elif player_direction == (0, 1): sprite_key = 'player_right'
                player_sprite = assets.images[sprite_key]
                if player_animator and not is_editor:
                    player_animator.set_sprite(player_sprite); player_animator.update()
                    player_sprite = player_animator.sprite
                player_rect = player_sprite.get_rect(center=rect.center)
                if player_animator and not is_editor: player_rect.y += player_animator.y_offset
                screen.blit(player_sprite, player_rect)

def draw_gradient_rect(screen, rect, color1, color2, vertical=True):
    surface = pygame.Surface((rect.width, rect.height))
    for i in range(rect.height if vertical else rect.width):
        alpha = i / (rect.height if vertical else rect.width); color = [int(c1 + (c2 - c1) * alpha) for c1, c2 in zip(color1, color2)]
        if vertical: pygame.draw.line(surface, color, (0, i), (rect.width, i))
        else: pygame.draw.line(surface, color, (i, 0), (i, rect.height))
    screen.blit(surface, rect.topleft)

def draw_header_button(screen, rect, symbol_text, assets, enabled=True, toggled=False):
    theme = assets.theme; shadow_rect = rect.copy(); shadow_rect.y += 3
    pygame.draw.rect(screen, theme['UI_BTN_SHADOW'], shadow_rect, border_radius=8)
    base_color = theme['UI_BTN_HOVER'] if toggled else theme['UI_BTN']
    color = base_color if enabled else tuple(int(c * 0.8) for c in base_color)
    gradient_color = tuple(int(c * 0.9) for c in color); draw_gradient_rect(screen, rect, color, gradient_color)
    if toggled: pygame.draw.rect(screen, theme['UI_BTN_TOGGLE_ON'], rect, 2, border_radius=8)
    text_surf = assets.font_medium.render(symbol_text, True, theme['UI_BTN_TEXT'])
    screen.blit(text_surf, text_surf.get_rect(center=rect.center))

def draw_star(surface, center, size, color):
    points = []; angle = np.pi / 2
    for _ in range(5):
        points.append((center[0] + size * np.cos(angle), center[1] - size * np.sin(angle))); angle += 2 * np.pi / 5
        points.append((center[0] + size / 2 * np.cos(angle), center[1] - size / 2 * np.sin(angle))); angle += 2 * np.pi / 5
    pygame.draw.polygon(surface, color, points)

async def fade_transition(screen, assets, fade_in=True, duration=0.25):
    W, H = screen.get_size(); overlay = pygame.Surface((W, H)); clock = pygame.time.Clock()
    steps = int(duration * assets.config.FPS)
    for i in range(steps):
        alpha = (i / steps) if fade_in else (1 - i / steps)
        overlay.set_alpha(int(alpha * 255)); overlay.fill(assets.theme['BG'])
        screen.blit(overlay, (0, 0)); pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)

# --- UI Screens ---
async def show_splash_screen(screen: pygame.Surface, assets: AssetManager) -> str:
    await fade_transition(screen, assets, fade_in=True); W, H = screen.get_size()
    clock = pygame.time.Clock(); start_time = time.time()
    while time.time() - start_time < 2:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "MAIN_MENU"
        screen.fill(assets.theme['BG']);
        if 'background' in assets.images: screen.blit(assets.images['background'],(0,0))
        title_surf = assets.font_title.render("SOKOBAN", True, assets.theme['TEXT'])
        screen.blit(title_surf, title_surf.get_rect(centerx=W // 2, centery=H // 3))
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)
    return "MAIN_MENU"

async def show_main_menu(screen: pygame.Surface, assets: AssetManager) -> str:
    await fade_transition(screen, assets, fade_in=True); W, H = screen.get_size()
    buttons = {"PLAY": pygame.Rect(W//2-150, H//2-120, 300, 70), "BUILD NEW BOARD": pygame.Rect(W//2-150, H//2-30, 300, 70), "HIGH SCORES": pygame.Rect(W//2-150, H//2+60, 300, 70), "QUIT": pygame.Rect(W//2-150, H//2+150, 300, 70)}
    boxes = [FloatingBox(W, H, assets) for _ in range(15)]
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if buttons["PLAY"].collidepoint(pos): assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "PLAYER_SELECT"
                if buttons["BUILD NEW BOARD"].collidepoint(pos): assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "EDITOR"
                if buttons["HIGH SCORES"].collidepoint(pos): assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "HIGH_SCORES"
                if buttons["QUIT"].collidepoint(pos): assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "QUIT"
        screen.fill(assets.theme['BG'])
        if 'background' in assets.images: screen.blit(assets.images['background'], (0,0))
        for box in boxes: box.update(); screen.blit(box.sprite, (box.x, box.y))
        title_surf = assets.font_large.render("MAIN MENU", True, assets.theme['TEXT']); screen.blit(title_surf, title_surf.get_rect(centerx=W / 2, y=50))
        for name, rect in buttons.items(): draw_header_button(screen, rect, name, assets, toggled=rect.collidepoint(pygame.mouse.get_pos()))
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)

async def show_high_scores(screen, assets):
    await fade_transition(screen, assets, fade_in=True); W, H = screen.get_size(); back_button = pygame.Rect(W//2-150, H-120, 300, 50)
    scores = [];
    for player_name, stars_dict in game.LEVEL_STARS.items(): scores.append({"name": player_name, "stars": sum(stars_dict.values())})
    scores.sort(key=lambda s: s["stars"], reverse=True); clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and back_button.collidepoint(event.pos):
                assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "MAIN_MENU"
        screen.fill(assets.theme['BG']);
        if 'background' in assets.images: screen.blit(assets.images['background'], (0,0))
        title_surf = assets.font_large.render("HIGH SCORES", True, assets.theme['TEXT']); screen.blit(title_surf, title_surf.get_rect(centerx=W/2, y=50))
        for i, score_data in enumerate(scores[:10]):
            y_pos = 150 + i * 50
            rank_surf = assets.font_medium.render(f"#{i+1}", True, assets.theme['TEXT']); screen.blit(rank_surf, rank_surf.get_rect(x=W/2-200, centery=y_pos))
            name_surf = assets.font_medium.render(score_data['name'], True, assets.theme['TEXT']); screen.blit(name_surf, name_surf.get_rect(x=W/2-100, centery=y_pos))
            star_surf = assets.font_medium.render(f"{score_data['stars']} ★", True, assets.theme['STAR']); screen.blit(star_surf, star_surf.get_rect(right=W/2+200, centery=y_pos))
        draw_header_button(screen, back_button, "BACK", assets, toggled=back_button.collidepoint(pygame.mouse.get_pos()))
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)

async def show_player_select_screen(screen, assets):
    await fade_transition(screen, assets, fade_in=True); W, H = screen.get_size(); players = list(game.LEVEL_STARS.keys())
    input_box = pygame.Rect(W//2-150, H-200, 300, 50); back_button = pygame.Rect(W//2-150, H-120, 300, 50)
    new_player_name = ""; input_active = False; clock = pygame.time.Clock()
    while True:
        player_buttons = {name: pygame.Rect(W//2-150, 150+i*70, 300, 60) for i, name in enumerate(players)}
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if back_button.collidepoint(pos): assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "MAIN_MENU"
                input_active = input_box.collidepoint(pos)
                for name, rect in player_buttons.items():
                    if rect.collidepoint(pos): game.CURRENT_PLAYER_NAME = name; assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "MODE_SELECT"
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    if new_player_name and new_player_name not in players:
                        game.CURRENT_PLAYER_NAME = new_player_name; game.LEVEL_STARS[game.CURRENT_PLAYER_NAME]={}; save_data(game.LEVEL_STARS, Path(game.SAVE_FILE))
                        assets.sounds['win'].play(); await fade_transition(screen, assets, fade_in=False); return "MODE_SELECT"
                    elif new_player_name in players:
                        game.CURRENT_PLAYER_NAME = new_player_name; assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "MODE_SELECT"
                elif event.key == pygame.K_BACKSPACE: new_player_name = new_player_name[:-1]
                else: new_player_name += event.unicode
        screen.fill(assets.theme['BG']);
        if 'background' in assets.images: screen.blit(assets.images['background'], (0,0))
        title_surf = assets.font_large.render("SELECT PLAYER", True, assets.theme['TEXT']); screen.blit(title_surf, title_surf.get_rect(centerx=W/2, y=50))
        mouse_pos = pygame.mouse.get_pos()
        for name, rect in player_buttons.items(): draw_header_button(screen, rect, name, assets, toggled=(name == game.CURRENT_PLAYER_NAME or rect.collidepoint(mouse_pos)))
        pygame.draw.rect(screen, assets.theme['UI_BTN_HOVER'] if input_active else assets.theme['UI_BTN'], input_box, border_radius=8); pygame.draw.rect(screen, assets.theme['UI_BTN_SHADOW'], input_box, 2, border_radius=8)
        input_surf = assets.font_medium.render(new_player_name or "Enter new name...", True, assets.theme['UI_BTN_TEXT']); screen.blit(input_surf, input_surf.get_rect(center=input_box.center))
        draw_header_button(screen, back_button, "BACK", assets, toggled=back_button.collidepoint(mouse_pos))
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)

async def show_mode_select(screen: pygame.Surface, assets: AssetManager) -> str:
    await fade_transition(screen, assets, fade_in=True); W, H = screen.get_size()
    buttons = {"MAIN STORY": pygame.Rect(W//2-150, H//2-80, 300, 70), "COMMUNITY LEVELS": pygame.Rect(W//2-150, H//2+10, 300, 70)}
    back_button = pygame.Rect(20, 20, 100, 50)
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if back_button.collidepoint(pos): assets.sounds['button'].play(); return "PLAYER_SELECT"
                if buttons["MAIN STORY"].collidepoint(pos): assets.sounds['button'].play(); return "main"
                if buttons["COMMUNITY LEVELS"].collidepoint(pos): assets.sounds['button'].play(); return "custom"
        screen.fill(assets.theme['BG']);
        if 'background' in assets.images: screen.blit(assets.images['background'], (0,0))
        title_surf = assets.font_large.render("SELECT MODE", True, assets.theme['TEXT']); screen.blit(title_surf, title_surf.get_rect(centerx=W / 2, y=50))
        for name, rect in buttons.items(): draw_header_button(screen, rect, name, assets, toggled=rect.collidepoint(pygame.mouse.get_pos()))
        draw_header_button(screen, back_button, "BACK", assets, toggled=back_button.collidepoint(pygame.mouse.get_pos()))
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)

async def show_level_select(screen, assets, levels_to_display: List[dict], mode: str):
    await fade_transition(screen, assets, fade_in=True); W, H = screen.get_size();
    back_btn = pygame.Rect(20, 50, 100, 50); player_stars = game.get_stars_for_player(game.CURRENT_PLAYER_NAME)
    clock = pygame.time.Clock(); scroll_y = 0

    num_levels = len(levels_to_display)
    cols, btn_size, spacing = 8, 120, 20
    grid_start_y, grid_end_y = 150, H - 20
    available_height = grid_end_y - grid_start_y
    num_rows = (num_levels + cols - 1) // cols if num_levels > 0 else 0
    total_grid_height = num_rows * btn_size + max(0, num_rows - 1) * spacing
    max_scroll_y = max(0, total_grid_height - available_height)
    start_x = (W - (cols * btn_size + (cols - 1) * spacing)) // 2

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT", -1, None
            if event.type == pygame.MOUSEWHEEL:
                scroll_y -= event.y * 20; scroll_y = max(0, min(scroll_y, max_scroll_y))
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if back_btn.collidepoint(pos): assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "MODE_SELECT", -1, None
                for i in range(num_levels):
                    level_info = levels_to_display[i]
                    rect = pygame.Rect(start_x + (i % cols)*(btn_size+spacing), grid_start_y + (i // cols)*(btn_size+spacing) - scroll_y, btn_size, btn_size)
                    if rect.collidepoint(event.pos):
                        assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False)
                        return "PLAY", i, level_info['key']
        screen.fill(assets.theme['BG']);
        if 'background' in assets.images: screen.blit(assets.images['background'], (0,0))
        title = "Main Levels" if mode == "main" else "Community Levels"
        title_text = assets.font_large.render(title, True, assets.theme['TEXT']); screen.blit(title_text, title_text.get_rect(centerx=W // 2, y=50))
        draw_header_button(screen, back_btn, "BACK", assets, toggled=back_btn.collidepoint(pygame.mouse.get_pos()))
        
        grid_area = pygame.Rect(0, grid_start_y, W, available_height)
        grid_surface = pygame.Surface(grid_area.size, pygame.SRCALPHA)

        for i in range(num_levels):
            level_info = levels_to_display[i]
            rect = pygame.Rect(start_x + (i % cols)*(btn_size+spacing), (i // cols)*(btn_size+spacing), btn_size, btn_size)
            level_name = level_info.get('name', str(i+1))
            draw_header_button(grid_surface, rect, level_name, assets, toggled=rect.move(0, grid_start_y - scroll_y).collidepoint(pygame.mouse.get_pos()))
            star_count = player_stars.get(level_info['key'], 0)
            for s in range(3):
                star_center = (rect.centerx - 25 + s * 25, rect.bottom - 20)
                color = assets.theme['STAR'] if s < star_count else (80,90,100); draw_star(grid_surface, star_center, 10, color)
        
        screen.blit(grid_surface, (0, grid_start_y), (0, scroll_y, W, available_height))

        if max_scroll_y > 0:
            scrollbar_bg_rect = pygame.Rect(W - 20, grid_start_y, 15, available_height)
            pygame.draw.rect(screen, assets.theme['UI_BTN_SHADOW'], scrollbar_bg_rect, border_radius=7)
            handle_height = max(20, available_height * (available_height / total_grid_height))
            handle_y = scrollbar_bg_rect.y + (scroll_y / max_scroll_y) * (available_height - handle_height)
            scrollbar_handle_rect = pygame.Rect(W - 20, handle_y, 15, handle_height)
            draw_header_button(screen, scrollbar_handle_rect, "", assets)

        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)


async def play_level(screen, assets):
    global current_level_idx, current_level_key, current_level_mode, player_animator
    await fade_transition(screen, assets, fade_in=True)
    levels_list = game.BASE_LEVELS if current_level_mode == 'main' else game.CUSTOM_LEVELS
    level_data = levels_list[current_level_idx]['data']; solution = game.ALL_SOLUTIONS.get(current_level_key)
    game_state = game.GameState(current_level_key, level_data, solution, assets); W, H = screen.get_size()
    player_animator = AnimatedPlayer(assets.images['player_front'])
    level_text_str = f"Level {current_level_idx + 1}" if current_level_mode == 'main' else "Custom Level"
    level_text = assets.font_large.render(level_text_str, True, assets.theme['TEXT']); text_rect = level_text.get_rect(centerx=W // 2, centery=assets.config.HEADER_HEIGHT // 2); btn_size_h, btn_spacing = 60, 15; nav_buttons = {"menu": pygame.Rect(btn_spacing, text_rect.centery - btn_size_h//2, btn_size_h, btn_size_h), "prev": pygame.Rect(text_rect.left - btn_size_h - btn_spacing, text_rect.centery - btn_size_h//2, btn_size_h, btn_size_h), "next": pygame.Rect(text_rect.right + btn_spacing, text_rect.centery - btn_size_h//2, btn_size_h, btn_size_h)}; btn_w_b, btn_h_b, btn_s_b = 110, 40, 15; bottom_buttons = {"Restart": pygame.Rect(20, H - btn_h_b - 20, btn_w_b, btn_h_b), "Solve": pygame.Rect(20 + btn_w_b + btn_s_b, H - btn_h_b - 20, btn_w_b, btn_h_b)}; board_w = game_state.current_board.shape[1] * assets.config.TILE_SIZE; board_h = game_state.current_board.shape[0] * assets.config.TILE_SIZE; board_offset = ((W - board_w) // 2, assets.config.HEADER_HEIGHT + (H - assets.config.HEADER_HEIGHT - board_h) // 2); last_auto_move = time.time(); clock = pygame.time.Clock(); move_flash = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.KEYDOWN:
                key_map = {pygame.K_UP: (-1, 0), pygame.K_w: (-1, 0), pygame.K_DOWN: (1, 0), pygame.K_s: (1, 0), pygame.K_LEFT: (0, -1), pygame.K_a: (0, -1), pygame.K_RIGHT: (0, 1), pygame.K_d: (0, 1)}
                if event.key in key_map:
                    if game_state.perform_move(key_map[event.key]): player_animator.trigger_move(); move_flash = 5
                elif event.key == pygame.K_z or event.key == pygame.K_u: game_state.undo()
                elif event.key in (pygame.K_ESCAPE, pygame.K_m): await fade_transition(screen, assets, fade_in=False); return "MODE_SELECT"
                elif event.key == pygame.K_r: game_state.restart(); assets.sounds['button'].play()
                elif event.key == pygame.K_h and game_state.solution: game_state.start_solver(); assets.sounds['button'].play()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if nav_buttons["menu"].collidepoint(pos): assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "LEVEL_SELECT"
                if nav_buttons["prev"].collidepoint(pos) and current_level_idx > 0: current_level_idx -= 1; current_level_key = levels_list[current_level_idx]['key']; assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "PLAY"
                if nav_buttons["next"].collidepoint(pos) and current_level_idx < len(levels_list) - 1: current_level_idx += 1; current_level_key = levels_list[current_level_idx]['key']; assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "PLAY"
                if bottom_buttons["Restart"].collidepoint(pos): game_state.restart(); assets.sounds['button'].play()
                if bottom_buttons["Solve"].collidepoint(pos) and game_state.solution: game_state.start_solver(); assets.sounds['button'].play()
        if game_state.auto_play and time.time() - last_auto_move > game_state.auto_play_speed: game_state.step_solver(); player_animator.trigger_move(); move_flash = 5; last_auto_move = time.time()
        screen.fill(assets.theme['BG'])
        if 'background' in assets.images: screen.blit(assets.images['background'],(0,0))
        if move_flash > 0: flash_surface = pygame.Surface((W, H)); flash_surface.set_alpha(move_flash * 20); flash_surface.fill((255, 255, 255)); screen.blit(flash_surface, (0, 0)); move_flash -= 1
        draw_board_and_objects(screen, game_state.current_board, assets, board_offset, target_mask=game_state.target_mask, player_direction=game_state.player_direction)
        screen.blit(level_text, text_rect); draw_header_button(screen, nav_buttons['menu'], 'II', assets); draw_header_button(screen, nav_buttons['prev'], '<', assets, enabled=current_level_idx > 0); draw_header_button(screen, nav_buttons['next'], '>', assets, enabled=current_level_idx < len(levels_list) - 1)
        for name, rect in bottom_buttons.items(): draw_header_button(screen, rect, name, assets, enabled=not (name == "Solve" and not game_state.solution))
        elapsed_time = time.time() - (game_state.win_time if game_state.is_won else game_state.start_time); moves_count = len(game_state.move_stack) - 1; score_text = f"Moves: {moves_count} | Time: {int(elapsed_time)}"; score_surf = assets.font_small.render(score_text, True, assets.theme['TEXT']); screen.blit(score_surf, score_surf.get_rect(right=W - 20, bottom=H - 20))
        if game_state.is_won:
            win_text = assets.font_large.render("Level Complete!", True, assets.theme['WIN']); screen.blit(win_text, win_text.get_rect(centerx=W // 2, bottom=H - 80))
            player_stars = game.get_stars_for_player(game.CURRENT_PLAYER_NAME)
            for s in range(3): star_center = (W // 2 - 40 + s * 40, H - 45); color = assets.theme['STAR'] if s < player_stars.get(game_state.level_key, 0) else (80, 90, 100); draw_star(screen, star_center, 20, color)
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)
    player_animator = None

async def level_editor(screen, assets, level_to_edit_idx, level_data):
    await fade_transition(screen, assets, fade_in=True); W, H = screen.get_size(); editor_w, editor_h = 20, 15; ts = assets.config.TILE_SIZE
    if level_data: board = get_initial_board(level_data); editor_h, editor_w = board.shape
    else: board = np.full((editor_h, editor_h), game.GameObject.EMPTY.value, dtype=int)
    paint_tools = [game.GameObject.WALL, game.GameObject.EMPTY]; stamp_tools = [game.GameObject.TARGET, game.GameObject.BOX, game.GameObject.PLAYER]
    current_paint_tool = game.GameObject.WALL; held_stamp = None
    palette_w = 200; board_offset_x = (W - palette_w - (editor_w * ts)) // 2; board_offset_y = (H - (editor_h * ts)) // 2; palette_x = board_offset_x + (editor_w * ts) + 20
    all_tools = paint_tools + stamp_tools
    tool_rects = {tool: pygame.Rect(palette_x, 100 + i * 70, 60, 60) for i, tool in enumerate(all_tools)}
    save_btn = pygame.Rect(palette_x, H - 220, 180, 50); back_btn = pygame.Rect(palette_x, H - 80, 180, 50)
    mouse_down = False; message = ""; message_color = 'red'; message_timer = 0; clock = pygame.time.Clock();
    while True:
        mouse_pos = pygame.mouse.get_pos()
        if message_timer > 0: message_timer -= 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
                if back_btn.collidepoint(mouse_pos): await fade_transition(screen, assets, fade_in=False); return "MAIN_MENU"
                if save_btn.collidepoint(mouse_pos):
                    p_count=np.count_nonzero(board==game.GameObject.PLAYER.value); b_count=np.count_nonzero(board==game.GameObject.BOX.value); t_count=np.count_nonzero(board==game.GameObject.TARGET.value)
                    if p_count == 1 and b_count > 0 and b_count == t_count:
                        if game.solve_new_level(board.tolist()):
                            game.save_custom_level(board.tolist())
                            await fade_transition(screen, assets, fade_in=False); return "MODE_SELECT"
                        else: message="Unsolvable!"; message_color=assets.theme['EDITOR_MSG_BAD']; message_timer=120
                    else: message="Invalid Layout!"; message_color=assets.theme['EDITOR_MSG_BAD']; message_timer=120
                clicked_on_board = True
                for tool, rect in tool_rects.items():
                    if rect.collidepoint(mouse_pos):
                        clicked_on_board = False
                        if tool in stamp_tools: held_stamp = tool; assets.sounds['button'].play()
                        else: current_paint_tool = tool; held_stamp = None; assets.sounds['button'].play()
                if clicked_on_board:
                    grid_col = (mouse_pos[0] - board_offset_x) // ts; grid_row = (mouse_pos[1] - board_offset_y) // ts
                    if 0 <= grid_row < editor_h and 0 <= grid_col < editor_w:
                        if held_stamp is not None:
                            if held_stamp == game.GameObject.PLAYER: board[board == game.GameObject.PLAYER.value] = game.GameObject.EMPTY.value
                            board[grid_row, grid_col] = held_stamp.value; held_stamp = None; assets.sounds['place_box'].play()
                        else: board[grid_row, grid_col] = current_paint_tool.value; assets.sounds['move'].play()
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1: mouse_down = False
            if event.type == pygame.MOUSEMOTION and mouse_down and held_stamp is None:
                grid_col = (mouse_pos[0] - board_offset_x) // ts; grid_row = (mouse_pos[1] - board_offset_y) // ts
                if 0 <= grid_row < editor_h and 0 <= grid_col < editor_w:
                    board[grid_row, grid_col] = current_paint_tool.value; assets.sounds['move'].play()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: await fade_transition(screen, assets, fade_in=False); return "MAIN_MENU"
        screen.fill(assets.theme['BG']);
        if 'background' in assets.images: screen.blit(assets.images['background'], (0,0))
        draw_board_and_objects(screen, board, assets, (board_offset_x, board_offset_y), is_editor=True)
        p_count=np.count_nonzero(board==game.GameObject.PLAYER.value); b_count=np.count_nonzero(board==game.GameObject.BOX.value); t_count=np.count_nonzero(board==game.GameObject.TARGET.value)
        valid_level = p_count == 1 and b_count > 0 and b_count == t_count
        if p_count!=1: help_text=f"Needs {1-p_count} Player"
        elif b_count==0: help_text="Needs Boxes"
        elif b_count!=t_count: help_text=f"{abs(b_count-t_count)} more {'Targets' if b_count > t_count else 'Boxes'}"
        else: help_text="Ready to Test!"
        help_surf = assets.font_small.render(help_text, True, assets.theme['WIN'] if valid_level else assets.theme['EDITOR_TEXT'])
        screen.blit(help_surf, help_surf.get_rect(centerx=palette_x + 90, y=H - 260))
        if message_timer>0: msg_surf = assets.font_small.render(message, True, message_color); screen.blit(msg_surf, msg_surf.get_rect(centerx=palette_x + 90, y=H - 280))
        for tool, rect in tool_rects.items():
            image_key = {game.GameObject.WALL: 'wall', game.GameObject.EMPTY: 'floor', game.GameObject.TARGET: 'target', game.GameObject.BOX: 'box', game.GameObject.PLAYER: 'player_face'}.get(tool)
            is_toggled = (tool in paint_tools and tool == current_paint_tool and held_stamp is None) or (tool == held_stamp)
            draw_header_button(screen, rect, "", assets, toggled=is_toggled)
            if image_key in assets.images: screen.blit(pygame.transform.smoothscale(assets.images[image_key], (50,50)), (rect.x+5, rect.y+5))
        if held_stamp:
            # THIS IS THE FIX: The stamp that follows the mouse is now the correct game sprite
            stamp_image_key = {game.GameObject.TARGET: 'target', game.GameObject.BOX: 'box', game.GameObject.PLAYER: 'player_front'}.get(held_stamp)
            if stamp_image_key in assets.images: sprite = assets.images[stamp_image_key]; sprite.set_alpha(150); screen.blit(sprite, (mouse_pos[0] - ts//2, mouse_pos[1] - ts//2)); sprite.set_alpha(255)
        draw_header_button(screen, save_btn, "SAVE & TEST", assets, enabled=valid_level); draw_header_button(screen, back_btn, "BACK", assets)
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)
# --- END OF CORRECTED FILE ui.py ---