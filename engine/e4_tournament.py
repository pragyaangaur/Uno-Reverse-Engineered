"""E4: game theory over a family of 48 strategies.

Two players: every ordered pair is played from both seats, which gives a
symmetric zero-sum matrix game. Its Nash equilibrium is found by linear
programming.

Four players: the payoff of a single deviant strategy i against three copies
of a field strategy j, averaged over the deviant's seat. A field j is an
equilibrium of the symmetric game among pure strategies when no deviant wins
more than 1/4 against it.
"""
import itertools
import json
import sys

import numpy as np
from scipy.optimize import linprog

from driver import run_one, WORKERS
from concurrent.futures import ThreadPoolExecutor

STRATS = [dict(w=w, a=a, c=c, k=k, s=s)
          for w, a, c, k, s in itertools.product((0, 1), (-1, 0, 1), (0, 1), (0, 2), (0, 3))]
spec = lambda d: f"{d['w']},{d['a']},{d['c']},{d['k']},{d['s']}"
RANDOM = STRATS.index(dict(w=0, a=0, c=0, k=0, s=0))


def label(d):
    parts = []
    parts.append("hold wilds" if d["w"] else "wilds any time")
    parts.append({-1: "save actions", 0: "actions neutral", 1: "dump actions"}[d["a"]])
    parts.append("best colour" if d["c"] else "random colour")
    parts.append("attack at 2" if d["k"] else "no attack")
    parts.append("steer colour" if d["s"] else "no steer")
    return ", ".join(parts)


def two_player(games):
    S = len(STRATS)
    jobs = [(i, j, seed) for i in range(S) for j in range(S) for seed in (1, 2)]

    def job(t):
        i, j, seed = t
        r = run_one(2, 7, games, 10_000 * seed + 100 * i + j, spec=spec(STRATS[i]) + ";" + spec(STRATS[j]))
        return i, j, r["wins"][0], sum(r["wins"])
    W = np.zeros((S, S)); N = np.zeros((S, S))
    with ThreadPoolExecutor(WORKERS) as ex:
        for i, j, w, n in ex.map(job, jobs):
            W[i, j] += w; N[i, j] += n          # i in seat 0 beats j
            W[j, i] += n - w; N[j, i] += n      # j in seat 1 beats i
    P = W / N                                   # P[i, j]: i beats j, both seats pooled
    return P, N


def solve_zero_sum(A):
    """Row player's maximin mixed strategy for payoff matrix A."""
    S = A.shape[0]
    c = np.zeros(S + 1); c[-1] = -1
    A_ub = np.hstack([-A.T, np.ones((S, 1))])
    b_ub = np.zeros(S)
    A_eq = np.hstack([np.ones((1, S)), np.zeros((1, 1))])
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=[1], bounds=[(0, None)] * S + [(None, None)])
    return res.x[:S], res.x[-1]


def four_player(games):
    S = len(STRATS)
    jobs = [(i, j, seat) for i in range(S) for j in range(S) for seat in range(4)]

    def job(t):
        i, j, seat = t
        specs = [spec(STRATS[j])] * 4
        specs[seat] = spec(STRATS[i])
        r = run_one(4, 7, games, 7_000_000 + 1000 * i + 10 * j + seat, spec=";".join(specs))
        return i, j, r["wins"][seat], sum(r["wins"])
    W = np.zeros((S, S)); N = np.zeros((S, S))
    with ThreadPoolExecutor(WORKERS) as ex:
        for i, j, w, n in ex.map(job, jobs):
            W[i, j] += w; N[i, j] += n
    return W / N, N


if __name__ == "__main__":
    g2 = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    g4 = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
    P, N2 = two_player(g2)
    A = P - 0.5
    x, v = solve_zero_sum(A)
    out = {"strategies": [spec(d) for d in STRATS], "labels": [label(d) for d in STRATS],
           "two_player_P": P.tolist(), "two_player_games_per_cell": float(N2[0, 1])}
    print(f"two players, {int(N2[0,1])} games per pair")
    print("Nash mixture (value should be 0 for a symmetric game):", round(v, 5))
    for k in np.argsort(-x):
        if x[k] > 1e-3:
            print(f"  {x[k]:.3f}  {spec(STRATS[k])}  {label(STRATS[k])}")
    vs_random = P[:, RANDOM]
    order = np.argsort(-vs_random)
    print("best against uniform random play:")
    for k in order[:5]:
        print(f"  {vs_random[k]:.4f}  {spec(STRATS[k])}  {label(STRATS[k])}")
    print("worst against uniform random play:")
    for k in order[-3:]:
        print(f"  {vs_random[k]:.4f}  {spec(STRATS[k])}  {label(STRATS[k])}")
    out["nash2"] = x.tolist()

    P4, N4 = four_player(g4)
    out["four_player_P"] = P4.tolist()
    out["four_player_games_per_cell"] = float(N4[0, 0])
    best_dev = P4.max(axis=0)       # for each field j, the best deviant's win rate
    print(f"\nfour players, {int(N4[0,0])} games per deviant and field")
    print("fields where no deviant wins much more than 1/4 (stable):")
    for j in np.argsort(best_dev)[:5]:
        i = int(np.argmax(P4[:, j]))
        print(f"  field {spec(STRATS[j])} ({label(STRATS[j])}): best deviant {spec(STRATS[i])} wins {best_dev[j]:.4f}")
    # best response dynamics from the random field
    j, path = RANDOM, [RANDOM]
    for _ in range(20):
        i = int(np.argmax(P4[:, j]))
        if P4[i, j] <= P4[j, j] + 0.002 or i in path:
            path.append(i)
            break
        j = i; path.append(j)
    print("best response path from random play:", " -> ".join(spec(STRATS[k]) for k in path))
    print("deviant against a random field, top 5:")
    for k in np.argsort(-P4[:, RANDOM])[:5]:
        print(f"  {P4[k, RANDOM]:.4f}  {spec(STRATS[k])}  {label(STRATS[k])}")
    json.dump(out, open("../results/e4_tournament.json", "w"))
