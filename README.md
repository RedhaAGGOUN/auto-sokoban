# Sokoban - A Modern Python Implementation

This is a feature-rich implementation of the classic puzzle game Sokoban, built with Python and Pygame. It includes a modern UI, a level editor, a player ranking system, and an in-game solver.

## ✨ Key Features

*   **Classic Sokoban Gameplay**: Enjoy dozens of pre-built, challenging levels.
*   **Built-in Level Editor**: Unleash your creativity! Design, build, and save your own puzzles. The editor validates your level to ensure it's playable.
*   **Community Levels**: Play levels created by other players. Your custom levels are automatically shared.
*   **Player Profiles & Progress**: Create a player profile to track your progress. Earn up to 3 stars on each level based on your performance.
*   **High Score Leaderboard**: Compete with other players! A global leaderboard ranks players by the total number of stars collected.
*   **In-Game Solver**: Stuck on a puzzle? The game can compute and demonstrate the optimal solution for you with its on-demand BFS-based solver.
*   **Modern UI & UX**: A clean, intuitive, and animated user interface makes navigating the game a breeze.
*   **Responsive Design**: The game window is fully resizable, and the UI elements and game board scale accordingly.
*   **Full Audio**: Includes background music and sound effects for an immersive experience.

## 📋 Requirements

*   Python 3.8+
*   Pygame
*   NumPy

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
| Key(s)               | Action                      |
| -------------------- | --------------------------- |
| **Arrow Keys / WASD**| Move the player             |
| **Z / U**            | Undo the last move          |
| **R**                | Restart the current level   |
| **H**                | Show the optimal solution   |
| **ESC / M**          | Return to the main menu     |

### Scoring
You earn stars based on how efficiently you solve a level. The number of stars is determined by comparing your move count to the optimal solution's move count.
*   **★★★**: Solved with the optimal number of moves.
*   **★★☆**: Solved with a good number of moves (up to 1.5x optimal).
*   **★☆☆**: Solved the level.

## 🛠️ Level Editor

The level editor allows you to create and save your own Sokoban puzzles.

1.  **Select a Tool**: Choose a tool from the palette on the right (Wall, Eraser, Target, Box, Player).
2.  **Paint/Stamp**:
    *   **Paint Tools** (Wall, Eraser): Click and drag on the canvas to draw.
    *   **Stamp Tools** (Target, Box, Player): Click a single tile to place the object. The Player tool will automatically replace any existing player on the board.
3.  **Validation**: The editor provides real-time feedback to ensure your level is valid. A valid level must have:
    *   Exactly one Player.
    *   At least one Box.
    *   An equal number of Boxes and Targets.
4.  **Save & Test**: Once your level is valid, click the **"SAVE & TEST"** button. The game will run the solver to confirm the level is solvable. If it is, it will be saved to the `custom_levels/` directory and become available in the "Community Levels" menu.

## 📂 Project Structure

The project is organized into several modules to separate concerns:
