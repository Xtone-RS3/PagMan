from typing import Any


class Movement():
    """Handles movement logic for sprites in the maze.

    Manages grid-based positioning, direction changes, wall collision,
    and smooth pixel movement between cells.
    """

    def __init__(
            self,
            cell_x_size: float,
            cell_y_size: float,
            spawn: tuple[float, float],
            speed: int,
            maze_offset_x: float,
            maze_offset_y: float
    ):
        """Initializes movement system.

        Args:
            cell_x_size: Width of each cell in pixels.
            cell_y_size: Height of each cell in pixels.
            spawn: Starting position in pixels.
            speed: Movement speed in pixels per update.
            maze_offset_x: X offset of maze in the window.
            maze_offset_y: Y offset of maze in the window.
        """
        self.maze_offset_x = maze_offset_x
        self.maze_offset_y = maze_offset_y
        self.cell_x_size = cell_x_size
        self.cell_y_size = cell_y_size
        self.pixel_x, self.pixel_y = spawn

        self.dir_x = 0
        self.dir_y = 0
        self.next_dir_x = 0
        self.next_dir_y = 0
        self.speed = speed
        self.grid_x = int((self.pixel_x - maze_offset_x) // cell_x_size)
        self.grid_y = int((self.pixel_y - maze_offset_y) // cell_y_size)

    def can_move(
            self, walls: Any, col: Any, row: Any, dx: Any, dy: Any
    ) -> bool:
        """Checks if movement in a direction is possible.

        Args:
            walls: 2D array representing maze walls.
            col: Current column position.
            row: Current row position.
            dx: X direction (-1, 0, or 1).
            dy: Y direction (-1, 0, or 1).

        Returns:
            True if movement is allowed, False if blocked by wall.
        """
        if row < 0 or row >= len(walls) or col < 0 or col >= len(walls[0]):
            return False
        cell = walls[row][col]
        # W -> cell[0], S -> cell[1], E -> cell[2], N -> cell[3]
        if dx == -1 and cell[0] == "1":
            return False  # West
        if dy == 1 and cell[1] == "1":
            return False  # South
        if dx == 1 and cell[2] == "1":
            return False  # East
        if dy == -1 and cell[3] == "1":
            return False  # North
        return True

    def update(
            self, walls: Any, next_dir_x: int, next_dir_y: int
    ) -> tuple[int, int]:
        """Updates position based on current and queued direction.

        Snaps to cell center when arriving, queues direction changes,
        and moves pixel position based on current direction.

        Args:
            walls: 2D array representing maze walls.
            next_dir_x: Queued X direction.
            next_dir_y: Queued Y direction.

        Returns:
            Tuple of (dir_x, dir_y) representing actual movement direction.
        """
        self.next_dir_x, self.next_dir_y = next_dir_x, next_dir_y
        # Calculate the center pixel of the current grid cell
        target_pixel_x = (
            self.grid_x * self.cell_x_size + self.cell_x_size / 2 +
            self.maze_offset_x
        )
        target_pixel_y = (
            self.grid_y * self.cell_y_size + self.cell_y_size / 2 +
            self.maze_offset_y
        )

        # Check if we are at the center of the current cell
        if (abs(self.pixel_x - target_pixel_x) <= self.speed and
                abs(self.pixel_y - target_pixel_y) <= self.speed):
            # Snap to center
            self.pixel_x = target_pixel_x
            self.pixel_y = target_pixel_y

            # Can we move in the queued direction?
            if (self.next_dir_x != 0 or self.next_dir_y != 0) and \
                    self.can_move(
                        walls, self.grid_x, self.grid_y,
                        self.next_dir_x, self.next_dir_y
                    ):
                self.dir_x, self.dir_y = self.next_dir_x, self.next_dir_y

            # If not, can we keep moving in current direction?
            if not self.can_move(
                walls, self.grid_x, self.grid_y, self.dir_x, self.dir_y
            ):
                self.dir_x, self.dir_y = 0, 0

            # Update grid position based on final direction
            if self.dir_x != 0 or self.dir_y != 0:
                self.grid_x += self.dir_x
                self.grid_y += self.dir_y
        self.pixel_x += self.dir_x * self.speed
        self.pixel_y += self.dir_y * self.speed
        return (self.dir_x, self.dir_y)
