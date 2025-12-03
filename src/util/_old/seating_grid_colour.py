from pathlib import Path
import random
import datetime
import os
import termcolor
import string

MIN_OFFSET = 3
OFFSET_PROPORTION = 3
DEFAULT_GENDER = 'C'

GENDER_TO_COLOUR = {
    'M' : 'blue',
    'F' : 'magenta',
    DEFAULT_GENDER : 'white'
}

def choose_names_file() -> Path:
    choices = {}

    paths = Path('src/names').glob('*.txt')
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

def parse_data(path: Path) -> tuple[list[str], dict[str, str], list[list[bool]]]:
    """
    Return:
      1. A list of names
      2. A dictionary of name to gender
      3. A list of lists of booleans representing placeable grid positions
    """
    names = []
    name_to_gender = {}
    grid = []

    with open(path, 'r', encoding='utf-8') as f:
        state = 0
        for line in filter(None, (line.strip() for line in f.readlines())):

            if '::' in line:
                k, v = line.split('::')
                
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

                    names.append(name)
                    name_to_gender[name] = gender

                elif state == 2:
                    ints = list(bool(int(c)) for c in line.replace(' ', ''))
                    grid.append(ints)

    return names, name_to_gender, grid

def format_now() -> str:
    now = datetime.datetime.now()

    # Seems to be the only pre-3.13 way to get no zero padding
    d = now.strftime('%d').lstrip('0')
    return now.strftime('%A, %B [], %Y').replace('[]', d)

def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def get_longest_name_length(names: list[str]) -> int:
    return len(max(names, key=len))

def get_longest_name_length_from_tiers(tiers: list[list[str]]) -> int:
    return len(max((name for t in tiers for name in t), key=len))

def get_offset(tiers: list[list[str]]) -> int:
    length = get_longest_name_length_from_tiers(tiers)
    return max(MIN_OFFSET, length // OFFSET_PROPORTION)

def get_row_width(tiers: list[list[str]]) -> int:
    w_names = get_longest_name_length_from_tiers(tiers) * 2
    w_offsets = (get_offset(tiers) * sum(range(len(tiers) - 1)))
    return w_names + w_offsets + MIN_OFFSET

    # return MIN_OFFSET + (get_longest_name_length(tiers) * 2) + (get_offset(tiers) * sum(range(len(tiers) - 1)))

def get_start_offset(base: int, i: int, n: int, reverse: bool=False) -> int:
    if not reverse:
        return base * (n - (i + 1))
    else:
        return base * (i + 1)

def get_grid_positions(grid: list[list[int]]) -> set[tuple[bool]]:
    positions = set()
    for (i_row, row) in enumerate(grid):
        for (i_col, col) in enumerate(row):
            if col:
                positions.add((i_row, i_col))
    return positions

def create_name_grid(names: list[str], name_to_gender: dict[str, str], grid: tuple[list[str]]) -> list[list]:
    positions = list(get_grid_positions(grid))
    random.shuffle(positions)

    length = get_longest_name_length(names)
    empty = " " * length

    name_grid = []
    for row in grid:
        new_row = list(empty for _ in row)
        name_grid.append(new_row)

    for (name, (row, col)) in zip(names, positions):
        colour = GENDER_TO_COLOUR[name_to_gender[name]]
        name_grid[row][col] = termcolor.colored(name.center(length), colour)

    return name_grid

def print_name_grid(name_grid: list[list[str]]) -> None:
    printable = set(string.printable)

    # lol. improve by saving length somewhere... maybe class-ify this
    w = len(list(c for c in name_grid[0][0] if c in printable)) * len(name_grid[0])

    print()
    print('Front'.center(w))
    print()

    for row in name_grid:
        print(' '.join(row))
        print()
    
    print('Back'.center(w))
    print()

def run() -> None:
    path = choose_names_file()
    names, name_to_gender, grid = parse_data(path)

    choice = ''
    while choice != 'Q':
        clear()

        random.shuffle(names)
        name_grid = create_name_grid(names, name_to_gender, grid)
        print_name_grid(name_grid)

        choice = input('Enter to rerun or Q to quit: ').upper().strip()

if __name__ == '__main__':
    run()
