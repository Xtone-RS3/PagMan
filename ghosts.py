import pygame
from abc import ABC, abstractmethod
from pagman import Movement, Player


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
        if player.grid_pos[1] == self.movement.grid_y and player.grid_pos[0] == self.movement.grid_x:
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
        # print(next_dir_x)
        # self.choose_direction(walls)
        # next_dir_x = random.choice([-1, 0, 1])
        # next_dir_y = random.choice([-1, 0, 1])
        self.movement.update(walls, 0, 1)
        self.rect.center = (
            int(self.movement.pixel_x),
            int(self.movement.pixel_y)
        )

        # def choose_direction(self, walls):
        #     self.movement.next_dir_x = dx
        #     self.movement.next_dir_y = dy
