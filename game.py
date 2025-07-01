# --- START OF CORRECTED FILE game.py ---

from typing import Dict, Tuple, List, Optional
import numpy as np
import time
from pathlib import Path
import json
from datetime import datetime

from constants import GameObject
from save_load import save_data, load_data
from assets import AssetManager
from solver import bfs_solver
from core import get_initial_board, get_targets_mask, is_win, move

# --- Global State ---
INITIAL_LEVELS = [ # The 15 base levels
    [[0,0,-1,-1,-1,0],[0,0,-1,1,-1,0],[0,0,-1,0,-1,-1],[-1,-1,-1,2,0,-1],[-1,1,0,2,3,-1],[-1,-1,-1,-1,-1,-1]],
    [[0,0,0,-1,-1,-1,0,0],[0,-1,-1,-1,1,-1,0,0],[-1,-1,0,0,0,-1,0,0],[-1,0,2,-1,3,-1,-1,-1],[-1,0,0,0,0,0,0,-1],[-1,-1,-1,-1,0,0,0,-1],[0,0,0,-1,-1,-1,-1,-1]],
    [[0,0,0,-1,-1,-1,0,0],[0,0,-1,-1,1,-1,-1,-1],[0,-1,-1,0,0,0,0,-1],[-1,-1,0,3,0,0,0,-1],[-1,0,2,0,-1,0,0,-1],[-1,0,0,0,0,0,-1,-1],[-1,-1,-1,-1,-1,-1,-1,0]],
    [[-1,-1,-1,-1,-1,-1,-1,-1],[-1,1,0,0,0,0,0,-1],[-1,0,2,0,2,0,0,-1],[-1,0,2,0,0,0,0,-1],[-1,-1,-1,-1,0,3,-1,-1],[0,0,0,-1,-1,-1,-1,-1]],
    [[0,0,0,0,0,-1,-1,-1],[0,0,0,0,0,-1,1,-1],[0,-1,-1,-1,-1,-1,0,-1],[0,-1,0,0,0,0,0,-1],[-1,-1,2,0,0,0,0,-1],[-1,0,0,0,-1,-1,-1,-1],[-1,0,0,0,0,3,-1,0],[-1,-1,-1,-1,-1,-1,-1,0]],
    [[0,0,0,0,0,-1,-1,-1],[0,0,0,0,-1,-1,1,-1],[0,0,0,0,-1,0,0,-1],[0,0,0,0,-1,2,0,-1],[-1,-1,-1,-1,-1,0,0,-1],[-1,0,0,0,0,0,0,-1],[-1,0,0,3,-1,0,0,-1],[-1,-1,-1,-1,-1,-1,-1,-1]],
    [[0,0,0,0,0,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1,0,3,-1],[-1,0,2,0,0,0,0,0,-1],[-1,1,0,0,0,-1,0,-1,-1],[-1,-1,-1,0,0,0,0,-1,-1],[0,0,-1,0,0,0,0,0,-1],[0,0,-1,-1,-1,0,-1,0,-1],[0,0,0,0,-1,0,0,0,-1],[0,0,0,0,-1,-1,-1,-1,-1]],
    [[-1,-1,-1,-1,-1,0],[-1,1,0,0,-1,0],[-1,-1,1,0,-1,-1],[-1,-1,0,2,0,-1],[-1,0,2,-1,0,-1],[-1,0,0,0,3,-1],[-1,-1,-1,-1,-1,-1]],
    [[-1,-1,-1,-1,-1,0],[-1,1,0,0,-1,0],[-1,0,1,2,-1,-1],[-1,3,2,0,0,-1],[-1,-1,0,0,0,-1],[0,-1,-1,-1,-1,-1]],
    [[-1,-1,-1,-1,-1,0],[-1,1,0,0,-1,0],[-1,0,1,2,-1,-1],[-1,3,2,0,0,-1],[-1,-1,0,0,0,-1],[0,-1,-1,-1,-1,-1]],
    [[-1,-1,-1,-1,-1,-1,0,0],[-1,1,-1,0,1,-1,-1,0],[-1,0,0,0,0,0,-1,0],[-1,0,2,0,0,2,-1,-1],[-1,-1,-1,3,-1,0,0,-1],[0,0,-1,0,0,0,0,-1],[0,0,-1,0,0,-1,-1,-1],[0,0,-1,-1,-1,0,0,0]],
    [[0,0,0,0,0,-1,-1,-1],[-1,-1,-1,-1,-1,-1,1,-1],[-1,0,0,0,2,1,0,-1],[-1,0,0,2,-1,0,3,-1],[-1,-1,-1,0,-1,-1,0,-1],[0,0,-1,0,0,0,0,-1],[0,0,-1,-1,-1,-1,-1,-1]],
    [[-1,-1,-1,-1,-1,-1,0,0],[-1,1,0,1,0,-1,-1,-1],[-1,0,0,0,2,0,0,-1],[-1,0,-1,0,2,0,0,-1],[-1,0,-1,-1,-1,0,0,-1],[-1,-1,-1,0,-1,-1,-1,-1]],
    [[-1,-1,-1,-1,-1,-1,0,0],[-1,1,0,0,1,-1,-1,0],[-1,0,-1,2,0,2,-1,0],[-1,0,0,2,3,2,-1,-1],[-1,-1,-1,-1,0,2,0,-1],[0,0,0,-1,0,0,0,-1],[0,0,0,-1,-1,-1,-1,-1]],
    [[-1,-1,-1,-1,-1,-1,-1,-1],[-1,0,0,-1,1,0,0,-1],[-1,3,2,1,0,0,0,-1],[-1,0,0,2,-1,0,-1,-1],[-1,-1,-1,0,0,0,-1,0],[0,0,-1,-1,-1,-1,-1,0]]
]

