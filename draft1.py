from random import randint
# Inner logic of the game

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


class Ship:  # A ships on the field
    def __init__(self, lenght, bow, orientation):
        self.len = lenght  # length of the ship
        self.bow = bow  # coordinates of the bow of the ship
        self.orient = orientation  # horizontal or vertical (0 or 1)
        self.hp = lenght  # current health points of the ship

    @property
    def dots(self):  # this class returns list of ship's dots
        s_dots = []  # list for ship's dots
        for i in range(self.len):  # cycle for appending s_dots[]
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.orient == 0:
                cur_x += i

            elif self.orient == 1:  # There's no exceptions for .orient cause class Ship belongs to inner logic
                cur_y += i

            s_dots.append(Dot(cur_x, cur_y))  # filling s_dots

        return s_dots

    def shooten(self, shot):  # class for True or False if someone hits a ship
        return shot in self.dots


class Board:
    def __init__(self, size=6, hide=False):
        self.size = size
        self.hide = hide  # type <bool>. If needs to hide a board (for printing enemy's board) or not (for player's)

        self.knocked = 0  # number of knocked down ships

        self.field = [["0"] * size for i in range(size)]  # matrix for current condition of the board

        self.busy = []  # for busy cells
        self.ships = []  # all ships on board

    def __str__(self):
        bg = ""  # bg as battleground (field) representation
        bg += "  | 1 | 2 | 3 | 4 | 5 | 6 |"

        for item in enumerate(self.field):
            bg += f"\n{item[0]+1} | " + " | ".join(item[1]) + " |"

        if self.hide:
            bg = bg.replace("0", "■")
        return bg

    def out_of_board(self, d):  # Is dot in range?
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        around = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]  # all points around any dot of the ship
        for d in ship.dots:   # iterating ship dots
            for dx, dy in around:  # iterating coordinates in around
                cur = Dot(d.x + dx, d.y + dy)  # getting dots around ship dots
                if not(self.out_of_board(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out_of_board(d) or d in self.busy:  # if dot is not in range of board and busy
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out_of_board(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)  # now this cell is busy

        for ship in self.ships:
            if ship.shooten(d):
                ship.hp -= 1
                self.field[d.x][d.y] = "X"
                if ship.hp == 0:
                    self.knocked += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль подбит!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []  # refreshing busy list


# Outer logic of the game


class Player:  # for AI and User
    def __init__(self, selfboard, othersboard):
        self.sb = selfboard
        self.ob = othersboard

    def ask(self):  # asks player where he is shooting
        pass

    def turn(self):  # makes a turn in game. Returns True if player needs one more turn
        while True:
            try:
                target = self.ask()
                repeat = self.ob.shot(target)
                return repeat
            except Exceptions as e:
                print(e)


class Ai(Player):
    def ask(self):  # redefining method ask for AI
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):  # redefining method ask for User
        while True:
            coords = input("Ваш ход: ").split()

            if len(coords) != 2:
                print("Такой точки нет!")
                continue

            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Такой точки нет!")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


# Main class - Game
class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = Ai(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
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

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.sb)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ob)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.sb.turn()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ob.turn()
            if repeat:
                num -= 1

            if self.ob.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.sb.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()


