from __future__ import annotations

from pathlib import Path
from typing import Iterator
import random
import datetime
import os
import termcolor

MIN_OFFSET = 3
OFFSET_PROPORTION = 3

PATH_CLASSES = Path('src/names')

DEFAULT_GENDER = 'C'

GENDER_TO_COLOUR = {
    'M' : 'blue',
    'F' : 'magenta',
    DEFAULT_GENDER : 'white'
}

class Student:
    name: str
    gender: str
    clique: str

    def __init__(self: Student, name: str, gender: str=DEFAULT_GENDER, clique: str=''):
        self.name, self.gender, self.clique = name, gender, clique

    def __repr__(self: Student) -> str:
        return self.name

class Classroom:
    layouts: list[ClassroomLayout]

    def __init__(self: Classroom):
        self.layouts = []

    @staticmethod
    def from_grid(grid: list[list[bool]]) -> Classroom:
        layout = PotentialLayout(grid)
        room = Classroom()
        room.layouts.append(layout)
        return room

class ClassroomLayout:
    grid: list[list]

    def __init__(self: ClassroomLayout, grid: list[list]=[[]]):
        self.grid = grid
    
    def __getitem__(self: ClassroomLayout, idx: int) -> object:
        return self.grid[idx]
    
    def __setitem__(self: ClassroomLayout, idx: int, val: object):
        self.grid[idx] = val

    def __iter__(self: ClassroomLayout) -> Iterator[list]:
        return self.grid.__iter__()

    @staticmethod
    def from_dimensions(n_rows: int, n_cols: int) -> BlankLayout:
        grid = []

        for _ in range(n_rows):
            new_row = list("" for _ in range(n_cols))
            grid.append(new_row)
        
        return BlankLayout(grid)
    
    def get_n_rows(self: ClassroomLayout) -> int:
        return len(self.grid)
    
    def get_n_cols(self: ClassroomLayout) -> int:
        return len(self.grid[0])
    
    def make_blank_layout(self: ClassroomLayout) -> BlankLayout:
        return BlankLayout.from_layout(self)

class BlankLayout(ClassroomLayout):

    @staticmethod
    def from_layout(layout: ClassroomLayout) -> BlankLayout:
        return ClassroomLayout.from_dimensions(layout.get_n_rows(), layout.get_n_cols())

class PotentialLayout(ClassroomLayout):
    grid: list[list[bool]]

    def get_n_seats(self: ClassroomLayout) -> int:
        return sum(sum(row) for row in self)
    
    def get_seats(self: ClassroomLayout) -> set[tuple[bool]]:
        """
        Return a set of tuples of [row, col] for available seats in this layout.
        """
        positions = set()
        for (i_row, row) in enumerate(self):
            for (i_col, col) in enumerate(row):
                if col:
                    positions.add((i_row, i_col))
        return positions

class PlannedLayout(ClassroomLayout):
    grid: list[list[str|Student]]

class SeatingPlan:
    c: Class
    layout: PlannedLayout

    def __init__(self: SeatingPlan, c: Class, layout: PlannedLayout):
        self.c, self.layout = c, layout
    
    def __str__(self: SeatingPlan):
        w_col = Utilities.get_longest_length(s.name for s in self.c.students)
        w_row = w_col * self.layout.get_n_cols()
        empty = ' ' * w_col

        s = '\n' + Utilities.format_now().center(w_row) + '\n\n'
        s += 'Front'.center(w_row) + '\n\n'

        for row in self.layout:
            line = ""

            for col in row:

                # Students are non-blank
                if col:
                    name = col.name
                    gender = col.gender
                    colour = GENDER_TO_COLOUR[gender]
                    line += termcolor.colored(name.center(w_col), colour)

                else:
                    line += empty
            
            s += line + '\n'

        s += '\n' + 'Back'.center(w_row) + '\n'
        return s
        
class Class:
    rooms: list[Classroom]
    students: list[Student]

    def __init__(self: Class):
        self.rooms = []
        self.students = []

class SeatingPlanner:
    c: Class
    name_length: int

    def __init__(self: SeatingPlanner):
        self.c = None
        self.name_length = 0

    @staticmethod
    def parse_data(path: Path) -> tuple[list[str], dict[str, str], list[list[bool]]]:
        """
        Return:
        1. A list of names
        2. A dictionary of name to gender
        3. A list of lists of booleans representing placeable grid positions
        """

        c = Class()
        grid = []

        with open(path, 'r', encoding='utf-8') as f:
            state = 0
            for line in filter(None, (line.strip() for line in f.readlines())):

                if '::' in line:
                    k, _ = line.split('::')
                    
                    if k == 'names':
                        state = 1
                    elif k == 'grid':
                        state = 2
                else:
                    if state == 1:
                        name, *parts = line.split(':')

                        if parts:
                            gender, *parts = parts
                        else:
                            gender = DEFAULT_GENDER

                        c.students.append(Student(name, gender))

                    elif state == 2:
                        ints = list(bool(int(c)) for c in line.replace(' ', ''))
                        grid.append(ints)
        
        c.rooms.append(Classroom.from_grid(grid))
        return c
    
    def get_layout(self: SeatingPlanner) -> PotentialLayout:
        """
        @TODO Temporary means of getting the single layout prévu at this point.
        """
        return self.c.rooms[0].layouts[0]

    def make_plan(self: SeatingPlanner) -> SeatingPlan:
        layout = self.get_layout()
        seats = list(layout.get_seats())
        random.shuffle(seats)

        layout = layout.make_blank_layout()

        for (s, (row, col)) in zip(self.c.students, seats):
            layout[row][col] = s

        return SeatingPlan(self.c, layout)
    
    def make_class_from_file(self: SeatingPlanner):
        path = Utilities.choose_names_file()
        self.c = SeatingPlanner.parse_data(path)
        self.name_length = Utilities.get_longest_length(s.name for s in self.c.students)

    @staticmethod
    def run():
        sp = SeatingPlanner()
        sp.make_class_from_file()

        choice = ''
        while choice != 'Q':
            Utilities.clear_terminal()
            print(sp.make_plan())
            choice = input('Enter to rerun or Q to quit: ').upper().strip()

class Utilities:

    @staticmethod
    def get_longest_length(items: list) -> int:
        m = 0
        for item in items:
            if len(item) > m:
                m = len(item)
        return m

    @staticmethod
    def clear_terminal():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def format_now() -> str:
        now = datetime.datetime.now()

        # Seems to be the only pre-3.13 way to get no zero padding
        d = now.strftime('%d').lstrip('0')
        return now.strftime('%A, %B [], %Y').replace('[]', d)

    @staticmethod
    def choose_names_file() -> Path:
        choices = {}

        paths = PATH_CLASSES.glob('*.txt')
        for path in paths:
            choices[path.stem] = path
        
        if len(choices) == 1:
            return list(choices.values()[0])
        
        else:
            print('Choose names file: ')
            print()
            for (i, choice) in enumerate(sorted(choices, reverse=True)):
                n = str(i + 1).zfill(len(str(len(choices))))
                print(f'[{i + 1}] {choice}')
            print()
            n = int(input('Selection [#]: '))

            return choices[sorted(choices, reverse=True)[n - 1]]

if __name__ == '__main__':
    SeatingPlanner.run()
