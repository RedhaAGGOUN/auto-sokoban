# --- START OF COMPLETE AND FINAL ui.py ---

import asyncio
import pygame
import numpy as np
import time
from typing import Tuple, Optional, List
from pathlib import Path
import random
import os
import re
from datetime import datetime

from config import GameConfig, DEFAULT_THEME as THEME
from assets import AssetManager
import game
from core import get_initial_board
from save_load import save_data, load_data

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
        self.sprite = pygame.transform.scale(self.original_sprite, (squash_w, squash_w))
    def trigger_move(self): self.move_timer = 10

class FloatingObject:
    def __init__(self, W: int, H: int, image: pygame.Surface):
        self.W, self.H = W, H
        self.sprite = pygame.transform.scale(image, (random.randint(30, 70), random.randint(30, 70)))
        self.x, self.y = random.randint(0, W), random.randint(0, H)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-1.5, -0.5)
    def update(self, W, H):
        self.W, self.H = W, H
        self.x += self.speed_x; self.y += self.speed_y
        if self.y < -self.sprite.get_height() or self.x < -self.sprite.get_width() or self.x > self.W:
            self.y = self.H; self.x = random.randint(0, self.W)

def draw_board_and_objects(screen, board, assets, offset=(0,0), is_editor=False, target_mask=None, player_direction=(1,0)):
    h, w = board.shape; start_x, start_y = offset; bg_tile = assets.images['floor']
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
                    player_animator.set_sprite(player_sprite); player_animator.update(); player_sprite = player_animator.sprite
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

def draw_header_button(screen, rect, symbol_text, assets, enabled=True, toggled=False, font=None):
    font = font or assets.font_medium
    theme = assets.theme; shadow_rect = rect.copy(); shadow_rect.y += 3
    pygame.draw.rect(screen, theme['UI_BTN_SHADOW'], shadow_rect, border_radius=8)
    base_color = theme['UI_BTN_HOVER'] if toggled else theme['UI_BTN']
    color = base_color if enabled else tuple(int(c * 0.8) for c in base_color)
    gradient_color = tuple(int(c * 0.9) for c in color); draw_gradient_rect(screen, rect, color, gradient_color)
    if toggled: pygame.draw.rect(screen, theme['UI_BTN_TOGGLE_ON'], rect, 2, border_radius=8)
    text_surf = font.render(symbol_text, True, theme['UI_BTN_TEXT']); screen.blit(text_surf, text_surf.get_rect(center=rect.center))

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
        overlay.set_alpha(int(alpha * 255)); overlay.fill(assets.theme['BG']); screen.blit(overlay, (0, 0)); pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)

