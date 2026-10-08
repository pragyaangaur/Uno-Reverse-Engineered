"""Draw the figures in figures/ from the JSON results in results/."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)
load = lambda f: json.load(open(os.path.join(RES, f)))
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})


def fig_length_grid():
    R = load("e1_grid.json")
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for n in range(2, 11):
        rs = [r for r in R if r["n"] == n]
        ax[0].plot([r["m"] for r in rs], [r["mean_turns"] for r in rs], marker="o", ms=3, label=f"N={n}")
        ax[1].plot([r["m"] for r in rs], [r["var_turns"] ** .5 for r in rs], marker="o", ms=3)
    ax[0].set_xlabel("starting hand M"); ax[0].set_ylabel("mean turns"); ax[0].legend(fontsize=7, ncol=2)
    ax[1].set_xlabel("starting hand M"); ax[1].set_ylabel("standard deviation of turns")
    fig.suptitle("Real 108 card deck, random legal play, 400,000 games per point")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "length_grid.png"), dpi=150)


def fig_fluid_limit():
    R = load("e2_infinite.json")
    B = load("e3_bigm.json") if os.path.exists(os.path.join(RES, "e3_bigm.json")) else []
    H = load("e3b_hugem.json") if os.path.exists(os.path.join(RES, "e3b_hugem.json")) else []
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for free, ls in ((False, "-"), (True, "--")):
        for n, col in zip((2, 3, 4, 6), ("C0", "C1", "C2", "C3")):
            pts = {}
            for r in R:
                if r["n"] == n and not free and r["m"] >= 5:
                    pts[r["m"]] = r["mean_turns"] / (n * r["m"])
            for r in B + H:
                if r["n"] == n and r["wd4_free"] == free:
                    pts[r["m"]] = r["mean_turns"] / (n * r["m"])
            if not pts:
                continue
            ms = sorted(pts)
            ax.plot(ms, [pts[m] for m in ms], ls, color=col, marker="o", ms=3,
                    label=f"N={n}, " + ("Draw Four always legal" if free else "official rule"))
    ax.axhline(27 / 19, color="k", lw=0.8, ls="--"); ax.text(5.5, 27 / 19 + 0.01, "27/19", fontsize=9)
    ax.axhline(53 / 46, color="k", lw=0.8); ax.text(5.5, 53 / 46 - 0.035, "53/46", fontsize=9)
    ax.axhline(26 / 23, color="grey", lw=0.6, ls=":"); ax.text(1500, 26 / 23 - 0.03, "26/23 (bulk only)", fontsize=8, color="grey")
    ax.set_xscale("log"); ax.set_xlabel("starting hand M (infinite deck)"); ax.set_ylabel("mean turns / (N M)")
    ax.set_ylim(1.0, 2.4); ax.legend(fontsize=7, ncol=2)
    ax.set_title("Game length per card converges to exact rational limits")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fluid_limit.png"), dpi=150)


def fig_tail():
    R = load("e1_grid.json")
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for r in R:
        if r["n"] == 4 and r["m"] in (1, 3, 7, 11, 15):
            h = np.array(r["hist"], float)
            surv = 1 - np.cumsum(h) / h.sum()
            t = np.arange(len(h))
            ax.semilogy(t[surv > 0], surv[surv > 0], label=f"M={r['m']}")
    ax.set_xlabel("turns t"); ax.set_ylabel("P(game lasts longer than t)")
    ax.set_title("Four players: the tail has the same slope for every M")
    ax.legend(); fig.tight_layout(); fig.savefig(os.path.join(FIG, "tail.png"), dpi=150)


def fig_shortest():
    if not os.path.exists(os.path.join(RES, "e5_shortest.json")):
        return
    S = load("e5_shortest.json")
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for key in ("2,7", "3,7", "4,7"):
        if key not in S:
            continue
        d = S[key]
        xs = [k for k, _ in d["hist"]]; tot = sum(v for _, v in d["hist"])
        line, = ax.plot(xs, [v / tot for _, v in d["hist"]], marker="o", ms=3, label=f"N={d['n']}, bound {d['bound']}")
        ax.axvline(d["bound"], color=line.get_color(), lw=0.7, ls=":")
    ax.set_xlabel("fewest possible turns from the deal"); ax.set_ylabel("share of deals")
    ax.set_title("Fastest possible game from a random 7 card deal")
    ax.legend(); fig.tight_layout(); fig.savefig(os.path.join(FIG, "shortest.png"), dpi=150)


def fig_tournament():
    T = load("e4_tournament.json")
    P = np.array(T["two_player_P"]); P4 = np.array(T["four_player_P"])
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.8))
    im = ax[0].imshow(P, cmap="RdBu_r", vmin=0.35, vmax=0.65)
    ax[0].set_title("Two players: P(row beats column)"); fig.colorbar(im, ax=ax[0], fraction=0.046)
    im = ax[1].imshow(P4, cmap="RdBu_r", vmin=0.15, vmax=0.35)
    ax[1].set_title("Four players: deviant (row) in a field (column)"); fig.colorbar(im, ax=ax[1], fraction=0.046)
    for a in ax:
        a.set_xlabel("strategy index"); a.set_ylabel("strategy index")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "tournament.png"), dpi=150)


if __name__ == "__main__":
    fig_length_grid(); fig_fluid_limit(); fig_tail(); fig_shortest(); fig_tournament()
    print("figures written to", FIG)
