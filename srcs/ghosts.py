from typing import Any, Dict, List
import pygame
from abc import ABC, abstractmethod
from movement import Movement
from player import Player
import random
from pygame.surface import Surface
from pygame.rect import Rect


class Ghost(pygame.sprite.Sprite, ABC):
    """Base class for all ghost enemies.

    Handles ghost movement, collision with player, edible state, and\
        respawning.
    Each ghost type has different AI behavior implemented in subclasses.
    """

    def __init__(
            self,
            spawn: tuple[float, float],
            color: str,
            images: List[Surface],
            cell_x_size: float,
            cell_y_size: float,
            maze_offset_x: float = 0,
            maze_offset_y: float = 0,
            config: Dict[str, Any] = None
    ):
        """Initializes ghost at the given spawn position.

        Loads ghost images, sets up movement system, and prepares hitbox
        for collision detection.
        """
        super().__init__()
        self.config = config
        self.is_alive = True
        self.is_edible = False
        self.spawn = spawn  # [x, y]
        self.spawn_coords = (
            int((self.spawn[0] - maze_offset_x) // cell_x_size),
            int((self.spawn[1] - maze_offset_y) // cell_y_size)
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
            pygame.transform.scale(img, (size, size))
            for img in self.images[1:5]  # down, up, right, left
        ]

        self.movement = Movement(
            cell_x_size,
            cell_y_size,
            spawn,
            speed=self.base_speed,
            maze_offset_x=maze_offset_x,
            maze_offset_y=maze_offset_y
        )
        self.hitbox = self.rect.inflate(-28, -28)
        self.eye_update()

    @abstractmethod
    def update(
        self, walls: Any, player: Player, ghosts: List["Ghost"]
    ) -> None:
        """Updates ghost state and position. Must be implemented by subclasses.
        """
        pass

    def eye_update(self) -> None:
        """Updates the ghost's eye direction based on movement.

        Shows normal eyes when alive, frightened face when edible,
        or just eyes when dead and returning to spawn.
        """
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

    def death_routine(self, player: Player, ghosts: List["Ghost"]) -> None:
        """Handles ghost collision with player.

        When a ghost collides with the player (and player is not invincible),
        all ghosts are reset to their spawn positions.
        """
        if player.lives != -1:
            if self.rect.colliderect(player.rect):
                for ghost in ghosts:
                    ghost.movement.pixel_x, ghost.movement.pixel_y = \
                        ghost.spawn
                    ghost.movement.grid_x = int(
                        (ghost.movement.pixel_x - ghost.movement.maze_offset_x)
                        // ghost.movement.cell_x_size
                    )
                    ghost.movement.grid_y = int(
                        (ghost.movement.pixel_y - ghost.movement.maze_offset_y)
                        // ghost.movement.cell_y_size
                    )
                    ghost.movement.dir_x, ghost.movement.dir_y = 0, 0
                    ghost.rect.center = (int(ghost.movement.pixel_x),
                                         int(ghost.movement.pixel_y))
                player.death()

    def escape(self, walls: Any, player: Player) -> None:
        """Handles ghost behavior when edible.

        Ghost flees from player using BFS pathfinding. When close to player
        or at safe distance, takes actions to maximize survival time.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.edible_start >= self.edible_duration:
            self.is_edible = False
            self.movement.speed = self.base_speed

        if self.rect.colliderect(player.rect):
            player.score_gain(self.config["points_per_ghost"])
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

        # Randomly choose direction when far from player
        self.movement.update(walls, next_dir_x, next_dir_y)
        self.rect.center = (
            int(self.movement.pixel_x),
            int(self.movement.pixel_y)
        )

    def respawn(self, walls: Any, player: Player) -> None:
        """Handles ghost respawn after being eaten.

        Moves ghost back to spawn point using BFS. When ghost reaches spawn
        and player is far away, ghost becomes alive again.
        """
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

    def bfs(
        self, walls: Any, target: tuple[int, int]
    ) -> tuple[int, int, List]:
        """Finds shortest path to target using Breadth-First Search.

        Returns the next direction to move towards the target and the
        full path from current position to target.
        """
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
            cell_y_size: float,
            maze_offset_x: float = 0,
            maze_offset_y: float = 0,
            config: Dict[str, Any] = None
    ):
        super().__init__(
            spawn,
            color,
            images,
            cell_x_size,
            cell_y_size,
            maze_offset_x,
            maze_offset_y,
            config
        )
    """Red ghost with direct chase behavior.

    Always chases the player using BFS pathfinding. The most aggressive
    ghost type that directly pursues the player.
    """

    def update(
        self, walls: Any, player: Player, ghosts: List["Ghost"]
    ) -> None:
        """Updates red ghost AI.

        Chases player directly when alive, flees when edible,
        and respawns when dead.
        """
        self.eye_update()
        if self.frozen:
            self.movement.speed = 0
            pass
        else:
            self.movement.speed = self.base_speed
        if self.is_edible is False and self.is_alive is True:
            if not self.frozen:
                self.death_routine(player, ghosts)
            next_dir_x, next_dir_y, path = self.bfs(walls, player.grid_pos)
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
            cell_y_size: float,
            maze_offset_x: float = 0,
            maze_offset_y: float = 0,
            config: Dict[str, Any] = None
    ):
        super().__init__(
            spawn,
            color,
            images,
            cell_x_size,
            cell_y_size,
            maze_offset_x,
            maze_offset_y,
            config
        )
    """Orange ghost with random movement behavior.

    Moves randomly when not chasing, avoiding backtracking.
    Less aggressive than red ghost.
    """

    def update(
        self, walls: Any, player: Player, ghosts: List["Ghost"]
    ) -> None:
        """Updates orange ghost AI.

        Moves randomly when chasing, flees when edible,
        and respawns when dead.
        """
        self.eye_update()
        if self.frozen:
            self.movement.speed = 0
            pass
        else:
            self.movement.speed = self.base_speed
        if self.is_edible is False and self.is_alive is True:
            if not self.frozen:
                self.death_routine(player, ghosts)
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
            cell_y_size: float,
            maze_offset_x: float = 0,
            maze_offset_y: float = 0,
            config: Dict[str, Any] = None
    ):
        super().__init__(
            spawn,
            color,
            images,
            cell_x_size,
            cell_y_size,
            maze_offset_x,
            maze_offset_y,
            config
        )
    """Pink ghost with ambush behavior.

    Chases aggressively when far from player (>8 cells), but wanders
    randomly when close to the player.
    """

    def update(
        self, walls: Any, player: Player, ghosts: List["Ghost"]
    ) -> None:
        """Updates pink ghost AI.

        Chases aggressively when far, wanders when close, flees when edible,
        and respawns when dead.
        """
        if self.frozen:
            self.movement.speed = 0
            pass
        else:
            self.movement.speed = self.base_speed
        self.eye_update()
        if self.is_edible is False and self.is_alive is True:
            if not self.frozen:
                self.death_routine(player, ghosts)

            # Pinky: chase if far (>8), scatter if close
            dist_to_player = abs(self.movement.grid_x - player.grid_pos[0]) + \
                abs(self.movement.grid_y - player.grid_pos[1])

            if dist_to_player > 8:
                # Far → chase
                next_dir_x, next_dir_y, _ = self.bfs(walls, player.grid_pos)
            else:
                # Close → random wander
                next_dir_x, next_dir_y = 0, 0
                possible_dirs = []
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    if self.movement.can_move(
                        walls, self.movement.grid_x, self.movement.grid_y, dx,
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


class cyanGhost(Ghost):
    def __init__(
            self,
            spawn: tuple[float, float],
            color: str,
            images: List[Surface],
            cell_x_size: float,
            cell_y_size: float,
            maze_offset_x: float = 0,
            maze_offset_y: float = 0,
            config: Dict[str, Any] = None
    ):
        super().__init__(
            spawn,
            color,
            images,
            cell_x_size,
            cell_y_size,
            maze_offset_x,
            maze_offset_y,
            config
        )
        self.last_player_dir = (1, 0)
    """Cyan ghost with predictive ambush behavior.

    Tracks player's movement direction and aims to intercept 2 cells
    ahead of the player's current position.
    """

    def update(
        self, walls: Any, player: Player, ghosts: List["Ghost"]
    ) -> None:
        """Updates cyan ghost AI.

        Predicts player position and ambushes ahead, flees when edible,
        and respawns when dead.
        """
        self.eye_update()
        if self.frozen:
            self.movement.speed = 0
            pass
        else:
            self.movement.speed = self.base_speed
        if self.is_edible is False and self.is_alive is True:
            if not self.frozen:
                self.death_routine(player, ghosts)

            # Save player direction for ambush
            if player.movement.dir_x != 0 or player.movement.dir_y != 0:
                self.last_player_dir = (player.movement.dir_x,
                                        player.movement.dir_y)

            # Ambush: aim 2 cells ahead of player
            tx = player.grid_pos[0] + 2 * self.last_player_dir[0]
            ty = player.grid_pos[1] + 2 * self.last_player_dir[1]
            tx = max(0, min(len(walls[0]) - 1, tx))
            ty = max(0, min(len(walls) - 1, ty))
            next_dir_x, next_dir_y, _ = self.bfs(walls, (tx, ty))

            self.movement.update(walls, next_dir_x, next_dir_y)
            self.rect.center = (
                int(self.movement.pixel_x),
                int(self.movement.pixel_y)
            )
        elif self.is_edible is True and self.is_alive is True:
            self.escape(walls, player)
        else:
            self.respawn(walls, player)
