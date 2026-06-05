import pygame

# Inicializar o pygame
pygame.init()

# Criar janela
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Primeiro teste Pygame")

# Relógio para controlar FPS
clock = pygame.time.Clock()

# Posição do quadrado
x = 100
y = 100

# Tamanho e velocidade
size = 50
speed = 5

running = True

while running:

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Teclas pressionadas
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        x -= speed

    if keys[pygame.K_RIGHT]:
        x += speed

    if keys[pygame.K_UP]:
        y -= speed

    if keys[pygame.K_DOWN]:
        y += speed

    # Fundo preto
    screen.fill((0, 0, 0))

    # Desenhar quadrado branco
    pygame.draw.rect(screen, (255, 255, 255), (x, y, size, size))

    # Atualizar ecrã
    pygame.display.flip()

    # 60 FPS
    clock.tick(60)

pygame.quit()