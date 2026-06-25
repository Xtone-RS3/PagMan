import pygame
from player import Player
from pygame import Surface
from typing import Dict, Any, Optional
import sys
import json


def draw_ui(
        screen: Surface,
        score: int,
        lives: int,
        time_left: int,
        screen_x: int,
        screen_y: int,
        ghost_speed: int,
        player: Player,
        level: int
) -> Dict[str, pygame.Rect]:
    font = pygame.font.SysFont("Serif", 40, True)
    cheat_font = pygame.font.SysFont("Serif", 20, True)
    pygame.draw.rect(screen, (0, 0, 0), (screen_x, 0, screen_x+250, screen_x))

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    lives_text = font.render("Lives:", True, (255, 255, 255))

    life_icon = pygame.image.load("PagMan.png")
    if lives <= 3 and lives > 0:
        for i in range(lives):
            screen.blit(life_icon, (screen_x + 129 + i * 40, 55))
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

    invinci_btn = pygame.Rect(screen_x + 20, 190, 200, 40)
    pygame.draw.rect(screen, (50, 50, 50), invinci_btn)
    invinci_text = font.render("invincibility", True, (255, 255, 255))
    screen.blit(invinci_text, (screen_x + 25, 195))

    ghost_speed_text = cheat_font.render("Ghost Speed", True, (255, 255, 255))
    screen.blit(ghost_speed_text, (screen_x + 25, 255))

    ghost_speed_minus = pygame.Rect(screen_x + 30+105, 255, 20, 20)
    pygame.draw.rect(screen, (50, 50, 50), ghost_speed_minus)
    ghost_speed_minus_text = cheat_font.render("-", True, (255, 255, 255))
    screen.blit(ghost_speed_minus_text, (screen_x + 36+105, 255))

    ghost_speed_stat_text = cheat_font.render(
        f"{ghost_speed}", True, (255, 255, 255)
    )
    screen.blit(ghost_speed_stat_text, (screen_x + 65+105, 255))

    ghost_speed_plus = pygame.Rect(screen_x + 90+105, 255, 20, 20)
    pygame.draw.rect(screen, (50, 50, 50), ghost_speed_plus)
    ghost_speed_plus_text = cheat_font.render("+", True, (255, 255, 255))
    screen.blit(ghost_speed_plus_text, (screen_x + 93+105, 255))

    life_cheat_text = cheat_font.render("Life cheat", True, (255, 255, 255))
    screen.blit(life_cheat_text, (screen_x + 25, 280))

    life_cheat_minus = pygame.Rect(screen_x + 30+105, 280, 20, 20)
    pygame.draw.rect(screen, (50, 50, 50), life_cheat_minus)
    life_cheat_minus_text = cheat_font.render("-", True, (255, 255, 255))
    screen.blit(life_cheat_minus_text, (screen_x + 36+105, 280))

    life_cheat_stat_text = cheat_font.render(
        f"{lives}", True, (255, 255, 255)
    )
    screen.blit(life_cheat_stat_text, (screen_x + 65+105, 280))

    life_cheat_plus = pygame.Rect(screen_x + 90+105, 280, 20, 20)
    pygame.draw.rect(screen, (50, 50, 50), life_cheat_plus)
    life_cheat_plus_text = cheat_font.render("+", True, (255, 255, 255))
    screen.blit(life_cheat_plus_text, (screen_x + 93+105, 280))

    # ###
    self_speed_text = cheat_font.render("Player speed", True, (255, 255, 255))
    screen.blit(self_speed_text, (screen_x + 25, 305))

    self_speed_minus = pygame.Rect(screen_x + 30+105, 305, 20, 20)
    pygame.draw.rect(screen, (50, 50, 50), self_speed_minus)
    self_speed_minus_text = cheat_font.render("-", True, (255, 255, 255))
    screen.blit(self_speed_minus_text, (screen_x + 36+105, 305))

    self_speed_stat_text = cheat_font.render(
        f"{player.movement.speed}", True, (255, 255, 255)
    )
    screen.blit(self_speed_stat_text, (screen_x + 65+105, 305))

    self_speed_plus = pygame.Rect(screen_x + 90+105, 305, 20, 20)
    pygame.draw.rect(screen, (50, 50, 50), self_speed_plus)
    self_speed_plus_text = cheat_font.render("+", True, (255, 255, 255))
    screen.blit(self_speed_plus_text, (screen_x + 93+105, 305))

    # ###
    level_skip_text = cheat_font.render("Level skip", True, (255, 255, 255))
    screen.blit(level_skip_text, (screen_x + 25, 330))

    level_skip_stat_text = cheat_font.render(
        f"{level}", True, (255, 255, 255)
    )
    screen.blit(level_skip_stat_text, (screen_x + 65+105, 330))

    level_skip_plus = pygame.Rect(screen_x + 90+105, 330, 20, 20)
    pygame.draw.rect(screen, (50, 50, 50), level_skip_plus)
    level_skip_plus_text = cheat_font.render("+", True, (255, 255, 255))
    screen.blit(level_skip_plus_text, (screen_x + 93+105, 330))
    # ###

    screen.blit(score_text, (screen_x + 20, 10))
    screen.blit(lives_text, (screen_x + 20, 50))
    screen.blit(timer_text, (screen_x + 20, 90))
    screen.blit(freeze_text, (screen_x + 25, 135))

    return {
        "ghost_freeze": freeze_btn,
        "invincibility": invinci_btn,
        "ghost_speed_plus": ghost_speed_plus,
        "ghost_speed_minus": ghost_speed_minus,
        "life_cheat_plus": life_cheat_plus,
        "life_cheat_minus": life_cheat_minus,
        "self_speed_plus": self_speed_plus,
        "self_speed_minus": self_speed_minus,
        "level_skip_plus": level_skip_plus
    }


