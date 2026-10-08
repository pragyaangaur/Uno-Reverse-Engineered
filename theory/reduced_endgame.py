"""Reduced model of the odd-N Draw Four endgame.

For odd N the exact endgame (engine/endgame.c) settles into a fixed pattern:
(N - 1)/2 dumpers sit at alternating seats and the other (N + 1)/2 players,
two of whom are neighbours, hold hands so large that they always have the
current colour and never play a Draw Four. This model keeps only that pattern.
Each dumper has an endless hoard and a small hand of other cards. Each big
hand plays a uniformly random legal card with the deck's proportions, as in
uno.c. Dumpers at different distances from the neighbouring pair of big
hands dump at different rates, and the game ends when the fastest one runs
out. So the output is the number of turns per Draw Four spent by the fastest
dumper, which is the endgame constant E if the pattern is the whole story.
"""
import random, sys

SKIP, REV, D2, WILD, WD4 = 10, 11, 12, 13, 14
DECK = [(c, 0) for c in range(4)] + [(c, r) for c in range(4) for r in range(1, 13) for _ in range(2)] + [(4, WILD)] * 4 + [(4, WD4)] * 4


def run(n, steps, seed, real_hands=False, start=200):
    """With real_hands the big hands are actual hands that start with `start`
    random cards, receive their penalty cards and play from what they hold, so
    their make-up drifts the way it does in a real game."""
    rng = random.Random(seed)
    big = {}
    if real_hands:
        for q in range(n):
            if q % 2 == 0 or q == n - 1:
                big[q] = [0] * len(DECK)
                for _ in range(start):
                    big[q][rng.randrange(len(DECK))] += 1
    dumpers = set(range(1, n - 1, 2))      # seats 1, 3, ..., n - 2
    small = {q: [] for q in dumpers}       # each dumper's hand apart from the hoard
    cur, d = 1, 1
    topc, topr = 0, 1
    turns = 0
    spent = {q: 0 for q in dumpers}
    for _ in range(steps):
        turns += 1
        p = cur
        if p in dumpers:
            hand = small[p]
            held = any(c == topc for c, _ in hand)
            legal = [i for i, (c, r) in enumerate(hand) if r == WILD or c == topc or (r == topr and c != 4)]
            nlegal = len(legal) + (0 if held else 1)   # the hoard counts as one more legal choice
            if nlegal == 0:
                card = rng.choice(DECK)
                if card[1] == WD4:
                    spent[p] -= 1
                    card = None
                else:
                    hand.append(card)
                cur = (p + d) % n
                continue
            if not held:
                # a hoard of size h dominates any small hand, so S plays a Draw Four
                card = (4, WD4); spent[p] += 1
            else:
                card = hand.pop(rng.choice(legal))
        elif real_hands:
            h = big[p]
            w = [h[i] if (r != WD4 and (r == WILD or c == topc or r == topr)) else 0 for i, (c, r) in enumerate(DECK)]
            i = rng.choices(range(len(DECK)), weights=w)[0]
            h[i] -= 1
            card = DECK[i]
        else:
            # a big hand: uniform over legal cards in deck proportions, never a Draw Four
            while True:
                card = rng.choice(DECK)
                c, r = card
                if r == WD4:
                    continue
                if r == WILD or c == topc or r == topr:
                    break
        c, r = card
        topr = r
        topc = rng.randrange(4) if c == 4 else c
        if r == SKIP:
            cur = (p + 2 * d) % n
        elif r == REV:
            d = -d; cur = (p + d) % n
        elif r in (D2, WD4):
            v = (p + d) % n
            if v in dumpers:
                for _ in range(2 if r == D2 else 4):
                    x = rng.choice(DECK)
                    if x[1] == WD4: spent[v] -= 1
                    else: small[v].append(x)
            elif real_hands:
                for _ in range(2 if r == D2 else 4):
                    big[v][rng.randrange(len(DECK))] += 1
            cur = (p + 2 * d) % n
        else:
            cur = (p + d) % n
    return turns / max(spent.values()), {q: round(turns / spent[q], 4) for q in sorted(spent)}


if __name__ == "__main__":
    real = "--real" in sys.argv
    steps = 600_000 if real else 2_000_000
    for n in (3, 5, 7, 9):
        runs = [run(n, steps, s, real_hands=real) for s in range(4)]
        m = sum(e for e, _ in runs) / len(runs)
        print(n, f"E_pattern={m:.4f}", " ".join(f"{e:.4f}" for e, _ in runs), "turns per dump by seat:", runs[0][1], flush=True)
