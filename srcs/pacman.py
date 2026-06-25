from mazegenerator import MazeGenerator
from typing import Any, Dict, List
from ghosts import redGhost, orangeGhost, pinkGhost, cyanGhost, Ghost
from player import Player


class PacMan:
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