def leaderboard(
    config: Dict[Any, Any], score: int = 0, screen: Optional[Surface] = None
) -> None:
    pygame.init()
    HS_file = config["highscore_filename"]
    if screen is None:
        screen_x = 720
        screen_y = 720
        screen = pygame.display.set_mode((screen_x, screen_y))
    else:
        screen.fill((0, 0, 0))
        screen_x = screen.get_width()
        screen_y = screen.get_height()
    font = pygame.font.SysFont("Serif", 40, True)
    font_title = pygame.font.SysFont("Serif", 100, True)
    name = ""
    finish_input = False
    pygame.key.start_text_input()
    valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNO\
PQRSTUVWXYZ0123456789 "
    if score != 0:
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.TEXTINPUT and len(name) < 10:
                    if event.text in valid_chars:
                        name += event.text
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    if event.key == pygame.K_RETURN:
                        finish_input = True
            screen.fill((0, 0, 0))

            # Title
            pagman_title = font_title.render("PAG-MAN", True, (255, 255, 0))
            screen.blit(pagman_title, (screen_x//2 -
                        pagman_title.get_width()//2, 50))

            # Score
            score_line = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_line, (screen_x//2 -
                        score_line.get_width()//2, 220))

            # Input label
            type_here = font.render("Write your name:", True, (255, 255, 255))
            screen.blit(type_here, (screen_x//2 -
                        type_here.get_width()//2, 310))

            # Larger input rect to fit 10 uppercase chars
            input_rect = pygame.Rect(screen_x//2 - 165, 355, 330, 55)
            pygame.draw.rect(screen, (255, 255, 255), input_rect, 2)

            # Render name centered in rect
            text_surface = font.render(name[:10], True, (255, 255, 255))
            screen.blit(text_surface, (screen_x//2 -
                        text_surface.get_width()//2, 362))

            # Max chars hint
            hint = pygame.font.SysFont("Serif", 20, True).render(
                "max 10 characters", True, (150, 150, 150))
            screen.blit(hint, (screen_x//2 - hint.get_width()//2, 418))

            if finish_input is True:
                pygame.key.stop_text_input()
                screen.fill((0, 0, 0))
                break
            pygame.display.flip()
            clock.tick(30)
        with open(HS_file) as file:
            highscores = json.load(file)
        highscores[name] = score
        with open(HS_file, "w") as file:
            json.dump(highscores, file, indent=4)
    lines = []
    with open(HS_file) as file:
        for line in file:
            if not line.lstrip().startswith("#"):
                lines.append(line)
    leaderboard = json.loads("".join(lines))

    sorted_leaderboard = sorted(
        leaderboard.items(), key=lambda x: x[1], reverse=True)

    num = 0
    screen.fill((0, 0, 0))
    pagman_title = font_title.render("PAG-MAN", True, (255, 255, 0))
    screen.blit(pagman_title, (screen_x//2 - pagman_title.get_width()//2, 50))
    press_space = font.render("Press SPACE for Main Menu",
                              True, (255, 255, 255))
    screen.blit(press_space, (screen_x//2 - press_space.get_width()//2, 175))

    # Header row
    rank_header = font.render("Rank", True, (255, 255, 0))
    name_header = font.render("Name", True, (255, 255, 0))
    score_header = font.render("Score", True, (255, 255, 0))
    screen.blit(rank_header, (screen_x//5 - rank_header.get_width()//2, 225))
    screen.blit(name_header, (screen_x//2 - name_header.get_width()//2, 225))
    screen.blit(score_header, (4*screen_x//5 -
                score_header.get_width()//2, 225))
    pygame.draw.line(screen,
                     (255, 255, 0), (screen_x//5, 265),
                     (4*screen_x//5, 265), 2)

    for player in sorted_leaderboard[0:10]:
        rank = font.render(f"#{num+1}", True, (255, 255, 255))
        player_name = font.render(f"{player[0][:10]}", True, (255, 255, 255))
        player_score = font.render(f"{player[1]}", True, (255, 255, 255))
        y = 280 + num * 42
        screen.blit(rank, (screen_x//5 - rank.get_width()//2, y))
        screen.blit(player_name, (screen_x//2 - player_name.get_width()//2, y))
        screen.blit(player_score, (4*screen_x//5 -
                    player_score.get_width()//2, y))
        num += 1
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main_menu(config, screen)
                if event.key == pygame.K_ESCAPE:
                    sys.exit()


def instructions(config: Dict[Any, Any], screen: Surface) -> None:
    pygame.init()
    font = pygame.font.SysFont("Serif", 40, True)
    font_title = pygame.font.SysFont("Serif", 100, True)
    font_small = pygame.font.SysFont("Serif", 28, True)
    while True:
        screen.fill((0, 0, 0))
        pagman_title = font_title.render("PAG-MAN", True, (255, 255, 0))
        screen.blit(pagman_title, (screen.get_width()//2 -
                    pagman_title.get_width()//2, 50))
        press_space = font.render("Press SPACE for Main Menu",
                                  True, (255, 255, 255))
        screen.blit(press_space, (screen.get_width()//2 -
                    press_space.get_width()//2, 175))

        # Separator line
        pygame.draw.line(screen, (255, 255, 0),
                         (screen.get_width()//4, 220),
                         (3*screen.get_width()//4, 220), 2)

        instructions = [
            ("Arrow Keys", "Movement"),
            ("P", "Pause / Resume"),
            ("Collect Pac-Gums", "+10 pts"),
            ("Collect Super Pac-Gums", "+50 pts + eat ghosts"),
            ("Ghost Freeze / Invincibility", "Cheat buttons"),
        ]
        for i, (key, desc) in enumerate(instructions):
            key_text = font_small.render(key, True, (255, 255, 0))
            desc_text = font_small.render(desc, True, (255, 255, 255))
            y = 260 + i * 60
            screen.blit(key_text, (screen.get_width()//4 -
                        key_text.get_width()//2, y))
            screen.blit(desc_text, (screen.get_width()//2 + 20, y))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main_menu(config, screen)
                if event.key == pygame.K_ESCAPE:
                    sys.exit()


def main_menu(
    config: Dict[Any, Any], screen: Optional[Surface] = None
) -> None:
    from game import game_start
    if screen is None:
        pygame.init()
        screen_x = 720
        screen_y = 720
        screen = pygame.display.set_mode((screen_x, screen_y))
    else:
        screen_x = pygame.display.Info().current_w
        screen_y = pygame.display.Info().current_h

    font = pygame.font.SysFont("Serif", 40, True)
    font_title = pygame.font.SysFont("Serif", 100, True)
    while True:
        screen.fill((0, 0, 0))
        pagman_title = font_title.render("PAG-MAN", True, (255, 255, 0))
        screen.blit(pagman_title, (screen_x//2 -
                    pagman_title.get_width()//2, 50))
        ###
        game_start_rect = pygame.Rect(250, 210, 210, 50)
        pygame.draw.rect(screen, (255, 255, 255), game_start_rect, 2)
        game_start_text = font.render("Start Game", True, (255, 255, 255))
        screen.blit(game_start_text, (255, 215))
        # ###
        hs_rect = pygame.Rect(250, 310, 210, 50)
        pygame.draw.rect(screen, (255, 255, 255), hs_rect, 2)
        hs_text = font.render("HighScores", True, (255, 255, 255))
        screen.blit(hs_text, (255, 315))
        # ###
        instructions_rect = pygame.Rect(250, 410, 210, 50)
        pygame.draw.rect(screen, (255, 255, 255), instructions_rect, 2)
        instructions_text = font.render("Instructions", True, (255, 255, 255))
        screen.blit(instructions_text, (255, 415))
        # ###
        exit_rect = pygame.Rect(250, 510, 210, 50)
        pygame.draw.rect(screen, (255, 255, 255), exit_rect, 2)
        exit_text = font.render("Exit", True, (255, 255, 255))
        screen.blit(exit_text, (255, 515))
        # ###
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_start_rect.collidepoint(event.pos):
                    pygame.quit()
                    game_start(config)
                if hs_rect.collidepoint(event.pos):
                    leaderboard(config, screen=screen)
                if instructions_rect.collidepoint(event.pos):
                    instructions(config, screen)
                if exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    pygame.quit()
                    game_start(config)
