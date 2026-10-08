"""E3b: two and four players with M up to 4000, official and free Draw Four."""
import json
from driver import run_many
out = []
for free in (False, True):
    for n, m, g in ((2, 2000, 2000), (2, 4000, 600), (4, 2000, 600), (4, 4000, 200)):
        c = dict(n=n, m=m, infinite=True, cap=10**8, wd4_free=free)
        r = run_many([c], g, base_seed=5000 + len(out))[0]
        r["wd4_free"] = free; out.append(r)
        done = r["games"] - r["unfinished"]
        sem = (r["var_turns"] / done) ** .5 / (n * m)
        L = n * m + r["mean_draws"] - r["mean_plays"]
        print("free" if free else "official", n, m, done, f"T/(NM)={r['mean_turns']/(n*m):.4f}±{sem:.4f}",
              f"plays/(NM)={r['mean_plays']/(n*m):.4f}", f"left/loser/M={L/(n-1)/m:.4f}", flush=True)
json.dump(out, open("../results/e3b_hugem.json", "w"))
