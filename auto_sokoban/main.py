import pygame
import numpy as np
from collections import deque
import time
import sys

pygame.init()
FONT = pygame.font.SysFont('Arial', 28)
SMALLFONT = pygame.font.SysFont('Arial', 18)

TILE = 36  # Smaller tile size for big boards
PADDING = 20  # Padding for nice visuals
BUTTON_Y = 10  # Y-position for button row at the top
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 80

WALL, EMPTY, TARGET, BOX, PLAYER = -1, 0, 1, 2, 3

# --------- All 8 boards here ---------
all_boards = [
    # Board 1
    [
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,0,0,0,-1,0,0,-1,-1,-1],
        [-1,-1,-1,-1,0,-1,0,-1,2,1,-1,-1,-1],
        [-1,-1,-1,-1,0,0,0,0,2,1,-1,-1,-1],
        [-1,-1,-1,-1,0,-1,0,-1,2,1,-1,-1,-1],
        [-1,-1,-1,-1,0,0,0,-1,0,0,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,3,0,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    ],
    # Board 2
    [
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,0,0,0,0,0,0,0,-1,-1,-1],
        [-1,-1,-1,0,2,-1,-1,-1,-1,0,-1,-1,-1],
        [-1,-1,-1,0,-1,1,0,1,-1,0,-1,-1,-1],
        [-1,-1,-1,0,-1,0,0,0,-1,0,-1,-1,-1],
        [-1,-1,-1,0,0,0,3,0,0,0,-1,-1,-1],
        [-1,-1,-1,0,-1,0,0,0,-1,0,-1,-1,-1],
        [-1,-1,-1,0,-1,2,0,2,-1,0,-1,-1,-1],
        [-1,-1,-1,0,2,-1,-1,-1,-1,0,-1,-1,-1],
        [-1,-1,-1,0,0,0,0,0,0,0,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    ],
    # Board 3
    [
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,0,0,0,0,0,0,0,-1,-1,-1],
        [-1,-1,-1,0,2,2,-1,-1,2,2,0,-1,-1],
        [-1,-1,-1,0,2,-1,1,1,-1,2,0,-1,-1],
        [-1,-1,-1,0,-1,1,0,0,1,-1,0,-1,-1],
        [-1,-1,-1,0,1,0,3,0,0,1,0,-1,-1],
        [-1,-1,-1,0,1,0,0,0,1,0,0,-1,-1],
        [-1,-1,-1,0,0,2,-1,-1,0,0,0,-1,-1],
        [-1,-1,-1,0,0,2,2,2,0,0,0,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    ],
    # Board 4
    [
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,0,0,0,-1,-1,-1,0,0,-1,-1],
        [-1,-1,-1,0,2,0,-1,-1,-1,0,2,-1,-1],
        [-1,-1,-1,0,2,0,1,1,0,0,2,-1,-1],
        [-1,-1,-1,0,2,0,0,0,0,0,2,-1,-1],
        [-1,-1,-1,0,0,1,0,0,1,0,0,-1,-1],
        [-1,-1,-1,0,0,1,3,0,1,0,0,-1,-1],
        [-1,-1,-1,0,0,1,0,0,1,0,0,-1,-1],
        [-1,-1,-1,0,0,0,0,0,0,0,0,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    ],
    # Board 5
    [
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,0,0,0,-1,-1,0,0,0,-1,-1],
        [-1,-1,-1,0,1,0,-1,-1,0,1,0,-1,-1],
        [-1,-1,-1,0,2,0,0,0,0,2,0,-1,-1],
        [-1,-1,-1,0,0,2,-1,-1,2,0,0,-1,-1],
        [-1,-1,-1,0,0,0,-1,-1,0,0,0,-1,-1],
        [-1,-1,-1,0,3,0,-1,-1,0,1,0,-1,-1],
        [-1,-1,-1,0,0,0,-1,-1,0,0,0,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    ],
    # Board 6
    [
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,0,0,0,0,0,0,0,-1,-1,-1],
        [-1,-1,-1,0,1,0,1,0,1,0,-1,-1,-1],
        [-1,-1,-1,0,0,0,2,0,0,0,-1,-1,-1],
        [-1,-1,-1,0,2,2,3,2,2,0,-1,-1,-1],
        [-1,-1,-1,0,0,0,2,0,0,0,-1,-1,-1],
        [-1,-1,-1,0,1,0,1,0,1,0,-1,-1,-1],
        [-1,-1,-1,0,0,0,0,0,0,0,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    ],
    # Board 7
    [
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,0,0,0,-1,-1,-1,-1,-1],
        [-1,-1,-1,0,0,0,2,0,0,0,-1,-1,-1],
        [-1,-1,0,1,2,1,0,1,2,1,0,-1,-1],
        [-1,0,2,0,0,0,2,0,0,0,2,0,-1],
        [0,0,2,0,3,0,2,0,3,0,2,0,0],
        [-1,0,2,0,0,0,2,0,0,0,2,0,-1],
        [-1,-1,0,1,2,1,0,1,2,1,0,-1,-1],
        [-1,-1,-1,0,0,0,2,0,0,0,-1,-1,-1],
        [-1,-1,-1,-1,-1,0,0,0,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    ],
    # Board 8
    [
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,0,0,0,-1,-1,0,0,0,-1,-1],
        [-1,-1,-1,0,2,0,-1,-1,0,2,0,-1,-1],
        [-1,-1,-1,0,2,0,1,1,0,2,0,-1,-1],
        [-1,-1,-1,0,2,0,0,0,0,2,0,-1,-1],
        [-1,-1,-1,0,0,1,0,0,1,0,0,-1,-1],
        [-1,-1,-1,0,0,1,3,0,1,0,0,-1,-1],
        [-1,-1,-1,0,0,1,0,0,1,0,0,-1,-1],
        [-1,-1,-1,0,0,0,0,0,0,0,0,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    ]
]

