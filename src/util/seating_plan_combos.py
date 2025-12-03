from itertools import permutations as perms
import time
import math

for N in range(2, 15):
    start = time.time()

    base = set()
    for i in range(1, N):
        base.add(frozenset({i, i + 1}))

    n_repeats = 0
    for p in perms(range(1, N + 1)):
        for i in range(len(p) - 1):
            if {p[i], p[i + 1]} in base:
                n_repeats += 1
                break
    
    end = time.time()

    pct = (n_repeats / math.perm(N)) * 100

    print(f'N = {N:>2} | {end - start:.5f} seconds')
    print(f'{n_repeats} / {math.perm(N)}'.ljust(30), ' | ', f'{pct:.2f}%'.ljust(6))
    print()
