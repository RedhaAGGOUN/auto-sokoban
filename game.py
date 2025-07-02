# --- START OF FINAL UPGRADED FILE game.py ---

from typing import Dict, Tuple, List, Optional
import numpy as np
import time
from pathlib import Path
import json
from datetime import datetime
import os
import re

from constants import GameObject
from save_load import save_data, load_data
from assets import AssetManager
from solver import bfs_solver
from core import get_initial_board, get_targets_mask, is_win, move

INITIAL_LEVELS = [ [[0,0,-1,-1,-1,0],[0,0,-1,1,-1,0],[0,0,-1,0,-1,-1],[-1,-1,-1,2,0,-1],[-1,1,0,2,3,-1],[-1,-1,-1,-1,-1,-1]],[[0,0,0,-1,-1,-1,0,0],[0,-1,-1,-1,1,-1,0,0],[-1,-1,0,0,0,-1,0,0],[-1,0,2,-1,3,-1,-1,-1],[-1,0,0,0,0,0,0,-1],[-1,-1,-1,-1,0,0,0,-1],[0,0,0,-1,-1,-1,-1,-1]],[[0,0,0,-1,-1,-1,0,0],[0,0,-1,-1,1,-1,-1,-1],[0,-1,-1,0,0,0,0,-1],[-1,-1,0,3,0,0,0,-1],[-1,0,2,0,-1,0,0,-1],[-1,0,0,0,0,0,-1,-1],[-1,-1,-1,-1,-1,-1,-1,0]],[[-1,-1,-1,-1,-1,-1,-1,-1],[-1,1,0,0,0,0,0,-1],[-1,0,2,0,2,0,0,-1],[-1,0,2,0,0,0,0,-1],[-1,-1,-1,-1,0,3,-1,-1],[0,0,0,-1,-1,-1,-1,-1]],[[0,0,0,0,0,-1,-1,-1],[0,0,0,0,0,-1,1,-1],[0,-1,-1,-1,-1,-1,0,-1],[0,-1,0,0,0,0,0,-1],[-1,-1,2,0,0,0,0,-1],[-1,0,0,0,-1,-1,-1,-1],[-1,0,0,0,0,3,-1,0],[-1,-1,-1,-1,-1,-1,-1,0]],[[0,0,0,0,0,-1,-1,-1],[0,0,0,0,-1,-1,1,-1],[0,0,0,0,-1,0,0,-1],[0,0,0,0,-1,2,0,-1],[-1,-1,-1,-1,-1,0,0,-1],[-1,0,0,0,0,0,0,-1],[-1,0,0,3,-1,0,0,-1],[-1,-1,-1,-1,-1,-1,-1,-1]],[[0,0,0,0,0,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1,0,3,-1],[-1,0,2,0,0,0,0,0,-1],[-1,1,0,0,0,-1,0,-1,-1],[-1,-1,-1,0,0,0,0,-1,-1],[0,0,-1,0,0,0,0,0,-1],[0,0,-1,-1,-1,0,-1,0,-1],[0,0,0,0,-1,0,0,0,-1],[0,0,0,0,-1,-1,-1,-1,-1]],[[-1,-1,-1,-1,-1,0],[-1,1,0,0,-1,0],[-1,-1,1,0,-1,-1],[-1,-1,0,2,0,-1],[-1,0,2,-1,0,-1],[-1,0,0,0,3,-1],[-1,-1,-1,-1,-1,-1]],[[-1,-1,-1,-1,-1,0],[-1,1,0,0,-1,0],[-1,0,1,2,-1,-1],[-1,3,2,0,0,-1],[-1,-1,0,0,0,-1],[0,-1,-1,-1,-1,-1]],[[-1,-1,-1,-1,-1,0],[-1,1,0,0,-1,0],[-1,0,1,2,-1,-1],[-1,3,2,0,0,-1],[-1,-1,0,0,0,-1],[0,-1,-1,-1,-1,-1]],[[-1,-1,-1,-1,-1,-1,0,0],[-1,1,-1,0,1,-1,-1,0],[-1,0,0,0,0,0,-1,0],[-1,0,2,0,0,2,-1,-1],[-1,-1,-1,3,-1,0,0,-1],[0,0,-1,0,0,0,0,-1],[0,0,-1,0,0,-1,-1,-1],[0,0,-1,-1,-1,0,0,0]],[[0,0,0,0,0,-1,-1,-1],[-1,-1,-1,-1,-1,-1,1,-1],[-1,0,0,0,2,1,0,-1],[-1,0,0,2,-1,0,3,-1],[-1,-1,-1,0,-1,-1,0,-1],[0,0,-1,0,0,0,0,-1],[0,0,-1,-1,-1,-1,-1,-1]],[[-1,-1,-1,-1,-1,-1,0,0],[-1,1,0,1,0,-1,-1,-1],[-1,0,0,0,2,0,0,-1],[-1,0,-1,0,2,0,0,-1],[-1,0,-1,-1,-1,0,0,-1],[-1,-1,-1,0,-1,-1,-1,-1]],[[-1,-1,-1,-1,-1,-1,0,0],[-1,1,0,0,1,-1,-1,0],[-1,0,-1,2,0,2,-1,0],[-1,0,0,2,3,2,-1,-1],[-1,-1,-1,-1,0,2,0,-1],[0,0,0,-1,0,0,0,-1],[0,0,0,-1,-1,-1,-1,-1]],[[-1,-1,-1,-1,-1,-1,-1,-1],[-1,0,0,-1,1,0,0,-1],[-1,3,2,1,0,0,0,-1],[-1,0,0,2,-1,0,-1,-1],[-1,-1,-1,0,0,0,-1,0],[0,0,-1,-1,-1,-1,-1,0]]]
BASE_LEVELS: List[dict] = []
CUSTOM_LEVELS: List[dict] = []
ALL_SOLUTIONS: Dict[str, Optional[list]] = {}
LEVEL_STARS: Dict[str, Dict] = {}
CURRENT_PLAYER_NAME = "Player"
CUSTOM_LEVELS_DIR = Path("custom_levels")
SAVE_FILE = "sokoban_save.json"

