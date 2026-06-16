from mazegenerator import MazeGenerator
import sys
import json
import random
from typing import List
import pygame
from ghosts import *
# from ghosts import redGhost, Ghost
# import ghosts

# # Create a simple 20x20 maze
# maze_gen = MazeGenerator(seed=10)

# # Get the maze structure
# maze_grid = maze_gen.maze
# shortest_path = maze_gen.shortest_path

# print(f"Maze dimensions: {len(maze_grid[0])}x{len(maze_grid)}")
# print(f"Entry: {maze_gen.maze_entry}, Exit: {maze_gen.maze_exit}")
# print(f"Shortest path length: {len(shortest_path)}")


class Pacgum(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # use gum1.png
        self.image = pygame.image.load("gum1.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Movement():
    def __init__(self, cell_x_size, cell_y_size, spawn, speed):
        self.cell_x_size = cell_x_size  # needed?
        self.cell_y_size = cell_y_size
        self.pixel_x, self.pixel_y = spawn

        self.grid_x = int(self.pixel_x // cell_x_size)
        self.grid_y = int(self.pixel_y // cell_y_size)

        self.dir_x = 0
        self.dir_y = 0
        self.next_dir_x = 0
        self.next_dir_y = 0
        self.speed = speed

    def can_move(self, walls, col, row, dx, dy):
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

    def update(self, walls, next_dir_x, next_dir_y) -> tuple[int, int]:
        self.next_dir_x, self.next_dir_y = next_dir_x, next_dir_y
        # Calculate the center pixel of the current grid cell
        target_pixel_x = self.grid_x * self.cell_x_size + self.cell_x_size / 2
        target_pixel_y = self.grid_y * self.cell_y_size + self.cell_y_size / 2

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


class Player(pygame.sprite.Sprite):
    def __init__(self, spawn, cell_x_size, cell_y_size, lives=3):
        super().__init__()
        self.spawn = (spawn)  # PacMan class
        self.cell_x_size = cell_x_size
        self.cell_y_size = cell_y_size
        self.lives = lives
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
        self.frame: int = 0
        self.current = self.orig_image[self.frame]
        self.last_angle = 0
        self.image = self.orig_image[self.frame]
        self.rect = self.orig_image[0].get_rect()
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
            speed=5
        )
        self.interval = 200
        self.next_tick = pygame.time.get_ticks() + self.interval

    def update_image(self):  # copy this exact logic for ghost eyes
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
    def grid_pos(self):
        return (
            int(self.movement.pixel_x // self.cell_x_size),
            int(self.movement.pixel_y // self.cell_y_size)
        )

    def update(self, walls, current_time):
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

    def death(self):
        sys.exit()
        # raise ValueError("Game Over")


class PacMan:
    def __init__(self, maze, config, spawn_x, spawn_y, image_list, cell_x_size,
                 cell_y_size):
        self.maze: MazeGenerator = maze
        self.config = config
        self.ghost_spawn = [
            [
                0 * cell_x_size + cell_x_size / 2,
                0 * cell_y_size + cell_y_size / 2
            ],
            [
                (config["height"]-1) * cell_x_size + cell_x_size / 2,
                (config["width"]-1) * cell_y_size + cell_y_size / 2
            ],
            [
                0 * cell_x_size + cell_x_size / 2,
                (config["width"]-1) * cell_y_size + cell_y_size / 2
            ],
            [
                (config["height"]-1) * cell_x_size + cell_x_size / 2,
                0 * cell_y_size + cell_y_size / 2
            ]
        ]
        self.ghosts: List[Ghost] = []
        self.player = Player(spawn=(spawn_x, spawn_y), cell_x_size=cell_x_size,
                             cell_y_size=cell_y_size,
                             lives=self.config["lives"])
        self.pacgum = config["pacgum"]
        self.points_per_pacgum = config["points_per_pacgum"]
        self.points_per_super_pacgum = config["points_per_super_pacgum"]
        self.points_per_ghost = config["points_per_ghost"]
        self.level_max_time = config["level_max_time"]
        self.image_list = image_list
        # print(self.image_list)
        self.ghost_gen(cell_x_size, cell_y_size)

    def ghost_gen(self, cell_x_size, cell_y_size):
        color_class = [redGhost, orangeGhost, pinkGhost, cyanGhost]
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
                    cell_y_size=cell_y_size
                )
            )


def game(maze: MazeGenerator, config: dict):
    pygame.init()
    screen_x = config["width"] * 48
    cell_x_size = screen_x/maze._width
    screen_y = config["width"] * 48
    cell_y_size = screen_y/maze._height
    screen = pygame.display.set_mode((screen_x, screen_y))
    maze_surface = pygame.Surface((screen_x, screen_y), pygame.SRCALPHA)
    maze_surface.fill((0, 0, 0, 0))
    #  for the window size just do x*height y*width
    clock = pygame.time.Clock()
    clock.tick(30)
    black = 10, 10, 26  # 0, 0, 0 <- this is pure black
    #  ^ this is the background, we need to on top of that draw our maze using pygame.draw.line() like this vvv
    # print(maze.maze)
    #  West, South, East, North
    walls: List[List[str]] = []
    for line in maze.maze:
        wall_line = []
        for cell in line:
            cell_walls = bin(cell)[2:]
            while len(cell_walls) != 4:
                cell_walls = "0"+cell_walls
            wall_line.append(cell_walls)
        walls.append(wall_line)
    # print(walls)
    wall_color = (68, 136, 221)
    wall_width = 3
    wall_collision = []
    # sprites = pygame.sprite.Group()
    # objects = pygame.sprite.Group()
    curr_y = 0
    for line in walls:
        curr_x = 0
        for cell in line:
            px = cell_x_size * curr_x
            py = cell_y_size * curr_y

            if maze.maze[curr_y][curr_x] == 15:
                pygame.draw.rect(maze_surface, (26, 58, 106), (px, py, cell_x_size, cell_y_size))
                pygame.draw.rect(maze_surface, (68, 136, 221), (px + 3, py + 3, cell_x_size - 6, cell_y_size - 6), 2)
                curr_x += 1
                continue
            if cell[3] == "1":  # North
                start_x = 0+cell_x_size*curr_x
                start_y = 0+cell_y_size*curr_y
                end_x = cell_x_size+cell_x_size*curr_x
                end_y = 0+cell_y_size*curr_y
                wall_collision.append(((start_x, start_y), (end_x, end_y)))
                pygame.draw.line(maze_surface, wall_color, (start_x, start_y), (end_x, end_y), wall_width)
            if cell[2] == "1":  # East
                start_x = cell_x_size+cell_x_size*curr_x
                start_y = cell_y_size+cell_y_size*curr_y
                end_x = cell_x_size+cell_x_size*curr_x
                end_y = 0+cell_y_size*curr_y
                wall_collision.append(((start_x, start_y), (end_x, end_y)))
                pygame.draw.line(maze_surface, wall_color, (start_x, start_y), (end_x, end_y), wall_width)
            if cell[1] == "1":  # South
                start_x = cell_x_size+cell_x_size*curr_x
                start_y = cell_y_size+cell_y_size*curr_y
                end_x = 0+cell_x_size*curr_x
                end_y = cell_y_size+cell_y_size*curr_y
                wall_collision.append(((start_x, start_y), (end_x, end_y)))
                pygame.draw.line(maze_surface, wall_color, (start_x, start_y), (end_x, end_y), wall_width)
            if cell[0] == "1":  # West
                start_x = 0+cell_x_size*curr_x
                start_y = 0+cell_y_size*curr_y
                end_x = 0+cell_x_size*curr_x
                end_y = cell_y_size+cell_y_size*curr_y
                wall_collision.append(((start_x, start_y), (end_x, end_y)))
                pygame.draw.line(maze_surface, wall_color, (start_x, start_y), (end_x, end_y), wall_width)
            curr_x += 1
        curr_y += 1

    # pygame.draw.lines(screen, wall_color, False, [(0, 0), (screen_x, screen_y), (500, 0), (0, 500)])
    #  ^ maybe try a big for loop like on amazing
    mid_col = (maze._width - 1) // 2
    mid_row = (maze._height - 1) // 2
    spawn_x = mid_col * cell_x_size + cell_x_size / 2
    spawn_y = mid_row * cell_y_size + cell_y_size / 2
    image_list = {}
    folder = {
        "cyan": "pacmen/cyan_ghost.png",
        "red": "pacmen/red_ghost.png",
        "orange": "pacmen/orange_ghost.png",
        "pink": "pacmen/pink_ghost.png",
        "right_eyes": "pacmen/right_eyes.png",
        "left_eyes": "pacmen/left_eyes.png",
        "up_eyes": "pacmen/up_eyes.png",
        "down_eyes": "pacmen/down_eyes.png",
        "dead": "pacmen/dead.png"
    }
    for key, file in folder.items():
        image_list[key] = pygame.image.load(file)
    pagman = PacMan(maze_gen, config, spawn_x, spawn_y, image_list, cell_x_size, cell_y_size)
    pacgum_group = pygame.sprite.Group()
    spwans = [(0, 0), (0, maze._height-1),
              (maze._width-1, 0), (maze._width-1, maze._height-1),
              (pagman.player.grid_x, pagman.player.grid_y)]
    l_pacgum = []
    for row in range(maze._height):
        for col in range(maze._width):
            gum_spwan = maze.maze[row][col]
            # cant spwan on walls and where the ghosts spawn and where the player spawns 
            if gum_spwan != 15 and (col, row) not in spwans:
                cx = col * cell_x_size + cell_x_size / 2
                cy = row * cell_y_size + cell_y_size / 2
                l_pacgum.append((cx, cy))
    for i in range(config["pacgum"]):
        if not l_pacgum:
            break
        spawn = random.choice(l_pacgum)
        l_pacgum.remove(spawn)
        pacgum_group.add(Pacgum(*spawn))
    pacman_group: pygame.sprite.Group = pygame.sprite.Group()
    ghost0_group: pygame.sprite.Group = pygame.sprite.Group()
    ghost0_group.add(pagman.ghosts[0])
    ghost1_group: pygame.sprite.Group = pygame.sprite.Group()
    ghost1_group.add(pagman.ghosts[1])
    ghost2_group: pygame.sprite.Group = pygame.sprite.Group()
    ghost2_group.add(pagman.ghosts[2])
    ghost3_group: pygame.sprite.Group = pygame.sprite.Group()
    ghost3_group.add(pagman.ghosts[3])
    pacman_group.add(pagman.player)
    while True:
        clock.tick(30)
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.fill(black)
        screen.blit(maze_surface, (0, 0))
        pacgum_group.draw(screen)
        eaten = pygame.sprite.spritecollide(pagman.player, pacgum_group, True)
        if eaten:
            pagman.pacgum -= len(eaten)
            if pagman.pacgum <= 0:
                print("You win!")
                sys.exit()
        pacman_group.update(walls, current_time)   # <- move all sprites using grid logically
        pacman_group.draw(screen)
        ghost0_group.update(walls, pagman.player)
        ghost0_group.draw(screen)
        ghost1_group.update(walls, pagman.player)
        ghost1_group.draw(screen)
        ghost2_group.update(walls, pagman.player)
        ghost2_group.draw(screen)
        ghost3_group.update(walls, pagman.player)
        ghost3_group.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "config.json"
    lines = []
    with open(config_file) as file:
        for line in file:
            if not line.lstrip().startswith("#"):
                lines.append(line)
    config = json.loads("".join(lines))
    maze_gen = MazeGenerator(seed=config["seed"], size=(config["height"], config["width"]))
    # hex_lists = [[hex(x) for x in inner] for inner in maze_gen.maze]
    # hex_lists2 = [[x.replace("0x", "") for x in hex] for hex in hex_lists]
    # print(hex_lists2)

    # print(config)
    game(maze_gen, config)
