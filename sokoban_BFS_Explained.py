import numpy as np
import pygame
from collections import deque
import sys
import time

# --- Game Levels (Copied from the main project) ---
INITIAL_LEVELS = [
    [[0,0,-1,-1,-1,0],[0,0,-1,1,-1,0],[0,0,-1,0,-1,-1],[-1,-1,-1,2,0,-1],[-1,1,0,2,3,-1],[-1,-1,-1,-1,-1,-1]],
    [[0,0,0,-1,-1,-1,0,0],[0,-1,-1,-1,1,-1,0,0],[-1,-1,0,0,0,-1,0,0],[-1,0,2,-1,3,-1,-1,-1],[-1,0,0,0,0,0,0,-1],[-1,-1,-1,-1,0,0,0,-1],[0,0,0,-1,-1,-1,-1,-1]],
    [[0,0,0,-1,-1,-1,0,0],[0,0,-1,-1,1,-1,-1,-1],[0,-1,-1,0,0,0,0,-1],[-1,-1,0,3,0,0,0,-1],[-1,0,2,0,-1,0,0,-1],[-1,0,0,0,0,0,-1,-1],[-1,-1,-1,-1,-1,-1,-1,0]],
    [[-1,-1,-1,-1,-1,-1,-1,-1],[-1,1,0,0,0,0,0,-1],[-1,0,-1,0,-1,0,0,-1],[-1,0,2,0,0,0,0,-1],[-1,-1,-1,-1,0,3,-1,-1],[0,0,0,-1,-1,-1,-1,-1]],
    [[0,0,0,0,0,-1,-1,-1],[0,0,0,0,0,-1,1,-1],[0,-1,-1,-1,-1,-1,0,-1],[0,-1,0,0,0,0,0,-1],[-1,-1,2,0,0,0,0,-1],[-1,0,0,0,-1,-1,-1,-1],[-1,0,0,0,0,3,-1,0],[-1,-1,-1,-1,-1,-1,-1,0]],
    [[0,0,0,0,0,-1,-1,-1],[0,0,0,0,-1,-1,1,-1],[0,0,0,0,-1,0,0,-1],[0,0,0,0,-1,2,0,-1],[-1,-1,-1,-1,-1,0,0,-1],[-1,0,0,0,0,0,0,-1],[-1,0,0,3,-1,0,0,-1],[-1,-1,-1,-1,-1,-1,-1,-1]],
    [[0,0,0,0,0,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1,0,3,-1],[-1,0,0,0,0,0,0,0,-1],[-1,1,0,0,0,-1,0,-1,-1],[-1,-1,-1,0,0,0,0,-1,-1],[0,0,-1,0,0,0,0,0,-1],[0,0,-1,-1,-1,2,-1,0,-1],[0,0,0,0,-1,0,0,0,-1],[0,0,0,0,-1,-1,-1,-1,-1]],
    [[-1,-1,-1,-1,-1,0],[-1,1,0,0,-1,0],[-1,-1,1,0,-1,-1],[-1,-1,0,2,0,-1],[-1,0,2,-1,0,-1],[-1,0,0,0,3,-1],[-1,-1,-1,-1,-1,-1]],
    [[-1,-1,-1,-1,-1,0],[-1,1,0,0,-1,0],[-1,0,1,2,-1,-1],[-1,3,2,0,0,-1],[-1,-1,0,0,0,-1],[0,-1,-1,-1,-1,-1]],
    [[-1,-1,-1,-1,-1,0],[-1,1,0,0,-1,0],[-1,0,1,2,-1,-1],[-1,3,2,0,0,-1],[-1,-1,0,0,0,-1],[0,-1,-1,-1,-1,-1]],
    [[-1,-1,-1,-1,-1,-1,0,0],[-1,1,-1,0,1,-1,-1,0],[-1,0,0,0,0,0,-1,0],[-1,0,2,0,0,2,-1,-1],[-1,-1,-1,3,-1,0,0,-1],[0,0,-1,0,0,0,0,-1],[0,0,-1,0,0,-1,-1,-1],[0,0,-1,-1,-1,0,0,0]],
    [[0,0,0,0,0,-1,-1,-1],[-1,-1,-1,-1,-1,-1,1,-1],[-1,0,0,0,2,1,0,-1],[-1,0,0,2,-1,0,3,-1],[-1,-1,-1,0,-1,-1,0,-1],[0,0,-1,0,0,0,0,-1],[0,0,-1,-1,-1,-1,-1,-1]],
    [[-1,-1,-1,-1,-1,-1,0,0],[-1,1,0,1,0,-1,-1,-1],[-1,0,0,0,2,0,0,-1],[-1,0,-1,0,2,0,0,-1],[-1,3,-1,-1,-1,0,0,-1],[-1,-1,-1,0,-1,-1,-1,-1]],
    [[-1,-1,-1,-1,-1,-1,0,0],[-1,1,0,0,1,-1,-1,0],[-1,0,-1,0,0,0,-1,0],[-1,0,0,0,3,2,-1,-1],[-1,-1,-1,-1,0,2,0,-1],[0,0,0,-1,0,0,0,-1],[0,0,0,-1,-1,-1,-1,-1]],
    [[-1,-1,-1,-1,-1,-1,-1,-1],[-1,0,0,-1,1,0,0,-1],[-1,3,2,1,0,0,0,-1],[-1,0,0,2,-1,0,-1,-1],[-1,-1,-1,0,0,0,-1,0],[0,0,-1,-1,-1,-1,-1,0]]
]

