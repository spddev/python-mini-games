from ursina import *
# работа с 3D-объектами
from ursina.prefabs.first_person_controller import FirstPersonController

# основное окно
app = Ursina()

# импорт текстуры травы
grass_texture = load_texture('assets/grass.png')
# импорт текстуры неба
sky_texture = load_texture('assets/sky.png')
# импорт текстуры грязи
dirt_texture = load_texture('assets/dirt.png')
# импорт текстуры дерева
oak_texture = load_texture('assets/oak.png')
# импорт текстуры песка
sand_texture = load_texture('assets/send.png')
# импорт текстуры досок
wood_texture = load_texture('assets/wood.png')
# импорт текстуры камня
stone_texture = load_texture('assets/stone.png')
# текстура по умолчанию
current_texture = grass_texture


# функция обновления кадра(фрейма)
def update():
    global current_texture
    # по нажатию клавиш строим определённый блок
    # если на клавиатуре нажата цифра 1, то добавляем блок травы
    if held_keys['1']:
        current_texture = grass_texture

    if held_keys['2']:
        current_texture = dirt_texture

    if held_keys['3']:
        current_texture = oak_texture

    if held_keys['4']:
        current_texture = sand_texture

    if held_keys['5']:
        current_texture = stone_texture

    if held_keys['6']:
        current_texture = wood_texture

    # запуск анимации руки по нажатию левой/правой кнопки мыши
    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.active()
    else:
        hand.passive()


# класс для отображения неба
class Sky(Entity):
    # создание UV-сферы
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            # размер
            scale=150,
            texture=sky_texture,
            double_sided=True  # Для "зацикливания" сферы
        )


# класс для анимации руки
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='cube',
            scale=(0.2, 0.3),
            color=color.white,
            rotation=Vec3(150, -10, 0),
            position=Vec2(0.4, -0.4)
        )

    # Функции анимации движения руки
    def active(self):
        self.position = Vec2(0.1, -0.5)
        self.rotation = Vec3(90, -10, 0)

    def passive(self):
        self.rotation = Vec3(150, -10, 0),
        self.position = Vec2(0.4, -0.4)


# класс для работы с 3D-объектами
class Voxel(Button):
    # инициализация класса
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=.5,
            texture='white_cube',
            color=color.color(0, 0, 255),
            highlight_color=color.lime  # подсветка при наведении мыши
        )

    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=.5,
            texture=texture,
            color=color.color(0, 0, 255),
            highlight_color=color.lime  # подсветка при наведении мыши
        )

    # обработка реакции на клавиатуру и мышь
    def input(self, key):
        if self.hovered:
            # если нажата правая кнопка мыши
            if key == 'right mouse down':
                # устанавливаем новый блок там, куда указывает мышь
                voxel = Voxel(position=self.position + mouse.normal,
                              texture=current_texture)
            # если нажата левая кнопка мыши
            if key == 'left mouse down':
                # уничтожаем блок там, куда указывает мышь
                destroy(self)


# генерация ландшафта
# 1 способ - область 15 х 15
for z in range(15):
    for x in range(15):
        voxel = Voxel((x, 0, z))

# 2 способ
# for z in range(8):
#     for x in range(8):
#         for y in range(8):
#             voxel = Voxel((x, z, y))
# отображаем игрока в качестве вида от первого лица
player = FirstPersonController()
# отображаем сферу
sky = Sky()
# отображаем руку
hand = Hand()
# запуск
app.run()
