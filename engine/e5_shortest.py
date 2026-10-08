"""E5: the fastest possible game from random deals, with every hand and the
stock order known and all players cooperating. Exact by IDA* (shortest.c)."""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
WORK = 10
cfgs = [(2, 7, 4000), (3, 7, 2000), (4, 7, 1000), (2, 3, 4000), (2, 5, 4000), (3, 3, 4000), (3, 5, 2000), (4, 3, 4000), (4, 5, 1000), (5, 7, 400), (6, 7, 200)]
def job(t):
    n, m, g, k = t
    out = subprocess.run(["./shortest", "-n", str(n), "-m", str(m), "-g", str(g), "-s", str(31337 + 97 * k + 1000 * n + m), "-L", "60", "-C", "200000000"],
                         capture_output=True, text=True, check=True).stdout
    return [list(map(int, l.split())) for l in out.splitlines()]
res = {}
for n, m, g in cfgs:
    per = g // WORK
    with ThreadPoolExecutor(WORK) as ex:
        rows = [r for part in ex.map(job, [(n, m, per, k) for k in range(WORK)]) for r in part]
    mins = [r[1] for r in rows]
    unsolved = sum(1 for x in mins if x < 0)
    ok = [x for x in mins if x >= 0]
    bound = m if n == 2 else 2 * m - 1
    c = Counter(ok)
    res[f"{n},{m}"] = dict(n=n, m=m, deals=len(rows), unsolved=unsolved, hist=sorted(c.items()), bound=bound,
                          winners=Counter(r[2] for r in rows if r[1] >= 0).most_common())
    mean = sum(ok) / len(ok)
    print(f"N={n} M={m} deals={len(rows)} unsolved={unsolved} bound={bound} mean={mean:.2f} min={min(ok)} max={max(ok)} "
          f"P(at bound)={c[bound]/len(ok):.4f} P(<=bound+2)={sum(v for k,v in c.items() if k<=bound+2)/len(ok):.3f}", flush=True)
    print("   ", " ".join(f"{k}:{v}" for k, v in sorted(c.items())), flush=True)
json.dump(res, open("../results/e5_shortest.json", "w"))
