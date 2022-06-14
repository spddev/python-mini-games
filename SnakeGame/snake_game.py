import pygame
from random import randrange

# основные настройки
# размеры игрового поля
RES = 800
SIZE = 50
# границы координат x и y
x, y = randrange(SIZE, RES - SIZE, SIZE), randrange(SIZE, RES - SIZE, SIZE)
# границы появления яблок
apple = randrange(SIZE, RES - SIZE, SIZE), randrange(SIZE, RES - SIZE, SIZE)
# длина змейки по умолчанию
length = 1
# отрисовка змейки
snake = [(x, y)]
# смещение координат от изначального положения змейки (по умолчанию)
dx, dy = 0, 0
# частота смены кадров
fps = 60
# Словарь клавиш управления змейкой
dirs = {'W': True, 'S': True, 'A': True, 'D': True, }
# игровые очки
score = 0
# скорость змейки и её изменение
speed_count, snake_speed = 0, 10
# инициализация pygame
pygame.init()
# отображение основного окна
surface = pygame.display.set_mode([RES, RES])
# частота смены кадров
clock = pygame.time.Clock()
# параметры шрифта для отрисовки игровых очков
font_score = pygame.font.SysFont('Arial', 26, bold=True)
# параметры шрифта для отрисовки сообщения об окончании игры
font_end = pygame.font.SysFont('Arial', 66, bold=True)
# фоновое изображение
img = pygame.image.load('img/snake_background.jpg').convert()


# закрытие игры
def close_game():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

# игра
while True:
    surface.blit(img, (0, 0))
    # отрисовка змеи
    [pygame.draw.rect(surface, pygame.Color('green'), (i, j, SIZE - 1, SIZE - 1)) for i, j in snake]
    # отрисовка яблок
    pygame.draw.rect(surface, pygame.Color('red'), (*apple, SIZE, SIZE))

    # отрисовка очков
    render_score = font_score.render(f'ОЧКИ: {score}', 1, pygame.Color('blue'))
    surface.blit(render_score, (5, 5))

    # движение змеи
    speed_count += 1
    if not speed_count % snake_speed:
        x += dx * SIZE
        y += dy * SIZE
        snake.append((x, y))
        snake = snake[-length:]

    # поедание еды
    if snake[-1] == apple:
        apple = randrange(SIZE, RES - SIZE, SIZE), randrange(SIZE, RES - SIZE, SIZE)
        length += 1
        score += 1
        snake_speed -= 1
        snake_speed = max(snake_speed, 4)



    # конец игры
    # x < 0 or x > RES - SIZE or y < 0 or y > RES - SIZE - выход за пределы экрана
    # len(snake) != len(set(snake)) - голова змеи врезается в её хвост
    if x < 0 or x > RES - SIZE or y < 0 or y > RES - SIZE or len(snake) != len(set(snake)):
        while True:
            render_end = font_end.render('КОНЕЦ ИГРЫ', 1, pygame.Color('blue'))
            surface.blit(render_end, (RES // 2 - 200, RES // 3))
            pygame.display.flip()
            close_game()

    pygame.display.flip()
    clock.tick(fps)
    close_game()



    # управление
    key = pygame.key.get_pressed()
    if key[pygame.K_w]:
        if dirs['W']:
            dx, dy = 0, -1
            dirs = {'W': True, 'S': False, 'A': True, 'D': True, }
    elif key[pygame.K_s]:
        if dirs['S']:
            dx, dy = 0, 1
            dirs = {'W': False, 'S': True, 'A': True, 'D': True, }
    elif key[pygame.K_a]:
        if dirs['A']:
            dx, dy = -1, 0
            dirs = {'W': True, 'S': True, 'A': True, 'D': False, }
    elif key[pygame.K_d]:
        if dirs['D']:
            dx, dy = 1, 0
            dirs = {'W': True, 'S': True, 'A': False, 'D': True, }