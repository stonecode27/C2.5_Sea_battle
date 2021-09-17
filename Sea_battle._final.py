from random import randint
from time import sleep

class Exceptions(Exception):
    pass


class BoardOutException(Exceptions):
    def __str__(self):
        return "Вы пытаетесь сделать выстрел за пределы морского горизонта!"


class BoardUsedException(Exceptions):
    def __str__(self):
        return "Снаряд уже был отправлен по этим координатам!"


class BoardWrongShipException(Exceptions):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.hp = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.knocked = 0
        self.field = [["O"] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        around = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in around:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        bg = ""
        bg += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for item in enumerate(self.field):
            bg += f"\n{item[0] + 1} | " + " | ".join(item[1]) + " |"

        if self.hid:
            bg = bg.replace("■", "O")
        return bg

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.hp -= 1
                self.field[d.x][d.y] = "X"
                if ship.hp == 0:
                    self.knocked += 1
                    self.contour(ship, verb=True)
                    print("Корабль потоплен!")
                    sleep(3)
                    return False
                else:
                    print("Корабль подбит!")
                    sleep(3)
                    return True

        self.field[d.x][d.y] = "."
        print("Промах!")
        sleep(3)
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def turn(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except Exceptions as e:
                print(e)


class Ai(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Выстрел противника: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            coords = input("Ваш ход: ").split()

            if len(coords) != 2:
                print("Таких координат не существует!")
                continue

            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Таких координат не существует!")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        user_board = self.random_board()
        comp_board = self.random_board()
        comp_board.hid = True

        self.ai = Ai(comp_board, user_board)
        self.us = User(user_board, comp_board)

    def random_ships(self):
        types_of_ships = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in types_of_ships:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.random_ships()
        return board


    def greet(self):
        print("""

╔════════════════════╗
║ Добро пожаловать в ║
║ игру "Морской бой" ║
╚════════════════════╝

        """)

        sleep(3)

        print("""

╔════════════════════╗
║ Формат ввода:      ║
║ x y                ║
║ x - номер строки   ║
║ y - номер столбца  ║
║ Пример: 1 2        ║
╚════════════════════╝

        """)

        sleep(5)

    def loop(self):
        num = 0
        while True:
            print("ﬨ" * 28)
            print("Доска пользователя:")
            print(self.us.board)
            print("ﬨ" * 28)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("ﬨ" * 28)
                print("Очередь игрока!")
                repeat = self.us.turn()
            else:
                print("ﬨ" * 28)
                print("Очередь компьютера!")
                repeat = self.ai.turn()
            if repeat:
                num -= 1

            if self.ai.board.knocked == 7:
                print("ﬨ" * 28)
                print("Победа!")
                break

            if self.us.board.knocked == 7:
                print("ﬨ" * 28)
                print("Поражение!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


game = Game()
game.start()