COLORS = {
    WALL: (180,180,180),
    EMPTY: (255,255,255),
    TARGET: (255,221,51),
    BOX: (40,140,255),
    PLAYER: (20,220,90),
    "BOX_ON_TARGET": (200,80,200),
    "PLAYER_ON_TARGET": (0,180,180),
}

def to_array(board):
    return np.array(board, dtype=int)

def is_target(i, j, target_map):
    return target_map[i, j] == 1

def find_player(board):
    board = to_array(board)
    pos = np.argwhere(board == PLAYER)
    return tuple(pos[0]) if len(pos) else None

def clone(board):
    return np.array(board, dtype=int)

def get_targets(board):
    board = to_array(board)
    return (board == TARGET).astype(int)

def is_win(board, target_map):
    board = to_array(board)
    return np.all((board == BOX) == (target_map == 1))

def move(board, direction, target_map):
    board = to_array(board)
    di, dj = direction
    pi, pj = find_player(board)
    ni, nj = pi + di, pj + dj
    if board[ni, nj] == WALL:
        return False
    if board[ni, nj] == BOX or (board[ni, nj] == BOX and is_target(ni, nj, target_map)):
        bi, bj = ni + di, nj + dj
        if board[bi, bj] in [EMPTY, TARGET]:
            board[bi, bj] = BOX
            board[ni, nj] = PLAYER
            board[pi, pj] = TARGET if is_target(pi, pj, target_map) else EMPTY
            return board
        else:
            return False
    if board[ni, nj] in [EMPTY, TARGET]:
        board[ni, nj], board[pi, pj] = PLAYER, (TARGET if is_target(pi, pj, target_map) else EMPTY)
        return board
    return False

def neighbors(board, target_map):
    board = to_array(board)
    dirs = [(-1,0),(1,0),(0,-1),(0,1)]
    pi, pj = find_player(board)
    for (di, dj) in dirs:
        ni, nj = pi + di, pj + dj
        bi, bj = ni + di, nj + dj
        if board[ni, nj] == WALL: continue
        if board[ni, nj] == BOX or (board[ni, nj] == BOX and is_target(ni, nj, target_map)):
            if board[bi, bj] in [EMPTY, TARGET]:
                b2 = clone(board)
                b2[bi, bj] = BOX
                b2[ni, nj] = PLAYER
                b2[pi, pj] = TARGET if is_target(pi, pj, target_map) else EMPTY
                yield (b2, (di, dj))
        elif board[ni, nj] in [EMPTY, TARGET]:
            b2 = clone(board)
            b2[ni, nj], b2[pi, pj] = PLAYER, (TARGET if is_target(pi, pj, target_map) else EMPTY)
            yield (b2, (di, dj))

