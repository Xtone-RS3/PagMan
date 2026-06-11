from mazegenerator import MazeGenerator
import sys
import json
import random
from typing import List
import pygame

# # Create a simple 20x20 maze
# maze_gen = MazeGenerator(seed=10)

# # Get the maze structure
# maze_grid = maze_gen.maze
# shortest_path = maze_gen.shortest_path

# print(f"Maze dimensions: {len(maze_grid[0])}x{len(maze_grid)}")
# print(f"Entry: {maze_gen.maze_entry}, Exit: {maze_gen.maze_exit}")
# print(f"Shortest path length: {len(shortest_path)}")


class Ghost:
    def __init__(self, spawn, color, images):
        self.is_alive = True
        self.is_edible = False
        self.spawn = spawn  # [x, y]
        self.color = color
        self.personality = ""
        self.position = spawn
        self.images: list[pygame.image.Surface] = images
        # Red (Blinky): Relentlessly chases Pac-Man directly.
        # Pink (Pinky): Tries to position herself ahead of Pac-Man to trap him.
        # Cyan/Light Blue (Inky): Has an unpredictable, flanking personality.
        # Orange (Clyde): Wanders aimlessly or moves randomly.
        # Dark blue: run away


class Player(pygame.sprite.Sprite):
    def __init__(self, spawn, lives=3):
        super().__init__()
        self.spawn = spawn  # PacMan class
        self.position = spawn
        self.lives = lives
        self.orig_image = pygame.image.load("PagMan.png")
        self.orig_image = pygame.transform.scale(self.orig_image, (32, 32))
        self.angle = 0
        self.image = self.orig_image
        self.rect = self.orig_image.get_rect()
        self.rect.center = spawn
        self.vx = 0
        self.vy = 0
        self.next_vx = 0
        self.next_vy = 0
        self.speed = 5  # PacMan class

    def rotate_image(self, angle):
        center = self.rect.center
        self.angle = angle
        self.image = pygame.transform.rotate(
            self.orig_image, self.angle
        )
        self.rect = self.image.get_rect(center=center)

    # vvvvvv MIGHT WANT TO MOVE ALL THIS MOVEMENT SHIT TO THE GAME'S CLASS SO GHOSTS HAVE ACCESS vvvvvvv
    def overlaps_wall(self, walls):
        inflated = self.rect.inflate(12, 13)  # this is THE crux, what this does is extend the collision so the walls get detected "sooner" (made up numbers)
        for (x1, y1), (x2, y2) in walls:
            if inflated.clipline(x1, y1, x2, y2):
                return True
        return False

    def move_axis(self, dx, dy, walls) -> bool:  # checks movements per step, not per speed, VERY IMPORTANT
        self.rect.x += dx
        self.rect.y += dy
        if self.overlaps_wall(walls):  # STEP BACK and find the LAST valid position
            self.rect.x -= dx
            self.rect.y -= dy
            steps = max(abs(dx), abs(dy))
            step_x = dx / steps if steps else 0  # binary search for the furthest we can go
            step_y = dy / steps if steps else 0  # less math-y than what i like, but simpler to explain
            for _ in range(steps):
                self.rect.x += int(step_x)
                self.rect.y += int(step_y)
                if self.overlaps_wall(walls):
                    self.rect.x -= int(step_x)
                    self.rect.y -= int(step_y)
                    break
            return False  # hit a wall
        return True  # moved freely

    def update(self, walls):
        keys = pygame.key.get_pressed()
        desired_vx, desired_vy = self.next_vx, self.next_vy

        if keys[pygame.K_LEFT]:
            desired_vx, desired_vy = -self.speed, 0
            self.rotate_image(180)
        elif keys[pygame.K_RIGHT]:
            desired_vx, desired_vy = self.speed, 0
            self.rotate_image(0)
        elif keys[pygame.K_UP]:
            desired_vx, desired_vy = 0, -self.speed
            self.rotate_image(90)
        elif keys[pygame.K_DOWN]:
            desired_vx, desired_vy = 0, self.speed
            self.rotate_image(270)

        if (desired_vx, desired_vy) != (self.vx, self.vy):  # same as before but smarter lol
            self.next_vx, self.next_vy = desired_vx, desired_vy

        if (self.next_vx, self.next_vy) != (self.vx, self.vy):
            # Speculatively move to test
            orig_x, orig_y = self.rect.x, self.rect.y
            moved_freely = self.move_axis(self.next_vx, self.next_vy, walls)
            self.rect.x, self.rect.y = orig_x, orig_y  # restore
            if moved_freely:
                self.vx, self.vy = self.next_vx, self.next_vy

        # Actually move
        moved_freely = self.move_axis(self.vx, self.vy, walls)
        if not moved_freely:
            self.vx, self.vy = 0, 0


class PacMan:
    def __init__(self, maze, config, spawn_x, spawn_y, image_list):
        self.maze: MazeGenerator = maze
        self.config = config
        self.ghost_spawn = [
            [0, 0],
            [config["height"]-1, config["width"]-1],
            [config["height"]-1, 0],
            [0, config["width"]-1]
        ]
        self.ghosts: List[Ghost] = []
        self.player = Player(spawn=(spawn_x, spawn_y), lives=self.config["lives"])
        self.pacgum = config["pacgum"]
        self.points_per_pacgum = config["points_per_pacgum"]
        self.points_per_super_pacgum = config["points_per_super_pacgum"]
        self.points_per_ghost = config["points_per_ghost"]
        self.level_max_time = config["level_max_time"]
        self.image_list = image_list
        print(self.image_list)
        self.ghost_gen()

    def ghost_gen(self):
        color_list = ["red", "pink", "cyan", "orange"]
        for coords in self.ghost_spawn:
            color = random.choice(color_list)
            color_list.remove(color)
            self.ghosts.append(
                Ghost(
                    spawn=coords,
                    color=color,
                    images=[
                        self.image_list[color],
                        self.image_list["down_eyes"],
                        self.image_list["up_eyes"],
                        self.image_list["right_eyes"],
                        self.image_list["left_eyes"],
                        self.image_list["dead"]
                    ]
                )
            )  # why always same color wtf?
        print(self.ghosts[0].color, self.ghosts[1].color, self.ghosts[2].color, self.ghosts[3].color)


def game(maze: MazeGenerator, config: dict):
    pygame.init()
    screen_x = 720
    cell_x_size = screen_x/maze._width
    print(cell_x_size)
    screen_y = 720
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
    print(walls)
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
    pagman = PacMan(maze_gen, config, spawn_x, spawn_y, image_list)
    group: pygame.sprite.GroupSingle = pygame.sprite.GroupSingle()
    player = pagman.player
    group.add(player)
    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.fill(black)
        screen.blit(maze_surface, (0, 0))
        group.update(wall_collision)   # <- move all sprites
        group.draw(screen)
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
