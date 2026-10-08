"""Fluid limit of Uno with random legal play and an infinite deck.

When every hand holds M cards with M large, a hand always contains a card of
the current colour, so every turn is a play. The composition of a hand then
changes slowly while the top card changes every turn, so the top card can be
treated as a fast Markov chain sitting in its stationary law.

Classes: ranks 0..12 summed over the four colours (10 Skip, 11 Reverse,
12 Draw Two), then Wild (13) and Wild Draw Four (14). Let x be one player's
hand as counts per class, scaled by M. A uniformly random playable card is
played, so given a top card of rank r the weight of class k is
    x_k / 4 + [k == r] * 3 x_r / 4      for a coloured class k,
    x_W                                  for a Wild,
    x_D if the Draw Four is legal, else 0.
After a Wild or a Draw Four only the colour matters (state 'C').

Each player plays 1/N of the turns and receives 2 cards per Draw Two and
4 per Draw Four played by someone, which also lands 1/N of the time on
average. In time tau = turns / (N M) one hand obeys
    dx/dtau = -phi(x) + (2 phi_D2 + 4 phi_D4) p,
with p the deck law and phi(x) the per-turn play rate of each class.
The bulk of the game ends when the hand runs out of the cards it can play.
"""
import numpy as np
from scipy.integrate import solve_ivp

K = 15
P = np.array([4] + [8] * 12 + [4, 4], float) / 108
D2, W, D4 = 12, 13, 14


def play_rates(x, wd4_legal):
    """Stationary per-turn probability that each class is played."""
    x = np.maximum(x, 0)
    S = 14  # states: top rank 0..12, then 13 = colour only
    T = np.zeros((S, S))
    rate_given = np.zeros((S, K))
    for s in range(S):
        w = np.zeros(K)
        w[:13] = x[:13] / 4
        if s < 13:
            w[s] += 3 * x[s] / 4
        w[W] = x[W]
        w[D4] = x[D4] if wd4_legal else 0.0
        tot = w.sum()
        if tot <= 0:
            return None
        w /= tot
        rate_given[s] = w
        T[s, :13] += w[:13]
        T[s, 13] += w[W] + w[D4]
    vals, vecs = np.linalg.eig(T.T)
    mu = np.real(vecs[:, np.argmin(abs(vals - 1))])
    mu /= mu.sum()
    return mu @ rate_given


def fluid(wd4_free, tmax=10.0):
    """Integrate one hand from x = p (M = 1). Returns tau at the end of the bulk
    and the hand left at that moment."""
    def rhs(t, x):
        legal = wd4_free
        phi = play_rates(x, legal)
        if phi is None:
            return np.zeros(K)
        g = 2 * phi[D2] + 4 * phi[D4]
        return -phi + g * P

    def bulk_left(t, x):
        # official rule: the bulk ends when the hand holds nothing but Draw Fours
        # (with a free Draw Four, when the hand is empty)
        return (x.sum() if wd4_free else x[:14].sum()) - 1e-6
    bulk_left.terminal = True
    sol = solve_ivp(rhs, (0, tmax), P.copy(), events=bulk_left, rtol=1e-9, atol=1e-12, max_step=1e-3)
    tau = sol.t_events[0][0]
    x_end = sol.y_events[0][0]
    return tau, x_end, sol


if __name__ == "__main__":
    for free in (True, False):
        tau, x_end, sol = fluid(free)
        x0 = P
        phi0 = play_rates(x0, free)
        print("rule:", "Draw Four always legal" if free else "official Draw Four rule")
        print(f"  bulk length tau* = T/(N M) = {tau:.5f}")
        print(f"  Draw Two rate at the start = {phi0[D2]:.5f}, Draw Four rate = {phi0[D4]:.5f}")
        print(f"  Draw Fours held at the end of the bulk = {x_end[D4]:.5f} M")
