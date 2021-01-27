# не ждите тут чего то понятного.

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from presenter import FilePresenter

input_path = Path(__file__).parent / 'input.json'
output_path = Path(__file__).parent / 'output.json'
a = json.load(input_path.open())

b = defaultdict(set)
for i in a:
    if i['faculty']:  # иногда пустой
        b[i['faculty']].add(i['group'].lower())

c = defaultdict(set)

for fac, groups in b.items():
    for g in groups:
        _, w, _ = FilePresenter._get_group_wildcard(g)
        c[fac].add(w.split('-')[0])

d = defaultdict(set)
for fac, groups in c.items():
    for g in groups:
        d[g].add(fac)

collision_groups = set([groups for groups, fac in d.items() if len(fac) > 1])

for i in c:
    c[i] = list(
        c[i].difference(collision_groups)
    )

with output_path.open('w') as f:
    json.dump(c, f, ensure_ascii=False)
