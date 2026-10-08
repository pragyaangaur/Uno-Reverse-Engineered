"""E7: the hoard endgame on its own, with hoards far larger than a full game can reach.

Every seat starts with h Draw Fours and k other random cards (see endgame.c). The endgame length per unit of hoard, E, gives the official large-hand limit T/(NM) = 26/23 + E/(23N), and the loser's leftover per unit of hoard, divided by 23, gives the leftover share of M."""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "endgame")
CHUNKS = 8


def run(n, h, k, games, seed):
    def one(j):
        a = [BIN, "-n", n, "-h", h, "-k", k, "-g", games // CHUNKS, "-s", seed + j]
        return json.loads(subprocess.run(list(map(str, a)), capture_output=True, text=True, check=True).stdout)
    with ThreadPoolExecutor(os.cpu_count() or 4) as ex:
        parts = list(ex.map(one, range(CHUNKS)))
    g = sum(p["games"] for p in parts)
    mean = sum(p["turns_per_h"] * p["games"] for p in parts) / g
    second = sum((p["sd_turns_per_h"] ** 2 + p["turns_per_h"] ** 2) * p["games"] for p in parts) / g
    left = sum(p["left_per_loser_per_h"] * p["games"] for p in parts) / g
    wins = [sum(p["wins"][i] for p in parts) for i in range(n)]
    return dict(n=n, h=h, k=k, games=g, turns_per_h=mean, sem=((second - mean ** 2) / g) ** .5, left_per_loser_per_h=left, wins=wins)


plan = [(n, h, 0, g) for h, g in ((10**3, 8000), (10**4, 4000), (10**5, 800), (10**6, 160)) for n in (2, 3, 4, 5, 6)]
plan += [(n, 10**5, k, 800) for k in (10, 300) for n in (3, 4, 5)]
plan += [(n, h, 0, g) for h, g in ((10**4, 4000), (10**5, 800)) for n in (7, 8, 9)]
# an optional argument resumes from that row of the plan, keeping the rows already saved
start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
out = json.load(open("../results/e7_endgame.json"))[:start] if start else []
for i, (n, h, k, g) in enumerate(plan):
    if i < start:
        continue
    r = run(n, h, k, g, 70000 + 100 * i)
    out.append(r)
    E = r["turns_per_h"]
    print(n, h, k, r["games"], f"E={E:.4f}±{r['sem']:.4f}", f"T/(NM)={26 / 23 + E / (23 * n):.5f}",
          f"left/loser/M={r['left_per_loser_per_h'] / 23:.4f}", "wins", r["wins"], flush=True)
    json.dump(out, open("../results/e7_endgame.json", "w"))
