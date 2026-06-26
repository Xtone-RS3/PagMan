import pygame
from player import Player
from pygame.surface import Surface
from typing import Dict, Any, Optional
import sys
import json


class UIState:
    def __init__(self) -> None:
        self.freeze_animation = 0
        self.invinci_animation = 0
        self.animation_speed = 0.1


_ui_state = UIState()


def draw_ui(
        screen: Surface,
        score: int,
        lives: int,
        time_left: int,
        screen_x: int,
        screen_y: int,
        ghost_speed: int,
        player: Player,
        level: int,
        life_icon: Surface,
        ghosts_frozen: bool = False,
        invincible: bool = False
) -> Dict[str, pygame.Rect]:
    font_large = pygame.font.SysFont("Serif", 40, True)
    font_medium = pygame.font.SysFont("Serif", 24, True)
    font_small = pygame.font.SysFont("Serif", 18, True)

    ui_bg_color = (15, 15, 35)
    ui_border_color = (68, 136, 221)
    pygame.draw.rect(
        screen, ui_bg_color, (screen_x, 0, screen_x + 250, screen_y)
    )
    pygame.draw.line(
        screen, ui_border_color, (screen_x, 0), (screen_x, screen_y), 3
    )

    # Score section
    score_text = font_large.render(f"Score: {score}", True, (255, 255, 0))
    screen.blit(score_text, (screen_x + 15, 15))
    pygame.draw.line(
        screen, ui_border_color, (screen_x + 10, 60), (screen_x + 240, 60), 2
    )

    # Lives section
    lives_label = font_medium.render("Lives:", True, (100, 200, 255))
    screen.blit(lives_label, (screen_x + 15, 75))

    if lives <= 4 and lives > 0:
        for i in range(lives):
            screen.blit(life_icon, (screen_x + 95 + i * 35, 70))
    elif lives == -1:
        lives_display = font_medium.render("∞", True, (100, 255, 100))
        screen.blit(lives_display, (screen_x + 95, 75))
    else:
        lives_display = font_medium.render(f"{lives}", True, (255, 150, 150))
        screen.blit(lives_display, (screen_x + 95, 75))

    # Timer section
    minutes = time_left // 60
    seconds = time_left % 60
    timer_color = (255, 255, 255) if time_left > 30 else (255, 100, 100)
    timer_text = font_medium.render(
        f"Time: {minutes:02}:{seconds:02}", True, timer_color
    )
    screen.blit(timer_text, (screen_x + 15, 115))
    pygame.draw.line(
        screen, ui_border_color, (screen_x + 10, 155), (screen_x + 240, 155), 2
    )

    # Update animations
    if ghosts_frozen:
        _ui_state.freeze_animation = int(min(
            1.0, _ui_state.freeze_animation + _ui_state.animation_speed
        ))
    else:
        _ui_state.freeze_animation = int(max(
            0.0, _ui_state.freeze_animation - _ui_state.animation_speed
        ))

    if invincible:
        _ui_state.invinci_animation = int(min(
            1.0, _ui_state.invinci_animation + _ui_state.animation_speed
        ))
    else:
        _ui_state.invinci_animation = int(max(
            0.0, _ui_state.invinci_animation - _ui_state.animation_speed
        ))

    # Ghost Freeze button with animation
    freeze_btn = pygame.Rect(screen_x + 15, 170, 220, 50)
    freeze_glow = int(50 * _ui_state.freeze_animation)
    freeze_base_color = (50, 100, 50) if ghosts_frozen else (80, 40, 40)
    freeze_highlight = (
        100 + freeze_glow, 150 + freeze_glow, 100 + freeze_glow
    ) if ghosts_frozen else (
        180 + freeze_glow, 100 + freeze_glow, 100 + freeze_glow
    )

    pygame.draw.rect(screen, freeze_base_color, freeze_btn)
    pygame.draw.rect(screen, freeze_highlight, freeze_btn, 3)

    freeze_text = font_medium.render("Ghost Freeze", True, (255, 255, 255))
    screen.blit(freeze_text, (screen_x + 25, 180))

    freeze_status = font_small.render(
        "ON" if ghosts_frozen else "OFF",
        True, (100, 255, 100) if ghosts_frozen else (255, 100, 100)
    )
    screen.blit(freeze_status, (screen_x + 190, 185))

    # Invincibility button with animation
    invinci_btn = pygame.Rect(screen_x + 15, 235, 220, 50)
    invinci_glow = int(50 * _ui_state.invinci_animation)
    invinci_base_color = (50, 100, 50) if invincible else (80, 40, 40)
    invinci_highlight = (
        100 + invinci_glow, 150 + invinci_glow, 100 + invinci_glow
    ) if invincible else (
        180 + invinci_glow, 100 + invinci_glow, 100 + invinci_glow
    )

    pygame.draw.rect(screen, invinci_base_color, invinci_btn)
    pygame.draw.rect(screen, invinci_highlight, invinci_btn, 3)

    invinci_text = font_medium.render("Invincibility", True, (255, 255, 255))
    screen.blit(invinci_text, (screen_x + 25, 245))

    invinci_status = font_small.render(
        "ON" if invincible else "OFF",
        True, (100, 255, 100) if invincible else (255, 100, 100)
    )
    screen.blit(invinci_status, (screen_x + 190, 250))

    pygame.draw.line(
        screen, ui_border_color, (screen_x + 10, 300), (screen_x + 240, 300), 2
    )

    # screen size math
    left = screen_x + 180
    right = screen_x + 215

    # Ghost Speed control
    ghost_speed_text = font_medium.render("Ghost Speed", True, (100, 200, 255))
    screen.blit(ghost_speed_text, (screen_x + 15, 320))

    ghost_speed_minus = pygame.Rect(screen_x + 155, 320, 25, 25)
    pygame.draw.rect(screen, (70, 70, 100), ghost_speed_minus)
    pygame.draw.rect(screen, (150, 150, 200), ghost_speed_minus, 2)
    ghost_speed_minus_text = font_small.render("-", True, (255, 255, 255))
    screen.blit(ghost_speed_minus_text, (screen_x + 165, 322))

    ghost_speed_stat_text = font_small.render(
        f"{ghost_speed}", True, (255, 200, 100)
    )
    screen.blit(
        ghost_speed_stat_text, (
            (left + right) // 2 - ghost_speed_stat_text.get_width() // 2, 323
        )
    )

    ghost_speed_plus = pygame.Rect(screen_x + 215, 320, 25, 25)
    pygame.draw.rect(screen, (70, 70, 100), ghost_speed_plus)
    pygame.draw.rect(screen, (150, 150, 200), ghost_speed_plus, 2)
    ghost_speed_plus_text = font_small.render("+", True, (255, 255, 255))
    screen.blit(ghost_speed_plus_text, (screen_x + 222, 322))

    # Life cheat control
    life_cheat_text = font_medium.render("Life Cheat", True, (100, 200, 255))
    screen.blit(life_cheat_text, (screen_x + 15, 360))

    life_cheat_minus = pygame.Rect(screen_x + 155, 360, 25, 25)
    pygame.draw.rect(screen, (70, 70, 100), life_cheat_minus)
    pygame.draw.rect(screen, (150, 150, 200), life_cheat_minus, 2)
    life_cheat_minus_text = font_small.render("-", True, (255, 255, 255))
    screen.blit(life_cheat_minus_text, (screen_x + 165, 362))

    life_cheat_stat_text = font_small.render(
        f"{lives if lives >= 0 else '∞'}", True, (255, 200, 100)
    )
    screen.blit(
        life_cheat_stat_text, (
            (left + right) // 2 - life_cheat_stat_text.get_width() // 2, 363
        )
    )

    life_cheat_plus = pygame.Rect(screen_x + 215, 360, 25, 25)
    pygame.draw.rect(screen, (70, 70, 100), life_cheat_plus)
    pygame.draw.rect(screen, (150, 150, 200), life_cheat_plus, 2)
    life_cheat_plus_text = font_small.render("+", True, (255, 255, 255))
    screen.blit(life_cheat_plus_text, (screen_x + 222, 362))

    # Player speed control
    self_speed_text = font_medium.render("Player Speed", True, (100, 200, 255))
    screen.blit(self_speed_text, (screen_x + 15, 400))

    self_speed_minus = pygame.Rect(screen_x + 155, 400, 25, 25)
    pygame.draw.rect(screen, (70, 70, 100), self_speed_minus)
    pygame.draw.rect(screen, (150, 150, 200), self_speed_minus, 2)
    self_speed_minus_text = font_small.render("-", True, (255, 255, 255))
    screen.blit(self_speed_minus_text, (screen_x + 165, 402))

    self_speed_stat_text = font_small.render(
        f"{player.movement.speed}", True, (255, 200, 100)
    )
    screen.blit(
        self_speed_stat_text, (
            (left + right) // 2 - self_speed_stat_text.get_width() // 2, 403
        )
    )

    self_speed_plus = pygame.Rect(screen_x + 215, 400, 25, 25)
    pygame.draw.rect(screen, (70, 70, 100), self_speed_plus)
    pygame.draw.rect(screen, (150, 150, 200), self_speed_plus, 2)
    self_speed_plus_text = font_small.render("+", True, (255, 255, 255))
    screen.blit(self_speed_plus_text, (screen_x + 222, 402))

    # Level skip control
    level_skip_text = font_medium.render("Level Skip", True, (100, 200, 255))
    screen.blit(level_skip_text, (screen_x + 15, 440))

    level_skip_stat_text = font_small.render(
        f"Lvl: {level}", True, (255, 200, 100)
    )
    screen.blit(level_skip_stat_text, (screen_x + 155, 443))

    level_skip_plus = pygame.Rect(screen_x + 215, 440, 25, 25)
    pygame.draw.rect(screen, (70, 70, 100), level_skip_plus)
    pygame.draw.rect(screen, (150, 150, 200), level_skip_plus, 2)
    level_skip_plus_text = font_small.render("→", True, (255, 255, 255))
    screen.blit(level_skip_plus_text, (screen_x + 220, 442))

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
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
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

    bg_color = (10, 10, 26)
    box_bg = (15, 15, 35)
    box_border = (68, 136, 221)
    font = pygame.font.SysFont("Serif", 40, True)
    font_title = pygame.font.SysFont("Serif", 100, True)
    while True:
        screen.fill(bg_color)

        # Title
        pagman_title = font_title.render("PAG-MAN", True, (255, 255, 0))
        screen.blit(pagman_title, (screen_x//2 -
                    pagman_title.get_width()//2, 50))
        # Title underline
        pygame.draw.line(
            screen, box_border,
            (screen_x//2 - pagman_title.get_width()//2, 165),
            (screen_x//2 + pagman_title.get_width()//2, 165), 3
        )

        game_start_rect = pygame.Rect(screen_x//2 - 130, 220, 260, 60)
        hs_rect = pygame.Rect(screen_x//2 - 130, 310, 260, 60)
        instructions_rect = pygame.Rect(screen_x//2 - 130, 400, 260, 60)
        exit_rect = pygame.Rect(screen_x//2 - 130, 490, 260, 60)

        menu_options = [
            ("Start Game", game_start_rect),
            ("HighScores", hs_rect),
            ("Instructions", instructions_rect),
            ("Exit", exit_rect),
        ]

        for text, option_rect in menu_options:
            pygame.draw.rect(screen, box_bg, option_rect, border_radius=8)
            pygame.draw.rect(
                screen, box_border, option_rect, 3, border_radius=8
            )
            option_text = font.render(text, True, (255, 255, 0))
            screen.blit(option_text, (
                option_rect.centerx - option_text.get_width()//2,
                option_rect.centery - option_text.get_height()//2
            ))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    pygame.quit()
                    game_start(config)
