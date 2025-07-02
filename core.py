from typing import Optional, Tuple
import numpy as np
from constants import GameObject

Board = np.ndarray

def get_initial_board(level_data: list) -> Board:
    """Converts level data into a NumPy array board."""
    max_width = max(len(row) for row in level_data) if level_data else 0
    board = np.full((len(level_data), max_width), GameObject.WALL.value, dtype=int)
    for i, row in enumerate(level_data):
        board[i, :len(row)] = row
    return board

def get_targets_mask(board: Board) -> Board:
    """Returns a mask of target locations."""
    return board == GameObject.TARGET.value

def find_player(board: Board) -> Optional[Tuple[int, int]]:
    """Finds the player's position on the board."""
    pos = np.argwhere(board == GameObject.PLAYER.value)
    return tuple(pos[0]) if len(pos) > 0 else None

def is_win(board: Board, target_mask: Board) -> bool:
    """Checks if all boxes are on targets."""
    box_locations = board == GameObject.BOX.value
    return np.any(box_locations) and np.all(target_mask[box_locations])

def move(board: Board, direction: Tuple[int, int], target_mask: Board) -> Optional[Board]:
    """Attempts to move the player or a box in the given direction."""
    player_pos = find_player(board)
    if not player_pos: return None
    h, w = board.shape; pi, pj = player_pos; di, dj = direction
    ni, nj = pi + di, pj + dj
    if not (0 <= ni < h and 0 <= nj < w) or board[ni, nj] == GameObject.WALL.value: return None
    if board[ni, nj] in [GameObject.EMPTY.value, GameObject.TARGET.value]:
        new_board = board.copy()
        new_board[ni, nj] = GameObject.PLAYER.value
        new_board[pi, pj] = GameObject.TARGET.value if target_mask[pi, pj] else GameObject.EMPTY.value
        return new_board
    if board[ni, nj] == GameObject.BOX.value:
        bi, bj = ni + di, nj + dj
        if not (0 <= bi < h and 0 <= bj < w) or board[bi, bj] not in [GameObject.EMPTY.value, GameObject.TARGET.value]: return None
        new_board = board.copy()
        new_board[bi, bj] = GameObject.BOX.value
        new_board[ni, nj] = GameObject.PLAYER.value
        new_board[pi, pj] = GameObject.TARGET.value if target_mask[pi, pj] else GameObject.EMPTY.value
        return new_board
    return None