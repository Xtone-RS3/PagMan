import pygame
from paths import asset


class Pacgum(pygame.sprite.Sprite):
    """Regular pac-gum collectible item.

    Small dot that gives points when collected by the player.
    """

    def __init__(self, x: float, y: float, size: float):
        """Creates a pac-gum at the specified position.

        Args:
            x: X coordinate of the center position.
            y: Y coordinate of the center position.
            size: Size in pixels for the sprite.
        """
        super().__init__()
        self.image = pygame.image.load(asset("pacmen_and_gums", "gum1.png"))
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        self.hitbox = self.rect.inflate(-28, -28)


class superPacgum(pygame.sprite.Sprite):
    """Super pac-gum (power pellet) that makes ghosts edible.

    When collected, ghosts become edible for a limited time,
    allowing the player to eat them for bonus points.
    """

    def __init__(self, x: float, y: float, size: float):
        """Creates a super pac-gum at the specified position.

        Args:
            x: X coordinate of the center position.
            y: Y coordinate of the center position.
            size: Size in pixels for the sprite.
        """
        super().__init__()
        self.image = pygame.image.load(asset("pacmen_and_gums", "gum3.png"))
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        self.hitbox = self.rect.inflate(-10, -10)
