import pygame
from abc import ABC, abstractmethod
from pagman import Movement, Player
import random


class Ghost(pygame.sprite.Sprite, ABC):
    def __init__(self, spawn, color, images, cell_x_size, cell_y_size):
        super().__init__()
        self.is_alive = True
        self.is_edible = False
        self.spawn = spawn  # [x, y]
        self.color = color
        self.position = spawn
        self.images: list[pygame.image.Surface] = images
        self.image: pygame.image.Surface = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (int(spawn[0]), int(spawn[1]))
        # Red (Blinky): Relentlessly chases Pac-Man directly.
        # Pink (Pinky): Tries to position herself ahead of Pac-Man to trap him.
        # Cyan/Light Blue (Inky): Has an unpredictable, flanking personality.
        # Orange (Clyde): Wanders aimlessly or moves randomly.
        # Dark blue: run away
        self.movement = Movement(
            cell_x_size,
            cell_y_size,
            spawn,
            speed=4
        )

    @abstractmethod
    def update(self, walls):
        pass

    def death_routine(self, player: Player):
        if self.rect.colliderect(player.rect):
            player.death()

    def escape(self, player: Player):
        pass

    def respawn(self):
        pass


class redGhost(Ghost):
    def __init__(self, spawn, color, images, cell_x_size, cell_y_size):
        super().__init__(
            spawn,
            color,
            images,
            cell_x_size,
            cell_y_size,
        )

    def update(self, walls, player: Player):
        self.death_routine(player)
        start = (self.movement.grid_x, self.movement.grid_y)
        target = tuple(player.grid_pos)
        queue = [start]
        visited = {start}
        origin = {start: None}
        found = False
        while queue:
            current = queue.pop(0)
            if current == target:
                found = True
                break
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor not in visited and self.movement.can_move(walls, current[0], current[1], dx, dy):
                    visited.add(neighbor)
                    queue.append(neighbor)
                    origin[neighbor] = current
        if not found:
            path = []
        else:
            path = []
            node = current
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

        # Atualiza movimento e posição do sprite
        self.movement.update(walls, next_dir_x, 0)
        self.rect.center = (
            int(self.movement.pixel_x),
            int(self.movement.pixel_y)
        )

        # def choose_direction(self, walls):
        #     self.movement.next_dir_x = dx
        #     self.movement.next_dir_y = dy


class orangeGhost(Ghost):
    def __init__(self, spawn, color, images, cell_x_size, cell_y_size):
        super().__init__(
            spawn,
            color,
            images,
            cell_x_size,
            cell_y_size,
        )

    def update(self, walls, player: Player):
        self.death_routine(player)
        next_dir_x = 0
        next_dir_y = 0

        # pick a random direction that is not the opposite of the current direction
        possible_dirs = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if self.movement.can_move(walls, self.movement.grid_x, self.movement.grid_y, dx, dy):
                if (dx, dy) != (-self.movement.dir_x, -self.movement.dir_y):
                    possible_dirs.append((dx, dy))
        if possible_dirs:
            next_dir_x, next_dir_y = random.choice(possible_dirs)

        self.movement.update(walls, next_dir_x, next_dir_y)
        self.rect.center = (
            int(self.movement.pixel_x),
            int(self.movement.pixel_y)
        )

        # def choose_direction(self, walls):
        #     self.movement.next_dir_x = dx
        #     self.movement.next_dir_y = dy


class pinkGhost(Ghost):
    def __init__(self, spawn, color, images, cell_x_size, cell_y_size):
        super().__init__(
            spawn,
            color,
            images,
            cell_x_size,
            cell_y_size,
        )

    def update(self, walls, player: Player):
        self.death_routine(player)
        