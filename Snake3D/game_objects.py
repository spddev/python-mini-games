from ursina import *
from random import randrange


# класс "Яблоко"(Apple), наследник класса "Сущность" (Entity)
# основной класс игровых объектов Ursina
class Apple(Entity):
    def __init__(self, MAP_SIZE, **kwargs):
        super().__init__(**kwargs)
        self.MAP_SIZE = MAP_SIZE
        self.new_position()

    # метод установки новой позиции объекта "Яблоко"
    def new_position(self):
        self.position = (randrange(self.MAP_SIZE) + 0.5, randrange(self.MAP_SIZE) + 0.5, -0.5)


# класс "Змейка"
class Snake:
    def __init__(self, MAP_SIZE):
        self.MAP_SIZE = MAP_SIZE
        # зададим начальную длину сегмента "змейки"
        self.segment_length = 1
        self.position_length = self.segment_length + 1
        # создадим список координат сегментов "змейки"
        # и добавим в список случайные координаты - это "голова" змейки
        self.segment_positions = [Vec3(randrange(MAP_SIZE) + 0.5, randrange(MAP_SIZE) + 0.5, -0.5)]
        # добавим в список сегментов сегмент туловища змейки - сферу зелёного цвета, после "головы"
        # self.segment_entities = [Entity(model='sphere', color=color.green, position=self.segment_positions[0])]
        self.segment_entities = []
        # вызов метода по созданию сглаженного сегмента
        self.create_segment(self.segment_positions[0])
        # словарь приращений движений змейки по клавишам WASD по четырём сторонам
        self.directions = {'a': Vec3(-1, 0, 0), 'd': Vec3(1, 0, 0), 'w': Vec3(0, 1, 0), 's': Vec3(0, -1, 0)}
        # зададим начальное приращение движения равное 0
        self.direction = Vec3(0, 0, 0)
        # словарь "разрешений", указывающий в какие стороны можно двигаться
        self.permissions = {'a': 1, 'd': 1, 'w': 1, 's': 1}
        # словарь для "запрета" движения змейки в противоположную сторону и через саму себя
        self.taboo_movement = {'a': 'd', 'd': 'a', 'w': 's', 's': 'w'}
        # скорость змейки и кол-во набранных очков
        self.speed, self.score = 12, 0
        # счётчик кадров
        self.frame_counter = 0

    # учим змейку кушать яблоки
    def add_segment(self):
        self.segment_length += 1
        self.position_length += 1
        self.score += 1
        self.speed = max(self.speed - 1, 5)
        self.create_segment(self.segment_positions[0])

    # метод создания сегмента
    def create_segment(self, position):
        entity = Entity(position=position)
        Entity(model='sphere', color=color.green, position=position).add_script(
            SmoothFollow(speed=12, target=entity, offset=(0, 0, 0))
        )
        # добавим в список сегментов всего лишь один объект,
        # так как другой будет следовать за ним
        self.segment_entities.insert(0, entity)

    # запуск змейки
    def run(self):
        # увеличиваем счётчик кадров на 1
        self.frame_counter += 1
        # когда счётчик кадров будет кратен скорости змейки
        if not self.frame_counter % self.speed:
            self.control()
            # добавляем приращение координат в список приращений сегментов
            self.segment_positions.append(self.segment_positions[-1] + self.direction)
            # производим срез данного списка по длине змейки
            self.segment_positions = self.segment_positions[-self.segment_length:]
            # из списка координат присваиваем новые положения сегментам змейки
            for segment, segment_position in zip(self.segment_entities, self.segment_positions):
                segment.position = segment_position

    # управление змейкой
    def control(self):
        for key in 'wasd':
            # если клавиши нажаты, и есть разрешение двигаться в направлении
            if held_keys[key] and self.permissions[key]:
                self.direction = self.directions[key]
                # вносим разрешение двигаться в словарь
                self.permissions = dict.fromkeys(self.permissions, 1)
                # вносим запрет на движение в противоположном направлении
                self.permissions[self.taboo_movement[key]] = 0
                break
