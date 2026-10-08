"""E1: game length and seat advantage over N players and M starting cards, random legal play."""
import json, sys
from driver import run_many
G = int(sys.argv[1]) if len(sys.argv) > 1 else 400000
configs = [dict(n=n, m=m) for n in range(2, 11) for m in range(1, 16) if n * m <= 100]
res = run_many(configs, G)
json.dump(res, open("../results/e1_grid.json", "w"))
for r in res:
    w = r["wins"]; tot = sum(w)
    print(r["n"], r["m"], round(r["mean_turns"], 2), round(r["var_turns"] ** .5, 2), r["min_turns"], r["max_turns"],
          " ".join(f"{x/tot:.4f}" for x in w))
