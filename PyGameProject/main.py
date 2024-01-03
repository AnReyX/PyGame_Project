import os
import sys
import pygame

pygame.init()
size = width, height = 700, 550
moves = {'u': 0, 'd': 0, 'l': 0, 'r': 0}
clock = pygame.time.Clock()
fps = 60
screen = pygame.display.set_mode(size)

player_sprite = pygame.sprite.Group()
tiles_sprite = pygame.sprite.Group()
border_sprite = pygame.sprite.Group()
ground_border_sprite = pygame.sprite.Group()
bullets_sprite = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

tile_len = 50
step = 5

# -------------------------------------------------------------------
player_stand_enemy = pygame.image.load('data\enemy_stand.png')
player_right_enemy = [pygame.image.load(f'data\enemy_right_{i}.png') for i in range(1, 5)]
player_left_enemy = [pygame.image.load(f'data\enemy_left_{i}.png') for i in range(1, 5)]
player_up_enemy = [pygame.image.load(f'data\enemy_up_{i}.png') for i in range(1, 5)]
player_down_enemy = [pygame.image.load(f'data\enemy_down_{i}.png') for i in range(1, 5)]

x_enemy = 540
y_enemy = 50

speed = 1
enemy_is_near = False

animation_count = 0

bullets_enemy = []


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
    def __init__(self, x, y, vec):
        super().__init__(bullets_sprite, all_sprites)
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        try:
            d = 10 / int(((x - vec[0]) ** 2 + (y - vec[1]) ** 2) ** (1 / 2) - 10)
            self.speed_x, self.speed_y = int((x + vec[0] * d) // (1 + d)) - x, int((y + vec[1] * d) // (1 + d)) - y
        except ZeroDivisionError:
            self.kill()
        self.x, self.y = vec[0] - x, vec[1] - y
        self.rect = pygame.draw.rect(screen, pygame.Color('yellow'), (x, y, 10, 10))

    def update(self):
        pygame.draw.rect(screen, pygame.Color('yellow'), (self.rect.x, self.rect.y, 10, 10))
        self.rect.x, self.rect.y = int(self.rect.x + self.speed_x), int(self.rect.y + self.speed_y)
        if pygame.sprite.spritecollideany(self, border_sprite):
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_sprite, all_sprites)
        self.is_shooting = False
        self.image = player_image
        self.rect = self.image.get_rect(center=((tile_len * pos_x - self.image.get_width()) // 2,
                                                (tile_len * pos_y - self.image.get_height()) // 2
                                                )).move(tile_len * pos_x + 2, tile_len * pos_y - 3)
        self.image = pygame.transform.scale(self.image, (34, 52))
        self.base_image = self.image

    def move(self):
        if not pygame.sprite.spritecollideany(self, border_sprite) or 1 > 0:
            self.rect = self.image.get_rect().move(step * (moves['r'] - moves['l']) + self.rect.x,
                                                   step * (moves['d'] - moves['u']) + self.rect.y)

    def shoot(self):
        if self.is_shooting:
            Bullet(*self.rect.center, pygame.mouse.get_pos())

    def Get_Coords(self):
        return [self.rect.x, self.rect.y]


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type in ('wall', 'box'):
            super().__init__(border_sprite, all_sprites)
        elif tile_type in ('water',):
            super().__init__(ground_border_sprite, all_sprites)
        else:
            super().__init__(tiles_sprite, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_len * pos_x, tile_len * pos_y)

    def update(self):
        if pygame.sprite.spritecollideany(self, player_sprite):
            if self.rect.x + 45 == player.rect.x:
                moves['l'] = 0
                return
            if self.rect.y + 45 == player.rect.y:
                moves['u'] = 0
                return
            if self.rect.x == player.rect.x + 30:
                moves['r'] = 0
                return
            if self.rect.y == player.rect.y + 50:
                moves['d'] = 0
                return


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


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
            elif level[y][x] == 'W':
                Tile('water', x, y)
            elif level[y][x] == 'S':
                Tile('sand', x, y)
            elif level[y][x] == 'D':
                Tile('dirt', x, y)
            elif level[y][x] == 'B':
                Tile('box', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def enemy(x1, y1):
    # Все переменные, которые будут использоваться не только в этой функции, объявляем как глобальные
    global left_enemy
    global right_enemy
    global down_enemy
    global x_enemy
    global y_enemy
    x = x1
    y = y1
    global up_enemy
    global enemy_is_near

    if x_enemy == x and y_enemy == y:   # Если вражеский персонаж находится на оптимальных для стрельбы координатах
        enemy_is_near = True    # Вражеский персонаж стоит на месте
        left_enemy = False
        right_enemy = False
        down_enemy = False
        up_enemy = False
    else:
        if x_enemy == x or y_enemy == y or x_enemy == x or y_enemy == y:
            # Если игрок удаляется, враг его преследует
            enemy_is_near = False

    if not enemy_is_near:  # Если вражеский персонаж не находится на оптимальных для стрельбы координатах
        if x_enemy != x or y_enemy != y:
            '''Условие, если координата x вражеского персонажа не равна координате x игрока 
            или координата y вражеского персонажа не равна координате y игрока'''
            if x_enemy != x and y_enemy != y:
                '''Повторяется это условие, для того, чтобы под каждое перемещение вражеского игрока 
                (вверх, вниз, влево, вправо) сделать анимацию'''
                if x_enemy > x and y_enemy > y:
                    '''Условие, если координата x вражеского персонажа больше координаты x игрока 
                или координата y вражеского персонажа больше координаты y игрока'''
                    left_enemy = True     # Отрисовываем анимацию перемещения влево
                    right_enemy = False
                    down_enemy = False
                    up_enemy = False
                    x_enemy -= speed  # Перемещаем вражеского персонажа влево
                    y_enemy -= speed  # И одновременно перемещаем его вверх
                elif x_enemy < x and y_enemy < y:
                    left_enemy = False
                    right_enemy = True    # Отрисовываем анимацию перемещения вправо
                    down_enemy = False
                    up_enemy = False
                    x_enemy += speed  # Перемещаем вражеского персонажа вправо
                    y_enemy += speed  # И одновременно перемещаем его вниз
                elif x_enemy < x and y_enemy > y:
                    left_enemy = False
                    right_enemy = True    # Отрисовываем анимацию перемещения вправо
                    down_enemy = False
                    up_enemy = False
                    x_enemy += speed  # Перемещаем вражеского персонажа вправо
                    y_enemy -= speed  # И одновременно перемещаем его вверх
                elif x_enemy > x and y_enemy < y:
                    left_enemy = True     # Отрисовываем анимацию перемещения влево
                    right_enemy = False
                    down_enemy = False
                    up_enemy = False
                    x_enemy -= speed  # Перемещаем вражеского персонажа влево
                    y_enemy += speed  # И одновременно перемещаем его вниз
            elif y_enemy != y:
                if y_enemy < y:
                    left_enemy = False
                    right_enemy = False
                    down_enemy = True # Отрисовываем анимацию перемещения вниз
                    up_enemy = False
                    y_enemy += speed  # Перемещаем вражеского персонажа вниз
                elif y_enemy > y:
                    left_enemy = False
                    right_enemy = False
                    down_enemy = False
                    up_enemy = True   # Отрисовываем анимацию перемещения вверх
                    y_enemy -= speed  # Перемещаем вражеского персонажа вверх
            elif x_enemy != x+170:
                if x_enemy < x+170:
                    x_enemy += speed  # Перемещаем вражеского персонажа вправо
                    left_enemy = False
                    right_enemy = True    # Отрисовываем анимацию перемещения вправо
                    down_enemy = False
                    up_enemy = False
                elif x_enemy > x+170:
                    x_enemy -= speed  # Перемещаем вражеского персонажа влево
                    left_enemy = True     # Отрисовываем анимацию перемещения влево
                    right_enemy = False
                    down_enemy = False
                    up_enemy = False
        else:
            left_enemy = False
            right_enemy = False
            down_enemy = False
            up_enemy = False


window = screen


def draw_window():
    global animation_count
    if left_enemy:   # Анимация перемещения влево
        window.blit(player_left_enemy[animation_count // 4], (x_enemy, y_enemy))
        animation_count += 1
        if animation_count == 8:
            animation_count = 0
    elif right_enemy:     # Анимация перемещения вправо
        window.blit(player_right_enemy[animation_count // 4], (x_enemy, y_enemy))
        animation_count += 1
        if animation_count == 8:
            animation_count = 0
    elif up_enemy:    # Анимация перемещения вверх
        window.blit(player_up_enemy[animation_count // 4], (x_enemy, y_enemy))
        animation_count += 1
        if animation_count == 8:
            animation_count = 0
    elif down_enemy:  # Анимация перемещения вниз
        window.blit(player_down_enemy[animation_count // 4], (x_enemy, y_enemy))
        animation_count += 1
        if animation_count == 8:
            animation_count = 0
    else:
        window.blit(player_stand_enemy, (x_enemy, y_enemy))
    pygame.display.update()


def text_display():
    font = pygame.font.SysFont('timesNewRoman', 25)
    s1 = font.render('Уровень 1', True, pygame.Color('white'))
    r1 = s1.get_rect().move(10, 10)
    s2 = font.render('Врагов: x / x', True, pygame.Color('white'))
    r2 = s2.get_rect().move(width - s2.get_rect().width - 10, height - s2.get_rect().height - 10)
    s3 = font.render('Патронов: y', True, pygame.Color('white'))
    r3 = s3.get_rect().move(10, height - s3.get_rect().height - 10)
    s4 = font.render('ОЗ: z / z', True, pygame.Color('white'))
    r4 = s4.get_rect().move(width // 3 - s4.get_rect().width + 20, height - s4.get_rect().height - 10)
    return [(s1, r1), (s2, r2), (s3, r3), (s4, r4)]


level_map = load_level('level1.txt')

tile_images = {
    'wall': load_image('wall.png'),
    'empty': load_image('grass.png'),
    'water': load_image('water.png'),
    'sand': load_image('sand.png'),
    'dirt': load_image('dirt.png'),
    'box': load_image('box.png')
}
player_image = load_image('character.png')
player, level_x, level_y = generate_level(level_map)
camera = Camera()
text = text_display()
i = 0
while True:
    screen.fill((0, 0, 0))
    camera.update(player)
    #  обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)
    border_sprite.draw(screen)
    ground_border_sprite.draw(screen)
    tiles_sprite.draw(screen)
    bullets_sprite.draw(screen)
    player_sprite.draw(screen)
    bullets_sprite.update()
    for line in text:
        screen.blit(line[0], line[1])
    if i == 15:
        player.shoot()
        i = 0
    i += 1
    #  x3 = player.Get_Coords()[0]
    #  y3 = player.Get_Coords()[1]
    #  print(x, y)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.is_shooting = True
            i = 15
        elif event.type == pygame.MOUSEBUTTONUP:
            player.is_shooting = False
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                moves['u'] = 1 if event.type == pygame.KEYDOWN else 0
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                moves['d'] = 1 if event.type == pygame.KEYDOWN else 0
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                moves['r'] = 1 if event.type == pygame.KEYDOWN else 0
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                moves['l'] = 1 if event.type == pygame.KEYDOWN else 0
    border_sprite.update()
    ground_border_sprite.update()
    player.move()
    #  enemy(x3, y3)
    #  draw_window()
    clock.tick(fps)
    pygame.display.flip()