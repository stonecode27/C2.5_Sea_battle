class Exceptions(Exception):  # Game's Exceptions inherited from build-in class Exception
    pass


class BoardOutException(Exceptions):  # Exception for shoots out of board
    def __str__(self):
        return "Вы стреляете за пределы морского горизонта!"


class BoardUsedException(Exceptions):  # Exception for shoots in same cell
    def __str__(self):
        return "Снаряд уже был отправлен в эти координаты!"


class BoardWrongShipException(Exceptions):  # Exception for correct ships placement
    pass


class Dot:  # Dots on the board
    def __init__(self, x, y):  # coordinates of dots
        self.x = x
        self.y = y

    def __eq__(self, other):  # for correct dots equaling
        return self.x == other.x and self.y == other.y

    def __repr__(self):  # for correct str represent of instances in containers (such as list)
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, length, bow, orientation):
        self.len = length
        self.bow = bow
        self.o = orientation  # 0 for horizontal, 1 for vertical
        self.hp = length  # health points of the ship

    def ship_dots(self):

        s_dots = []

        for i in range(self.len):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i
                s_dots.append(Dot(cur_x, self.bow.y))

            elif self.o == 1:
                cur_y += i
                s_dots.append(Dot(self.bow.x, cur_y))

        return s_dots

# Самый важный класс во внутренней логике — класс Board — игровая доска. Доска описывается параметрами:
#
# - Двумерный список, в котором хранятся состояния каждой из клеток.
# - Список кораблей доски.
# - Параметр hid типа bool — информация о том, нужно ли скрывать корабли на доске (для вывода доски врага) или нет (для своей доски).
# - Количество живых кораблей на доске.
#
# И имеет методы:
#
# Метод add_ship, который ставит корабль на доску (если ставить не получается, выбрасываем исключения).
# Метод contour, который обводит корабль по контуру. Он будет полезен и в ходе самой игры, и в при расстановке кораблей
#     (помечает соседние точки, где корабля по правилам быть не может).
# Метод, который выводит доску в консоль в зависимости от параметра hid.
# Метод out, который для точки (объекта класса Dot) возвращает True,
#     если точка выходит за пределы поля, и False, если не выходит.
# Метод shot, который делает выстрел по доске (если есть попытка выстрелить за пределы и в использованную точку,
#     нужно выбрасывать исключения).

class Board:
    def __init__(self, size= 6, hid=False):
        self.size = size
        self.hid = hid

        self.m = [["0"] * size for i in range(size)]  # matrix for current condition of the board
        self.alive = 9  # number of alive ships

    def __str__(self):
        bg = ""  # bg as battleground (field) representation
        bg += "  | 1 | 2 | 3 | 4 | 5 | 6 |"

        for item in enumerate(self.m):
            bg += f"\n{item[0]+1} | " + " | ".join(item[1]) + " |"

        if self.hid:
            bg = bg.replace("0", "₪")
        return bg

