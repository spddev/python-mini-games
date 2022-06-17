from __future__ import division

import sys
import math
import random
import time
from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse
from noise_gen import NoiseGen

# Размер одного тика в секундах, будет использоваться при загрузке блоков и
# чанков(присоединяемых объектов)
TICKS_PER_SEC = 60

# Размер нашей карты текстуры и генерации карты по чанкам
SECTOR_SIZE = 16

# Другие параметры для нашего персонажа:
WALKING_SPEED = 5
FLYING_SPEED = 15
CROUCH_SPEED = 2
SPRINT_SPEED = 7
SPRINT_FOV = SPRINT_SPEED / 2

GRAVITY = 20.0
MAX_JUMP_HEIGHT = 1.0  # 1 - один блок в высоту

JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)
TERMINAL_VELOCITY = 50

# Размер нашего персонажа/высота/ и отдалённость камеры
PLAYER_HEIGHT = 2
PLAYER_FOV = 80.0

if sys.version_info[0] >= 3:
    xrange = range


def cube_vertices(x, y, z, n):
    return [
        x - n, y + n, z - n, x - n, y + n, z + n, x + n, y + n, z + n, x + n, y + n, z - n,  # верх
        x - n, y - n, z - n, x + n, y - n, z - n, x + n, y - n, z + n, x - n, y - n, z + n,  # низ
        x - n, y - n, z - n, x - n, y - n, z + n, x - n, y + n, z + n, x - n, y + n, z - n,  # лево
        x + n, y - n, z + n, x + n, y - n, z - n, x + n, y + n, z - n, x + n, y + n, z + n,  # право
        x - n, y - n, z + n, x + n, y - n, z + n, x + n, y + n, z + n, x - n, y + n, z + n,  # перед
        x + n, y - n, z - n, x - n, y - n, z - n, x - n, y + n, z - n, x + n, y + n, z - n,  # назад
    ]


def tex_coord(x, y, n=4):
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top, bottom, side):
    # Тут будем возвращать список с текстурами и давать им направление
    # (вверх/вниз)

    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side = tex_coord(*side)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)
    return result


# Парсим текстурки и делаем разеделение на модельки
TEXTURE_PATH = 'texture.png'

GRASS = tex_coords((1, 0), (0, 1), (0, 0))
SAND = tex_coords((1, 1), (1, 1), (1, 1))
BRICK = tex_coords((2, 0), (2, 0), (2, 0))
STONE = tex_coords((2, 1), (2, 1), (2, 1))
WOOD = tex_coords((3, 1), (3, 1), (3, 1))
LEAF = tex_coords((3, 0), (3, 0), (3, 0))
WATER = tex_coords((0, 2), (0, 2), (0, 2))

FACES = [
    (0, 1, 0),
    (0, -1, 0),
    (-1, 0, 0),
    (1, 0, 0),
    (0, 0, 1),
    (0, 0, -1)
]


def normalize(position):
    # Будет принимать "позицию" и перенаправлять блоки, а также их возвращать
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return x, y, z


def sectorize(position):
    # Функция будет возвращать схему из секторов позиций
    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return (x, 0, z)


class Model(object):

    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())
        self.world = {}
        self.shown = {}
        self._shown = {}
        self.sectors = {}
        self.queue = deque()

        self._initialize()

    def _initialize(self):

        gen = NoiseGen(452692)  # наш сид генерации
        n = 128  # размер всей нашей карты (чем больше укажем, тем сильнее будет нагрузка на ПК)
        s = 1  # чанк карты (присоединённый объект)
        y = 0  # минимальная высота по y

        heightMap = []
        for x in xrange(0, n, s):
            for z in xrange(0, n, s):
                heightMap.append(0)
        for x in xrange(0, n, s):
            for z in xrange(0, n, s):
                heightMap[z + x * n] = int(gen.getHeight(x, z))

        # Создание мира
        for x in xrange(0, n, s):
            for z in xrange(0, n, s):
                h = heightMap[z + x * n]
                if h < 15:
                    self.add_block((x, h, z), SAND, immediate=False)
                    for y in range(h, 15):
                        self.add_block((x, y, z), WATER, immediate=False)
                    continue
                if h < 18:
                    self.add_block((x, h, z), SAND, immediate=False)
                self.add_block((x, h, z), GRASS, immediate=False)
                for y in xrange(h - 1, 0, -1):
                    self.add_block((x, y, z), STONE, immediate=False)
                if h > 20:
                    if random.randrange(0, 1000) > 990:
                        treeHeight = random.randrange(5, 7)
                        # деревья
                        for y in xrange(h + 1, h + treeHeight):
                            self.add_block((x, y, z), WOOD, immediate=False)
                        # листва
                        leaf = h + treeHeight
                        for lz in xrange(z + -2, z + 3):
                            for lx in xrange(x + -2, x + 3):
                                for ly in xrange(3):
                                    self.add_block((lx, leaf, + ly, lz),
                                                   LEAF, immediate=False)

    def hit_test(self, position, vector, max_distance=8):
        # Функция, которая будет создавать поиск линии прямой видимости
        # от текущей позиции.
        # Если блок пересечённый, он будет возращаться вместе с массивом блоков
        # ранее находившимся в строке зрения. Если блок не найден - возращаем None
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position):
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(self, position, texture, immediate=False):
        # Функция, с помощью которой мы будем ставить и разрушать блоки
        # (точнее ставить и удалять их с нашей карты мира)
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            self.check_neighbors(position)

    def remove_block(self, position, immediate=True):
        # Функция, которая будет убирать блоки с определённой позиции
        # (брат функции add_block)
        del self.world[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            self.check_neighbors(position)

    def check_neighbors(self, position):
        # Проверка и обновление структур блоков
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.show_block(key)

    def show_block(self, position, immediate=True):
        # Отображение блоков на сетке координат (позиции)
        texture = self.world[position]
        self.shown[position] = texture
        if immediate:
            self._show_block(position, texture)
        else:
            self._enqueue(self._show_block, position, texture)

    def _show_block(self, position, texture):
        # Приватная функция для "show_block()", она будет расставлять блоки
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)
        self._shown[position] = self.batch.add(24, GL_QUADS, self.group,
                                               ('v3f/static', vertex_data),
                                               ('t2f/static', texture_data))

    def hide_block(self, position, immediate=True):
        # Тут будем прятать блоки с нашей позиции
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position):
        self._shown.pop(position).delete()

    def show_sector(self, sector):
        for position in self.sectors.get(sector, []):
            if position not in self.shown and self.exposed(position):
                self.show_block(position, False)

    def hide_sector(self, sector):
        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hide_block(position, False)

    def change_sectors(self, before, after):
        before_set = set()
        after_set = set()
        pad = 4
        for dx in xrange(-pad, pad + 1):
            for dy in [0]:
                for dz in xrange(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, y, z = before
                        before_set.add((x + dx, y + dy, z + dz))
                    if after:
                        x, y, z = after
                        after_set.add((x + dx, y + dy, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

