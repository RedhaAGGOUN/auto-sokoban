# Sokoban - A Modern Python Implementation

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.5.2-green?style=for-the-badge&logo=pygame)](https://www.pygame.org/)

A feature-rich implementation of the classic puzzle game Sokoban, built with Python and Pygame. It includes a modern UI, a level editor, a player ranking system, an in-game AI solver, and a separate educational tool to visualize pathfinding algorithms.

![Sokoban Gameplay Screenshot](https://github.com/user-attachments/assets/b83375c3-1e4e-4e4b-b2c6-d97f5ac04a11)

## ✨ Key Features

-   **Classic Sokoban Gameplay**: Enjoy 15 challenging, pre-built levels.
-   **Built-in Level Editor**: Design, build, and save your own puzzles with an intuitive editor that validates level solvability before saving.
-   **Community Levels**: Play levels created and shared by other players.
-   **Player Profiles & 3-Star Rating**: Create a profile to track your progress. Earn up to 3 stars on each level by solving it in the fewest moves.
-   **High Score Leaderboard**: Compete with others! A global leaderboard ranks players by total stars collected.
-   **In-Game AI Solver**: Stuck on a puzzle? The game can compute and demonstrate the optimal solution for you with its on-demand BFS-based solver.
-   **🤖 AI Algorithm Visualizer**: A standalone tool that runs BFS and DFS side-by-side to visually explain why BFS is the superior choice for finding the *optimal* solution. [Learn more below](#-the-bfs-vs-dfs-showdown).
-   **Modern UI & UX**: A clean, intuitive, and animated user interface makes navigating the game a breeze.
-   **Responsive Design**: The game window is fully resizable, and all UI elements scale accordingly.
-   **Full Audio**: Includes background music and sound effects for an immersive experience.

## 🚀 Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/sokoban-project.git
    cd sokoban-project
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    A `requirements.txt` file is provided for easy installation.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the game:**
    ```bash
    python main.py
    ```

## 🎮 How to Play

### Objective

The goal is to push every box onto a target location. You can only push one box at a time, and you cannot pull boxes.

### Controls

| Key(s)              | Action                    |
| ------------------- | ------------------------- |
| **Arrow Keys / WASD** | Move the player           |
| **Z / U**           | Undo the last move        |
| **R**               | Restart the current level |
| **H**               | Show the optimal solution |
| **ESC / M**         | Return to the main menu   |

### Scoring

You earn stars based on how efficiently you solve a level by comparing your move count to the optimal solution.
-   **★★★**: Solved with the optimal number of moves.
-   **★★☆**: Solved with a good number of moves (up to 1.5x optimal).
-   **★☆☆**: Solved the level.

## 🤖 The BFS vs. DFS Showdown

To demonstrate and justify our choice of the Breadth-First Search (BFS) algorithm for the in-game solver, we built a standalone visualizer tool.

**Purpose:** This tool runs BFS and DFS algorithms in parallel on the same level to provide a clear, visual comparison of their behavior and performance. It proves why BFS, despite being slower, is essential for our 3-star rating system.

### How to Run the Visualizer

Execute the script directly from your terminal:

```bash
python sokoban_BFS_Explained.pyFeatures
Live Side-by-Side Race: Watch as BFS methodically explores layer-by-layer while DFS dives deep down potentially inefficient paths.
Interactive Controls: Start, pause, reset, and change the animation speed.
Cycle Through All Levels: Use the "Prev/Next Level" buttons to see how the algorithms fare on different types of puzzles.
Clear Results: An end screen provides a quantitative comparison of solution length, time taken, and states explored, highlighting the winner.
🛠️ Level Editor
The level editor allows you to create and save your own Sokoban puzzles.
Select a Tool: Choose a tool from the palette on the right (Wall, Eraser, Target, Box, Player).
Paint/Stamp:
Paint Tools (Wall, Eraser): Click and drag on the canvas.
Stamp Tools (Target, Box, Player): Click a single tile to place the object.
Validation: A valid level must have exactly one player and an equal number of boxes and targets.
Save & Test: The "SAVE & TEST" button will first run the solver to confirm the level is solvable. If it is, your level is saved to the custom_levels/ directory and becomes available in the "Community Levels" menu.
📂 Project Structure
The project is organized into several modules to separate concerns:
Generated code
.
├── assets/               # Contains all images and sound files
├── custom_levels/        # User-created levels are saved here as .json
├── main.py               # Main application entry point and game loop manager
├── ui.py                 # Handles all UI screens, rendering, and user input
├── game.py               # Core game state, level management, and player data
├── core.py               # Stateless game logic (move function, win check)
├── solver.py             # BFS-based puzzle solver
├── assets.py             # Asset loading and management class
├── config.py             # Game configuration (FPS, tile size, colors)
├── constants.py          # Game object enumerations (Wall, Box, etc.)
├── save_load.py          # Helper functions for saving/loading JSON data
├── sokoban_BFS_Explained.py # Standalone tool to visualize and compare AI algorithms
├── sokoban_save.json     # Save file for player profiles and scores
└── requirements.txt      # Python package dependencies
Use code with caution.
💾 Save Data
Player Progress: All player profiles, stars earned, and last play times are stored in sokoban_save.json.
Custom Levels: Each custom level is saved as a separate .json file in the custom_levels/ directory, named PlayerName_1.json, etc.
🙏 Credits
This game was created as a project for La Plateforme_.
Generated code
