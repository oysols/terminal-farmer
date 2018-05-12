#!/usr/bin/env python3
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
import random
import time


class Seed():
    pass

class Money():
    pass

class Person():
    def __init__(self, world):
        self.y = 10
        self.x = 4
        self.symbol = "@"
        self.world = world
        self.inventory = [Seed() for i in range(10)]

    def count_inventory(self, inv_type):
        return len([item for item in self.inventory if isinstance(item, inv_type)])

    def move(self, y, x):
        new_y = self.y + y
        new_x = self.x + x
        if self.world[new_x][new_y] == "#":
            return
        self.y = new_y
        self.x = new_x

class Farmland():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.growth = 0

    @property
    def symbol(self):
        if self.growth > 6:
            return "|"
        elif self.growth > 3:
            return ":"
        else:
            return "."

    def pick_up(self):
        if self.growth > 6:
            items = [Money(), Seed()]
            if prob(0.5):
                items += [Seed()]
            return items
        elif prob(0.5):
            return [Seed()]
        else:
            return []

    def tick(self):
        if self.growth < 7 and prob(0.1):
            self.growth += 1

def prob(probability):
    return True if random.random() < probability else False

def create_world(y, x):
    # !world is reversed: world[x][y]
    world = []
    world.append(["#" for i in range(x)])
    for i in range(y - 2):
        world.append(["#"] + [" " for i in range(x - 2)] + ["#"])
    world.append(["#" for i in range(x)])
    return world

def print_world(win, world, person, objects):
    for i, line in enumerate(world[:-1]):
        win.addnstr(i, 0, "".join(line), 60)
    for i, char in enumerate(world[-1]):
        win.insch(len(world)-1, i, char)
    for obj in objects:
        win.addstr(obj.x, obj.y, obj.symbol, curses.color_pair(1))
    win.addch(person.x, person.y, person.symbol)

def get_obj_at_coord(objects, y, x):
    for obj in objects:
        if obj.y == y and obj.x == x:
            return obj
    return None

def main(stdscr):
    WIN_Y = 15
    WIN_X = 30
    win = stdscr.subwin(WIN_Y, WIN_X, 0, 0)
    win.keypad(True)  # catch keypad
    curses.noecho()  # do not echo keys
    curses.curs_set(0)  # do not display cursor
    win.timeout(300)  # timeout getch
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Initialize color

    world = create_world(WIN_Y, WIN_X)
    objects = []
    person = Person(world)
    tick_timer = time.time()


    while True:
        # Draw screen
        win.erase()
        print_world(win, world, person, objects)
        win.border(0)
        stdscr.addstr(0, 2, ' TERMINAL FARMER ')
        stdscr.addstr(1, WIN_X + 2, 'Money: {} '.format(person.count_inventory(Money)))
        stdscr.addstr(2, WIN_X + 2, 'Seeds: {} '.format(person.count_inventory(Seed)))
        stdscr.addstr(6, WIN_X + 2, 'Move with arrow keys')
        stdscr.addstr(7, WIN_X + 2, '1. Press [.] to sow seeds')
        stdscr.addstr(8, WIN_X + 2, '2. Press [space] to reap')
        stdscr.addstr(9, WIN_X + 2, '3. Profit!')
        stdscr.addstr(13, WIN_X + 2, '              [q] to quit')
        stdscr.refresh()

        # Listen for keys
        key = win.getch()

        # Move player
        if key == KEY_UP:
            person.move(0, -1)
        elif key == KEY_DOWN:
            person.move(0, 1)
        elif key == KEY_LEFT:
            person.move(-1, 0)
        elif key == KEY_RIGHT:
            person.move(1, 0)

        # Sow
        elif key == ord("."):
            if not get_obj_at_coord(objects, person.y, person.x):
                for item in person.inventory:
                    if isinstance(item, Seed):
                        objects.append(Farmland(person.x, person.y))
                        person.inventory.remove(item)
                        break

        # Reap
        elif key == ord(" "):
            obj = get_obj_at_coord(objects, person.y, person.x)
            if isinstance(obj, Farmland):
                person.inventory += obj.pick_up()
                objects.remove(obj)

        # Quit
        elif key == ord("q"):
            break

        # Tick world
        if time.time() - tick_timer > 1:
            tick_timer += 1
            for obj in objects:
                obj.tick()


if __name__ == "__main__":
    curses.wrapper(main)
