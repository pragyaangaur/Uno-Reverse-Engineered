"""E3: very large hands on the infinite deck, to test the exact fluid limits
27/19 (Draw Four always legal) and 53/46 (official rule, even N)."""
import json
from driver import run_many
cfg, G = [], []
for free in (False, True):
    for n in (2, 3, 4, 6):
        for m, g in ((320, 40000), (640, 10000), (1000, 4000)):
            cfg.append(dict(n=n, m=m, infinite=True, cap=10**7, wd4_free=free)); G.append(g)
out = []
for c, g in zip(cfg, G):
    r = run_many([c], g, base_seed=900 + len(out))[0]
    r["wd4_free"] = c["wd4_free"]; out.append(r)
    n, m = r["n"], r["m"]
    sem = (r["var_turns"] / (r["games"] - r["unfinished"])) ** .5 / (n * m)
    print("free" if c["wd4_free"] else "official", n, m, r["games"], r["unfinished"],
          f"T/(NM)={r['mean_turns']/(n*m):.4f}±{sem:.4f}", f"left/loser/M={(n*m + r['mean_draws'] - r['mean_plays'])/(n-1)/m:.4f}", flush=True)
json.dump(out, open("../results/e3_bigm.json", "w"))
