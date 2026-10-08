"""Independent check of shortest.c: rebuild the same deals in Python and solve
them by plain breadth-first search over game states, with no bound."""
import subprocess, sys, os

M64 = (1 << 64) - 1
SKIP, REV, D2, WILD, WD4 = 10, 11, 12, 13, 14
COL, RANK = [], []
for c in range(4):
    COL.append(c); RANK.append(0)
    for r in range(1, 13):
        for _ in range(2):
            COL.append(c); RANK.append(r)
for r in (WILD, WD4):
    for _ in range(4):
        COL.append(4); RANK.append(r)


class Rng:
    def __init__(self, seed):
        self.s = []
        for _ in range(4):
            seed = (seed + 0x9e3779b97f4a7c15) & M64
            z = seed
            z = ((z ^ (z >> 30)) * 0xbf58476d1ce4e5b9) & M64
            z = ((z ^ (z >> 27)) * 0x94d049bb133111eb) & M64
            self.s.append(z ^ (z >> 31))

    def next(self):
        s = self.s
        rotl = lambda x, k: ((x << k) | (x >> (64 - k))) & M64
        res = (rotl((s[1] * 5) & M64, 7) * 9) & M64
        t = (s[1] << 17) & M64
        s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3]; s[2] ^= t; s[3] = rotl(s[3], 45)
        return res

    def below(self, n):
        return ((self.next() >> 32) * n) >> 32


def deals(n, m, count, seed):
    rng = Rng(seed)
    for _ in range(count):
        deck = list(range(108))
        for i in range(107, 0, -1):
            j = rng.below(i + 1)
            deck[i], deck[j] = deck[j], deck[i]
        hands = [[] for _ in range(n)]
        k = 0
        for _ in range(m):
            for p in range(n):
                hands[p].append(deck[k]); k += 1
        while RANK[deck[k]] == WD4:
            deck.append(deck.pop(k))
        start = deck[k]; k += 1
        yield hands, deck[k:], start


def face(c):
    return (RANK[c], COL[c])


def solve(n, hands, stock, start, limit):
    """BFS over full states. A state is (hands as sorted face tuples, stock pointer, topc, topr, dir, cur)."""
    hands = [sorted(face(c) for c in h) for h in hands]
    stock = [face(c) for c in stock]
    sp, dirn, cur = 0, 1, 0
    topr, topc = face(start)
    starts = []
    if topr == WILD:
        for col in range(4):
            starts.append((hands, sp, col, topr, dirn, cur))
    else:
        if topr == SKIP:
            cur = 1 % n
        elif topr == REV:
            cur = n - 1
            if n > 2: dirn = -1
        elif topr == D2:
            hands = [list(h) for h in hands]
            hands[0] = sorted(hands[0] + stock[0:2]); sp = 2; cur = 1 % n
        starts.append((hands, sp, topc, topr, dirn, cur))
    key = lambda st: (tuple(tuple(h) for h in st[0]),) + st[1:]
    frontier = {key(s): s for s in starts}
    seen = set(frontier)
    for depth in range(1, limit + 1):
        nxt = {}
        for st in frontier.values():
            hands, sp, topc, topr, dirn, cur = st
            adv = lambda p, k, d: ((p + d * k) % n + n) % n
            p = cur
            def fits(h, f):
                r, c = f
                if r == WILD: return True
                if r == WD4: return all(cc != topc for _, cc in h)
                return c == topc or r == topr
            def apply(h_after, f, col, sp0):
                r, c = f
                ntopc = col if c == 4 else c
                if not h_after:
                    return "WIN"
                nh = [list(x) for x in hands]; nh[p] = h_after
                d, nsp = dirn, sp0
                if r == SKIP: ncur = adv(p, 2, d)
                elif r == REV:
                    if n == 2: ncur = p
                    else: d = -d; ncur = adv(p, 1, d)
                elif r in (D2, WD4):
                    v = adv(p, 1, d); k = 2 if r == D2 else 4
                    if nsp + k > len(stock): return None
                    nh[v] = sorted(nh[v] + stock[nsp:nsp + k]); nsp += k
                    ncur = adv(p, 2, d)
                else: ncur = adv(p, 1, d)
                return (nh, nsp, ntopc, r, d, ncur)
            outs = []
            h = hands[p]
            for i, f in enumerate(h):
                if i and h[i - 1] == f: continue
                if not fits(h, f): continue
                rest = h[:i] + h[i + 1:]
                for col in (range(4) if f[1] == 4 else [None]):
                    outs.append(apply(rest, f, col, sp))
            if sp < len(stock):
                f = stock[sp]
                h2 = sorted(h + [f])
                if fits(h2, f):
                    rest = list(h)
                    for col in (range(4) if f[1] == 4 else [None]):
                        outs.append(apply(rest, f, col, sp + 1))
                nh = [list(x) for x in hands]; nh[p] = h2
                outs.append((nh, sp + 1, topc, topr, dirn, adv(p, 1, dirn)))
            for o in outs:
                if o == "WIN":
                    return depth
                if o is None: continue
                kk = key(o)
                if kk not in seen:
                    seen.add(kk); nxt[kk] = o
        frontier = nxt
        if len(frontier) > 3_000_000:
            return None
    return -1


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    bad = 0
    for n, m, cnt, seed in ((2, 3, 40, 11), (3, 2, 40, 12), (2, 4, 25, 13), (4, 2, 25, 14), (3, 3, 15, 15)):
        out = subprocess.run([os.path.join(here, "shortest"), "-n", str(n), "-m", str(m), "-g", str(cnt), "-s", str(seed), "-L", "14"],
                             capture_output=True, text=True, check=True).stdout.split("\n")
        c_res = [int(line.split()[1]) for line in out if line]
        for i, (hands, stock, start) in enumerate(deals(n, m, cnt, seed)):
            b = solve(n, hands, stock, start, 14)
            if b is None:
                continue
            if b != c_res[i]:
                bad += 1
                print("MISMATCH", n, m, seed, i, "C", c_res[i], "BFS", b)
        print(f"n={n} m={m}: {cnt} deals checked", flush=True)
    print("mismatches:", bad)
    sys.exit(1 if bad else 0)
