from typing import Any
import pygame
import sys
from movement import Movement
from pygame.rect import Rect


class Player(pygame.sprite.Sprite):
    def __init__(
            self,
            spawn: tuple[float, float],
            cell_x_size: float,
            cell_y_size: float,
            lives: int = 3,
            score: int = 0,
            player_died: int = 32867,
            maze_offset_x: float = 0,
            maze_offset_y: float = 0
    ):
        super().__init__()
        self.spawn = (spawn)  # PacMan class
        self.cell_x_size = cell_x_size
        self.cell_y_size = cell_y_size
        self.lives = lives
        self.score = score
        self.just_died = False
        self.orig_image = [pygame.image.load("PagMan.png"),
                           pygame.image.load("PauseMan.png")]
        a = int(cell_x_size * 2/3)
        b = int(cell_y_size * 2/3)
        size = min(a, b)
        self.orig_image = [
            pygame.transform.scale(self.orig_image[0],
                                   (size, size)),
            pygame.transform.scale(self.orig_image[1],
                                   size=(size, size))
        ]
        self.frame: int = 1
        self.current = self.orig_image[self.frame]
        self.last_angle = 0
        self.image = self.orig_image[self.frame]
        self.rect: Rect = self.orig_image[0].get_rect()
        self.pixel_x, self.pixel_y = spawn
        self.rect.center = (int(self.pixel_x), int(self.pixel_y))

        self.grid_x = int(self.pixel_x // cell_x_size)
        self.grid_y = int(self.pixel_y // cell_y_size)

        self.next_dir_x = 0
        self.next_dir_y = 0
        self.speed = 5  # PacMan class
        self.movement = Movement(
            cell_x_size,
            cell_y_size,
            spawn,
            5,
            maze_offset_x,
            maze_offset_y
        )
        self.interval = 200
        self.next_tick = pygame.time.get_ticks() + self.interval
        self.player_died = player_died

    def update_image(self) -> None:  # copy this exact logic for ghost eyes
        center = self.rect.center
        image = self.orig_image[self.frame]
        if self.movement.dir_x == -1 or (self.movement.dir_x == 0 and
                                         self.movement.dir_y == 0 and
                                         self.last_angle == -180):
            self.last_angle = -180
            image = pygame.transform.flip(image, True, False)
        elif self.movement.dir_y == -1 or (self.movement.dir_x == 0 and
                                           self.movement.dir_y == 0 and
                                           self.last_angle == 90):
            self.last_angle = 90
            image = pygame.transform.rotate(image, 90)
        elif self.movement.dir_y == 1 or (self.movement.dir_x == 0 and
                                          self.movement.dir_y == 0 and
                                          self.last_angle == -90):
            self.last_angle = -90
            image = pygame.transform.rotate(image, -90)
        else:
            self.last_angle = 0
        self.image = image
        self.rect = self.image.get_rect(center=center)

    @property
    def grid_pos(self) -> tuple[int, int]:
        return (
            int((self.movement.pixel_x - self.movement.maze_offset_x) // self.cell_x_size),
            int((self.movement.pixel_y - self.movement.maze_offset_y) // self.cell_y_size)
        )

    def update(self, walls: Any, current_time: int) -> None:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.next_dir_x, self.next_dir_y = -1, 0
        elif keys[pygame.K_RIGHT]:
            self.next_dir_x, self.next_dir_y = 1, 0
        elif keys[pygame.K_UP]:
            self.next_dir_x, self.next_dir_y = 0, -1
        elif keys[pygame.K_DOWN]:
            self.next_dir_x, self.next_dir_y = 0, 1

        self.movement.update(walls, self.next_dir_x, self.next_dir_y)
        self.rect.center = (
            int(self.movement.pixel_x),
            int(self.movement.pixel_y)
        )
        moving = (
            self.movement.dir_x != 0 or self.movement.dir_y != 0
        )
        if not moving:
            self.frame = 1
            self.next_tick = current_time + self.interval
            self.update_image()
        if moving and current_time >= self.next_tick:
            self.next_tick += self.interval
            self.frame = (self.frame + 1) % len(self.orig_image)
            self.update_image()

    def death(self) -> None:
        self.lives -= 1
        # death anim
        if self.lives == 0:
            # this should only end the game and boot the player to scoreboard
            print("here")
            pygame.event.post(pygame.event.Event(self.player_died))
            # sys.exit()
        else:
            self.movement.pixel_x, self.movement.pixel_y = self.spawn
            self.movement.grid_x = int(
                (self.movement.pixel_x - self.movement.maze_offset_x) // self.cell_x_size
            )
            self.movement.grid_y = int(
                (self.movement.pixel_y - self.movement.maze_offset_y) // self.cell_y_size
            )
            self.movement.dir_x, self.movement.dir_y = 0, 0
            self.next_dir_x, self.next_dir_y = 0, 0
            self.rect.center = (int(self.movement.pixel_x),
                                int(self.movement.pixel_y))
            self.just_died = True

    def score_gain(self, score_gained: int) -> None:
        self.score += score_gained
