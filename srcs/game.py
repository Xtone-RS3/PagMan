import pygame
from mazegenerator import MazeGenerator
from typing import Dict, List, Any, Tuple
from pacman import PacMan
import random
from gums import Pacgum, superPacgum
from ui import draw_ui, leaderboard, main_menu
import sys
import json
from pygame import Surface


def game(
    level: int,
    config: dict,
    score: int,
    screen: Surface, screen_x: int,
    screen_y: int,
    cell_x_size: int,
    cell_y_size: int,
    player_died: int,
    maze_offset_x: int,
    maze_offset_y: int
) -> tuple[bool, Dict[str, int]]:
    try:
        maze = MazeGenerator(
            seed=config["seed"] + level,
            size=(config["width"],
                  config["height"])
        )
    except RecursionError:
        print("Parsing error detected, defaulting to size: 15x15")
        maze = MazeGenerator(
            seed=config["seed"] + level, size=(15, 15)
        )
        config["width"], config["height"] = 15, 15
        cell_x_size = int(screen_x / 15)
        cell_y_size = int(screen_y / 15)
        cell_x_size, cell_y_size = \
            min(cell_x_size, cell_y_size), min(cell_x_size, cell_y_size)
    pygame.display.set_caption("Pac-Man")
    maze_surface: pygame.Surface = pygame.Surface(
        (screen_x, screen_y), pygame.SRCALPHA
    )
    maze_surface.fill((0, 0, 0, 0))
    clock = pygame.time.Clock()
    clock.tick(30)
    black = 10, 10, 26

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
            px = cell_x_size * curr_x + maze_offset_x
            py = cell_y_size * curr_y + maze_offset_y

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
                start_x = 0+cell_x_size*curr_x + maze_offset_x
                start_y = 0+cell_y_size*curr_y + maze_offset_y
                end_x = cell_x_size+cell_x_size*curr_x + maze_offset_x
                end_y = 0+cell_y_size*curr_y + maze_offset_y
                wall_collision.append(((start_x, start_y), (end_x, end_y)))
                pygame.draw.line(
                    maze_surface,
                    wall_color,
                    (start_x, start_y),
                    (end_x, end_y),
                    wall_width
                )
            if cell[2] == "1":  # East
                start_x = cell_x_size+cell_x_size*curr_x + maze_offset_x
                start_y = cell_y_size+cell_y_size*curr_y + maze_offset_y
                end_x = cell_x_size+cell_x_size*curr_x + maze_offset_x
                end_y = 0+cell_y_size*curr_y + maze_offset_y
                wall_collision.append(((start_x, start_y), (end_x, end_y)))
                pygame.draw.line(
                    maze_surface,
                    wall_color,
                    (start_x, start_y),
                    (end_x, end_y),
                    wall_width
                )
            if cell[1] == "1":  # South
                start_x = cell_x_size+cell_x_size*curr_x + maze_offset_x
                start_y = cell_y_size+cell_y_size*curr_y + maze_offset_y
                end_x = 0+cell_x_size*curr_x + maze_offset_x
                end_y = cell_y_size+cell_y_size*curr_y + maze_offset_y
                wall_collision.append(((start_x, start_y), (end_x, end_y)))
                pygame.draw.line(
                    maze_surface,
                    wall_color,
                    (start_x, start_y),
                    (end_x, end_y),
                    wall_width
                )
            if cell[0] == "1":  # West
                start_x = 0+cell_x_size*curr_x + maze_offset_x
                start_y = 0+cell_y_size*curr_y + maze_offset_y
                end_x = 0+cell_x_size*curr_x + maze_offset_x
                end_y = cell_y_size+cell_y_size*curr_y + maze_offset_y
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
        "cyan": "ghosts/cyan_ghost.png",
        "red": "ghosts/red_ghost.png",
        "orange": "ghosts/orange_ghost.png",
        "pink": "ghosts/pink_ghost.png",
        "right_eyes": "ghosts/right_eyes.png",
        "left_eyes": "ghosts/left_eyes.png",
        "up_eyes": "ghosts/up_eyes.png",
        "down_eyes": "ghosts/down_eyes.png",
        "dead": "ghosts/dead.png"
    }
    for key, file in folder.items():
        image_list[key] = pygame.image.load(file)

    pagman = PacMan(
        maze,
        config,
        spawn_x + maze_offset_x,
        spawn_y + maze_offset_y,
        image_list,
        cell_x_size,
        cell_y_size,
        score,
        player_died,
        maze_offset_x,
        maze_offset_y
    )
    pygame.display.set_caption(f"Pac-Man level: {level}")
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
                cx = col * cell_x_size + cell_x_size / 2 + maze_offset_x
                cy = row * cell_y_size + cell_y_size / 2 + maze_offset_y
                l_pacgum.append((cx, cy))
    if len(l_pacgum) < config["pacgum"]:
        print(
            f"Warning: Requested {config['pacgum']} pacgums,\
but only {len(l_pacgum)} valid spawn locations available."
        )
    size = min(cell_x_size * (2/3), cell_y_size * (2/3))
    for i in range(config["pacgum"]):
        if not l_pacgum:
            break
        spawn = random.choice(l_pacgum)
        l_pacgum.remove(spawn)
        pacgum_group.add(Pacgum(spawn[0], spawn[1], size))
    super_spawns = []
    super_spawns.append(
        (cell_x_size / 2 + maze_offset_x, cell_y_size * mid_row + cell_y_size
            / 2 + maze_offset_y)
    )
    super_spawns.append(
        (cell_x_size * mid_col + cell_x_size / 2 + maze_offset_x, cell_y_size
            / 2 + maze_offset_y)
    )
    super_spawns.append(
        (cell_x_size * mid_col + cell_x_size / 2 + maze_offset_x,
         cell_y_size * (maze._height - 1) + cell_y_size / 2 + maze_offset_y)
    )
    super_spawns.append(
        (cell_x_size * (maze._width - 1) + cell_x_size / 2 + maze_offset_x,
         cell_y_size * mid_row + cell_y_size / 2 + maze_offset_y)
    )
    for spawn in super_spawns:
        if spawn in spwans:
            continue
        super_pacgum_group.add(superPacgum(spawn[0], spawn[1], size))

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
    time_left = config["level_max_time"]

    buttons = draw_ui(
        screen,
        pagman.player.score,
        pagman.player.lives,
        time_left,
        screen_x,
        screen_y,
        min(
            pagman.ghosts[0].base_speed,
            pagman.ghosts[1].base_speed,
            pagman.ghosts[2].base_speed,
            pagman.ghosts[3].base_speed
        ),
        pagman.player,
        level,
        ghosts_frozen=pagman.ghosts[0].frozen,
        invincible=pagman.player.lives == -1
    )

    def draw_text_box(
        screen: Surface,
        text: str,
        x: int,
        y: int,
        font: pygame.font.Font,
        text_color: tuple[int, int, int] = (255, 255, 0),
        box_color: tuple[int, int, int] = (15, 15, 35),
        border_color: tuple[int, int, int] = (68, 136, 221),
        padding: int = 12,
        border_width: int = 2
    ) -> None:
        text_surf = font.render(text, True, text_color)
        box_rect = pygame.Rect(
            x - text_surf.get_width() // 2 - padding,
            y - text_surf.get_height() // 2 - padding,
            text_surf.get_width() + padding * 2,
            text_surf.get_height() + padding * 2
        )
        pygame.draw.rect(screen, box_color, box_rect, border_radius=6)
        pygame.draw.rect(screen, border_color, box_rect, border_width,
                         border_radius=6)
        screen.blit(text_surf, (
            x - text_surf.get_width() // 2,
            y - text_surf.get_height() // 2
        ))

    def wait_for_keypress(
            message: str = "Press any key to start"
    ) -> Tuple[bool, Dict]:
        waiting = True
        while waiting:
            screen.fill(black)
            screen.blit(maze_surface, (0, 0))
            pacgum_group.draw(screen)
            super_pacgum_group.draw(screen)
            pacman_group.draw(screen)
            ghost0_group.draw(screen)
            ghost1_group.draw(screen)
            ghost2_group.draw(screen)
            ghost3_group.draw(screen)
            draw_ui(
                screen,
                pagman.player.score,
                pagman.player.lives,
                time_left,
                screen_x,
                screen_y,
                min(
                    pagman.ghosts[0].base_speed,
                    pagman.ghosts[1].base_speed,
                    pagman.ghosts[2].base_speed,
                    pagman.ghosts[3].base_speed
                ),
                pagman.player,
                level,
                ghosts_frozen=pagman.ghosts[0].frozen,
                invincible=pagman.player.lives == -1
            )
            font = pygame.font.SysFont("Serif", 40, True)
            draw_text_box(
                screen, f"Level: {level}", screen_x // 2, screen_y // 2 - 60,
                font, (255, 255, 0)
            )
            draw_text_box(
                screen, message, screen_x // 2, screen_y // 2,
                font, (255, 255, 0)
            )
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running_stats = {"lives": pagman.player.lives,
                                     "score": pagman.player.score}
                    return (False, running_stats)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    waiting = False
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
                    if buttons["invincibility"].collidepoint(
                        event.pos
                    ) and pagman.player.lives != -1:
                        hold_lives = pagman.player.lives
                        pagman.player.lives = -1
                    elif buttons["invincibility"].collidepoint(
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
                    if buttons["life_cheat_plus"].collidepoint(event.pos):
                        if pagman.player.lives >= 1:
                            pagman.player.lives += 1
                    if buttons["life_cheat_minus"].collidepoint(event.pos):
                        if pagman.player.lives >= 2:
                            pagman.player.lives -= 1
                    if buttons["self_speed_plus"].collidepoint(event.pos):
                        pagman.player.movement.speed += 1
                    if buttons["self_speed_minus"].collidepoint(event.pos):
                        if pagman.player.movement.speed > 1:
                            pagman.player.movement.speed -= 1
                    if buttons["level_skip_plus"].collidepoint(event.pos):
                        # pagman.player.movement.speed += 1
                        running_stats = {"lives": pagman.player.lives,
                                         "score": pagman.player.score}
                        return (True, running_stats)
        return (True, {})  # TODO is this correct?

    success, stats = wait_for_keypress()
    # if not success:
    #     return False, stats
    current_time = 0
    pagman.player.next_tick = pygame.time.get_ticks() + pagman.player.interval
    paused = False
    start_ticks = pygame.time.get_ticks()
    paused_timer = 0
    paused_timer_value = 0
    time_left = config["level_max_time"]
    death_freeze_elapsed = 0
    while True:
        clock.tick(30)
        if not paused:
            elapsed = (pygame.time.get_ticks() - start_ticks -
                       death_freeze_elapsed -
                       paused_timer_value) // 1000
            time_left = max(0, config["level_max_time"] - elapsed)
        screen.fill(black)
        buttons = draw_ui(
            screen,
            pagman.player.score,
            pagman.player.lives,
            time_left,
            screen_x,
            screen_y,
            min(
                pagman.ghosts[0].base_speed,
                pagman.ghosts[1].base_speed,
                pagman.ghosts[2].base_speed,
                pagman.ghosts[3].base_speed
            ),
            pagman.player,
            level,
            ghosts_frozen=pagman.ghosts[0].frozen,
            invincible=pagman.player.lives == -1
        )
        for event in pygame.event.get():
            # vvv COPY into a func vvv
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
                if buttons["invincibility"].collidepoint(
                    event.pos
                ) and pagman.player.lives != -1:
                    hold_lives = pagman.player.lives
                    pagman.player.lives = -1
                elif buttons["invincibility"].collidepoint(
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
                if buttons["life_cheat_plus"].collidepoint(event.pos):
                    if pagman.player.lives >= 1:
                        pagman.player.lives += 1
                if buttons["life_cheat_minus"].collidepoint(event.pos):
                    if pagman.player.lives >= 2:
                        pagman.player.lives -= 1
                if buttons["self_speed_plus"].collidepoint(event.pos):
                    pagman.player.movement.speed += 1
                if buttons["self_speed_minus"].collidepoint(event.pos):
                    if pagman.player.movement.speed > 1:
                        pagman.player.movement.speed -= 1
                if buttons["level_skip_plus"].collidepoint(event.pos):
                    # pagman.player.movement.speed += 1
                    running_stats = {"lives": pagman.player.lives,
                                     "score": pagman.player.score}
                    return (True, running_stats)
            # ^^^ COPY into a func ^^^
            if event.type == pygame.QUIT:
                running_stats = {"lives": pagman.player.lives,
                                 "score": pagman.player.score}
                return (False, running_stats)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if paused:
                        paused_timer_value += paused_timer
                    paused = not paused
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    if paused:
                        pygame.quit()
                        main_menu(config)
            if event.type == player_died:
                running_stats = {"lives": pagman.player.lives,
                                 "score": pagman.player.score}
                return (False, running_stats)

        screen.blit(maze_surface, (0, 0))
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
                running_stats = {"lives": pagman.player.lives,
                                 "score": pagman.player.score}
                return (True, running_stats)
        if not paused:
            current_time = pygame.time.get_ticks() - paused_timer
            pacman_group.update(walls, current_time)
            pacman_group.draw(screen)
            ghost0_group.update(walls, pagman.player, pagman.ghosts)
            ghost0_group.draw(screen)
            ghost1_group.update(walls, pagman.player, pagman.ghosts)
            ghost1_group.draw(screen)
            ghost2_group.update(walls, pagman.player, pagman.ghosts)
            ghost2_group.draw(screen)
            ghost3_group.update(walls, pagman.player, pagman.ghosts)
            ghost3_group.draw(screen)
        else:
            paused_timer = pygame.time.get_ticks() - current_time
            font = pygame.font.SysFont("Serif", 40, True)
            pacman_group.draw(screen)
            ghost0_group.draw(screen)
            ghost1_group.draw(screen)
            ghost2_group.draw(screen)
            ghost3_group.draw(screen)
            draw_text_box(
                screen, "PAUSED", screen_x // 2, screen_y // 2 - 60,
                font, (255, 255, 0)
            )
            draw_text_box(
                screen, "Press P to resume",
                screen_x // 2, screen_y // 2,
                font, (255, 255, 0)
            )
            draw_text_box(
                screen, "Press 'space' to Main Menu",
                screen_x // 2, screen_y // 2 + 60,
                font, (255, 255, 0)
            )
        if time_left <= 0:
            running_stats = {"lives": pagman.player.lives,
                             "score": pagman.player.score}
            return (False, running_stats)

        # Respawn do jogador e ecrã de espera caso tenha acabado de morrer
        if pagman.player.just_died:
            pagman.player.just_died = False
            # Drenar apenas eventos player_died da queue para evitar que
            # sejam consumidos antes de chegarmos ao wait_for_keypress
            death_time = pygame.time.get_ticks()
            while True:
                event = pygame.event.poll()
                if event.type == pygame.NOEVENT or event.type == player_died:
                    break
                if event.type != player_died:
                    pygame.event.post(event)
            success, stats = wait_for_keypress("You died! Press any" +
                                               "key to respawn")
            if not success:
                return (False, stats)
            death_freeze_elapsed += (pygame.time.get_ticks() - death_time)
            pagman.player.next_tick = pygame.time.get_ticks() + \
                pagman.player.interval

        pygame.display.flip()


PLAYER_DIED = pygame.event.custom_type()


def game_start(config: Dict[Any, Any]) -> None:
    score = 0
    pygame.init()
    screen_x = 720
    cell_x_size = screen_x/config["width"]
    screen_y = 720
    cell_y_size = screen_y/config["height"]
    cell_x_size, cell_y_size = \
        min(cell_x_size, cell_y_size), min(cell_x_size, cell_y_size)
    maze_offset_x = int((screen_x - cell_x_size * config["width"]) // 2)
    maze_offset_y = int((screen_y - cell_y_size * config["height"]) // 2)
    window_x = 0
    if pygame.display.Info().current_w > screen_x:
        window_x = screen_x + 250
    screen = pygame.display.set_mode((window_x, screen_y))
    base_lives = config["lives"]
    for level in range(config["level_cap"]):
        completion = game(level, config, score, screen, screen_x, screen_y,
                          cell_x_size, cell_y_size, PLAYER_DIED, maze_offset_x,
                          maze_offset_y)
        if completion[0] is True:
            config["lives"] = completion[1]["lives"]
            score = completion[1]["score"]
        else:
            config["lives"] = base_lives
            score = completion[1]["score"]
            leaderboard(config, score)
    leaderboard(config, score)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "config.json"
    lines = []
    config_default = {
        "highscore_filename": "HS.json",
        "level_cap": 10,
        "width": 15,
        "height": 15,
        "lives": 3,
        "pacgum": 42,
        "points_per_pacgum": 10,
        "points_per_super_pacgum": 50,
        "points_per_ghost": 200,
        "seed": 42,
        "level_max_time": 1000
    }
    try:
        with open(config_file) as file:
            for line in file:
                if not line.lstrip().startswith("#"):
                    lines.append(line)
        config: Dict = json.loads("".join(lines))
        if not isinstance(config["highscore_filename"], str):
            raise Exception("Parsing error")
        config_hold = config.copy()
        config_hold.pop("highscore_filename")
        for config_key, config_value in config_hold.items():
            if not isinstance(config_value, int):
                raise Exception("Parsing error")
        if not set(list(config_default.keys())).issubset(list(config.keys())):
            raise Exception("Parsing error")
    except Exception as e:
        print(e)
        config = config_default
    main_menu(config)
