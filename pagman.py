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
    def __init__(self, spawn, color):
        self.is_alive = True
        self.is_edible = False
        self.spawn = spawn  # [x, y]
        self.color = color
        self.personality = ""
        self.position = spawn
        # Red (Blinky): Relentlessly chases Pac-Man directly.
        # Pink (Pinky): Tries to position herself ahead of Pac-Man to trap him.
        # Cyan/Light Blue (Inky): Has an unpredictable, flanking personality.
        # Orange (Clyde): Wanders aimlessly or moves randomly.
        # Dark blue: run away


class Player(pygame.sprite.Sprite):
    def __init__(self, spawn, lives=3):
        super().__init__()
        self.spawn = spawn  # [x, y]
        self.position = spawn
        self.lives = lives
        self.image = pygame.image.load("PagMan.png")
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.center = spawn
        self.vx = 0
        self.vy = 0
        self.speed = 3
        print(spawn)

    def update(self, walls):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
            self.vy = 0
        elif keys[pygame.K_RIGHT]:
            self.vx = self.speed
            self.vy = 0
        elif keys[pygame.K_UP]:
            self.vx = 0
            self.vy = -self.speed
        elif keys[pygame.K_DOWN]:
            self.vx = 0
            self.vy = self.speed
        can_move = True
        next_rect = self.rect.move(self.vx, self.vy)  # posição futura
        for wall in walls:
            if next_rect.clipline(*wall):
                can_move = False
                break
        if can_move:
            self.rect.x += self.vx
            self.rect.y += self.vy


class PacMan:
    def __init__(self, maze, config, spawn_x, spawn_y):
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
        self.ghost_gen()

    def ghost_gen(self):
        color_list = ["red", "pink", "cyan", "orange"]
        for coords in self.ghost_spawn:
            color = random.choice(color_list)
            color_list.remove(color)
            self.ghosts.append(Ghost(spawn=coords, color=color))  # why always same color wtf?
        print(self.ghosts[0].color, self.ghosts[1].color, self.ghosts[2].color, self.ghosts[3].color)




def game(maze: MazeGenerator, config: dict):
    pygame.init()
    screen_x = 720
    cell_x_size = screen_x/maze._width
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
    pagman = PacMan(maze_gen, config, spawn_x, spawn_y)
    group = pygame.sprite.GroupSingle()
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
