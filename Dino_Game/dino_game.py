from ursina import *
import random as r
from ursina import curve

# основное окно Ursina
app = Ursina()
# задаём белый цвет фона основного окна Ursina
window.color = color.white

# добавляем динозаврика
dino = Animation("assets/dino.gif",
                 collider="box",
                 scale=(1, 1, 1),
                 x=-5)
# добавляем дорогу, по которой будет бегать динозаврик
ground1 = Entity(
    model="quad",
    texture="assets/ground.png",
    scale=(50, 0.5, 10),
    z=1
)
ground2 = duplicate(ground1, x=50)
pair = [ground1, ground2]

# добавляем преграды на пути динозаврика - кактусы
cactus = Entity(
    model="quad",
    texture="assets/cactus.png",
    collider="box",
    scale=(0.8, 1, 0.8),
    x=20
)
cactuses = []


# функция создания новых кактусов
def NewCactus():
    new = duplicate(cactus, x=10 + r.randint(0, 5))
    cactuses.append(new)
    invoke(NewCactus, delay=2)  # появление новых препятствий - кактусов


NewCactus()

# подсчёт заработанных очков, которые будут выводиться на главный экран
label = Text(text=f"Очки: {0}", color=color.black, position=(-0.6, 0.4))
points = 0


# основные механики игры
def update():
    global points
    # увеличение счётчика очков и отображение обновлённой информации на главном экране
    points += 1
    label.text = f"Очки: {points}"
    # механика дорожки для динозаврика
    for ground in pair:
        ground.x -= 6 * time.dt
        if ground.x < -35:
            ground.x += 100
    for c in cactuses:
        c.x -= 6 * time.dt


# прыжок динозаврика по клавише "Пробел" на клавиатуре
def input(key):
    if key == "space":
        if dino.y < 0.01:
            dino.animate_y(2, duration=0.4, curve=curve.out_sine)
            dino.animate_y(0, duration=0.4, delay=0.4, curve=curve.in_sine)


# настройки камеры
# ортографическая проекция камеры
camera.orthographic = True
# радиус видимости камеры
camera.fov = 10
# запуск
app.run()
