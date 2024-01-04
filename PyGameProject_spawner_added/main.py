import os
import sys
import pygame

pygame.init()
pygame.display.set_caption('Snake Arena')
size = width, height = 700, 550
moves = {'u': 0, 'd': 0, 'l': 0, 'r': 0}
font = pygame.font.SysFont('timesNewRoman', 25)
clock = pygame.time.Clock()
fps = 60
screen = pygame.display.set_mode(size)

player_sprite = pygame.sprite.Group()
tiles_sprite = pygame.sprite.Group()
border_sprite = pygame.sprite.Group()
g_border_sprite = pygame.sprite.Group()
after_player_sprite = pygame.sprite.Group()
bullets_sprite = pygame.sprite.Group()
enemy_sprite = pygame.sprite.Group()
spawner_sprite = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

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
        if pygame.sprite.spritecollideany(self, border_sprite) and not pygame.sprite.spritecollideany(self,
                                                                                                      g_border_sprite):
            self.kill()
        if pygame.sprite.spritecollideany(self, enemy_sprite):
            pygame.sprite.spritecollide(self, enemy_sprite, False)[0].health -= 1
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_sprite, all_sprites)
        self.hp, self.ammo = 10, 30
        self.max_hp, self.pack = 10, 5
        self.is_reloading = False
        self.is_shooting = False
        self.safe_frames = False
        self.flag = False
        self.image = pygame.transform.scale(load_image('character.png'), (34, 52))
        self.rect = self.image.get_rect(center=((tile_len * pos_x - self.image.get_width()) // 2,
                                                (tile_len * pos_y - self.image.get_height()) // 2
                                                )).move(tile_len * pos_x + 2, tile_len * pos_y - 3)

    def move(self):
        if pygame.sprite.spritecollideany(self, border_sprite):
            sp = [player.rect.clip(i) for i in pygame.sprite.spritecollide(player, border_sprite, False)]
            sp = sorted([[i.left, i.right, i.bottom, i.top, i.width, i.height] for i in sp], key=lambda x: (x[4], x[5]))
            if len(sp) != 1:
                sp += [[min(sp[0][0], sp[1][0]), max(sp[0][1], sp[1][1]), max(sp[0][2], sp[1][2]), min(sp[0][3],
                                                                                                       sp[1][3])]]
                for _ in range(2):
                    del sp[0]
            for i in sp:
                if i[3] >= self.rect.bottom - 2:
                    moves['d'] = 0
                if i[1] <= self.rect.left + 5:
                    moves['l'] = 0
                if i[2] <= self.rect.top + 5:
                    moves['u'] = 0
                if i[0] >= self.rect.right - 4:
                    moves['r'] = 0
            self.flag = True
        elif self.flag:
            keys = pygame.key.get_pressed()
            if moves['d'] == 0 and (keys[pygame.K_s] or keys[pygame.K_DOWN]):
                moves['d'] = 1
            if moves['u'] == 0 and (keys[pygame.K_w] or keys[pygame.K_UP]):
                moves['u'] = 1
            if moves['l'] == 0 and (keys[pygame.K_a] or keys[pygame.K_LEFT]):
                moves['l'] = 1
            if moves['r'] == 0 and (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
                moves['r'] = 1
            self.flag = False
        self.rect = self.image.get_rect().move(step * (moves['r'] - moves['l']) + self.rect.x,
                                               step * (moves['d'] - moves['u']) + self.rect.y)

    def shoot(self):
        if self.is_shooting and self.ammo != 0:
            Bullet(*self.rect.center, pygame.mouse.get_pos())
            self.ammo -= 1

    def reload(self):
        if self.pack != 0:
            self.ammo = 30
            self.pack -= 1

    def damage(self):
        if not self.safe_frames:
            self.hp -= 1
            if self.hp == 0:
                terminate()
            self.safe_frames = True


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type in ('wall', 'box'):
            super().__init__(border_sprite, all_sprites)
        elif tile_type in ('water'):
            super().__init__(border_sprite, g_border_sprite, all_sprites)
        elif tile_type in ('tree'):
            super().__init__(after_player_sprite, all_sprites)
        else:
            super().__init__(tiles_sprite, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_len * pos_x, tile_len * pos_y)
            

class Spawner(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, interval):
        super().__init__(spawner_sprite, all_sprites)
        self.interval = interval
        self.past_time = 0
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_len * pos_x, tile_len * pos_y)

    def update(self):
        self.past_time += 1
        if self.past_time >= self.interval:
            enemy = Enemy(self.rect.x + 40, self.rect.y + 20, 1)
            self.past_time = 0


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.x_spawn = 500
        self.y_spawn = 400

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)
        self.x_spawn += self.dx
        self.y_spawn += self.dy
        
    def get_spawner_coords(self):
        return [self.x_spawn, self.y_spawn]


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x_enemy, y_enemy, speed):
        super().__init__(all_sprites, enemy_sprite)
        self.left_enemy = False
        self.right_enemy = False
        self.down_enemy = False
        self.up_enemy = False
        self.health = 3
        self.animation_count = 0

        self.player_stand_enemy = pygame.image.load('data\enemy_stand.png')
        self.player_right_enemy = [pygame.image.load(f'data\enemy_right_{i}.png') for i in range(1, 5)]
        self.player_left_enemy = [pygame.image.load(f'data\enemy_left_{i}.png') for i in range(1, 5)]
        self.player_up_enemy = [pygame.image.load(f'data\enemy_up_{i}.png') for i in range(1, 5)]
        self.player_down_enemy = [pygame.image.load(f'data\enemy_down_{i}.png') for i in range(1, 5)]

        self.speed = speed
        self.image = self.player_stand_enemy
        self.rect = self.image.get_rect().move(x_enemy, y_enemy)

        self.enemy_is_near = False

    def update(self):
        if self.health == 0:
            self.kill()
        if pygame.sprite.spritecollideany(self, player_sprite):
            player.damage()
        x, y = player.rect.x, player.rect.y
        if self.rect.x == x and self.rect.y == y:  # Если вражеский персонаж находится на оптимальных для стрельбы к.
            self.enemy_is_near = True  # Вражеский персонаж стоит на месте
            self.left_enemy = False
            self.right_enemy = False
            self.down_enemy = False
            self.up_enemy = False
        else:
            if self.rect.x == x or self.rect.y == y or self.rect.x == x or self.rect.y == y:
                # Если игрок удаляется, враг его преследует
                self.enemy_is_near = False

        if not self.enemy_is_near:  # Если вражеский персонаж не находится на оптимальных для стрельбы координатах
            if self.rect.x != x or self.rect.y != y:
                '''Условие, если координата x вражеского персонажа не равна координате x игрока 
                или координата y вражеского персонажа не равна координате y игрока'''
                if self.rect.x != x and self.rect.y != y:
                    '''Повторяется это условие, для того, чтобы под каждое перемещение вражеского игрока 
                    (вверх, вниз, влево, вправо) сделать анимацию'''
                    if self.rect.x > x and self.rect.y > y:
                        '''Условие, если координата x вражеского персонажа больше координаты x игрока 
                    или координата y вражеского персонажа больше координаты y игрока'''
                        self.left_enemy = True  # Отрисовываем анимацию перемещения влево
                        self.right_enemy = False
                        self.down_enemy = False
                        self.up_enemy = False
                        self.rect.x, self.rect.y = self.rect.x - self.speed, self.rect.y - self.speed
                    elif self.rect.x < x and self.rect.y < y:
                        self.left_enemy = False
                        self.right_enemy = True  # Отрисовываем анимацию перемещения вправо
                        self.down_enemy = False
                        self.up_enemy = False
                        self.rect.x, self.rect.y = self.rect.x + self.speed, self.rect.y + self.speed
                    elif self.rect.x < x and self.rect.y > y:
                        self.left_enemy = False
                        self.right_enemy = True  # Отрисовываем анимацию перемещения вправо
                        self.down_enemy = False
                        self.up_enemy = False
                        self.rect.x, self.rect.y = self.rect.x + self.speed, self.rect.y - self.speed
                    elif self.rect.x > x and self.rect.y < y:
                        self.left_enemy = True  # Отрисовываем анимацию перемещения влево
                        self.right_enemy = False
                        self.down_enemy = False
                        self.up_enemy = False
                        self.rect.x, self.rect.y = self.rect.x - self.speed, self.rect.y + self.speed
                elif self.rect.y != y:
                    if self.rect.y < y:
                        self.left_enemy = False
                        self.right_enemy = False
                        self.down_enemy = True  # Отрисовываем анимацию перемещения вниз
                        self.up_enemy = False
                        self.rect.y = self.rect.y + self.speed
                    elif self.rect.y > y:
                        self.left_enemy = False
                        self.right_enemy = False
                        self.down_enemy = False
                        self.up_enemy = True  # Отрисовываем анимацию перемещения вверх
                        self.rect.y = self.rect.y - self.speed
                elif self.rect.x != x:
                    if self.rect.x < x:
                        self.rect.x = self.rect.x + self.speed
                        self.left_enemy = False
                        self.right_enemy = True  # Отрисовываем анимацию перемещения вправо
                        self.down_enemy = False
                        self.up_enemy = False
                    elif self.rect.x > x:
                        self.rect.x = self.rect.x - self.speed
                        self.left_enemy = True  # Отрисовываем анимацию перемещения влево
                        self.right_enemy = False
                        self.down_enemy = False
                        self.up_enemy = False
            else:
                self.left_enemy = False
                self.right_enemy = False
                self.down_enemy = False
                self.up_enemy = False
        if self.left_enemy:  # Анимация перемещения влево
            self.image = self.player_left_enemy[self.animation_count // 4]
            self.animation_count += 1
            if self.animation_count == 8:
                self.animation_count = 0
        elif self.right_enemy:  # Анимация перемещения вправо
            self.image = self.player_right_enemy[self.animation_count // 4]
            self.animation_count += 1
            if self.animation_count == 8:
                self.animation_count = 0
        elif self.up_enemy:  # Анимация перемещения вверх
            self.image = self.player_up_enemy[self.animation_count // 4]
            self.animation_count += 1
            if self.animation_count == 8:
                self.animation_count = 0
        elif self.down_enemy:  # Анимация перемещения вниз
            self.image = self.player_down_enemy[self.animation_count // 4]
            self.animation_count += 1
            if self.animation_count == 8:
                self.animation_count = 0
        else:
            self.image = self.player_stand_enemy


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
                Tile('plant_1', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == 'W':
                Tile('water', x, y)
            elif level[y][x] == 's':
                Tile('empty', x, y)
            elif level[y][x] == 'S':
                Tile('sand', x, y)
            elif level[y][x] == 'T':
                Tile('empty', x, y)
            elif level[y][x] == 'D':
                Tile('dirt', x, y)
            elif level[y][x] == 'B':
                Tile('box', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == 'T':
                Tile('tree', x, y)
            elif level[y][x] == 's':
                Spawner('spawner', x, y, fps * 5)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def text_display():
    ev_disp = []
    s1 = font.render('Уровень 1', True, pygame.Color('white'))
    r1 = s1.get_rect().move(10, 10)
    s2 = font.render('Врагов: x / x', True, pygame.Color('white'))
    r2 = s2.get_rect().move(width - s2.get_rect().width - 10, height - s2.get_rect().height - 10)
    s3 = font.render(f'Патронов: {player.ammo} | {player.pack}', True, pygame.Color('white'))
    r3 = s3.get_rect().move(10, height - s3.get_rect().height - 10)
    s4 = font.render(f'ОЗ: {player.hp} / {player.max_hp}', True, pygame.Color('white'))
    r4 = s4.get_rect().move(width // 2 - s4.get_rect().width, height - s4.get_rect().height - 10)
    if player.is_reloading:
        s5 = font.render('Перезарядка!', True, pygame.Color('white'))
        ev_disp += [(s5, s5.get_rect().move(width - s5.get_rect().width - 10, 10))]
    return [(s1, r1), (s2, r2), (s3, r3), (s4, r4)] + ev_disp


level_map = load_level('level1.txt')

tile_images = {
    'wall': load_image('wall.png'),
    'empty': load_image('grass.png'),
    'water': load_image('water.png'),
    'sand': load_image('sand.png'),
    'dirt': load_image('dirt.png'),
    'box': load_image('box.png'),
    'tree': load_image('plant.png'),
    'plant_1': load_image('plant_1.png'),
    'plant_2': load_image('plant_2.png'),
    'plant_3': load_image('plant_3.png'),
    'block': load_image('block.png'),
    'spawner': load_image('spawner.png')
}
player, level_x, level_y = generate_level(level_map)
camera = Camera()
i = 0
sf = 0

while True:
    screen.fill((0, 0, 0))
    camera.update(player)

    for sprite in all_sprites:
        camera.apply(sprite)
    border_sprite.draw(screen)
    g_border_sprite.draw(screen)
    tiles_sprite.draw(screen)
    spawner_sprite.draw(screen)
    spawner_sprite.update()
    bullets_sprite.draw(screen)
    player_sprite.draw(screen)
    enemy_sprite.draw(screen)
    enemy_sprite.update()
    bullets_sprite.update()
    text = text_display()
    
    if player.safe_frames:
        sf += 1
    if sf == 100:
        player.safe_frames = False
        sf = 0
    for line in text:
        screen.blit(line[0], line[1])
    if i == 15:
        if player.ammo != 0:
            player.shoot()
        i = 0
    if i == 150:
        player.reload()
        player.is_reloading = False
        i = 0
    i += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            player.is_shooting = True
            i = 15
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            player.is_shooting = False
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            if event.key == pygame.K_r and event.type == pygame.KEYDOWN:
                i = 20 if not player.is_reloading else 0
                player.is_reloading = not player.is_reloading
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                moves['u'] = 1 if event.type == pygame.KEYDOWN else 0
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                moves['d'] = 1 if event.type == pygame.KEYDOWN else 0
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                moves['r'] = 1 if event.type == pygame.KEYDOWN else 0
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                moves['l'] = 1 if event.type == pygame.KEYDOWN else 0
    player.move()
    after_player_sprite.draw(screen)
    clock.tick(fps)
    pygame.display.flip()
