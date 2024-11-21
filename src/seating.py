from pathlib import Path
import random
import datetime
import os

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

def get_names(path: Path) -> list[str]:
    names = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in filter(None, (line.strip() for line in f.readlines())):
            names.append(line)
    return names

def get_tiers(names: list[str]) -> list[list[str]]:
    tiers = []

    if len(names) % 2:
        tiers.append([names[0]])
        names = names[1:]
    else:
        tiers.append([names[0], names[1]])
        names = names[2:]

    while names:
        tiers.append([names[0], names[1]])
        names = names[2:]

    return tiers

def format_now() -> str:
    now = datetime.datetime.now()

    # Seems to be the only pre-3.13 way to get no zero padding
    d = now.strftime('%d').lstrip('0')
    return now.strftime('%A, %B [], %Y').replace('[]', d)

def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def get_longest_name_length(tiers: list[list[str]]) -> int:
    return len(max((name for t in tiers for name in t), key=len))

def get_offset(tiers: list[list[str]]) -> int:
    length = get_longest_name_length(tiers)
    return max(MIN_OFFSET, length // OFFSET_PROPORTION)

def get_row_width(tiers: list[list[str]]) -> int:
    return (round(get_longest_name_length(tiers) * 3.5)) + (len(tiers) * (get_offset(tiers)))

def get_start_offset(base: int, i: int, n: int, reverse: bool=False) -> int:
    if not reverse:
        return base * (n - (i + 1))
    else:
        return base * (i + 1)

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
    names = get_names(path)
    random.shuffle(names)
    tiers = get_tiers(names)
    clear()
    print_front_at_top(tiers)

if __name__ == '__main__':
    run()
