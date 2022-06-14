from ursina import *
import random

# создание окна Ursina
app = Ursina()
# настройка камеры
camera.ortographic = True
camera.fov = 40

# создание объекта "автомобиль"
car = Entity(
    model='quad',
    texture='assets/car2.png',
    collider='box',
    scale=(2, 1),
    rotation_z=-90
)
# создание объекта "дорога"
road1 = Entity(
    model='quad',
    texture='assets/roadnew.png',
    collider='box',
    scale=15,
    z=1
)
# создание второго объекта "дорога" путём дублирования первого объекта "дорога"
road2 = duplicate(road1, y=15)
# список частей дороги
pair = [road1, road2]

# основная часть
# добавление игровых противников NPC
enemies = []


def newEnemy():
    val = random.uniform(-2, 2)
    new = duplicate(
        car,
        texture='assets/car3.png',
        x=2 * val,
        y=25,
        color=color.random_color(),
        rotation_z=
        90 if val < 0
        else -90
    )
    # добавляем созданный объект "автомобиль" в список игровых противников
    enemies.append(new)
    # отрисовываем объект на экране через временной интервал задержки
    invoke(newEnemy, delay=0.5)


newEnemy()


# движение автомобиля влево и вправо
def update():
    car.x -= held_keys['a'] * 5 * time.dt
    car.x += held_keys['d'] * 5 * time.dt

    # иллюзия движения дороги
    for road in pair:
        road.y -= 6 * time.dt
        if road.y < -15:
            road.y += 30
    for enemy in enemies:
        if enemy.x < 0:
            enemy.y -= 10 * time.dt
        else:
            enemy.y -= 5 * time.dt
        # если координата y противника станет меньше -10,
        # то противник скрывается с экрана
        if enemy.y < -10:
            enemies.remove(enemy)
            destroy(enemy)
    # анализ столкновений "автомобиля игрока" с "автомобилями игровых противников"
    if car.intersects().hit:
        car.shake()


# запуск приложения
app.run()