# --- UI Screens ---
async def show_splash_screen(screen: pygame.Surface, assets: AssetManager) -> str:
    await fade_transition(screen, assets, fade_in=True)
    clock = pygame.time.Clock()
    
    while True:
        W, H = screen.get_size()
        logo_rect = assets.images['logo'].get_rect(center=(W//2, H//3)) if 'logo' in assets.images and assets.images['logo'] else pygame.Rect(0,0,0,0)
        title_surf = assets.font_title.render("SOKOBAN", True, assets.theme['TEXT'])
        title_rect = title_surf.get_rect(center=(W//2, logo_rect.bottom + 80 if logo_rect.height > 0 else H//2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "MAIN_MENU"
        
        screen.fill(assets.theme['BG']);
        if 'background' in assets.images: screen.blit(assets.images['background'],(0,0))
        if 'logo' in assets.images and assets.images['logo']: screen.blit(assets.images['logo'], logo_rect)
        color = assets.theme['UI_BTN_HOVER'] if title_rect.collidepoint(pygame.mouse.get_pos()) else assets.theme['TEXT']
        screen.blit(assets.font_title.render("SOKOBAN", True, color), title_rect)
        
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)

async def show_main_menu(screen: pygame.Surface, assets: AssetManager) -> str:
    await fade_transition(screen, assets, fade_in=True)
    floating_images = [assets.images['box'], assets.images['wall'], assets.images['target'], assets.images['player_face']]
    floating_objects = [FloatingObject(screen.get_width(), screen.get_height(), random.choice(floating_images)) for _ in range(20)]
    credit_font = pygame.font.SysFont(assets.config.FONT_NAME, 20, bold=True)
    credit_surf = credit_font.render("Made by Redha & Rooney - June 2025 @La Plateforme_", True, assets.theme['TEXT'])
    clock = pygame.time.Clock()
    
    while True:
        W, H = screen.get_size()
        buttons = {
            "PLAY": pygame.Rect(W//2-150, H//2-80, 300, 70), 
            "BUILD NEW BOARD": pygame.Rect(W//2-150, H//2+10, 300, 70), 
            "HIGH SCORES": pygame.Rect(W//2-150, H//2+100, 300, 70), 
            "QUIT": pygame.Rect(W//2-150, H//2+190, 300, 70)
        }
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if buttons["PLAY"].collidepoint(pos): assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "PLAYER_SELECT"
                if buttons["BUILD NEW BOARD"].collidepoint(pos): assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "EDITOR"
                if buttons["HIGH SCORES"].collidepoint(pos): assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "HIGH_SCORES"
                if buttons["QUIT"].collidepoint(pos): assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "QUIT"
        
        screen.fill(assets.theme['BG']);
        if 'background' in assets.images: screen.blit(assets.images['background'], (0,0))
        for obj in floating_objects: 
            obj.update(W, H)
            screen.blit(obj.sprite, (obj.x, obj.y))
        
        if 'logo' in assets.images and assets.images['logo']:
            logo_rect = assets.images['logo'].get_rect(center=(W//2, H//4)); screen.blit(assets.images['logo'], logo_rect)
        
        for name, rect in buttons.items(): 
            draw_header_button(screen, rect, name, assets, toggled=rect.collidepoint(pygame.mouse.get_pos()))
        
        screen.blit(credit_surf, credit_surf.get_rect(centerx=W // 2, bottom=H - 20))
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)

async def show_confirmation_dialog(screen, assets, message: str) -> bool:
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA); overlay.fill((0,0,0,180))
    clock = pygame.time.Clock()
    
    while True:
        W, H = screen.get_size()
        popup_rect = pygame.Rect(W//2 - 250, H//2 - 100, 500, 200)
        yes_button = pygame.Rect(popup_rect.left + 50, popup_rect.bottom - 70, 150, 50)
        no_button = pygame.Rect(popup_rect.right - 200, popup_rect.bottom - 70, 150, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if yes_button.collidepoint(event.pos): assets.sounds['button'].play(); return True
                if no_button.collidepoint(event.pos): assets.sounds['button'].play(); return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: assets.sounds['button'].play(); return True
                if event.key == pygame.K_ESCAPE: assets.sounds['button'].play(); return False
        
        screen.blit(overlay, (0,0)); draw_header_button(screen, popup_rect, "", assets)
        msg_surf = assets.font_medium.render(message, True, assets.theme['TEXT']); screen.blit(msg_surf, msg_surf.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 40))
        draw_header_button(screen, yes_button, "Yes", assets, toggled=yes_button.collidepoint(pygame.mouse.get_pos()))
        draw_header_button(screen, no_button, "No", assets, toggled=no_button.collidepoint(pygame.mouse.get_pos()))
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)

async def show_rank_popup(screen, assets, old_rank, new_rank):
    if new_rank < old_rank and new_rank <= 3: assets.sounds.get('new_highscore', lambda:None).play()
    else: assets.sounds['button'].play()
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA); overlay.fill((0,0,0,180))
    clock = pygame.time.Clock(); start_time = time.time()
    
    while time.time() - start_time < 5:
        W, H = screen.get_size()
        popup_rect = pygame.Rect(W//2 - 250, H//2 - 100, 500, 200)
        overlay = pygame.transform.scale(overlay, (W,H))

        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN): return
        
        screen.blit(overlay, (0,0)); draw_header_button(screen, popup_rect, "", assets)
        if new_rank < old_rank: msg = f"You are now ranked #{new_rank}!"; color = assets.theme['WIN']
        else: msg = f"You are still ranked #{new_rank}."; color = assets.theme['TEXT']
        rank_surf = assets.font_large.render("RANKING UPDATE", True, assets.theme['TEXT']); screen.blit(rank_surf, rank_surf.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 20))
        msg_surf = assets.font_medium.render(msg, True, color); screen.blit(msg_surf, msg_surf.get_rect(center=popup_rect.center))
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)

async def show_high_scores(screen, assets):
    await fade_transition(screen, assets, fade_in=True)
    scores = game.get_player_rankings(); clock = pygame.time.Clock()
    
    while True:
        W, H = screen.get_size()
        back_button = pygame.Rect(W//2-150, H-120, 300, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and back_button.collidepoint(event.pos):
                assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "MAIN_MENU"
        
        screen.fill(assets.theme['BG']);
        if 'background' in assets.images: screen.blit(assets.images['background'], (0,0))
        if 'logo_small' in assets.images and assets.images['logo_small']: 
            logo_rect = assets.images['logo_small'].get_rect(topright=(W-20, 20)); screen.blit(assets.images['logo_small'], logo_rect)
        
        title_surf = assets.font_large.render("HIGH SCORES", True, assets.theme['TEXT']); screen.blit(title_surf, title_surf.get_rect(centerx=W/2, y=H*0.1))
        
        header_y = H * 0.2
        rank_x, name_x, stars_x, date_x = W/2 - 300, W/2 - 200, W/2 + 100, W/2 + 200
        
        rank_header = assets.font_medium.render("Rank", True, assets.theme['TEXT']); screen.blit(rank_header, rank_header.get_rect(centerx=rank_x, centery=header_y))
        name_header = assets.font_medium.render("Name", True, assets.theme['TEXT']); screen.blit(name_header, name_header.get_rect(centerx=name_x, centery=header_y))
        stars_header = assets.font_medium.render("Stars", True, assets.theme['TEXT']); screen.blit(stars_header, stars_header.get_rect(centerx=stars_x, centery=header_y))
        date_header = assets.font_medium.render("Last Activity", True, assets.theme['TEXT']); screen.blit(date_header, date_header.get_rect(centerx=date_x + 50, centery=header_y))

        for i, score_data in enumerate(scores[:10]):
            y_pos = H*0.25 + (i+1) * 50
            rank_surf = assets.font_medium.render(f"#{i+1}", True, assets.theme['TEXT']); screen.blit(rank_surf, rank_surf.get_rect(centerx=rank_x, centery=y_pos))
            name_surf = assets.font_medium.render(score_data['name'], True, assets.theme['TEXT']); screen.blit(name_surf, name_surf.get_rect(centerx=name_x, centery=y_pos))
            star_surf = assets.font_medium.render(f"{score_data['stars']} ★", True, assets.theme['STAR']); screen.blit(star_surf, star_surf.get_rect(centerx=stars_x, centery=y_pos))
            date_surf = assets.font_small.render(score_data['last_played'], True, assets.theme['TEXT']); screen.blit(date_surf, date_surf.get_rect(centerx=date_x + 50, centery=y_pos))
        
        draw_header_button(screen, back_button, "BACK", assets, toggled=back_button.collidepoint(pygame.mouse.get_pos()))
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)

async def show_player_select_screen(screen, assets):
    await fade_transition(screen, assets, fade_in=True)
    players = list(game.LEVEL_STARS.keys())
    new_player_name = ""; input_active = False; clock = pygame.time.Clock()
    
    while True:
        W, H = screen.get_size()
        player_buttons = {name: pygame.Rect(W//2-150, 150+i*70, 300, 60) for i, name in enumerate(players)}
        input_box = pygame.Rect(W//2-150, H-200, 300, 50)
        back_button = pygame.Rect(W//2-150, H-120, 300, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if input_box.collidepoint(pos):
                    input_active = True
                else:
                    input_active = False
                    if back_button.collidepoint(pos):
                        assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "MAIN_MENU"
                    for name, rect in player_buttons.items():
                        if rect.collidepoint(pos):
                            game.CURRENT_PLAYER_NAME = name
                            assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "MODE_SELECT"

            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    clean_name = new_player_name.strip()
                    if clean_name and clean_name not in players:
                        game.CURRENT_PLAYER_NAME = clean_name
                        game.LEVEL_STARS[game.CURRENT_PLAYER_NAME] = {
                            'scores': {}, 
                            'last_played': datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        save_data(game.LEVEL_STARS, Path(game.SAVE_FILE))
                        assets.sounds['win'].play(); await fade_transition(screen, assets, fade_in=False); return "MODE_SELECT"
                    elif clean_name in players:
                        game.CURRENT_PLAYER_NAME = clean_name
                        assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "MODE_SELECT"
                    new_player_name = ""
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    new_player_name = new_player_name[:-1]
                elif len(new_player_name) < 20:
                    new_player_name += event.unicode
        
        screen.fill(assets.theme['BG']);
        if 'background' in assets.images: screen.blit(assets.images['background'], (0,0))
        if 'logo_small' in assets.images and assets.images['logo_small']: 
            logo_rect=assets.images['logo_small'].get_rect(topright=(W-20,20)); screen.blit(assets.images['logo_small'],logo_rect)
        
        title_surf = assets.font_large.render("SELECT PLAYER", True, assets.theme['TEXT']); screen.blit(title_surf, title_surf.get_rect(centerx=W/2, y=50))
        for name, rect in player_buttons.items(): 
            draw_header_button(screen, rect, name, assets, toggled=(name == game.CURRENT_PLAYER_NAME or rect.collidepoint(pygame.mouse.get_pos())))
        
        pygame.draw.rect(screen, assets.theme['UI_BTN_HOVER'] if input_active else assets.theme['UI_BTN'], input_box, border_radius=8); pygame.draw.rect(screen, assets.theme['UI_BTN_SHADOW'], input_box, 2, border_radius=8)
        
        display_text = new_player_name
        if not input_active and not new_player_name:
            display_text = "Enter new name..."

        input_surf = assets.font_medium.render(display_text, True, assets.theme['UI_BTN_TEXT']); screen.blit(input_surf, input_surf.get_rect(center=input_box.center))
        draw_header_button(screen, back_button, "BACK", assets, toggled=back_button.collidepoint(pygame.mouse.get_pos()))
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)

async def show_mode_select(screen, assets):
    await fade_transition(screen, assets, fade_in=True)
    clock = pygame.time.Clock()
    
    while True:
        W, H = screen.get_size()
        buttons = {
            "MAIN STORY": pygame.Rect(W//2-150, H//2-80, 300, 70), 
            "COMMUNITY LEVELS": pygame.Rect(W//2-150, H//2+10, 300, 70)
        }
        back_button = pygame.Rect(20, 20, 100, 50)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if back_button.collidepoint(pos): assets.sounds['button'].play(); return "PLAYER_SELECT"
                if buttons["MAIN STORY"].collidepoint(pos): assets.sounds['button'].play(); return "main"
                if buttons["COMMUNITY LEVELS"].collidepoint(pos): assets.sounds['button'].play(); return "custom"
        
        screen.fill(assets.theme['BG']);
        if 'background' in assets.images: screen.blit(assets.images['background'], (0,0))
        if 'logo_small' in assets.images and assets.images['logo_small']: 
            logo_rect=assets.images['logo_small'].get_rect(topright=(W-20,20)); screen.blit(assets.images['logo_small'],logo_rect)
        
        title_surf = assets.font_large.render("SELECT MODE", True, assets.theme['TEXT']); screen.blit(title_surf, title_surf.get_rect(centerx=W / 2, y=50))
        for name, rect in buttons.items(): 
            draw_header_button(screen, rect, name, assets, toggled=rect.collidepoint(pygame.mouse.get_pos()))
        draw_header_button(screen, back_button, "BACK", assets, toggled=back_button.collidepoint(pygame.mouse.get_pos()))
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)

async def show_level_select(screen, assets, levels_to_display: List[dict], mode: str):
    await fade_transition(screen, assets, fade_in=True)
    player_stars = game.get_stars_for_player(game.CURRENT_PLAYER_NAME)
    clock = pygame.time.Clock(); scroll_y = 0; selected_level_idx = None
    
    while True:
        W, H = screen.get_size()
        back_btn = pygame.Rect(20, 50, 100, 50)
        num_levels = len(levels_to_display); cols, btn_size, spacing = 8, 120, 20
        grid_start_y, grid_end_y = 150, H - 100; available_height = grid_end_y - grid_start_y
        num_rows = (num_levels + cols - 1) // cols if num_levels > 0 else 0
        total_grid_height = num_rows * btn_size + max(0, num_rows - 1) * spacing; max_scroll_y = max(0, total_grid_height - available_height)
        start_x = (W - (cols * btn_size + (cols - 1) * spacing)) // 2
        
        play_button = pygame.Rect(W//2 - 200, H - 80, 180, 50)
        delete_button = pygame.Rect(W//2 + 20, H - 80, 180, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT", None, None
            if event.type == pygame.MOUSEWHEEL: scroll_y -= event.y * 20; scroll_y = max(0, min(scroll_y, max_scroll_y))
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if back_btn.collidepoint(pos): assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "MODE_SELECT", None, None
                
                if selected_level_idx is not None:
                    if play_button.collidepoint(pos):
                        level_info = levels_to_display[selected_level_idx]; assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False)
                        return "PLAY", selected_level_idx, level_info['key']
                    
                    can_delete = mode == 'custom' and levels_to_display[selected_level_idx].get('creator') == game.CURRENT_PLAYER_NAME
                    if can_delete and delete_button.collidepoint(pos):
                        if await show_confirmation_dialog(screen, assets, "Delete this level?"):
                            game.delete_custom_level(levels_to_display[selected_level_idx]['key']); return "MODE_SELECT", None, None
                
                selected_level_idx_before = selected_level_idx
                selected_level_idx = None
                for i in range(num_levels):
                    rect = pygame.Rect(start_x + (i % cols)*(btn_size+spacing), grid_start_y + (i // cols)*(btn_size+spacing) - scroll_y, btn_size, btn_size)
                    if rect.collidepoint(pos) and grid_start_y < pos[1] < grid_end_y:
                        if i != selected_level_idx_before: assets.sounds['button'].play()
                        selected_level_idx = i; break
                            
        screen.fill(assets.theme['BG']);
        if 'background' in assets.images: screen.blit(assets.images['background'], (0,0))
        if 'logo_small' in assets.images and assets.images['logo_small']: logo_rect = assets.images['logo_small'].get_rect(topright=(W-20, 20)); screen.blit(assets.images['logo_small'], logo_rect)
        title = "Main Levels" if mode == "main" else "Community Levels"; title_text = assets.font_large.render(title, True, assets.theme['TEXT']); screen.blit(title_text, title_text.get_rect(centerx=W // 2, y=50))
        draw_header_button(screen, back_btn, "BACK", assets, toggled=back_btn.collidepoint(pygame.mouse.get_pos()))
        
        grid_clip_rect = pygame.Rect(0, grid_start_y, W, available_height)
        
        for i in range(num_levels):
            level_info = levels_to_display[i]
            rect_on_screen = pygame.Rect(start_x + (i % cols)*(btn_size+spacing), grid_start_y + (i // cols)*(btn_size+spacing) - scroll_y, btn_size, btn_size)
            
            if grid_clip_rect.colliderect(rect_on_screen):
                is_selected = i == selected_level_idx
                level_name = level_info.get('name', str(i+1))
                font_to_use = assets.font_tiny if len(level_name) > 12 else assets.font_medium
                draw_header_button(screen, rect_on_screen, level_name, assets, toggled=is_selected or rect_on_screen.collidepoint(pygame.mouse.get_pos()), font=font_to_use)
                star_count = player_stars.get(level_info['key'], 0)
                for s in range(3):
                    star_center = (rect_on_screen.centerx - 25 + s * 25, rect_on_screen.bottom - 20)
                    color = assets.theme['STAR'] if s < star_count else (80,90,100)
                    draw_star(screen, star_center, 10, color)

        if selected_level_idx is not None:
            draw_header_button(screen, play_button, "PLAY", assets, toggled=play_button.collidepoint(pygame.mouse.get_pos()))
            can_delete = mode == 'custom' and levels_to_display[selected_level_idx].get('creator') == game.CURRENT_PLAYER_NAME
            draw_header_button(screen, delete_button, "DELETE", assets, enabled=can_delete, toggled=can_delete and delete_button.collidepoint(pygame.mouse.get_pos()))

        if max_scroll_y > 0:
            scrollbar_bg_rect = pygame.Rect(W - 20, grid_start_y, 15, available_height); pygame.draw.rect(screen, assets.theme['UI_BTN_SHADOW'], scrollbar_bg_rect, border_radius=7)
            handle_height = max(20, available_height * (available_height / total_grid_height)); handle_y = scrollbar_bg_rect.y + (scroll_y / max_scroll_y) * (available_height - handle_height)
            scrollbar_handle_rect = pygame.Rect(W - 20, handle_y, 15, handle_height); draw_header_button(screen, scrollbar_handle_rect, "", assets)
        
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)

async def play_level(screen, assets, level_key, level_idx, mode):
    global player_animator
    pygame.mixer.music.fadeout(1000)
    await fade_transition(screen, assets, fade_in=True)
    levels_list = game.BASE_LEVELS if mode == 'main' else game.CUSTOM_LEVELS
    level_data = next((lvl['data'] for lvl in levels_list if lvl['key'] == level_key), None)
    if level_data is None: return "MODE_SELECT", None, None
    level_name_display = next((lvl['name'] for lvl in levels_list if lvl['key'] == level_key), "Sokoban")

    game_state = game.GameState(level_key, level_data, assets)
    player_animator = AnimatedPlayer(assets.images['player_front'])
    
    last_auto_move = time.time(); clock = pygame.time.Clock(); move_flash = 0
    rankings = game.get_player_rankings(); old_rank = next((i+1 for i, p in enumerate(rankings) if p['name'] == game.CURRENT_PLAYER_NAME), len(rankings)+1)
    
    while True:
        W, H = screen.get_size()
        level_text = assets.font_large.render(level_name_display, True, assets.theme['TEXT'])
        text_rect = level_text.get_rect(centerx=W // 2, centery=assets.config.HEADER_HEIGHT // 2)
        btn_size_h, btn_spacing = 60, 15
        nav_buttons = {
            "menu": pygame.Rect(btn_spacing, text_rect.centery - btn_size_h//2, btn_size_h, btn_size_h), 
            "prev": pygame.Rect(text_rect.left - btn_size_h - btn_spacing, text_rect.centery - btn_size_h//2, btn_size_h, btn_size_h), 
            "next": pygame.Rect(text_rect.right + btn_spacing, text_rect.centery - btn_size_h//2, btn_size_h, btn_size_h)
        }
        btn_w_b, btn_h_b, btn_s_b = 110, 40, 15
        bottom_buttons = {
            "Restart": pygame.Rect(20, H - btn_h_b - 20, btn_w_b, btn_h_b), 
            "Solve": pygame.Rect(20 + btn_w_b + btn_s_b, H - btn_h_b - 20, btn_w_b, btn_h_b)
        }
        board_w = game_state.current_board.shape[1] * assets.config.TILE_SIZE
        board_h = game_state.current_board.shape[0] * assets.config.TILE_SIZE
        board_offset = ((W - board_w) // 2, assets.config.HEADER_HEIGHT + (H - assets.config.HEADER_HEIGHT - board_h) // 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT", None, None
            if event.type == pygame.KEYDOWN:
                key_map = {pygame.K_UP: (-1, 0), pygame.K_w: (-1, 0), pygame.K_DOWN: (1, 0), pygame.K_s: (1, 0), pygame.K_LEFT: (0, -1), pygame.K_a: (0, -1), pygame.K_RIGHT: (0, 1), pygame.K_d: (0, 1)}
                if event.key in key_map:
                    if game_state.perform_move(key_map[event.key]): player_animator.trigger_move(); move_flash = 5
                elif event.key == pygame.K_z or event.key == pygame.K_u: game_state.undo()
                elif event.key in (pygame.K_ESCAPE, pygame.K_m):
                    new_rank = next((i+1 for i,p in enumerate(game.get_player_rankings()) if p['name']==game.CURRENT_PLAYER_NAME), old_rank+1)
                    await show_rank_popup(screen, assets, old_rank, new_rank); await fade_transition(screen, assets, fade_in=False); return "MODE_SELECT", None, None
                elif event.key == pygame.K_r: game_state.restart(); assets.sounds['button'].play()
                elif event.key == pygame.K_h: assets.sounds['button'].play(); game_state.start_solver()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if nav_buttons["menu"].collidepoint(pos):
                    new_rank = next((i+1 for i,p in enumerate(game.get_player_rankings()) if p['name']==game.CURRENT_PLAYER_NAME), old_rank+1)
                    await show_rank_popup(screen, assets, old_rank, new_rank); await fade_transition(screen, assets, fade_in=False); return "MODE_SELECT", None, None
                if nav_buttons["prev"].collidepoint(pos) and level_idx > 0:
                    new_idx = level_idx - 1; new_key = levels_list[new_idx]['key']; assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "PLAY", new_idx, new_key
                if nav_buttons["next"].collidepoint(pos) and level_idx < len(levels_list) - 1:
                    new_idx = level_idx + 1; new_key = levels_list[new_idx]['key']; assets.sounds['button'].play(); await fade_transition(screen, assets, fade_in=False); return "PLAY", new_idx, new_key
                if bottom_buttons["Restart"].collidepoint(pos): game_state.restart(); assets.sounds['button'].play()
                if bottom_buttons["Solve"].collidepoint(pos): assets.sounds['button'].play(); game_state.start_solver()

        if game_state.auto_play and time.time() - last_auto_move > game_state.auto_play_speed: game_state.step_solver(); player_animator.trigger_move(); move_flash = 5; last_auto_move = time.time()
        screen.fill(assets.theme['BG'])
        if 'background' in assets.images: screen.blit(assets.images['background'],(0,0))
        if move_flash > 0: flash_surface = pygame.Surface((W, H)); flash_surface.set_alpha(move_flash * 20); flash_surface.fill((255, 255, 255)); screen.blit(flash_surface, (0, 0)); move_flash -= 1
        draw_board_and_objects(screen, game_state.current_board, assets, board_offset, target_mask=game_state.target_mask, player_direction=game_state.player_direction)
        screen.blit(level_text, text_rect); draw_header_button(screen, nav_buttons['menu'], 'Menu', assets); draw_header_button(screen, nav_buttons['prev'], '<', assets, enabled=level_idx > 0); draw_header_button(screen, nav_buttons['next'], '>', assets, enabled=level_idx < len(levels_list) - 1)
        for name, rect in bottom_buttons.items(): draw_header_button(screen, rect, name, assets)
        elapsed_time = time.time() - (game_state.win_time if game_state.is_won else game_state.start_time); moves_count = len(game_state.move_stack) - 1; score_text = f"Moves: {moves_count} | Time: {int(elapsed_time)}"; score_surf = assets.font_small.render(score_text, True, assets.theme['TEXT']); screen.blit(score_surf, score_surf.get_rect(right=W-20, bottom=H-20))
        if game_state.is_won:
            win_text = assets.font_large.render("Level Complete!", True, assets.theme['WIN']); screen.blit(win_text, win_text.get_rect(centerx=W // 2, bottom=H - 80))
            player_stars = game.get_stars_for_player(game.CURRENT_PLAYER_NAME)
            for s in range(3): star_center = (W//2 - 40 + s * 40, H - 45); color = assets.theme['STAR'] if s < player_stars.get(game_state.level_key, 0) else (80, 90, 100); draw_star(screen, star_center, 20, color)
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)
    player_animator = None

async def level_editor(screen, assets):
    await fade_transition(screen, assets, fade_in=True)
    EDITOR_W, EDITOR_H = 20, 15
    board = np.full((EDITOR_H, EDITOR_W), game.GameObject.EMPTY.value, dtype=int)
    paint_tools = [game.GameObject.WALL, game.GameObject.EMPTY]
    stamp_tools = [game.GameObject.TARGET, game.GameObject.BOX, game.GameObject.PLAYER]
    all_tools = paint_tools + stamp_tools
    tool_names = {game.GameObject.EMPTY:"Eraser", game.GameObject.WALL:"Wall", game.GameObject.TARGET:"Target", game.GameObject.BOX:"Box", game.GameObject.PLAYER:"Player"}
    current_tool = game.GameObject.WALL
    
    mouse_down = False; message = ""; message_color = 'red'; message_timer = 0; clock = pygame.time.Clock()
    
    while True:
        W, H = screen.get_size()
        ts = assets.config.TILE_SIZE
        
        palette_w = 220
        palette_x = W - palette_w + 10
        board_pixel_w = EDITOR_W * ts
        board_pixel_h = EDITOR_H * ts
        board_area_w = W - palette_w - 40
        board_offset_x = 20 + (board_area_w - board_pixel_w) // 2
        board_offset_y = (H - board_pixel_h) // 2
        
        tool_rects = {tool: pygame.Rect(palette_x + (i % 2) * 80 + 20, 100 + (i // 2) * 70, 60, 60) for i, tool in enumerate(all_tools)}
        save_btn = pygame.Rect(palette_x, H - 150, 180, 50)
        back_btn = pygame.Rect(palette_x, H - 80, 180, 50)

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
                            game.save_custom_level(board.tolist()); await fade_transition(screen, assets, fade_in=False); return "MODE_SELECT"
                        else: message = "Unsolvable!"; message_color = assets.theme['EDITOR_MSG_BAD']; message_timer = 120
                    else: message = "Invalid Layout!"; message_color = assets.theme['EDITOR_MSG_BAD']; message_timer = 120
                
                clicked_on_palette = False
                for tool, rect in tool_rects.items():
                    if rect.collidepoint(mouse_pos): current_tool = tool; assets.sounds['button'].play(); clicked_on_palette = True
                
                if not clicked_on_palette and current_tool is not None:
                    grid_col = (mouse_pos[0] - board_offset_x) // ts; grid_row = (mouse_pos[1] - board_offset_y) // ts
                    if 0 <= grid_row < EDITOR_H and 0 <= grid_col < EDITOR_W:
                        if current_tool == game.GameObject.PLAYER: board[board == game.GameObject.PLAYER.value] = game.GameObject.EMPTY.value
                        board[grid_row, grid_col] = current_tool.value
                        if current_tool in stamp_tools: current_tool = None
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1: mouse_down = False
            
            if event.type == pygame.MOUSEMOTION and mouse_down:
                if current_tool is not None and current_tool in paint_tools:
                    grid_col = (mouse_pos[0] - board_offset_x) // ts; grid_row = (mouse_pos[1] - board_offset_y) // ts
                    if 0 <= grid_row < EDITOR_H and 0 <= grid_col < EDITOR_W: board[grid_row, grid_col] = current_tool
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: await fade_transition(screen, assets, fade_in=False); return "MAIN_MENU"
        
        screen.fill(assets.theme['BG']);
        if 'background' in assets.images: screen.blit(assets.images['background'], (0,0))
        draw_board_and_objects(screen, board, assets, (board_offset_x, board_offset_y), is_editor=True)
        
        p_count=np.count_nonzero(board==game.GameObject.PLAYER.value); b_count=np.count_nonzero(board==game.GameObject.BOX.value); t_count=np.count_nonzero(board==game.GameObject.TARGET.value)
        valid_level = p_count == 1 and b_count > 0 and b_count == t_count
        
        if p_count != 1: help_text=f"Needs {1 - p_count} Player"
        elif b_count == 0: help_text="Needs Boxes"
        elif b_count != t_count: help_text=f"{abs(b_count - t_count)} more {'Targets' if b_count > t_count else 'Boxes'}"
        else: help_text = "Ready to Test!"
        
        help_surf = assets.font_small.render(help_text, True, assets.theme['WIN'] if valid_level else assets.theme['EDITOR_TEXT'])
        screen.blit(help_surf, help_surf.get_rect(centerx=palette_x + 90, y=H - 260))
        
        if message_timer > 0: msg_surf = assets.font_small.render(message, True, message_color); screen.blit(msg_surf, msg_surf.get_rect(centerx=palette_x + 90, y=H - 280))
        
        for tool, rect in tool_rects.items():
            tool_name = tool_names.get(tool, ""); draw_header_button(screen, rect, "", assets, toggled=(tool == current_tool))
            image_key = {game.GameObject.WALL:'wall', game.GameObject.EMPTY:'floor', game.GameObject.TARGET:'target', game.GameObject.BOX:'box', game.GameObject.PLAYER:'player_face'}.get(tool)
            if image_key in assets.images: screen.blit(pygame.transform.smoothscale(assets.images[image_key], (50,50)), (rect.x+5, rect.y+5))
        
        if current_tool is not None and current_tool in stamp_tools:
            stamp_image_key = {game.GameObject.TARGET:'target', game.GameObject.BOX:'box', game.GameObject.PLAYER:'player_front'}.get(current_tool)
            if stamp_image_key in assets.images:
                sprite = assets.images[stamp_image_key]; sprite.set_alpha(150); screen.blit(sprite, (mouse_pos[0] - ts//2, mouse_pos[1] - ts//2)); sprite.set_alpha(255)
        
        draw_header_button(screen, save_btn, "SAVE & TEST", assets, enabled=valid_level); draw_header_button(screen, back_btn, "BACK", assets)
        pygame.display.flip(); await asyncio.sleep(0); clock.tick(assets.config.FPS)
# --- END OF FINAL UPGRADED FILE ui.py ---