# --- Constants ---
class Tile:
    EMPTY, WALL, PLAYER, BOX, TARGET = 0, 1, 2, 3, 4

COLORS = {
    'background': (248, 249, 250), 'wall': (52, 58, 64), 'grid': (222, 226, 230),
    'text': (33, 37, 41), 'instructions': (108, 117, 125), 'title': (0, 80, 150),
    'path_current': (255, 190, 0), 'path_solution': (40, 167, 69),
    'target': (255, 165, 0, 150), 'highlight_win': (200, 255, 200),
    'btn_bg': (222, 226, 230), 'btn_hover': (206, 212, 218), 'btn_text': (73, 80, 87)
}
FONT_SIZES = {
    'title': 42, 'board_title': 30, 'definition': 18,
    'medium': 24, 'small': 20, 'btn': 22
}
CELL_SIZE = 45
FPS = 60
BFS_DEFINITION = "Explores layer-by-layer. Slower, but GUARANTEES the shortest path."
DFS_DEFINITION = "Dives down one path. Faster to find *a* solution, but it is often NOT the shortest."

# --- UI Button Class ---
class Button:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.is_enabled = True

    def draw(self, screen, font):
        bg_color = (180, 180, 180) if not self.is_enabled else (COLORS['btn_hover'] if self.is_hovered else COLORS['btn_bg'])
        text_color = (120, 120, 120) if not self.is_enabled else COLORS['btn_text']
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        draw_text(screen, self.text, font, text_color, center=self.rect.center)

    def handle_event(self, event):
        if not self.is_enabled: return False
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered and event.button == 1:
            return True
        return False

# --- Helper Functions ---
def convert_level_format(level_data):
    mapping = {-1: Tile.WALL, 0: Tile.EMPTY, 1: Tile.TARGET, 2: Tile.BOX, 3: Tile.PLAYER}
    max_width = max(len(row) for row in level_data) if level_data else 0
    new_board = np.full((len(level_data), max_width), Tile.WALL, dtype=int)
    for i, row in enumerate(level_data):
        for j, cell in enumerate(row):
            new_board[i, j] = mapping[cell]
    return new_board

def draw_text(screen, text, font, color, **rect_kwargs):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(**rect_kwargs)
    screen.blit(text_surf, text_rect)

