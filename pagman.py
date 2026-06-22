from mazegenerator import MazeGenerator
import sys
import json
import random
from typing import Any, Dict, List
import pygame
from ghosts import redGhost, orangeGhost, pinkGhost, cyanGhost, Ghost
from player import Player
from pygame.surface import Surface


class Pacgum(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float):
        super().__init__()
        self.image = pygame.image.load("gum1.png")
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        self.hitbox = self.rect.inflate(-28, -28)
        # TODO divide cell size by a factor, 48 / x = 28


class superPacgum(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float):
        super().__init__()
        self.image = pygame.image.load("gum3.png")
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        self.hitbox = self.rect.inflate(-10, -10)  # TODO


class PacMan:
    def __init__(
            self,
            maze: MazeGenerator,
            config: Dict[Any, Any],
            spawn_x: float,
            spawn_y: float,
            image_list: Dict[Any, Any],
            cell_x_size: float,
            cell_y_size: float
    ):
        self.maze: MazeGenerator = maze
        self.level_cap = config["level_cap"]
        self.config = config
        self.ghost_spawn = [
            (
                0 * cell_x_size + cell_x_size / 2,
                0 * cell_y_size + cell_y_size / 2
            ),
            (
                (config["width"]-1) * cell_x_size + cell_x_size / 2,
                (config["height"]-1) * cell_y_size + cell_y_size / 2
            ),
            (
                0 * cell_x_size + cell_x_size / 2,
                (config["height"]-1) * cell_y_size + cell_y_size / 2
            ),
            (
                (config["width"]-1) * cell_x_size + cell_x_size / 2,
                0 * cell_y_size + cell_y_size / 2
            )
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
        self.ghost_gen(cell_x_size, cell_y_size)

    def ghost_gen(self, cell_x_size: float, cell_y_size: float) -> None:
        color_class: list[type[Ghost]] = [
            redGhost, orangeGhost, pinkGhost, cyanGhost
        ]
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


def draw_ui(
        screen: Surface,
        score: int,
        lives: int,
        time_left: int,
        screen_x: int,
        screen_y: int,
        ghost_speed: int
) -> Dict[str, pygame.Rect]:
    font = pygame.font.SysFont("Serif", 40, True)
    cheat_font = pygame.font.SysFont("Serif", 20, True)
    pygame.draw.rect(screen, (0, 0, 0), (screen_x, 0, screen_x+250, screen_x))

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    lives_text = font.render("Lives:", True, (255, 255, 255))

    life_icon = pygame.image.load("PagMan.png")
    if lives <= 3 and lives > 0:
        for i in range(lives):
            screen.blit(life_icon, (screen_x + 109 + i * 40, 50))
    elif lives == -1:
        lives_text = font.render("Lives: ∞", True, (255, 255, 255))
    else:
        lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))

    minutes = time_left // 60
    seconds = time_left % 60
    timer_text = font.render(
        f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255)
    )

    freeze_btn = pygame.Rect(screen_x + 20, 130, 200, 40)
    pygame.draw.rect(screen, (50, 50, 50), freeze_btn)
    freeze_text = font.render("Ghost Freeze", True, (255, 255, 255))
    screen.blit(freeze_text, (screen_x + 25, 135))

    invenci_btn = pygame.Rect(screen_x + 20, 190, 200, 40)
    pygame.draw.rect(screen, (50, 50, 50), invenci_btn)
    invenci_text = font.render("Invencibility", True, (255, 255, 255))
    screen.blit(invenci_text, (screen_x + 25, 195))

    ghost_speed_text = cheat_font.render("Ghost Speed", True, (255, 255, 255))
    screen.blit(ghost_speed_text, (screen_x + 25, 255))

    ghost_speed_minus = pygame.Rect(screen_x + 30+105, 255, 20, 20)
    pygame.draw.rect(screen, (50, 50, 50), ghost_speed_minus)
    ghost_speed_minus_text = cheat_font.render("-", True, (255, 255, 255))
    screen.blit(ghost_speed_minus_text, (screen_x + 36+105, 255))

    # ghost_speed_stat = pygame.Rect(screen_x + 30+105, 255, 20, 20)
    # pygame.draw.rect(screen, (50, 50, 50), ghost_speed_stat)
    ghost_speed_stat_text = cheat_font.render(
        f"{ghost_speed}", True, (255, 255, 255)
    )
    screen.blit(ghost_speed_stat_text, (screen_x + 65+105, 255))

    ghost_speed_plus = pygame.Rect(screen_x + 90+105, 255, 20, 20)
    pygame.draw.rect(screen, (50, 50, 50), ghost_speed_plus)
    ghost_speed_plus_text = cheat_font.render("+", True, (255, 255, 255))
    screen.blit(ghost_speed_plus_text, (screen_x + 93+105, 255))

    screen.blit(score_text, (screen_x + 20, 10))
    screen.blit(lives_text, (screen_x + 20, 50))
    screen.blit(timer_text, (screen_x + 20, 90))
    screen.blit(freeze_text, (screen_x + 25, 135))

    return {
        "ghost_freeze": freeze_btn,
        "invencibility": invenci_btn,
        "ghost_speed_plus": ghost_speed_plus,
        "ghost_speed_minus": ghost_speed_minus
    }


