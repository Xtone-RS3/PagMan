from typing import Any, List
import pygame
from abc import ABC, abstractmethod
from movement import Movement
from player import Player
import random
from pygame.surface import Surface
from pygame.rect import Rect


class Ghost(pygame.sprite.Sprite):  # , ABC
    def __init__(
            self,
            spawn: tuple[float, float],
            color: str,
            images: List[Surface],
            cell_x_size: float,
            cell_y_size: float
    ):
        super().__init__()
        self.is_alive = True
        self.is_edible = False
        self.spawn = spawn  # [x, y]
        self.spawn_coords = (
            int(self.spawn[0] // cell_x_size),
            int(self.spawn[1] // cell_y_size)
        )
        self.color = color
        self.position = spawn
        self.base_speed = 4
        self.frozen = False
        self.edible_start = 0
        self.edible_duration = 8000  # -(level_n*1000)
        a = int(cell_x_size * 2/3)
        b = int(cell_y_size * 2/3)
        size = min(a, b)
        self.images = [
            pygame.transform.scale(img, (size, size))
            for img in images
        ]
        self.body: Surface = self.images[0]
        self.image = self.body.copy()
        self.rect: Rect = self.image.get_rect()
        self.rect.center = (int(spawn[0]), int(spawn[1]))
        self.eyes = [
            img  # pygame.transform.scale(img, (size, size))
            for img in self.images[1:5]  # down, up, right, left
        ]
        # Red (Blinky): Relentlessly chases Pac-Man directly.
        # Pink (Pinky): Tries to position herself ahead of Pac-Man to trap him.
        # Cyan/Light Blue (Inky): Has an unpredictable, flanking personality.
        # Orange (Clyde): Wanders aimlessly or moves randomly.
        # Dark blue: run away
        self.movement = Movement(
            cell_x_size,
            cell_y_size,
            spawn,
            speed=self.base_speed
        )
        self.hitbox = self.rect.inflate(-28, -28)

    @abstractmethod
    def update(self, walls: Any, player: Player) -> None:    
        pass

    def eye_update(self) -> None:
        """TODO"""
        if self.is_alive is True and self.is_edible is False:
            self.image = self.body.copy()
            if self.movement.dir_x == 1:
                self.image.blit(self.eyes[2], (0, 0))
            elif self.movement.dir_x == -1:
                self.image.blit(self.eyes[3], (0, 0))
            elif self.movement.dir_y == 1:
                self.image.blit(self.eyes[0], (0, 0))
            elif self.movement.dir_y == -1:
                self.image.blit(self.eyes[1], (0, 0))
            else:
                self.image.blit(self.eyes[1], (0, 0))
        elif self.is_alive is True and self.is_edible is True:
            self.image = self.images[5]
        elif self.is_alive is False:
            if self.movement.dir_x == 1:
                self.image = self.eyes[2]
            elif self.movement.dir_x == -1:
                self.image = self.eyes[3]
            elif self.movement.dir_y == 1:
                self.image = self.eyes[0]
            elif self.movement.dir_y == -1:
                self.image = self.eyes[1]
            else:
                self.image = self.eyes[1]

    def death_routine(self, player: Player) -> None:
        if player.lives != -1:
            if self.rect.colliderect(player.rect):
                self.movement.pixel_x, self.movement.pixel_y = self.spawn
                self.movement.grid_x = int(self.movement.pixel_x // self.movement.cell_x_size)
                self.movement.grid_y = int(self.movement.pixel_y // self.movement.cell_y_size)
                self.movement.dir_x, self.movement.dir_y = 0, 0
                player.death()
                self.is_alive = False

    def escape(self, walls: Any, player: Player) -> None:
        current_time = pygame.time.get_ticks()
        if current_time - self.edible_start >= self.edible_duration:
            self.is_edible = False
            self.movement.speed = self.base_speed

        if self.rect.colliderect(player.rect):
            player.score_gain(100)
            self.is_edible = False
            self.is_alive = False
            self.movement.speed = self.base_speed
            return

        next_dir_x, next_dir_y, path = self.bfs(walls, player.grid_pos)

        if len(path) <= 8:
            possible_dirs = []
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                if self.movement.can_move(
                    walls, self.movement.grid_x, self.movement.grid_y, dx, dy
                ):
                    possible_dirs.append((dx, dy))

            dist = []
            for dx, dy in possible_dirs:
                tx = self.movement.grid_x + dx
                ty = self.movement.grid_y + dy
                dist.append(
                    (tx - player.grid_pos[0]) ** 2
                    + (ty - player.grid_pos[1]) ** 2
                )

            if dist:
                max_dist = max(dist)
                best_dirs = [
                    possible_dirs[i] for i in range(len(possible_dirs))
                    if dist[i] == max_dist
                ]
                next_dir_x, next_dir_y = random.choice(best_dirs)
        else:
            # randomly
            possible_dirs = []
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                if self.movement.can_move(
                    walls, self.movement.grid_x, self.movement.grid_y, dx, dy
                ):
                    if (dx, dy) != (
                        -self.movement.dir_x, -self.movement.dir_y
                    ):
                        possible_dirs.append((dx, dy))
            if possible_dirs:
                next_dir_x, next_dir_y = random.choice(possible_dirs)

        self.movement.update(walls, next_dir_x, next_dir_y)
        self.rect.center = (
            int(self.movement.pixel_x),
            int(self.movement.pixel_y)
        )

    def respawn(self, walls: Any, player: Player) -> None:
        self.movement.speed = self.base_speed*2
        next_dir_x, next_dir_y, path_ghost = self.bfs(walls, self.spawn_coords)
        _, _, path = self.bfs(walls, player.grid_pos)
        self.movement.update(walls, next_dir_x, next_dir_y)
        self.rect.center = (
            int(self.movement.pixel_x),
            int(self.movement.pixel_y)
        )
        if (
            self.movement.grid_x, self.movement.grid_y) == (self.spawn_coords)\
                and (self.movement.dir_x, self.movement.dir_y) == (0, 0) and\
                len(path) > 4:
            self.is_alive = True
            self.is_edible = False
            self.movement.speed = self.base_speed

    def bfs(self, walls: Any, target: tuple[int, int]) -> tuple[int, int, List]:
        start = (self.movement.grid_x, self.movement.grid_y)
        queue = [start]
        visited = {start}
        origin: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        found = False
        current = start
        while queue:
            current = queue.pop(0)
            if current == target:
                found = True
                break
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor not in visited and self.movement.can_move(
                    walls, current[0], current[1], dx, dy
                ):
                    visited.add(neighbor)
                    queue.append(neighbor)
                    origin[neighbor] = current
        path: List = []
        if found:
            node: tuple[int, int] | None = current
            while node is not None:
                path.append(node)
                node = origin.get(node)
            path.reverse()
        if len(path) >= 2:
            curr_cell = path[0]
            next_cell = path[1]
            next_dir_x = next_cell[0] - curr_cell[0]
            next_dir_y = next_cell[1] - curr_cell[1]
        else:
            next_dir_x, next_dir_y = 0, 0
        return next_dir_x, next_dir_y, path


class redGhost(Ghost):
    def __init__(
            self,
            spawn: tuple[float, float],
            color: str,
            images: List[Surface],
            cell_x_size: float,
            cell_y_size: float
    ):
        super().__init__(
            spawn,
            color,
            images,
            cell_x_size,
            cell_y_size,
        )

    def update(self, walls: Any, player: Player) -> None:
        self.eye_update()
        if self.frozen:
            self.movement.speed = 0
            pass
        else:
            self.movement.speed = self.base_speed
        if self.is_edible is False and self.is_alive is True:
            self.death_routine(player)
            next_dir_x, next_dir_y, path = self.bfs(walls, player.grid_pos)
            # Atualiza movimento e posição do sprite
            if len(path) < 8:
                self.movement.update(walls, next_dir_x, next_dir_y)
            else:
                next_dir_x = 0
                next_dir_y = 0

                possible_dirs = []
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    if self.movement.can_move(
                        walls,
                        self.movement.grid_x,
                        self.movement.grid_y,
                        dx,
                        dy
                    ):
                        if (dx, dy) != (
                            -self.movement.dir_x, -self.movement.dir_y
                        ):
                            possible_dirs.append((dx, dy))
                if possible_dirs:
                    next_dir_x, next_dir_y = random.choice(possible_dirs)

                self.movement.update(walls, next_dir_x, next_dir_y)
            self.rect.center = (
                int(self.movement.pixel_x),
                int(self.movement.pixel_y)
            )
        elif self.is_edible is True and self.is_alive is True:
            self.escape(walls, player)
        else:
            self.respawn(walls, player)


class orangeGhost(Ghost):
    def __init__(
            self,
            spawn: tuple[float, float],
            color: str,
            images: List[Surface],
            cell_x_size: float,
            cell_y_size: float
    ):
        super().__init__(
            spawn,
            color,
            images,
            cell_x_size,
            cell_y_size,
        )

    def update(self, walls: Any, player: Player) -> None:
        self.eye_update()
        if self.frozen:
            self.movement.speed = 0
            pass
        else:
            self.movement.speed = self.base_speed
        if self.is_edible is False and self.is_alive is True:
            self.death_routine(player)
            next_dir_x = 0
            next_dir_y = 0

            possible_dirs = []
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                if self.movement.can_move(
                    walls, self.movement.grid_x, self.movement.grid_y, dx, dy
                ):
                    if (dx, dy) != (
                        -self.movement.dir_x, -self.movement.dir_y
                    ):
                        possible_dirs.append((dx, dy))
            if possible_dirs:
                next_dir_x, next_dir_y = random.choice(possible_dirs)

            self.movement.update(walls, next_dir_x, next_dir_y)
            self.rect.center = (
                int(self.movement.pixel_x),
                int(self.movement.pixel_y)
            )
        elif self.is_edible is True and self.is_alive is True:
            self.escape(walls, player)
        else:
            self.respawn(walls, player)


class pinkGhost(Ghost):
    def __init__(
            self,
            spawn: tuple[float, float],
            color: str,
            images: List[Surface],
            cell_x_size: float,
            cell_y_size: float
    ):
        super().__init__(
            spawn,
            color,
            images,
            cell_x_size,
            cell_y_size,
        )

    def update(self, walls: Any, player: Player) -> None:
        if self.frozen:
            self.movement.speed = 0
            pass
        else:
            self.movement.speed = self.base_speed
        self.eye_update()
        if self.is_edible is False and self.is_alive is True:
            self.death_routine(player)
            spawn_grid = (
                int(self.spawn[0] // self.movement.cell_x_size),
                int(self.spawn[1] // self.movement.cell_y_size)
            )
            next_dir_x, next_dir_y, path = self.bfs(walls, player.grid_pos)
            if len(path) <= 8:
                next_dir_x, next_dir_y, path = self.bfs(walls, spawn_grid)

            self.movement.update(walls, next_dir_x, next_dir_y)
            self.rect.center = (
                int(self.movement.pixel_x),
                int(self.movement.pixel_y)
            )
        elif self.is_edible is True and self.is_alive is True:
            self.escape(walls, player)
        else:
            self.respawn(walls, player)


class cyanGhost(Ghost):
    def __init__(
            self,
            spawn: tuple[float, float],
            color: str,
            images: List[Surface],
            cell_x_size: float,
            cell_y_size: float
    ):
        super().__init__(
            spawn,
            color,
            images,
            cell_x_size,
            cell_y_size,
        )

    def update(self, walls: Any, player: Player) -> None:
        self.eye_update()
        if self.frozen:
            self.movement.speed = 0
            pass
        else:
            self.movement.speed = self.base_speed
        if self.is_edible is False and self.is_alive is True:
            self.death_routine(player)
            if player.movement.dir_x == 0 and player.movement.dir_y == 0:
                next_dir_x, next_dir_y = 0, 0
            else:
                next_dir_x, next_dir_y = 0, 0
                for i in range(2, 0, -1):
                    tx = player.grid_pos[0] + i * player.movement.dir_x
                    ty = player.grid_pos[1] + i * player.movement.dir_y
                    if 0 <= tx < len(walls[0]) and 0 <= ty < len(walls):
                        next_dir_x, next_dir_y, _ = self.bfs(walls, (tx, ty))
                        break
            self.movement.update(walls, next_dir_x, next_dir_y)
            self.rect.center = (
                int(self.movement.pixel_x),
                int(self.movement.pixel_y)
            )
        elif self.is_edible is True and self.is_alive is True:
            self.escape(walls, player)
        else:
            self.respawn(walls, player)