# --- Solver Logic ---
class SokobanSolver:
    def __init__(self, initial_board, algorithm):
        self.initial_board = initial_board
        self.base_layout = initial_board.copy()
        self.algorithm = algorithm
        self.target_positions = [tuple(pos) for pos in np.argwhere(self.base_layout == Tile.TARGET)]
        self.setup_search()

    def setup_search(self):
        self.clean_board = self.initial_board.copy()
        for r, c in np.argwhere(self.clean_board == Tile.TARGET):
            self.clean_board[r, c] = Tile.EMPTY
        
        player_pos_list = np.argwhere(self.initial_board == Tile.PLAYER)
        if len(player_pos_list) > 0:
             self.clean_board[player_pos_list[0][0], player_pos_list[0][1]] = Tile.PLAYER

        for r_box, c_box in np.argwhere(self.initial_board == Tile.BOX):
            self.clean_board[r_box, c_box] = Tile.BOX

        key = self._get_board_state_key(self.clean_board)
        initial_state = (self.clean_board.copy(), [])
        
        self.frontier = deque([initial_state]) if self.algorithm == 'bfs' else [initial_state]
        self.visited = {key}
        self.nodes_expanded, self.is_finished, self.solution_path = 0, False, None
        self.metrics, self.start_time = {}, time.time()
        self.current_board, self.current_path = self.clean_board, []

    def _get_board_state_key(self, board):
        p_pos_list = np.argwhere(board == Tile.PLAYER)
        p_pos = tuple(p_pos_list[0]) if len(p_pos_list) > 0 else None
        b_pos = tuple(sorted([tuple(pos) for pos in np.argwhere(board == Tile.BOX)]))
        return (p_pos, b_pos)

    def _is_win(self, board):
        if not self.target_positions: return False
        return all(board[pos] == Tile.BOX for pos in self.target_positions)

    def step(self):
        if not self.frontier or self.is_finished:
            if not self.is_finished: self.finalize_results(solved=False)
            return self.current_board, self.current_path

        self.current_board, self.current_path = self.frontier.popleft() if self.algorithm == 'bfs' else self.frontier.pop()
        self.nodes_expanded += 1

        if self._is_win(self.current_board):
            self.finalize_results(solved=True)
            return self.current_board, self.current_path

        p_pos_list = np.argwhere(self.current_board == Tile.PLAYER)
        if not len(p_pos_list): return self.current_board, self.current_path
        player_pos = tuple(p_pos_list[0])

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_player_pos = (player_pos[0] + dr, player_pos[1] + dc)
            if not (0 <= new_player_pos[0] < self.base_layout.shape[0] and 0 <= new_player_pos[1] < self.base_layout.shape[1]) \
               or self.base_layout[new_player_pos] == Tile.WALL:
                continue

            next_board = self.current_board.copy()
            if next_board[new_player_pos] == Tile.EMPTY:
                next_board[new_player_pos], next_board[player_pos] = Tile.PLAYER, Tile.EMPTY
                key = self._get_board_state_key(next_board)
                if key not in self.visited:
                    self.visited.add(key); self.frontier.append((next_board, self.current_path + [(dr, dc)]))
            elif next_board[new_player_pos] == Tile.BOX:
                box_new_pos = (new_player_pos[0] + dr, new_player_pos[1] + dc)
                if (0 <= box_new_pos[0] < self.base_layout.shape[0] and 0 <= box_new_pos[1] < self.base_layout.shape[1]) \
                   and self.base_layout[box_new_pos] != Tile.WALL and next_board[box_new_pos] != Tile.BOX:
                    next_board[box_new_pos], next_board[new_player_pos], next_board[player_pos] = Tile.BOX, Tile.PLAYER, Tile.EMPTY
                    key = self._get_board_state_key(next_board)
                    if key not in self.visited:
                        self.visited.add(key); self.frontier.append((next_board, self.current_path + [(dr, dc)]))
        return self.current_board, self.current_path
    
    def finalize_results(self, solved):
        self.is_finished, self.solution_path = True, self.current_path if solved else None
        self.metrics = {
            'time': time.time() - self.start_time, 'len': len(self.solution_path) if solved else 'Fail',
            'visited': len(self.visited), 'expanded': self.nodes_expanded
        }