BASE_LEVELS: List[dict] = []
CUSTOM_LEVELS: List[dict] = []
ALL_SOLUTIONS: Dict[str, Optional[list]] = {} # Keyed by level key
LEVEL_STARS: Dict[str, Dict[str, int]] = {} # {'PlayerName': {'level_key': stars}}
CURRENT_PLAYER_NAME = "Player"

CUSTOM_LEVELS_DIR = Path("custom_levels")
SAVE_FILE = "sokoban_save.json"

class GameState:
    def __init__(self, level_key: str, level_data: list, solution: Optional[List[Tuple[int, int]]], assets: AssetManager):
        self.assets = assets; self.level_key = level_key; self.solution = solution
        self.initial_board = get_initial_board(level_data); self.target_mask = get_targets_mask(self.initial_board)
        self.move_stack: List[np.ndarray] = [self.initial_board.copy()]; self.redo_stack: List[np.ndarray] = []
        self.start_time = time.time(); self.win_time: Optional[float] = None; self.is_won = False
        self.auto_play = False; self.auto_play_idx = 0; self.auto_play_speed = 0.1
        self.player_direction: Tuple[int, int] = (1, 0)
        
    @property
    def current_board(self) -> np.ndarray: return self.move_stack[-1]
    def perform_move(self, direction: Tuple[int, int]) -> bool:
        if self.is_won or self.auto_play: return False
        new_board = move(self.current_board, direction, self.target_mask)
        if new_board is not None:
            self.player_direction = direction
            if np.count_nonzero((self.current_board==GameObject.BOX.value)&self.target_mask) < np.count_nonzero((new_board==GameObject.BOX.value)&self.target_mask):
                self.assets.sounds['place_box'].play()
            else: self.assets.sounds['move'].play()
            self.move_stack.append(new_board); self.redo_stack.clear(); self.check_win(); return True
        return False
    def undo(self):
        if len(self.move_stack) > 1 and not self.auto_play: self.assets.sounds['undo'].play(); self.redo_stack.append(self.move_stack.pop())
    def restart(self):
        self.move_stack=[self.initial_board.copy()]; self.redo_stack=[]; self.start_time=time.time()
        self.is_won=False; self.win_time=None; self.auto_play=False; self.player_direction=(1,0)
    def start_solver(self):
        if self.solution: self.restart(); self.auto_play=True; self.auto_play_idx=0
    def step_solver(self):
        if self.auto_play and self.auto_play_idx < len(self.solution):
            direction = self.solution[self.auto_play_idx]; self.player_direction=direction
            new_board = move(self.current_board, direction, self.target_mask)
            if new_board is not None: self.move_stack.append(new_board)
            self.auto_play_idx += 1; self.check_win()
        else: self.auto_play=False
    def check_win(self):
        global LEVEL_STARS
        if not self.is_won and is_win(self.current_board, self.target_mask):
            self.is_won = True; self.win_time = time.time(); self.auto_play=False; self.assets.sounds['win'].play()
            moves = len(self.move_stack)-1; optimal_moves = len(self.solution) if self.solution else float('inf')
            stars = 1
            if moves <= optimal_moves * 1.5: stars=2
            if moves <= optimal_moves: stars=3
            player_stars = LEVEL_STARS.setdefault(CURRENT_PLAYER_NAME, {})
            player_stars[self.level_key] = max(player_stars.get(self.level_key, 0), stars)
            save_data(LEVEL_STARS, Path(SAVE_FILE))

def get_stars_for_player(player_name: str) -> Dict[str, int]: return LEVEL_STARS.get(player_name, {})

def initialize_game_data():
    global BASE_LEVELS, CUSTOM_LEVELS, ALL_SOLUTIONS, LEVEL_STARS, CURRENT_PLAYER_NAME
    
    BASE_LEVELS = [{'key': f'base_{i}', 'name': f'Level {i+1}', 'data': lvl} for i, lvl in enumerate(INITIAL_LEVELS)]
    
    CUSTOM_LEVELS_DIR.mkdir(exist_ok=True)
    CUSTOM_LEVELS = []
    for file_path in CUSTOM_LEVELS_DIR.glob("*.json"):
        try:
            level_data = load_data(file_path)
            player_name = file_path.stem.split('_')[0]
            CUSTOM_LEVELS.append({'key': file_path.name, 'name': f"By {player_name}", 'data': level_data})
        except Exception as e: print(f"Error loading custom level {file_path}: {e}")

    saved_progress = load_data(Path(SAVE_FILE))
    if saved_progress and isinstance(saved_progress, dict):
        LEVEL_STARS = saved_progress
        player_list = list(LEVEL_STARS.keys())
        if player_list: CURRENT_PLAYER_NAME = player_list[-1]
    else: LEVEL_STARS = {}
    
    print("Pre-computing solutions..."); ALL_SOLUTIONS.clear()
    all_levels_to_solve = BASE_LEVELS + CUSTOM_LEVELS
    for level in all_levels_to_solve:
        board = get_initial_board(level['data'])
        solution = bfs_solver(board)
        ALL_SOLUTIONS[level['key']] = solution
        status="SOLVABLE"if solution else"UNSOLVABLE"
        print(f"  - {level['key']}: {status}(len:{len(solution)if solution else'N/A'})")
    print("Done.")

def save_custom_level(level_data: list):
    """Saves a new custom level with a unique, timestamped filename."""
    filename = f"{CURRENT_PLAYER_NAME}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
    save_path = CUSTOM_LEVELS_DIR / filename
    save_data(level_data, save_path)
    print(f"New custom level saved to {save_path}")
    initialize_game_data() # Reload all data to include the new level

# --- END OF CORRECTED FILE game.py ---