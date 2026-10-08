"""E8: the Draw Four made legal at any time, M up to 16000, to fit how the losers' leftover and T/(NM) approach the 27/19 law."""
import json
from driver import run_many

PLAN = [(n, m, g) for m, g in ((500, 2000), (1000, 1600), (2000, 800), (4000, 800), (8000, 400), (16000, 200)) for n in (2, 4)]
out = []
for i, (n, m, g) in enumerate(PLAN):
    r = run_many([dict(n=n, m=m, infinite=True, cap=10**9, wd4_free=True)], g, base_seed=80000 + 100 * i)[0]
    out.append(r)
    done = r["games"] - r["unfinished"]
    sem = (r["var_turns"] / done) ** .5 / (n * m)
    left = n * m + r["mean_draws"] - r["mean_plays"]
    print(n, m, done, f"T/(NM)={r['mean_turns'] / (n * m):.5f}±{sem:.5f}", f"left/loser/M={left / (n - 1) / m:.5f}", flush=True)
    json.dump(out, open("../results/e8_free.json", "w"))