def game(maze: MazeGenerator, config: dict) -> None:
    pygame.init()
    screen_x = 720
    cell_x_size = screen_x/maze._width
    screen_y = 720
    cell_y_size = screen_y/maze._height
    cell_x_size, cell_y_size = \
        min(cell_x_size, cell_y_size), min(cell_x_size, cell_y_size)
    display_info = pygame.display.Info()
    window_x = 0
    if display_info.current_w > screen_x:
        window_x = screen_x + 250
    screen = pygame.display.set_mode((window_x, screen_y))
    pygame.display.set_caption("Pac-Man")
    maze_surface: pygame.Surface = pygame.Surface(
        (screen_x, screen_y), pygame.SRCALPHA
    )
    maze_surface.fill((0, 0, 0, 0))
    #  for the window size just do x*height y*width
    clock = pygame.time.Clock()
    clock.tick(30)
    black = 10, 10, 26
    #  West, South, East, North
    walls: List[List[str]] = []
    for line in maze.maze:
        wall_line: List[str] = []
        for raw_cell in line:
            cell_walls = bin(raw_cell)[2:]
            while len(cell_walls) != 4:
                cell_walls = "0"+cell_walls
            wall_line.append(cell_walls)
        walls.append(wall_line)
    wall_color = (68, 136, 221)
    wall_width = 3
    wall_collision = []
    curr_y = 0
    while curr_y < len(walls):
        curr_x = 0
        while curr_x < len(walls[curr_y]):
            cell: str = walls[curr_y][curr_x]
            px = cell_x_size * curr_x
            py = cell_y_size * curr_y

            if maze.maze[curr_y][curr_x] == 15:
                pygame.draw.rect(
                    maze_surface,
                    (26, 58, 106),
                    (int(px), int(py), int(cell_x_size), int(cell_y_size))
                )
                pygame.draw.rect(
                    maze_surface,
                    (68, 136, 221),
                    (
                        int(px) + 3,
                        int(py) + 3,
                        int(cell_x_size) - 6,
                        int(cell_y_size) - 6
                    ),
                    2
                )
                curr_x += 1
                continue
            if cell[3] == "1":  # North
                start_x = 0+cell_x_size*curr_x
                start_y = 0+cell_y_size*curr_y
                end_x = cell_x_size+cell_x_size*curr_x
                end_y = 0+cell_y_size*curr_y
                wall_collision.append(((start_x, start_y), (end_x, end_y)))
                pygame.draw.line(
                    maze_surface,
                    wall_color,
                    (start_x, start_y),
                    (end_x, end_y),
                    wall_width
                )
            if cell[2] == "1":  # East
                start_x = cell_x_size+cell_x_size*curr_x
                start_y = cell_y_size+cell_y_size*curr_y
                end_x = cell_x_size+cell_x_size*curr_x
                end_y = 0+cell_y_size*curr_y
                wall_collision.append(((start_x, start_y), (end_x, end_y)))
                pygame.draw.line(
                    maze_surface,
                    wall_color,
                    (start_x, start_y),
                    (end_x, end_y),
                    wall_width
                )
            if cell[1] == "1":  # South
                start_x = cell_x_size+cell_x_size*curr_x
                start_y = cell_y_size+cell_y_size*curr_y
                end_x = 0+cell_x_size*curr_x
                end_y = cell_y_size+cell_y_size*curr_y
                wall_collision.append(((start_x, start_y), (end_x, end_y)))
                pygame.draw.line(
                    maze_surface,
                    wall_color,
                    (start_x, start_y),
                    (end_x, end_y),
                    wall_width
                )
            if cell[0] == "1":  # West
                start_x = 0+cell_x_size*curr_x
                start_y = 0+cell_y_size*curr_y
                end_x = 0+cell_x_size*curr_x
                end_y = cell_y_size+cell_y_size*curr_y
                wall_collision.append(((start_x, start_y), (end_x, end_y)))
                pygame.draw.line(
                    maze_surface,
                    wall_color,
                    (start_x, start_y),
                    (end_x, end_y),
                    wall_width
                )
            curr_x += 1
        curr_y += 1

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
    # split this into LEVEL load
    pagman = PacMan(
        maze_gen,
        config,
        spawn_x,
        spawn_y,
        image_list,
        cell_x_size,
        cell_y_size
    )
    # pygame.display.set_caption(f"Pac-Man level: {level}")  # level is one of\
    # the args passed on game()
    pacgum_group: pygame.sprite.Group = pygame.sprite.Group()
    super_pacgum_group: pygame.sprite.Group = pygame.sprite.Group()
    spwans = [(0, 0), (0, maze._height-1),
              (maze._width-1, 0), (maze._width-1, maze._height-1),
              (pagman.player.grid_x, pagman.player.grid_y)]
    l_pacgum: List[tuple[float, float]] = []
    for row in range(maze._height):
        for col in range(maze._width):
            gum_spawn = maze.maze[row][col]
            if gum_spawn != 15 and (col, row) not in spwans:
                cx = col * cell_x_size + cell_x_size / 2
                cy = row * cell_y_size + cell_y_size / 2
                l_pacgum.append((cx, cy))
    if len(l_pacgum) < config["pacgum"]:
        print(
            f"Warning: Requested {config['pacgum']} pacgums,\
but only {len(l_pacgum)} valid spawn locations available."
        )
    for i in range(config["pacgum"]):
        if not l_pacgum:
            break
        spawn = random.choice(l_pacgum)
        l_pacgum.remove(spawn)
        pacgum_group.add(Pacgum(spawn[0], spawn[1]))
    super_spawns = []
    super_spawns.append(
        (cell_x_size / 2, cell_y_size * mid_row + cell_y_size / 2)
    )
    super_spawns.append(
        (cell_x_size * mid_col + cell_x_size / 2, cell_y_size / 2)
    )
    super_spawns.append(
        (cell_x_size * mid_col + cell_x_size / 2,
         cell_y_size * (maze._height - 1) + cell_y_size / 2)
    )
    super_spawns.append(
        (cell_x_size * (maze._width - 1) + cell_x_size / 2,
         cell_y_size * mid_row + cell_y_size / 2)
    )
    for spawn in super_spawns:
        if spawn in spwans:
            continue
        super_pacgum_group.add(superPacgum(*spawn))

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
    hold_lives = 0
    while True:
        clock.tick(30)
        elapsed = (pygame.time.get_ticks() - 0) // 1000
        time_left = max(0, config["level_max_time"] - elapsed)
        screen.fill(black)
        buttons = draw_ui(
            screen,
            pagman.player.score,
            pagman.player.lives,
            time_left,
            screen_x,
            screen_y,
            pagman.ghosts[0].movement.speed
        )
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons["ghost_freeze"].collidepoint(
                    event.pos
                ) and pagman.ghosts[0].frozen is False:
                    for ghost in pagman.ghosts:
                        ghost.frozen = True
                elif buttons["ghost_freeze"].collidepoint(
                    event.pos
                ) and pagman.ghosts[0].frozen is True:
                    for ghost in pagman.ghosts:
                        ghost.frozen = False
                if buttons["invencibility"].collidepoint(
                    event.pos
                ) and pagman.player.lives != -1:
                    hold_lives = pagman.player.lives
                    pagman.player.lives = -1
                elif buttons["invencibility"].collidepoint(
                    event.pos
                ) and pagman.player.lives == -1:
                    if hold_lives == 0:
                        hold_lives = 3
                    pagman.player.lives = hold_lives
                if buttons["ghost_speed_plus"].collidepoint(event.pos):
                    for ghost in pagman.ghosts:
                        ghost.base_speed += 1
                        if ghost.base_speed <= 1:
                            ghost.base_speed = 1
                if buttons["ghost_speed_minus"].collidepoint(event.pos):
                    for ghost in pagman.ghosts:
                        ghost.base_speed -= 1
                        if ghost.base_speed <= 1:
                            ghost.base_speed = 1
            if event.type == pygame.QUIT:
                sys.exit()

        # extra_screen.fill(black)

        screen.blit(maze_surface, (0, 0))
        # extra_screen.blit()
        pacgum_group.draw(screen)
        super_pacgum_group.draw(screen)
        eaten = pygame.sprite.spritecollide(
            pagman.player,
            pacgum_group,
            True,
            collided=lambda a, b: a.rect.colliderect(b.hitbox)
        )
        if pygame.sprite.spritecollide(
            pagman.player,
            super_pacgum_group,
            True, collided=lambda a, b: a.rect.colliderect(b.hitbox)
        ):
            pagman.player.score_gain(config["points_per_super_pacgum"])
            for ghost in pagman.ghosts:
                ghost.is_edible = True
                ghost.edible_start = current_time
                ghost.movement.speed = ghost.base_speed // 2
        if eaten:
            pagman.pacgum -= len(eaten)
            pagman.player.score_gain(config["points_per_pacgum"])
            if pagman.pacgum <= 0:
                print("You win!")
                sys.exit()
        pacman_group.update(walls, current_time)
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
    maze_gen = MazeGenerator(
        seed=config["seed"], size=(config["width"], config["height"])
    )
    # hex_lists = [[hex(x) for x in inner] for inner in maze_gen.maze]
    # hex_lists2 = [[x.replace("0x", "") for x in hex] for hex in hex_lists]
    # print(hex_lists2)
    # print(config)
    game(maze_gen, config)