def get_or_compute_solution(level_key: str) -> Optional[List[Tuple[int, int]]]:
    """Retrieves a solution from cache or computes it on-demand."""
    if level_key in ALL_SOLUTIONS:
        return ALL_SOLUTIONS[level_key]

    print(f"Computing solution for {level_key}...")
    all_levels = BASE_LEVELS + CUSTOM_LEVELS
    level_info = next((lvl for lvl in all_levels if lvl['key'] == level_key), None)
    
    if not level_info:
        print(f"!! ERROR: Could not find level data for key {level_key}")
        return None
        
    board = get_initial_board(level_info['data'])
    solution = bfs_solver(board)
    ALL_SOLUTIONS[level_key] = solution # Cache the result, even if it's None
    
    status = "SOLVABLE" if solution else "UNSOLVABLE"
    print(f"  - {level_key}: {status} (len: {len(solution) if solution else 'N/A'})")
    
    return solution

class GameState:
    def __init__(self,level_key:str,level_data:list,assets:AssetManager):
        self.assets=assets; self.level_key=level_key
        self.initial_board=get_initial_board(level_data); self.target_mask=get_targets_mask(self.initial_board)
        self.move_stack:List[np.ndarray]=[self.initial_board.copy()]; self.redo_stack:List[np.ndarray]=[]
        self.start_time=time.time(); self.win_time:Optional[float]=None; self.is_won=False
        self.auto_play=False; self.auto_play_idx=0; self.auto_play_speed=0.1; self.player_direction:Tuple[int,int]=(1,0)
        self.solution: Optional[List[Tuple[int,int]]] = None
        
    @property
    def current_board(self)->np.ndarray:return self.move_stack[-1]
    
    def perform_move(self,direction:Tuple[int,int])->bool:
        if self.is_won or self.auto_play:return False
        new_board=move(self.current_board,direction,self.target_mask)
        if new_board is not None:
            self.player_direction=direction
            if np.count_nonzero((self.current_board==GameObject.BOX.value)&self.target_mask)<np.count_nonzero((new_board==GameObject.BOX.value)&self.target_mask):self.assets.sounds['place_box'].play()
            else:self.assets.sounds['move'].play()
            self.move_stack.append(new_board);self.redo_stack.clear();self.check_win();return True
        return False
        
    def undo(self):
        if len(self.move_stack)>1 and not self.auto_play:self.assets.sounds['undo'].play();self.redo_stack.append(self.move_stack.pop())
        
    def restart(self):
        self.move_stack=[self.initial_board.copy()];self.redo_stack=[];self.start_time=time.time();self.is_won=False;self.win_time=None;self.auto_play=False;self.player_direction=(1,0)
        
    def start_solver(self):
        self.solution = get_or_compute_solution(self.level_key)
        if self.solution:
            self.restart()
            self.auto_play=True
            self.auto_play_idx=0
            
    def step_solver(self):
        if self.auto_play and self.solution and self.auto_play_idx < len(self.solution):
            direction=self.solution[self.auto_play_idx];self.player_direction=direction;new_board=move(self.current_board,direction,self.target_mask)
            if new_board is not None:self.move_stack.append(new_board)
            self.auto_play_idx+=1;self.check_win()
        else:self.auto_play=False
        
    def check_win(self):
        global LEVEL_STARS
        if not self.is_won and is_win(self.current_board,self.target_mask):
            self.is_won=True;self.win_time=time.time();self.auto_play=False;self.assets.sounds['win'].play()
            
            solution = get_or_compute_solution(self.level_key)
            moves=len(self.move_stack)-1;optimal_moves=len(solution) if solution else float('inf')
            
            stars=1
            if moves<=optimal_moves*1.5:stars=2
            if moves<=optimal_moves:stars=3
            
            player_data = LEVEL_STARS.setdefault(CURRENT_PLAYER_NAME, {'scores': {}, 'last_played': ''})
            player_scores = player_data.get('scores', {})
            player_scores[self.level_key] = max(player_scores.get(self.level_key, 0), stars)
            player_data['scores'] = player_scores
            player_data['last_played'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            save_data(LEVEL_STARS,Path(SAVE_FILE))

def get_stars_for_player(player_name: str) -> Dict[str, int]:
    return LEVEL_STARS.get(player_name, {}).get('scores', {})

def get_player_rankings()->List[dict]:
    scores=[]
    for player_name, player_data in LEVEL_STARS.items():
        total_stars = sum(player_data.get('scores', {}).values())
        last_played = player_data.get('last_played', 'N/A')
        scores.append({"name": player_name, "stars": total_stars, "last_played": last_played})
    scores.sort(key=lambda s:s["stars"],reverse=True);return scores

def _migrate_save_data(data: dict) -> dict:
    migrated = False
    for player_name, player_data in data.items():
        if isinstance(player_data, dict) and 'scores' not in player_data:
            print(f"Migrating save data for player: {player_name}")
            data[player_name] = {
                'scores': player_data,
                'last_played': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            migrated = True
    if migrated:
        save_data(data, Path(SAVE_FILE))
    return data

def initialize_game_data():
    global BASE_LEVELS,CUSTOM_LEVELS,ALL_SOLUTIONS,LEVEL_STARS,CURRENT_PLAYER_NAME
    BASE_LEVELS=[{'key':f'base_{i}','name':f'Level {i+1}','data':lvl} for i,lvl in enumerate(INITIAL_LEVELS)]
    CUSTOM_LEVELS_DIR.mkdir(exist_ok=True);CUSTOM_LEVELS=[]
    
    creator_counts = {}
    sorted_files = sorted(CUSTOM_LEVELS_DIR.glob("*.json"), key=os.path.getmtime)

    for file_path in sorted_files:
        try:
            level_data=load_data(file_path);creator=file_path.stem.split('_')[0]
            creator_counts[creator] = creator_counts.get(creator, 0) + 1
            player_level_count = creator_counts[creator]
            CUSTOM_LEVELS.append({'key':file_path.name,'name':f'#{player_level_count} by {creator}','data':level_data,'creator':creator})
        except Exception as e:print(f"Error loading custom level {file_path}: {e}")
    
    saved_progress=load_data(Path(SAVE_FILE))
    if saved_progress and isinstance(saved_progress,dict):
        LEVEL_STARS = _migrate_save_data(saved_progress)
        player_list=list(LEVEL_STARS.keys())
        if player_list:CURRENT_PLAYER_NAME=player_list[-1]
    else:LEVEL_STARS={}
    
    ALL_SOLUTIONS.clear()
    print("Game initialized without pre-computing solutions.")

def save_custom_level(level_data:list):
    player_levels=list(CUSTOM_LEVELS_DIR.glob(f"{CURRENT_PLAYER_NAME}_*.json"))
    level_numbers=[int(re.search(r'_(\d+)\.json$',f.name).group(1)) for f in player_levels if re.search(r'_(\d+)\.json$',f.name)]
    next_level_num=max(level_numbers)+1 if level_numbers else 1
    filename=f"{CURRENT_PLAYER_NAME}_{next_level_num}.json";save_path=CUSTOM_LEVELS_DIR/filename
    save_data(level_data,save_path);print(f"New custom level saved to {save_path}")

    player_data = LEVEL_STARS.setdefault(CURRENT_PLAYER_NAME, {'scores': {}, 'last_played': ''})
    player_data['last_played'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_data(LEVEL_STARS, Path(SAVE_FILE))

    initialize_game_data()

def delete_custom_level(level_key:str):
    try:
        file_path=CUSTOM_LEVELS_DIR/level_key
        if file_path.exists():
            os.remove(file_path);print(f"Deleted custom level: {file_path}")
            for player in LEVEL_STARS:
                if level_key in LEVEL_STARS[player].get('scores', {}):
                    del LEVEL_STARS[player]['scores'][level_key]
            save_data(LEVEL_STARS,Path(SAVE_FILE));initialize_game_data()
            return True
    except Exception as e:print(f"Error deleting level {level_key}: {e}")
    return False

def solve_new_level(level_data:list):
    print("Checking level solvability...");board=get_initial_board(level_data)
    solution=bfs_solver(board)
    status="SOLVABLE"if solution else"UNSOLVABLE";print(f"Level Check:{status}(len:{len(solution)if solution else'N/A'})")
    return solution is not None
# --- END OF FINAL UPGRADED FILE game.py ---