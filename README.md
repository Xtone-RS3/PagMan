*This project has been created as part of the 42 curriculum by gasoares, rumontei.*

## Description

PAG-MAN is a modern implementation of the classic Pac-Man arcade game featuring procedurally generated mazes, four distinct ghost AI behaviors, and a fully functional scoring system with persistent highscores. The game runs on Pygame and includes an interactive sidebar with real-time cheat controls for testing and experimentation.

### Core Features

- **Procedural Maze Generation**: Each level generates a unique maze using a depth-first search algorithm with a seeded random generator for reproducible results
- **Four Ghost AI Types**: Each ghost has unique behavior:
  - **Red Ghost (Blinky)**: Direct chase using BFS pathfinding
  - **Orange Ghost (Clyde)**: Random movement with backtrack avoidance
  - **Pink Ghost (Pinky)**: Ambush behavior - chases when far (>8 cells), wanders when close
  - **Cyan Ghost (Inky)**: Predictive ambush targeting 2 cells ahead of player's direction
- **Power-ups System**: Super Pac-Gums make ghosts edible for 8 seconds, awarding 200 points per ghost
- **Highscore Persistence**: Scores are saved to JSON and displayed in a ranked leaderboard
- **Interactive Cheat Controls**: Real-time sidebar with buttons for Ghost Freeze, Invincibility, speed adjustments, life manipulation, and level skipping
- **Multi-level Progression**: Levels changing the seed for maze generation
- **Time Pressure**: Each level has a countdown timer (configurable)

## Instructions

### Installation

```bash
# Create virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install and run the game
make run
```

### Controls

| Key | Action |
|-----|--------|
| Arrow Keys | Move Pac-Man |
| P | Pause/Resume game |
| ESC | Exit to main menu |
| SPACE | Return to main menu |

### Building Executable

```bash
make install
```

The executable will be created in the `dist/` directory.

## Configuration

The game reads configuration from `config.json`. All settings can be customized:

```json
{
    "highscore_filename": "HS.json",      # Highscore save file
    "level_cap": 10,                       # Maximum number of levels
    "width": 19,                          # Maze width in cells (minimum 14)
    "height": 19,                         # Maze height in cells (minimum 14)
    "lives": 100,                         # Starting lives
    "pacgum": 42,                         # Number of pac-gums per level
    "points_per_pacgum": 10,               # Points per regular pac-gum
    "points_per_super_pacgum": 50,         # Points per super pac-gum
    "points_per_ghost": 200,               # Points per eaten ghost
    "seed": 42,                           # Random seed for maze generation
    "level_max_time": 1000                 # Time limit per level (seconds)
}
```

**Note**: The maze size must be at least 14x14 cells to properly display the "42" pattern.

### Cheat Controls (Sidebar)

The right sidebar provides interactive cheat buttons:

| Control | Function |
|---------|----------|
| Ghost Freeze | Toggle ON/OFF - freezes all ghosts |
| Invincibility | Toggle ON/OFF - makes Pac-Man immortal |
| Ghost Speed +/- | Adjust ghost movement speed (1-9) |
| Life Cheat +/- | Add or remove lives |
| Player Speed +/- | Adjust Pac-Man speed |
| Level Skip → | Advance to next level |

## Highscore System

Highscores are stored in `HS.json` using JSON format. When a game ends, players enter their name (max 10 characters) and their score is saved.

### Why JSON?

- Human-readable format for easy debugging
- Direct Python dictionary serialization with `json.dump()`
- No external database dependencies
- Simple backup and modification

### Leaderboard Display

- Top 10 scores are displayed
- Sorted in descending order by score
- Shows rank, player name, and score
- Accessible from main menu and after game over

## Implementation

### Architecture

The game follows a modular architecture with clear separation of concerns:

