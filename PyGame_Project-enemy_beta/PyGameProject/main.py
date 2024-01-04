import os
import sys
import pygame

pygame.init()
size = width, height = 700, 550
moves = {'u': 0, 'd': 0, 'l': 0, 'r': 0}
clock = pygame.time.Clock()
fps = 60
screen = pygame.display.set_mode(size)
screen.fill((0, 0, 0))

player_sprite = pygame.sprite.Group()
tiles_sprite = pygame.sprite.Group()
border_sprite = pygame.sprite.Group()
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


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_sprite, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect(center=((tile_len * pos_x - self.image.get_width()) // 2,
                                                (tile_len * pos_y - self.image.get_height()) // 2
                                                )).move(tile_len * pos_x, tile_len * pos_y)
        self.image = pygame.transform.scale(self.image, (34, 52))
        self.base_image = self.image

    def rotate(self, x, y):
        if not pygame.sprite.spritecollideany(self, border_sprite):
            direction = pygame.math.Vector2(x, y) - self.rect.center
            self.image = pygame.transform.rotate(self.base_image, direction.angle_to((1, 0)))
            self.rect = self.image.get_rect(center=self.rect.center)

    def move(self):
        if not pygame.sprite.spritecollideany(self, border_sprite) or 1 > 0:
            self.rect = self.image.get_rect().move(step * (moves['r'] - moves['l']) + self.rect.x,
                                                   step * (moves['d'] - moves['u']) + self.rect.y)

    def Get_Coords(self):
        return [self.rect.x, self.rect.y]


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'wall':
            super().__init__(border_sprite, all_sprites)
        else:
            super().__init__(tiles_sprite, all_sprites)
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


