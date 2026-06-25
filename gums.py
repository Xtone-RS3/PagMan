import pygame


class Pacgum(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, size: float):
        super().__init__()
        self.image = pygame.image.load("gum1.png")
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        self.hitbox = self.rect.inflate(-28, -28)


class superPacgum(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, size: float):
        super().__init__()
        self.image = pygame.image.load("gum3.png")
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        self.hitbox = self.rect.inflate(-10, -10)