```
srcs/
├── game.py      # Main game loop, maze rendering, event handling
├── pacman.py    # Game entity coordinator (player + ghosts)
├── player.py   # Player sprite, movement, death handling
├── ghosts.py    # Ghost AI classes with unique behaviors
├── movement.py  # Grid-based movement and collision
├── gums.py      # Pac-gum and Super Pac-gum sprites
├── ui.py       # Sidebar UI, menus, leaderboard
└── paths.py     # Asset path resolution

mazegenerator/
└── mazegenerator.py  # External maze generation library
```

### Key Classes

| Class | Responsibility |
|-------|----------------|
| `PacMan` | Coordinates player, ghosts, and game-level config |
| `Player` | Handles input, movement, death, scoring |
| `Ghost` (ABC) | Base ghost with movement, collision, edible state |
| `redGhost` | Chases player using BFS |
| `orangeGhost` | Random movement |
| `pinkGhost` | Distance-based chase/wander |
| `cyanGhost` | Predictive ambush AI |
| `Movement` | Grid-based position and direction management |
| `Pacgum/SuperPacgum` | Collectible items |

### Technical Decisions

1. **Sprite-based Rendering**: All game entities use Pygame sprites for efficient collision detection
2. **Grid-based Movement**: Position stored as both grid coordinates (for logic) and pixel coordinates (for rendering)
3. **BFS Pathfinding**: Ghosts use Breadth-First Search for optimal pathfinding
4. **Custom Event System**: Uses `pygame.event.custom_type()` for player death events
5. **State Machine Pattern**: Ghosts transition between states (chase, flee, respawn, dead)

### Game Loop

1. **Event Polling**: Handle keyboard, mouse, and system events
2. **Update Phase**: Move player, update ghosts, check collisions
3. **Collision Detection**: Pac-gum collection, ghost collision, wall collision
4. **Render Phase**: Draw maze, sprites, UI sidebar
5. **State Management**: Track lives, score, level progression

## General Software Architecture

### Module Overview

```
┌──────────────────────────────────────────────────────────────┐
│                         game.py                              │
│  (Main loop, maze rendering, event coordination)             │
└──────────────────────┬───────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ pacman.py│  │  ui.py   │  │ gums.py  │
   │          │  │          │  │          │
   │  Player  │  │  Menus   │  │ Pacgum   │
   │  Ghosts  │  │ Sidebar  │  │SuperGum  │
   └────┬─────┘  └──────────┘  └──────────┘
        │
   ┌────┴──────┐
   │movement.py│
   │           │
   │ Collision │
   │ Pathfind  │
   └───────────┘
```

### Class Relationships

- **Player** ↔ **Movement**: Has-a relationship for position updates
- **Ghost** ↔ **Movement**: Has-a relationship for ghost movement
- **PacMan** → **Player**: Contains one player instance
- **PacMan** → **Ghost**: Contains list of 4 ghosts
- **Game** → **PacMan**: Contains game entity for current level

### Data Flow

1. User input → Player.update() → Movement.update()
2. Game tick → Ghost.update() → BFS pathfinding → Movement.update()
3. Collision → Sprite collision → Score/lives update → UI update
4. Level complete → New maze → Reset entities → Continue

## Project Management

This project was developed collaboratively by the team members using iterative development:

1. **Phase 1**: Core game loop and basic movement
2. **Phase 2**: Ghost AI implementation with distinct behaviors
3. **Phase 3**: UI system with sidebar and cheat controls
4. **Phase 4**: Highscore system and persistence
5. **Phase 5**: Polish and bug fixes

### Development Tools

- **Git**: Version control with feature branches
- **Pygame**: Game development library
- **Flake8/Mypy**: Code quality and type checking

## Resources

- [Breadth-First Search Algorithm](https://en.wikipedia.org/wiki/Breadth-first_search)

### AI Usage

AI was used in this project for:

- **Code Review**: Identifying potential bugs and race conditions
- **Architecture Suggestions**: Improving module separation
- **Documentation**: Generating docstrings and type hints
- **Bug Investigation**: Tracing complex collision edge cases
- **Refactoring**: Improving code clarity and reducing duplication

All AI assistance was reviewed and integrated by the human developers to ensure correctness and alignment with the project goals.