class Enemy:
    def __init__(self, x_enemy, y_enemy, speed):
        self.left_enemy = False
        self.right_enemy = False
        self.down_enemy = False
        self.up_enemy = False

        self.x_enemy = x_enemy
        self.y_enemy = y_enemy

        self.animation_count = 0

        self.player_stand_enemy = pygame.image.load('data\enemy_stand.png')
        self.player_right_enemy = [pygame.image.load(f'data\enemy_right_{i}.png') for i in range(1, 5)]
        self.player_left_enemy = [pygame.image.load(f'data\enemy_left_{i}.png') for i in range(1, 5)]
        self.player_up_enemy = [pygame.image.load(f'data\enemy_up_{i}.png') for i in range(1, 5)]
        self.player_down_enemy = [pygame.image.load(f'data\enemy_down_{i}.png') for i in range(1, 5)]

        self.speed = speed

        self.enemy_is_near = False

    def Update_Enemy(self, x, y):
        if self.x_enemy == x and self.y_enemy == y:   # Если вражеский персонаж находится на оптимальных для стрельбы координатах
            self.enemy_is_near = True    # Вражеский персонаж стоит на месте
            self.left_enemy = False
            self.right_enemy = False
            self.down_enemy = False
            self.up_enemy = False
        else:
            if self.x_enemy == x or self.y_enemy == y or self.x_enemy == x or self.y_enemy == y:
                # Если игрок удаляется, враг его преследует
                self.enemy_is_near = False

        if self.enemy_is_near == False:  # Если вражеский персонаж не находится на оптимальных для стрельбы координатах
            if self.x_enemy != x or self.y_enemy != y:
                '''Условие, если координата x вражеского персонажа не равна координате x игрока 
                или координата y вражеского персонажа не равна координате y игрока'''
                if self.x_enemy != x and self.y_enemy != y:
                    '''Повторяется это условие, для того, чтобы под каждое перемещение вражеского игрока 
                    (вверх, вниз, влево, вправо) сделать анимацию'''
                    if self.x_enemy > x and self.y_enemy > y:
                        '''Условие, если координата x вражеского персонажа больше координаты x игрока 
                    или координата y вражеского персонажа больше координаты y игрока'''
                        self.left_enemy = True     # Отрисовываем анимацию перемещения влево
                        self.right_enemy = False
                        self.down_enemy = False
                        self.up_enemy = False
                        self.x_enemy -= self.speed  # Перемещаем вражеского персонажа влево
                        self.y_enemy -= self.speed  # И одновременно перемещаем его вверх
                    elif self.x_enemy < x and self.y_enemy < y:
                        self.left_enemy = False
                        self.right_enemy = True    # Отрисовываем анимацию перемещения вправо
                        self.down_enemy = False
                        self.up_enemy = False
                        self.x_enemy += self.speed  # Перемещаем вражеского персонажа вправо
                        self.y_enemy += self.speed  # И одновременно перемещаем его вниз
                    elif self.x_enemy < x and self.y_enemy > y:
                        self.left_enemy = False
                        self.right_enemy = True    # Отрисовываем анимацию перемещения вправо
                        self.down_enemy = False
                        self.up_enemy = False
                        self.x_enemy += self.speed  # Перемещаем вражеского персонажа вправо
                        self.y_enemy -= self.speed  # И одновременно перемещаем его вверх
                    elif self.x_enemy > x and self.y_enemy < y:
                        self.left_enemy = True     # Отрисовываем анимацию перемещения влево
                        self.right_enemy = False
                        self.down_enemy = False
                        self.up_enemy = False
                        self.x_enemy -= self.speed  # Перемещаем вражеского персонажа влево
                        self.y_enemy += self.speed  # И одновременно перемещаем его вниз
                elif self.y_enemy != y:
                    if self.y_enemy < y:
                        self.left_enemy = False
                        self.right_enemy = False
                        self.down_enemy = True # Отрисовываем анимацию перемещения вниз
                        self.up_enemy = False
                        self.y_enemy += self.speed  # Перемещаем вражеского персонажа вниз
                    elif self.y_enemy > y:
                        self.left_enemy = False
                        self.right_enemy = False
                        self.down_enemy = False
                        self.up_enemy = True   # Отрисовываем анимацию перемещения вверх
                        self.y_enemy -= self.speed  # Перемещаем вражеского персонажа вверх
                elif self.x_enemy != x:
                    if self.x_enemy < x:
                        self.x_enemy += self.speed  # Перемещаем вражеского персонажа вправо
                        self.left_enemy = False
                        self.right_enemy = True    # Отрисовываем анимацию перемещения вправо
                        self.down_enemy = False
                        self.up_enemy = False
                    elif self.x_enemy > x+170:
                        self.x_enemy -= self.speed  # Перемещаем вражеского персонажа влево
                        self.left_enemy = True     # Отрисовываем анимацию перемещения влево
                        self.right_enemy = False
                        self.down_enemy = False
                        self.up_enemy = False
            else:
                self.left_enemy = False
                self.right_enemy = False
                self.down_enemy = False
                self.up_enemy = False

    def Update_Animation(self, screen):
        if self.left_enemy:   # Анимация перемещения влево
            screen.blit(self.player_left_enemy[self.animation_count // 4], (self.x_enemy, self.y_enemy))
            self.animation_count += 1
            if self.animation_count == 8:
                self.animation_count = 0
        elif self.right_enemy:     # Анимация перемещения вправо
            screen.blit(self.player_right_enemy[self.animation_count // 4], (self.x_enemy, self.y_enemy))
            self.animation_count += 1
            if self.animation_count == 8:
                self.animation_count = 0
        elif self.up_enemy:    # Анимация перемещения вверх
            screen.blit(self.player_up_enemy[self.animation_count // 4], (self.x_enemy, self.y_enemy))
            self.animation_count += 1
            if self.animation_count == 8:
                self.animation_count = 0
        elif self.down_enemy:  # Анимация перемещения вниз
            screen.blit(self.player_down_enemy[self.animation_count // 4], (self.x_enemy, self.y_enemy))
            self.animation_count += 1
            if self.animation_count == 8:
                self.animation_count = 0
        else:
            screen.blit(self.player_stand_enemy, (self.x_enemy, self.y_enemy))
        pygame.display.update()


level_map = load_level('level1.txt')

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('character.png')
player, level_x, level_y = generate_level(load_level('level1.txt'))

Enemy_1 = Enemy(490, 150, 1)
Enemy_2 = Enemy(40, 150, 1)
Enemy_3 = Enemy(490, -150, 1)
Enemy_4 = Enemy(40, -150, 1)

Enemy_list = [Enemy_1, Enemy_2, Enemy_3, Enemy_4]

running = True
while running:
    screen.fill((0, 0, 0))
    tiles_sprite.draw(screen)
    border_sprite.draw(screen)
    player_sprite.draw(screen)
    x = player.Get_Coords()[0]
    y = player.Get_Coords()[1]
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
    player.move()
    for Enemy in Enemy_list:
        Enemy.Update_Enemy(x, y)
        Enemy.Update_Animation(screen)
    clock.tick(fps)
    pygame.display.flip()
terminate()
