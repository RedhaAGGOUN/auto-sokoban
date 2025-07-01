from collections import deque
from typing import Optional, List, Tuple
import numpy as np
from constants import GameObject
from core import move, is_win, find_player, get_targets_mask

def bfs_solver(initial_board: np.ndarray, max_iters: int = 150000) -> Optional[List[Tuple[int, int]]]:
    """Finds the shortest solution using Breadth-First Search."""
    target_mask = get_targets_mask(initial_board)
    
    def get_board_key(b: np.ndarray) -> tuple:
        player_pos = find_player(b)
        box_pos = tuple(sorted(map(tuple, np.argwhere(b == GameObject.BOX.value))))
        return (player_pos, box_pos)

    queue = deque([(initial_board, [])])
    visited = {get_board_key(initial_board)}
    
    for _ in range(max_iters):
        if not queue: break
        current_board, path = queue.popleft()
        if is_win(current_board, target_mask):
            return path
        for direction in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            next_board = move(current_board, direction, target_mask)
            if next_board is not None:
                key = get_board_key(next_board)
                if key not in visited:
                    visited.add(key)
                    queue.append((next_board, path + [direction]))
    return None