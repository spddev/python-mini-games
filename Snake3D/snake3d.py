from ursina import *
# импортируем объекты из нового файла
from game_objects import *


# основной класс игры
class Game(Ursina):
    def __init__(self):
        super().__init__()
        # цвет заливки окна
        window.color = color.black
        # установка разрешения полноэкранного режима окна
        window.fullscreen_size = 1920, 1080
        # появление окна в полноэкранном режиме
        window.fullscreen = True
        # освещение для ощущения глубины
        Light(type='ambient', color=(0.5, 0.5, 0.5, 1))
        Light(type='directional', color=(0.5, 0.5, 0.5, 1), direction=(1, 1, 1))
        # размер карты
        self.MAP_SIZE = 20
        self.new_game()
        # установка камеры
        # переносим камеру на половину размера карты по осям x и y,
        # а по оси z отдалим камеру чуть по-дальше
        # 2D-камера
        # camera.position=(self.MAP_SIZE // 2, self.MAP_SIZE // 2, -50)
        # 3D-камера
        camera.position = (self.MAP_SIZE // 2, -20.5, -20)
        camera.rotation_x = -57

    # метод создания карты
    def create_map(self, MAP_SIZE):
        # создаём плоскость карты с началом координат в точке (0, 0, 0)
        Entity(model='quad',
               scale=MAP_SIZE,
               position=(MAP_SIZE // 2, MAP_SIZE // 2, 0),
               color=color.dark_gray)
        # поверх плоскости расположим объект типа сетки белого цвета
        Entity(model=Grid(MAP_SIZE, MAP_SIZE),
               scale=MAP_SIZE,
               position=(MAP_SIZE // 2, MAP_SIZE // 2, -0.01),
               color=color.white)

    # метод загрузки новой игры
    def new_game(self):
        # очистка сцены от всех игровых объектов при запуске новой игры
        scene.clear()
        # создаём карту при создании новой игры
        self.create_map(self.MAP_SIZE)
        # создаём 3D-объект "Яблоко" как сферу красного цвета
        self.apple = Apple(self.MAP_SIZE, model='sphere', color=color.red)
        # создаём экземляр класса "Змейка"
        self.snake = Snake(self.MAP_SIZE)

    # метод анализа ввода клавиш
    def input(self, key):
        # переключение проекции камеры на 2D-вид
        if key == '2':
            camera.rotation_x = 0
            camera.position = (self.MAP_SIZE // 2, self.MAP_SIZE // 2, -50)
        # переключение проекции камеры на 3D-вид
        elif key == '3':
            camera.position = (self.MAP_SIZE // 2, -20.5, -20)
            camera.rotation_x = -57
        super().input(key)

    # метод проверки съеденых яблок
    def check_apple_eaten(self):
        if self.snake.segment_positions[-1] == self.apple.position:
            self.snake.add_segment()
            self.apple.new_position()

    # метод проверки условия окончания игры
    def check_game_over(self):
        snake = self.snake.segment_positions
        # проверка нахождения головы змейки в пределах игрового поля
        # и соответствие длины змейки длине самого списка координат
        if 0 < snake[-1][0] < self.MAP_SIZE and 0 < snake[-1][1] < self.MAP_SIZE and len(snake) == len(set(snake)):
            return
        # выводим на экран сообщение об окончании игры
        print_on_screen('ИГРА ОКОНЧЕНА', position=(-0.7, 0.1), scale=10, duration=1)
        # обнуляем приращение координат движения змейки
        self.snake.direction = Vec3(0, 0, 0)
        # обнуляем словарь разрешений на движение в определённом направлении
        self.snake_permissions = dict.fromkeys(self.snake.permissions, 0)
        # спустя 1 секунду делаем загрузку новой игры
        invoke(self.new_game, delay=1)

    # метод обновления кадра
    def update(self):
        print_on_screen(f'Очки: {self.snake.score}', position=(-0.85, 0.45), scale=3, duration=1 / 20)
        self.check_apple_eaten()
        self.check_game_over()
        self.snake.run()


# функция запуска игры
if __name__ == '__main__':
    game = Game()
    update = game.update
    game.run()