# --- Pygame Visualization Class ---
class SokobanComparison:
    def __init__(self, assets_path):
        self.assets_path = assets_path
        self.current_level_index = 10
        self.mode = "READY"
        self.setup_board_and_pygame()
        self.images = self.load_assets()
        self.create_buttons()
        self.reset_solvers()

    def setup_board_and_pygame(self):
        self.initial_board = convert_level_format(INITIAL_LEVELS[self.current_level_index])
        self.board_shape = self.initial_board.shape
        pygame.init()
        self.screen_w, self.screen_h = 1800, 1000
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("Parallel Showdown: BFS (Left) vs. DFS (Right)")
        
        self.fonts = {key: pygame.font.Font(None, size) for key, size in FONT_SIZES.items()}
        self.clock = pygame.time.Clock()

        board_pixel_w = self.board_shape[1] * CELL_SIZE
        board_pixel_h = self.board_shape[0] * CELL_SIZE
        
        # *** CHANGED: Increased top margin for board area to accommodate new button layout ***
        board_area_y = 180 + (self.screen_h - 250 - board_pixel_h) / 2
        
        self.bfs_offset = (self.screen_w // 4 - board_pixel_w // 2, board_area_y)
        self.dfs_offset = (self.screen_w * 3 // 4 - board_pixel_w // 2, board_area_y)


    def create_buttons(self):
        panel_y = self.screen_h - 70
        # *** CHANGED: Y-coordinate for level buttons is now lower ***
        level_btn_y = 100
        self.buttons = {
            'start_pause': Button(self.screen_w / 2 - 100, panel_y, 200, 50, "Start Search"),
            'speed_down': Button(self.screen_w / 2 - 200, panel_y, 50, 50, "-"),
            'speed_up': Button(self.screen_w / 2 + 150, panel_y, 50, 50, "+"),
            'reset': Button(20, panel_y, 120, 50, "Reset"),
            'prev_lvl': Button(self.screen_w / 2 - 320, level_btn_y, 180, 50, "<< Prev Level"),
            'next_lvl': Button(self.screen_w / 2 + 140, level_btn_y, 180, 50, "Next Level >>"),
            'quit': Button(self.screen_w - 140, panel_y, 120, 50, "Quit")
        }

    def reset_solvers(self):
        self.setup_board_and_pygame()
        self.create_buttons()
        self.bfs_solver = SokobanSolver(self.initial_board, 'bfs')
        self.dfs_solver = SokobanSolver(self.initial_board, 'dfs')
        self.bfs_board, self.bfs_path = self.bfs_solver.clean_board, []
        self.dfs_board, self.dfs_path = self.dfs_solver.clean_board, []
        self.mode, self.visualization_delay, self.delay_counter = "READY", 5, 0
        self.buttons['start_pause'].text = "Start Search"

    def load_assets(self):
        try:
            player_img = pygame.image.load(f"{self.assets_path}/playerFace.png").convert_alpha()
            box_img = pygame.image.load(f"{self.assets_path}/box.png").convert_alpha()
            return {
                Tile.PLAYER: pygame.transform.smoothscale(player_img, (CELL_SIZE, CELL_SIZE)),
                Tile.BOX: pygame.transform.smoothscale(box_img, (CELL_SIZE, CELL_SIZE)),
            }
        except pygame.error as e: print(f"Asset loading error: {e}"); pygame.quit(); sys.exit(1)

    def draw(self):
        self.screen.fill(COLORS['background'])
        
        # --- NEW LAYOUT DRAWING ---
        # Main title
        draw_text(self.screen, "BFS vs. DFS Parallel Showdown", self.fonts['title'], COLORS['text'], center=(self.screen_w / 2, 50))
        # Level selection UI, now positioned below the main title
        level_text = f"Level {self.current_level_index + 1} / {len(INITIAL_LEVELS)}"
        draw_text(self.screen, level_text, self.fonts['medium'], COLORS['text'], center=(self.screen_w / 2, 125))
        self.buttons['prev_lvl'].draw(self.screen, self.fonts['btn'])
        self.buttons['next_lvl'].draw(self.screen, self.fonts['btn'])

        if self.mode in ["SEARCHING", "PAUSED"]: self.draw_search_state()
        elif self.mode == "RESULTS": self.draw_results_screen()
        elif self.mode == "READY": self.draw_ready_screen()
        
        self.draw_control_panel()
        pygame.display.flip()

    def draw_search_state(self):
        self.draw_single_board(self.bfs_solver, self.bfs_board, self.bfs_path, self.bfs_offset)
        self.draw_single_board(self.dfs_solver, self.dfs_board, self.dfs_path, self.dfs_offset)

    def draw_single_board(self, solver, board, path, offset):
        # Position board titles relative to the top of the board area
        board_top_y = offset[1]
        board_center_x = offset[0] + (self.board_shape[1] * CELL_SIZE) / 2
        
        draw_text(self.screen, solver.algorithm.upper(), self.fonts['board_title'], COLORS['title'], centerx=board_center_x, bottom=board_top_y - 50)
        draw_text(self.screen, BFS_DEFINITION if solver.algorithm == 'bfs' else DFS_DEFINITION, self.fonts['definition'], COLORS['instructions'], centerx=board_center_x, bottom=board_top_y - 20)
        
        for r in range(self.board_shape[0]):
            for c in range(self.board_shape[1]):
                rect = pygame.Rect(c * CELL_SIZE + offset[0], r * CELL_SIZE + offset[1], CELL_SIZE, CELL_SIZE)
                if solver.base_layout[r, c] == Tile.WALL:
                    pygame.draw.rect(self.screen, COLORS['wall'], rect, border_radius=4)
                else:
                    pygame.draw.rect(self.screen, COLORS['grid'], rect, 1)
                    if solver.base_layout[r, c] == Tile.TARGET:
                        pygame.draw.rect(self.screen, COLORS['target'], rect.inflate(-8, -8), border_radius=8)

        p_pos_list = np.argwhere(board == Tile.PLAYER)
        if len(p_pos_list) > 0:
             player_pos = tuple(p_pos_list[0])
             self.screen.blit(self.images[Tile.PLAYER], (player_pos[1] * CELL_SIZE + offset[0], player_pos[0] * CELL_SIZE + offset[1]))
        
        for pos in np.argwhere(board == Tile.BOX):
            self.screen.blit(self.images[Tile.BOX], (pos[1] * CELL_SIZE + offset[0], pos[0] * CELL_SIZE + offset[1]))
        
        hud_y = offset[1] + self.board_shape[0] * CELL_SIZE + 20
        draw_text(self.screen, f"Frontier Size: {len(solver.frontier):,}", self.fonts['small'], COLORS['text'], topleft=(offset[0], hud_y))
        draw_text(self.screen, f"Visited States: {len(solver.visited):,}", self.fonts['small'], COLORS['text'], topleft=(offset[0], hud_y + 25))
        time_text = f"Time: {time.time() - solver.start_time:.2f}s" if not solver.is_finished else f"Time: {solver.metrics['time']:.2f}s"
        draw_text(self.screen, time_text, self.fonts['small'], COLORS['text'], topleft=(offset[0], hud_y + 50))
        draw_text(self.screen, f"Path Length: {len(path)}", self.fonts['small'], COLORS['text'], topleft=(offset[0] + 250, hud_y))

    def draw_ready_screen(self):
        self.draw_single_board(self.bfs_solver, self.bfs_board, [], self.bfs_offset)
        self.draw_single_board(self.dfs_solver, self.dfs_board, [], self.dfs_offset)

    def draw_results_screen(self):
        draw_text(self.screen, "Final Results", self.fonts['title'], COLORS['text'], center=(self.screen_w / 2, 200))
        headers, bfs_res, dfs_res = ["Metric", "BFS", "DFS"], self.bfs_solver.metrics, self.dfs_solver.metrics
        data = [
            ("Time Taken", f"{bfs_res.get('time', 'N/A'):.4f}s", f"{dfs_res.get('time', 'N/A'):.4f}s"),
            ("Solution Length", str(bfs_res.get('len', 'N/A')), str(dfs_res.get('len', 'N/A'))),
            ("States Visited", f"{bfs_res.get('visited', 'N/A'):,}", f"{dfs_res.get('visited', 'N/A'):,}"),
            ("Nodes Expanded", f"{bfs_res.get('expanded', 'N/A'):,}", f"{dfs_res.get('expanded', 'N/A'):,}")
        ]
        bfs_len = bfs_res.get('len', float('inf')) if isinstance(bfs_res.get('len'), int) else float('inf')
        dfs_len = dfs_res.get('len', float('inf')) if isinstance(dfs_res.get('len'), int) else float('inf')
        
        col_widths = [260, 220, 220]; start_x = (self.screen_w - sum(col_widths)) // 2; start_y = 280
        
        for i, header in enumerate(headers):
            draw_text(self.screen, header, self.fonts['medium'], COLORS['text'], center=(start_x + sum(col_widths[:i]) + col_widths[i]//2, start_y))
        
        for r, row_data in enumerate(data):
            y = start_y + (r + 1) * 70
            if r == 1: 
                if bfs_len < dfs_len: pygame.draw.rect(self.screen, COLORS['highlight_win'], (start_x + col_widths[0], y - 10, col_widths[1], 50), border_radius=8)
                elif dfs_len < bfs_len: pygame.draw.rect(self.screen, COLORS['highlight_win'], (start_x + col_widths[0] + col_widths[1], y - 10, col_widths[2], 50), border_radius=8)
            for c, cell_data in enumerate(row_data):
                draw_text(self.screen, str(cell_data), self.fonts['medium'], COLORS['text'], center=(start_x + sum(col_widths[:c]) + col_widths[c]//2, y))

        conclusion_y = start_y + (len(data) + 1.5) * 70
        if bfs_len < dfs_len: conclusion_text = "Conclusion: BFS found the SHORTEST path, even if it took longer and visited more states."
        elif dfs_len < bfs_len: conclusion_text = "Conclusion: DFS got lucky and found a shorter path first, but this is NOT guaranteed."
        elif bfs_len == dfs_len and bfs_len != float('inf'): conclusion_text = "Conclusion: Both found the optimal path. BFS guarantees this; DFS was fortunate."
        else: conclusion_text = "Conclusion: Neither algorithm found a solution in the given constraints."
        
        draw_text(self.screen, conclusion_text, self.fonts['medium'], COLORS['title'], center=(self.screen_w/2, conclusion_y))

    def draw_control_panel(self):
        panel_y = self.screen_h - 100
        pygame.draw.rect(self.screen, (233, 236, 239), (0, panel_y, self.screen_w, 100))
        pygame.draw.line(self.screen, (206, 212, 218), (0, panel_y), (self.screen_w, panel_y), 2)
        
        for name, button in self.buttons.items():
            if name not in ['prev_lvl', 'next_lvl']: button.draw(self.screen, self.fonts['btn'])
        
        if self.mode in ['SEARCHING', 'PAUSED']:
            draw_text(self.screen, f"Speed Delay: {self.visualization_delay}", self.fonts['small'], COLORS['instructions'], centerx=self.buttons['start_pause'].rect.centerx, y=self.buttons['start_pause'].rect.bottom + 5)

    def run(self):
        while True:
            self.buttons['prev_lvl'].is_enabled = (self.mode != "SEARCHING" and self.current_level_index > 0)
            self.buttons['next_lvl'].is_enabled = (self.mode != "SEARCHING" and self.current_level_index < len(INITIAL_LEVELS)-1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                    pygame.quit(); sys.exit()
                
                if self.buttons['prev_lvl'].handle_event(event):
                    self.current_level_index -= 1; self.reset_solvers()
                if self.buttons['next_lvl'].handle_event(event):
                    self.current_level_index += 1; self.reset_solvers()

                for btn_name, button in self.buttons.items():
                    if button.handle_event(event):
                        if btn_name == 'quit': pygame.quit(); sys.exit()
                        if btn_name == 'reset': self.reset_solvers()
                        if btn_name == 'start_pause':
                            if self.mode == "READY": self.mode = "SEARCHING"; button.text = "Pause"
                            elif self.mode == "SEARCHING": self.mode = "PAUSED"; button.text = "Resume"
                            elif self.mode == "PAUSED": self.mode = "SEARCHING"; button.text = "Pause"
                        if btn_name == 'speed_down': self.visualization_delay += 1
                        if btn_name == 'speed_up': self.visualization_delay = max(0, self.visualization_delay - 1)

            if self.mode == "SEARCHING":
                self.delay_counter += 1
                if self.delay_counter >= self.visualization_delay:
                    self.delay_counter = 0
                    self.bfs_board, self.bfs_path = self.bfs_solver.step()
                    self.dfs_board, self.dfs_path = self.dfs_solver.step()
                    if self.bfs_solver.is_finished and self.dfs_solver.is_finished:
                        self.mode = "RESULTS"
            self.draw(); self.clock.tick(FPS)

def main():
    assets_path = "./assets" 
    import os
    if not os.path.exists(assets_path) or not os.path.exists(f"{assets_path}/playerFace.png") or not os.path.exists(f"{assets_path}/box.png"):
        print(f"FATAL ERROR: Could not find 'assets' folder at '{assets_path}' or it's missing required images."); return

    SokobanComparison(assets_path).run()

if __name__ == "__main__":
    main()