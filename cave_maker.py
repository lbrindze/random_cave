import curses
import sys
import time
from random import random

SHIP_CHAR = "x"


class CaveSlice:
    """
    CaveSlice is a single verticle slice of the cave. Put together in series,
    This makes up the entirety of the cave.  It exposes convenience methods
    to raise and lower the ceiling and the floor and also contains the logic
    to prevent these actions from being nonesensicle.
    """

    def __init__(self, max_height, min_opening, ceiling=None, floor=0):
        self.max_height = max_height
        self.min_opening = min_opening
        self.ceiling = max_height - 1
        if ceiling is not None:
            self.ceiling = ceiling
        self.floor = floor
        self.ship_position = None

    def build_slice(self):
        out = []
        out.append("*")
        for i in reversed(range(self.max_height)):
            if i == self.ceiling or i == self.floor:
                out.append("_")
            elif i is self.ship_position:
                out.append(SHIP_CHAR)
            else:
                out.append(" ")

        out.append("*")
        return out

    def _at_min_opening(self):
        return (self.ceiling - self.floor) == self.min_opening

    def raise_ceiling(self):
        if self.ceiling < self.max_height - 1:
            self.ceiling += 1

    def lower_ceiling(self):
        if not self._at_min_opening():
            self.ceiling -= 1

    def raise_floor(self):
        if not self._at_min_opening():
            self.floor += 1

    def lower_floor(self):
        if self.floor > 0:
            self.floor -= 1

    def __str__(self):
        cave_slice = self.build_slice()
        return "\n".join(cave_slice)


class Cave:
    """
    Cave is the primary object that models our 'cave' and is composed
    as a list of CaveSlices.  Cave also implements iterator and provides
    an endless scrolling cave in buffer frames that remove the first most slice
    and appends a new randomly generated slice in each iterator 'step'.
    """

    def __init__(self, max_height=10, width=10, min_opening=3, ship=None):
        self.max_height = max_height
        self.min_opening = min_opening
        self.cave_buffer = [self.init_cave_slice() for _ in range(width)]
        self.ship = ship
        self.key_frame = width // 5

    def init_cave_slice(self):
        return CaveSlice(self.max_height, self.min_opening)

    def __iter__(self):
        return self

    def __next__(self):
        del self.cave_buffer[0]
        last_slice = self.cave_buffer[-1]
        next_slice = CaveSlice(
            last_slice.max_height,
            last_slice.min_opening,
            ceiling=last_slice.ceiling,
            floor=last_slice.floor,
        )

        ceiling = random()
        if ceiling > 0.5:
            next_slice.raise_ceiling()
        else:
            next_slice.lower_ceiling()

        floor = random()
        if floor > 0.5:
            next_slice.raise_floor()
        else:
            next_slice.lower_floor()

        self.cave_buffer.append(next_slice)
        return self

    def __str__(self):
        flipped = [cave_slice.build_slice() for cave_slice in self.cave_buffer]
        out = list(map(list, zip(*flipped)))
        return "\n".join(["".join(line) for line in out])


class Ship:
    def __init__(self, cave):
        self.cave = cave
        self.position = cave.max_height // 2
        self.last_thrust = 0
        self.has_crashed = False

    def thrust(self):
        self.position += 2
        self.last_thrust = 0

    def fall(self):
        if self.has_crashed:
            return

        self.position = self.position - self.last_thrust ** 2
        if self.position < 0:
            self.position = 0
        self.last_thrust += 1

    def plot_position(self):
        frame = self.cave.cave_buffer[self.cave.key_frame]
        frame.ship_position = self.position

    def clear(self):
        frame = self.cave.cave_buffer[self.cave.key_frame - 1]
        frame.ship_position = None

    def crash(self):
        self.has_crashed = True


def main(stdscr, height, length, min_opening):
    curses.noecho()
    curses.cbreak()
    stdscr.nodelay(1)
    cave = Cave(height, length, min_opening)
    ship = Ship(cave)
    while True:
        stdscr.clear()
        if stdscr.getch() == -1:
            ship.fall()
        else:
            ship.thrust()
        ship.plot_position()
        ship.clear()
        stdscr.addstr(str(next(cave)))
        stdscr.refresh()
        time.sleep(0.2)
        if ship.has_crashed:
            sys.exit(0)

    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()


if __name__ == "__main__":
    args = [int(x) for x in sys.argv[1:]]
    curses.wrapper(main, *args)
