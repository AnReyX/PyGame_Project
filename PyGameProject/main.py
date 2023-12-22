import os
import sys
import pygame

pygame.init()
size = width, height = 700, 600
moves = {'u': 0, 'd': 0, 'l': 0, 'r': 0}
clock = pygame.time.Clock()
fps = 60
screen = pygame.display.set_mode(size)
screen.fill((0, 0, 0))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Player(pygame.sprite.Sprite):
    image = load_image('character.png')

    def __init__(self):
        super().__init__(player_sprite)
        pygame.sprite.Sprite.__init__(self)
        self.image = Player.image
        self.rect = self.image.get_rect(center=(width // 2, height // 2))
        self.image = pygame.transform.scale(self.image, (208, 104))
        self.base_image = self.image
        self.rect.x = width // 3
        self.rect.y = height // 3

    def rotate(self, x, y):
        direction = pygame.math.Vector2(x, y) - self.rect.center
        self.image = pygame.transform.rotate(self.base_image, direction.angle_to((1, 0)))
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        self.rect = self.image.get_rect().move(step * (moves['r'] - moves['l']) +
                                               self.rect.x, step * (moves['d'] - moves['u']) + self.rect.y)


player_sprite = pygame.sprite.Group()
player = Player()
step = 5

running = True
while running:
    screen.fill((0, 0, 0))
    player_sprite.draw(screen)
    player_sprite.update()
    for event in pygame.event.get():
        player.rotate(*pygame.mouse.get_pos())
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                moves['u'] = 1 if event.type == pygame.KEYDOWN else 0
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                moves['d'] = 1 if event.type == pygame.KEYDOWN else 0
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                moves['r'] = 1 if event.type == pygame.KEYDOWN else 0
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                moves['l'] = 1 if event.type == pygame.KEYDOWN else 0
    clock.tick(fps)
    pygame.display.flip()