def bfs_solver(board, target_map, max_iters=100000):
    from copy import deepcopy
    board = to_array(board)
    visited = set()
    queue = deque()
    queue.append((deepcopy(board), []))
    def board_key(b):
        player = tuple(np.argwhere(b == PLAYER)[0])
        boxes = tuple(sorted(map(tuple, np.argwhere(b == BOX))))
        return (player, boxes)
    while queue and max_iters > 0:
        state, path = queue.popleft()
        k = str(board_key(state))
        if k in visited:
            continue
        visited.add(k)
        if is_win(state, target_map):
            return path
        for nb, move in neighbors(state, target_map):
            queue.append((nb, path + [move]))
        max_iters -= 1
    return None

def draw_board(screen, board, target_map, moves, show_win=False):
    board = to_array(board)
    h, w = board.shape
    for i in range(h):
        for j in range(w):
            x, y = j * TILE + PADDING, i * TILE + PADDING + BUTTON_HEIGHT + 10
            if board[i, j] == WALL:
                pygame.draw.rect(screen, COLORS[WALL], (x, y, TILE, TILE))
            elif board[i, j] == EMPTY:
                pygame.draw.rect(screen, COLORS[EMPTY], (x, y, TILE, TILE))
                if is_target(i, j, target_map):
                    pygame.draw.circle(screen, COLORS[TARGET], (x + TILE // 2, y + TILE // 2), TILE // 4)
            elif board[i, j] == TARGET:
                pygame.draw.rect(screen, COLORS[EMPTY], (x, y, TILE, TILE))
                pygame.draw.circle(screen, COLORS[TARGET], (x + TILE // 2, y + TILE // 2), TILE // 4)
            elif board[i, j] == BOX:
                pygame.draw.rect(screen, COLORS[BOX], (x, y, TILE, TILE))
                if is_target(i, j, target_map):
                    pygame.draw.rect(screen, COLORS["BOX_ON_TARGET"], (x+6, y+6, TILE-12, TILE-12))
            elif board[i, j] == PLAYER:
                pygame.draw.rect(screen, COLORS[PLAYER], (x, y, TILE, TILE))
                pygame.draw.circle(screen, (30, 30, 30), (x + TILE // 2, y + TILE // 2), TILE // 4)
                if is_target(i, j, target_map):
                    pygame.draw.circle(screen, COLORS["PLAYER_ON_TARGET"], (x + TILE // 2, y + TILE // 2), TILE // 4)

    # Moves Counter
    moves_txt = SMALLFONT.render(f"Moves: {moves}", True, (0, 0, 0))
    screen.blit(moves_txt, (20, BUTTON_Y + BUTTON_HEIGHT + 10))

    # Buttons (top row)
    buttons = [
        ("Undo", (20, BUTTON_Y, 80, BUTTON_HEIGHT)),
        ("Restart", (120, BUTTON_Y, 90, BUTTON_HEIGHT)),
        ("Back", (230, BUTTON_Y, 80, BUTTON_HEIGHT)),
        ("Main", (330, BUTTON_Y, 80, BUTTON_HEIGHT)),
        ("Solve", (430, BUTTON_Y, 90, BUTTON_HEIGHT)),
    ]
    for text, rect in buttons:
        pygame.draw.rect(screen, (210,210,210), rect, border_radius=8)
        pygame.draw.rect(screen, (60,60,60), rect, 2, border_radius=8)
        t = SMALLFONT.render(text, True, (10,10,10))
        screen.blit(t, (rect[0]+12, rect[1]+10))

    # Win message
    if show_win:
        win_txt = FONT.render("🎉 YOU WIN!", True, (30, 220, 90))
        screen.blit(win_txt, (w*TILE//2 - 100, BUTTON_Y + BUTTON_HEIGHT + 10))

    return buttons

def button_clicked(mouse_pos, buttons):
    for idx, (_, rect) in enumerate(buttons):
        x, y, w, h = rect
        if x <= mouse_pos[0] <= x+w and y <= mouse_pos[1] <= y+h:
            return idx
    return -1

def main_menu():
    W, H = 550, 300
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Auto-Sokoban")
    run = True
    while run:
        screen.fill((45,65,100))
        title = FONT.render("Auto-Sokoban", True, (255, 240, 50))
        play_btn = pygame.Rect(170, 120, 200, 60)
        quit_btn = pygame.Rect(170, 200, 200, 60)
        pygame.draw.rect(screen, (240,240,180), play_btn, border_radius=10)
        pygame.draw.rect(screen, (120,120,60), play_btn, 3, border_radius=10)
        pygame.draw.rect(screen, (230,200,200), quit_btn, border_radius=10)
        pygame.draw.rect(screen, (130,80,80), quit_btn, 3, border_radius=10)
        screen.blit(title, (140, 30))
        screen.blit(FONT.render("Play", True, (50,50,50)), (play_btn.x+60, play_btn.y+10))
        screen.blit(FONT.render("Quit", True, (80,10,10)), (quit_btn.x+60, quit_btn.y+10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(event.pos):
                    return
                if quit_btn.collidepoint(event.pos):
                    pygame.quit(); sys.exit()

def level_select_menu():
    h = len(all_boards[0])
    W, H = 800, 250
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Auto-Sokoban - Select Level")
    font = pygame.font.SysFont('arial', 32, bold=True)
    small = pygame.font.SysFont('arial', 24)
    level_rects = []
    for i in range(8):
        rect = pygame.Rect(60+90*i, 100, 75, 75)
        level_rects.append(rect)
    while True:
        screen.fill((40, 60, 80))
        txt = font.render("Select Level:", 1, (250,250,0))
        screen.blit(txt, (320, 30))
        for i, rect in enumerate(level_rects):
            pygame.draw.rect(screen, (240,220,120), rect, border_radius=12)
            pygame.draw.rect(screen, (120,120,60), rect, 3, border_radius=12)
            t = FONT.render(str(i+1), True, (50,50,50))
            screen.blit(t, (rect.x+20, rect.y+18))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(level_rects):
                    if rect.collidepoint(event.pos):
                        return i

def play(board):
    board = to_array(board)
    target_map = get_targets(board)
    original_board = board.copy()
    stack = [board.copy()]
    move_count = 0
    h, w = board.shape
    screen = pygame.display.set_mode((w*TILE+2*PADDING, h*TILE+PADDING*2+BUTTON_HEIGHT))
    pygame.display.set_caption("Auto-Sokoban")
    clock = pygame.time.Clock()
    while True:
        screen.fill((40, 40, 40))
        win = is_win(board, target_map)
        buttons = draw_board(screen, board, target_map, move_count, show_win=win)
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "main"
            if event.type == pygame.KEYDOWN and not win:
                moved = False
                if event.key in [pygame.K_UP, pygame.K_w]:
                    nb = move(board, (-1, 0), target_map)
                    if isinstance(nb, np.ndarray): board[:] = nb; stack.append(board.copy()); move_count += 1; moved=True
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    nb = move(board, (1, 0), target_map)
                    if isinstance(nb, np.ndarray): board[:] = nb; stack.append(board.copy()); move_count += 1; moved=True
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    nb = move(board, (0, -1), target_map)
                    if isinstance(nb, np.ndarray): board[:] = nb; stack.append(board.copy()); move_count += 1; moved=True
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    nb = move(board, (0, 1), target_map)
                    if isinstance(nb, np.ndarray): board[:] = nb; stack.append(board.copy()); move_count += 1; moved=True
            if event.type == pygame.MOUSEBUTTONDOWN:
                idx = button_clicked(event.pos, buttons)
                if idx == 0:  # Undo
                    if len(stack) > 1:
                        stack.pop()
                        board[:] = stack[-1]
                        move_count -= 1 if move_count > 0 else 0
                elif idx == 1:  # Restart
                    board[:] = original_board
                    stack = [board.copy()]
                    move_count = 0
                elif idx == 2:  # Back
                    return "level"
                elif idx == 3:  # Main
                    return "main"
                elif idx == 4 and not win:  # Solve
                    solution = bfs_solver(board, target_map)
                    if not solution:
                        print("No solution found!")
                    else:
                        for m in solution:
                            pygame.event.pump()
                            nb = move(board, m, target_map)
                            if isinstance(nb, np.ndarray): board[:] = nb; stack.append(board.copy()); move_count += 1
                            draw_board(screen, board, target_map, move_count)
                            pygame.display.flip()
                            time.sleep(0.09)
                        break
        if win:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "main"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    idx = button_clicked(event.pos, buttons)
                    if idx == 1:  # Restart
                        board[:] = original_board
                        stack = [board.copy()]
                        move_count = 0
                    elif idx == 2:
                        return "level"
                    elif idx == 3:
                        return "main"

if __name__ == "__main__":
    while True:
        main_menu()
        while True:
            level_idx = level_select_menu()
            board = [row[:] for row in all_boards[level_idx]]
            res = play(board)
            if res == "main":
                break
