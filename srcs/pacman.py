from mazegenerator import MazeGenerator
from typing import Any, Dict, List
from ghosts import redGhost, orangeGhost, pinkGhost, cyanGhost, Ghost
from player import Player


class PacMan:
    """Main game entity that manages player and ghosts.

    Coordinates the player character, ghost spawning, and game-level
    configuration including score tracking and pac-gum management.
    """

    def __init__(
            self,
            maze: MazeGenerator,
            config: Dict[Any, Any],
            spawn_x: float,
            spawn_y: float,
            image_list: Dict[Any, Any],
            cell_x_size: float,
            cell_y_size: float,
            score: int,
            player_died: int,
            maze_offset_x: float,
            maze_offset_y: float
    ):
        """Initializes Pac-Man game entity.

        Args:
            maze: The maze generator instance.
            config: Game configuration dictionary.
            spawn_x: Player spawn X coordinate.
            spawn_y: Player spawn Y coordinate.
            image_list: Dictionary of loaded sprite images.
            cell_x_size: Cell width in pixels.
            cell_y_size: Cell height in pixels.
            score: Initial player score.
            player_died: Pygame event type for death notification.
            maze_offset_x: X offset of maze in window.
            maze_offset_y: Y offset of maze in window.
        """
        self.maze_offset_x = maze_offset_x
        self.maze_offset_y = maze_offset_y
        self.maze: MazeGenerator = maze
        self.level_cap = config["level_cap"]
        self.config = config
        self.ghost_spawn = [
            (
                0 * cell_x_size + cell_x_size / 2 + maze_offset_x,
                0 * cell_y_size + cell_y_size / 2 + maze_offset_y
            ),
            (
                (config["width"]-1) * cell_x_size + cell_x_size / 2 +
                maze_offset_x,
                (config["height"]-1) * cell_y_size + cell_y_size / 2 +
                maze_offset_y
            ),
            (
                0 * cell_x_size + cell_x_size / 2 + maze_offset_x,
                (config["height"]-1) * cell_y_size + cell_y_size / 2 +
                maze_offset_y
            ),
            (
                (config["width"]-1) * cell_x_size + cell_x_size / 2 +
                maze_offset_x,
                0 * cell_y_size + cell_y_size / 2 + maze_offset_y
            )
        ]

        self.ghosts: List[Ghost] = []

        self.player = Player((spawn_x, spawn_y), cell_x_size,
                             cell_y_size,
                             self.config["lives"], score,
                             player_died, maze_offset_x, maze_offset_y)
        self.pacgum = config["pacgum"]
        self.points_per_pacgum = config["points_per_pacgum"]
        self.points_per_super_pacgum = config["points_per_super_pacgum"]
        self.points_per_ghost = config["points_per_ghost"]
        self.level_max_time = config["level_max_time"]
        self.image_list = image_list
        self.ghost_gen(cell_x_size, cell_y_size)

    def ghost_gen(self, cell_x_size: float, cell_y_size: float) -> None:
        """Spawns all four ghosts at their designated positions.

        Args:
            cell_x_size: Cell width in pixels.
            cell_y_size: Cell height in pixels.
        """
        color_class: list[type[Ghost]] = [
            redGhost, orangeGhost, pinkGhost, cyanGhost
        ]
        color_list = ["red", "orange", "pink", "cyan"]
        for i, coords in enumerate(self.ghost_spawn):
            color = color_list[i]
            self.ghosts.append(
                color_class[i](
                    spawn=coords,
                    color=color,
                    images=[
                        self.image_list[color],
                        self.image_list["down_eyes"],
                        self.image_list["up_eyes"],
                        self.image_list["right_eyes"],
                        self.image_list["left_eyes"],
                        self.image_list["dead"]
                    ],
                    cell_x_size=cell_x_size,
                    cell_y_size=cell_y_size,
                    maze_offset_x=self.maze_offset_x,
                    maze_offset_y=self.maze_offset_y
                )
            )
