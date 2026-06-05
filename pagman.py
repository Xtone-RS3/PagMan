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


class Player:
    def __init__(self, spawn, lives=3):
        self.spawn = spawn  # [x, y]
        self.position = spawn
        self.lives = lives


class PacMan:
    def __init__(self, maze, config):
        self.maze: MazeGenerator = maze
        self.config = config
        self.ghost_spawn = [
            [0, 0],
            [config["height"]-1, config["width"]-1],
            [config["height"]-1, 0],
            [0, config["width"]-1]
        ]
        self.ghosts: List[Ghost] = []
        self.player = Player(spawn=[config["height"]/2, config["width"]/2], lives=self.config["lives"])
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


def game():
    pygame.init()
    screen = pygame.display.set_mode((720, 720))
    #  for the window size just do x*height y*width
    clock = pygame.time.Clock()
    clock.tick(30)
    black = 0, 0, 100  # 0, 0, 0 <- this is pure black
    #  ^ this is the background, we need to on top of that draw our maze using pygame.draw.line() like this vvv
    pygame.draw.lines(screen, (150, 150, 150), False, [(0, 0), (720, 720), (500, 0), (0, 500)])
    #  ^ maybe try a big for loop like on amazing
    pagman = pygame.image.load("PagMan.png")
    pagman = pygame.transform.scale(pagman, (64, 64))
    pagmanrect = pagman.get_rect()
    #  ^ this sets the hit box for the player pagman, meaning, you know when that hit box hits stuff
    velocity = [1, 1]
    while True:
        pagmanrect = pagmanrect.move(velocity)
        if pagmanrect.left < 0 or pagmanrect.right > 720:
            velocity[0] = -velocity[0]
            pagman = pygame.transform.flip(pagman, True, False)
        if pagmanrect.top < 0 or pagmanrect.bottom > 720:
            velocity[1] = -velocity[1]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        # screen update
        screen.fill(black)
        pygame.draw.lines(screen, (150, 150, 150), False, [(0, 0), (720, 720), (500, 0), (0, 500)])
        # ^ this is what re-draws, but we cannot use it, we must re-draw tge whole map
        screen.blit(pagman, pagmanrect)
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
    pagman = PacMan(maze_gen, config)
    game()
