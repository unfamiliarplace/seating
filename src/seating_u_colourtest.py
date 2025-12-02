from pathlib import Path
import random
import datetime
import os
import termcolor

MIN_OFFSET = 3
OFFSET_PROPORTION = 3

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

def parse_data(path: Path) -> list[list[tuple[str]], list[list[bool]]]:
    names = []
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
                    names.append(line.split(':'))

                elif state == 2:
                    ints = list(bool(int(c)) for c in line.replace(' ', ''))
                    grid.append(ints)

    return names, grid

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

def create_name_grid(names: list[str], grid: tuple[list[str]]) -> list[list]:
    positions = list(get_grid_positions(grid))
    random.shuffle(positions)

    length = get_longest_name_length(names)
    empty = " " * length

    name_grid = []
    for row in grid:
        new_row = list(empty for _ in row)
        name_grid.append(new_row)

    for (name, (row, col)) in zip(names, positions):
        # colour = 'blue' if name[1] == 'M' else 'pink'
        # name_grid[row][col] = lambda: termcolor.colored(name, colour)
        name_grid[row][col] = name[0].center(length)

    return name_grid

def print_name_grid(name_grid: list[list[str]]) -> None:

    w = len(name_grid[0][0]) * len(name_grid[0])

    print()
    print('Front'.center(w))
    print()

    for row in name_grid:
        print(' '.join(row))
        print()
    
    print('Back'.center(w))
    print()

def print_tiers(tiers: list[list[str]], reverse: bool=False) -> None:
    w = get_row_width(tiers)
    base_offset = get_offset(tiers)

    for (i, tier) in enumerate(tiers):
        if len(tier) == 1:
            print(tier[0].center(w))

        else:
            L, R = tier

            start_offset = get_start_offset(base_offset, i, len(tiers), reverse)
            mid_offset = w - len(L) - len(R) - (start_offset * 2)
            
            print(' ' * start_offset, end='')
            print(L, end='')
            print(' ' * mid_offset, end='')
            print(R)

def print_back_at_top(tiers: list[list[str]]) -> None:

    w = get_row_width(tiers)

    print()
    print(format_now().center(w))
    print()
    print('Back'.center(w))
    print()

    print_tiers(tiers, reverse=False)
            
    print()
    print('Front'.center(w))
    print()

def print_front_at_top(tiers: list[list[str]]) -> None:

    w = get_row_width(tiers)

    print()
    print(format_now().center(w))
    print()
    print('Front'.center(w))
    print()

    # Swap a possible lone name from start to end
    tiers[0], tiers[-1] = tiers[-1], tiers[0]
    print_tiers(tiers, reverse=True)
            
    print()
    print('Back'.center(w))
    print()

def run() -> None:
    path = choose_names_file()
    names, grid = parse_data(path)

    choice = ''
    while choice != 'Q':
        clear()

        random.shuffle(names)
        name_grid = create_name_grid(names, grid)
        print_name_grid(name_grid)

        choice = input('Enter to rerun or Q to quit: ').upper().strip()

if __name__ == '__main__':
    run()
