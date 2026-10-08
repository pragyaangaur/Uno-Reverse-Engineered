"""E6b: the official Draw Four rule for three and five players at M = 32000, added to E6.

For each run it prints T/(NM), the leftover cards per loser as a share of M, and the turns after the first turn a player holds only Draw Fours (the hoard endgame) in units of M/23."""
import json
from driver import run_many

PLAN = [(3, 32000, 160), (5, 32000, 100)]
out = []
for i, (n, m, g) in enumerate(PLAN):
    c = dict(n=n, m=m, infinite=True, cap=10**9)
    r = run_many([c], g, base_seed=61000 + 100 * i)[0]
    out.append(r)
    done = r["games"] - r["unfinished"]
    sem = (r["var_turns"] / done) ** .5 / (n * m)
    left = n * m + r["mean_draws"] - r["mean_plays"]
    end = (r["mean_turns"] - r["mean_hoard_turn"]) / (m / 23)
    print(n, m, done, f"T/(NM)={r['mean_turns'] / (n * m):.5f}±{sem:.5f}", f"left/loser/M={left / (n - 1) / m:.4f}",
          f"hoard_start/(NM)={r['mean_hoard_turn'] / (n * m):.5f}", f"endgame/(M/23)={end:.3f}", flush=True)
    json.dump(out, open("../results/e6b_odd.json", "w"))
