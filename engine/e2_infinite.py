"""E2: infinite deck, large hands. Tests the linear law for the mean, the growth of the variance and the decay of the seat advantage."""
import json, sys
from driver import run_many
G = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
configs = [dict(n=n, m=m, infinite=True, cap=1000000) for n in (2, 3, 4, 6) for m in (1, 2, 3, 5, 7, 10, 20, 40, 80, 160, 320)]
res = run_many(configs, G, base_seed=77)
json.dump(res, open("../results/e2_infinite.json", "w"))
for r in res:
    w = r["wins"]; tot = sum(w)
    print(r["n"], r["m"], r["unfinished"], round(r["mean_turns"], 2), round(r["var_turns"], 1), " ".join(f"{x/tot:.4f}" for x in w))
