from typing import Any
import pygame
from movement import Movement
from pygame.rect import Rect
from paths import asset


class Player(pygame.sprite.Sprite):
    """The player-controlled Pac-Man character.

    Handles player input, movement, animation, death, and score tracking.
    """

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
        """Initializes the player sprite.

        Args:
            spawn: Starting position in pixels.
            cell_x_size: Width of each cell in pixels.
            cell_y_size: Height of each cell in pixels.
            lives: Starting number of lives.
            score: Initial score.
            player_died: Pygame event type for death notification.
            maze_offset_x: X offset of maze in window.
            maze_offset_y: Y offset of maze in window.
        """
        super().__init__()
        self.spawn = (spawn)  # PacMan class
        self.cell_x_size = cell_x_size
        self.cell_y_size = cell_y_size
        self.lives = lives
        self.score = score
        self.just_died = False
        self.orig_image = [
            pygame.image.load(asset("pacmen_and_gums", "PagMan.png")),
            pygame.image.load(asset("pacmen_and_gums", "PauseMan.png"))
        ]
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

    def update_image(self) -> None:
        """Updates the player sprite based on movement direction.

        Rotates or flips the base sprite image to face the current
        movement direction.
        """
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
        """Returns the player's current grid position.

        Calculated from pixel position accounting for maze offset.
        """
        return (
            int((self.movement.pixel_x - self.movement.maze_offset_x) //
                self.cell_x_size),
            int((self.movement.pixel_y - self.movement.maze_offset_y) //
                self.cell_y_size)
        )

    def update(self, walls: Any, current_time: int) -> None:
        """Updates player state based on keyboard input.

        Reads arrow key input to queue direction changes and updates
        movement animation frames.

        Args:
            walls: 2D array representing maze walls.
            current_time: Current game time in milliseconds.
        """
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
        """Handles player death.

        Decrements lives and either respawns at the start position
        or posts a death event to end the game.
        """
        if self.lives > 0:
            self.lives -= 1
        # death anim
        if self.lives <= 0:
            pygame.event.post(pygame.event.Event(self.player_died))
        else:
            self.movement.pixel_x, self.movement.pixel_y = self.spawn
            self.movement.grid_x = int(
                (self.movement.pixel_x - self.movement.maze_offset_x) //
                self.cell_x_size
            )
            self.movement.grid_y = int(
                (self.movement.pixel_y - self.movement.maze_offset_y) //
                self.cell_y_size
            )
            self.movement.dir_x, self.movement.dir_y = 0, 0
            self.next_dir_x, self.next_dir_y = 0, 0
            self.rect.center = (int(self.movement.pixel_x),
                                int(self.movement.pixel_y))
            self.just_died = True

    def score_gain(self, score_gained: int) -> None:
        """Adds points to the player's score.

        Args:
            score_gained: Number of points to add.
        """
        self.score += score_gained
