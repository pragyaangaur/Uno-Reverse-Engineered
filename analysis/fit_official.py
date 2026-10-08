"""Fit how T/(NM) under the official Draw Four rule approaches its large-hand limit.

The limit for each N comes from the endgame runs: T/(NM) -> 26/23 + E/(23N), where E is the endgame length per unit of hoard. Each fit is T/(NM) = L + a M^(-p), once with L free and once with L fixed at the predicted value."""
import json
import os
import numpy as np
from scipy.optimize import curve_fit

RES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")


def limits():
    """Predicted T/(NM) and leftover share per loser for each N, from the largest hoard run."""
    best = {}
    for r in json.load(open(os.path.join(RES, "e7_endgame.json"))):
        if r["k"] == 0 and r["h"] >= best.get(r["n"], {"h": 0})["h"]:
            best[r["n"]] = r
    return {n: (26 / 23 + r["turns_per_h"] / (23 * n), r["sem"] / (23 * n), r["left_per_loser_per_h"] / 23) for n, r in best.items()}


def points(n, free=False, names=("e6_official.json", "e6b_odd.json")):
    out = []
    rows = [r for f in names if os.path.exists(os.path.join(RES, f)) for r in json.load(open(os.path.join(RES, f)))]
    for r in rows:
        if r["n"] != n or bool(r.get("wd4_free")) != free:
            continue
        done = r["games"] - r["unfinished"]
        nm = n * r["m"]
        left = nm + r["mean_draws"] - r["mean_plays"]
        out.append((r["m"], r["mean_turns"] / nm, (r["var_turns"] / done) ** .5 / nm, left / (n - 1) / r["m"]))
    return np.array(sorted(out))


if __name__ == "__main__":
    lim = limits()
    for n in sorted(lim):
        L, Lsem, share = lim[n]
        print(f"N={n} predicted T/(NM)={L:.5f}±{Lsem:.5f} leftover per loser={share:.4f}M")
    print()
    for n in (2, 3, 4, 5):
        d = points(n)
        if len(d) < 4:
            continue
        M, T, s, left = d.T
        L = lim[n][0]
        (Lf, a, p), cov = curve_fit(lambda m, L, a, p: L + a * m ** -p, M, T, p0=(L, -1, .5), sigma=s, absolute_sigma=True, maxfev=20000)
        e = np.sqrt(np.diag(cov))
        (a2, p2), cov2 = curve_fit(lambda m, a, p: L + a * m ** -p, M, T, p0=(-1, .5), sigma=s, absolute_sigma=True, maxfev=20000)
        chi2 = float(np.sum((((L + a2 * M ** -p2) - T) / s) ** 2))
        (L3, a3), cov3 = curve_fit(lambda m, L, a: L + a * m ** -.5, M, T, p0=(L, -1), sigma=s, absolute_sigma=True)
        chi3 = float(np.sum((((L3 + a3 * M ** -.5) - T) / s) ** 2))
        print(f"N={n} M={[int(x) for x in M]}")
        print(f"  T/(NM) = {', '.join(f'{x:.5f}' for x in T)}")
        print(f"  free fit:  L={Lf:.4f}±{e[0]:.4f} p={p:.2f}±{e[2]:.2f}")
        print(f"  fixed L={L:.5f}: p={p2:.2f} chi2={chi2:.1f} on {len(M) - 2} dof")
        print(f"  p fixed at 1/2: L={L3:.5f}±{cov3[0, 0] ** .5:.5f} chi2={chi3:.1f} on {len(M) - 2} dof")
        print(f"  leftover per loser / M = {', '.join(f'{x:.4f}' for x in left)} (limit {lim[n][2]:.4f})")
