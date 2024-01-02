import os
import sys
import pygame

pygame.init()
size = width, height = 700, 550
moves = {'u': 0, 'd': 0, 'l': 0, 'r': 0}
bullets = []
clock = pygame.time.Clock()
fps = 60
screen = pygame.display.set_mode(size)
screen.fill((0, 0, 0))

player_sprite = pygame.sprite.Group()
bullets_sprite = pygame.sprite.Group()
tiles_sprite = pygame.sprite.Group()
border_sprite = pygame.sprite.Group()

tile_len = 50
step = 5


def terminate():
    pygame.quit()
    sys.exit()


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


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, vector):
        super().__init__(bullets_sprite)
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        self.x, self.y = vector[0] - start_x, vector[1] - start_y
        self.rect = pygame.draw.rect(screen, pygame.Color('yellow'), (start_x, start_y, 10, 10))

    def update(self):
        pygame.draw.rect(screen, pygame.Color('yellow'), (self.rect.x, self.rect.y, 10, 10))
        self.rect.x, self.rect.y = int(self.rect.x + 0.1 * self.x), int(self.rect.y + 0.1 * self.y)
        if pygame.sprite.spritecollideany(self, border_sprite):
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_sprite)
        self.is_shooting = False
        self.image = player_image
        self.rect = self.image.get_rect(center=((tile_len * pos_x - self.image.get_width()) // 2,
                                                (tile_len * pos_y - self.image.get_height()) // 2
                                                )).move(tile_len * pos_x, tile_len * pos_y)
        self.image = pygame.transform.scale(self.image, (104, 52))
        self.base_image = self.image

    def rotate(self, x, y):
        if not pygame.sprite.spritecollideany(self, border_sprite):
            direction = pygame.math.Vector2(x, y) - self.rect.center
            self.image = pygame.transform.rotate(self.base_image, direction.angle_to((1, 0)))
            self.rect = self.image.get_rect(center=self.rect.center)

    def move(self):
        if not pygame.sprite.spritecollideany(self, border_sprite):
            self.rect = self.image.get_rect().move(step * (moves['r'] - moves['l']) + self.rect.x,
                                                   step * (moves['d'] - moves['u']) + self.rect.y)

    def shoot(self):
        if self.is_shooting:
            Bullet(self.rect.x, self.rect.y, pygame.mouse.get_pos())


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'wall':
            super().__init__(border_sprite)
        else:
            super().__init__(tiles_sprite)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_len * pos_x, tile_len * pos_y)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level = [line.strip() for line in mapFile]
    max_width = max(map(len, level))
    return list(map(lambda x: x.ljust(max_width, '.'), level))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


level_map = load_level('level1.txt')

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('character.png')
player, level_x, level_y = generate_level(load_level('level1.txt'))

running = True
i = 0
while running:
    screen.fill((0, 0, 0))
    border_sprite.draw(screen)
    tiles_sprite.draw(screen)
    player_sprite.draw(screen)
    bullets_sprite.draw(screen)
    bullets_sprite.update()
    player.rotate(*pygame.mouse.get_pos())
    if i == 10:
        player.shoot()
        i = 0
    i += 1
    player.move()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            player.is_shooting = True if event.type == pygame.MOUSEBUTTONDOWN else False
        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
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
terminate()
