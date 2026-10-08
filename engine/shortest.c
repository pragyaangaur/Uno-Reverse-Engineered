/*
 * shortest.c: the fastest possible game from a given deal.
 *
 * Every hand and the order of the stock are known, and all players cooperate
 * to end the round in as few turns as possible (any player may be the one who
 * goes out). Official rules: one card per turn, a player may always draw
 * instead of playing, a drawn card that fits may be played at once, Reverse
 * acts as Skip with two players, Wild Draw Four only without a card of the
 * current colour. Searched exactly with iterative deepening A*.
 *
 * The admissible bound: player q with k cards needs k plays of their own. With
 * two players nothing forces the opponent to move between them, so q needs at
 * least k turns, plus one if q is not the player to move. With three or more
 * players every play hands the turn to someone else, so q needs at least
 * 2k - 1 turns, plus one if q is not to move.
 *
 * Usage: ./shortest -n PLAYERS -m HANDSIZE -g DEALS -s SEED [-L LIMIT]
 * Prints one line per deal: deal index, minimum turns (or -1 past LIMIT),
 * the winner, and the number of search nodes.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NCARDS 108
#define MAXP 10
#define MAXH 64
enum { SKIP = 10, REV = 11, D2 = 12, WILD = 13, WD4 = 14 };
static int ccol[NCARDS], crank[NCARDS];

static void build_deck(void) {
    int k = 0;
    for (int c = 0; c < 4; c++) {
        ccol[k] = c; crank[k++] = 0;
        for (int r = 1; r <= 12; r++)
            for (int t = 0; t < 2; t++) { ccol[k] = c; crank[k++] = r; }
    }
    for (int t = 0; t < 4; t++) { ccol[k] = 4; crank[k++] = WILD; }
    for (int t = 0; t < 4; t++) { ccol[k] = 4; crank[k++] = WD4; }
}

typedef struct { uint64_t s[4]; } rng_t;
static inline uint64_t rotl(uint64_t x, int k) { return (x << k) | (x >> (64 - k)); }
static inline uint64_t rnext(rng_t *r) {
    uint64_t *s = r->s, res = rotl(s[1] * 5, 7) * 9, t = s[1] << 17;
    s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3]; s[2] ^= t; s[3] = rotl(s[3], 45);
    return res;
}
static inline uint32_t rbelow(rng_t *r, uint32_t n) { return (uint32_t)(((rnext(r) >> 32) * (uint64_t)n) >> 32); }
static void rseed(rng_t *r, uint64_t seed) {
    for (int i = 0; i < 4; i++) {
        uint64_t z = (seed += 0x9e3779b97f4a7c15ULL);
        z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL; z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
        r->s[i] = z ^ (z >> 31);
    }
}

static int n, m;
static int hand[MAXP][MAXH], hs[MAXP];
static int stock[NCARDS], sp;   /* next card to draw is stock[sp] */
static int nstock;
static int topc, topr, dir, cur;
static long nodes, node_cap;
static int winner;

static inline int adv(int p, int k) { return ((p + dir * k) % n + n) % n; }

static int has_colour(int p, int col) {
    for (int i = 0; i < hs[p]; i++) if (ccol[hand[p][i]] == col) return 1;
    return 0;
}
static int fits(int p, int c) {
    if (crank[c] == WILD) return 1;
    if (crank[c] == WD4) return !has_colour(p, topc);
    return ccol[c] == topc || crank[c] == topr;
}

static int bound(void) {
    int best = 1 << 30;
    for (int q = 0; q < n; q++) {
        int k = hs[q];
        int b = (n == 2 ? k : 2 * k - 1) + (q == cur ? 0 : 1);
        if (b < best) best = b;
    }
    return best;
}

static int search(int g, int limit);

/* Apply playing card at hand[p][i] with colour choice col, recurse, undo. */
static int try_play(int p, int i, int col, int g, int limit) {
    int c = hand[p][i];
    int s_topc = topc, s_topr = topr, s_dir = dir, s_cur = cur, s_sp = sp;
    int victim = -1, vdraw = 0;
    hand[p][i] = hand[p][--hs[p]];
    topr = crank[c]; topc = ccol[c] == 4 ? col : ccol[c];
    int found = 0;
    if (hs[p] == 0) { winner = p; found = 1; goto undo; }
    switch (crank[c]) {
    case SKIP: cur = adv(p, 2); break;
    case REV: if (n == 2) cur = p; else { dir = -dir; cur = adv(p, 1); } break;
    case D2: victim = adv(p, 1); vdraw = 2; cur = adv(p, 2); break;
    case WD4: victim = adv(p, 1); vdraw = 4; cur = adv(p, 2); break;
    default: cur = adv(p, 1);
    }
    if (victim >= 0) {
        if (sp + vdraw > nstock) goto undo;
        for (int t = 0; t < vdraw; t++) hand[victim][hs[victim]++] = stock[sp++];
    }
    found = search(g + 1, limit);
    if (victim >= 0) hs[victim] -= vdraw;
undo:
    hand[p][hs[p]++] = hand[p][i];
    hand[p][i] = c;
    topc = s_topc; topr = s_topr; dir = s_dir; cur = s_cur; sp = s_sp;
    return found;
}

static int search(int g, int limit) {
    if (++nodes > node_cap) return 0;
    if (g + bound() > limit) return 0;
    int p = cur;
    /* play a card from hand, skipping duplicates of the same face */
    int seen[16][5] = {{0}};
    for (int i = 0; i < hs[p]; i++) {
        int c = hand[p][i];
        if (seen[crank[c]][ccol[c]]) continue;
        seen[crank[c]][ccol[c]] = 1;
        if (!fits(p, c)) continue;
        if (ccol[c] == 4) {
            for (int col = 0; col < 4; col++) if (try_play(p, i, col, g, limit)) return 1;
        } else if (try_play(p, i, -1, g, limit)) return 1;
    }
    /* draw one card, then either play it or pass */
    if (sp >= nstock) return 0;
    int d = stock[sp++];
    hand[p][hs[p]++] = d;
    int found = 0;
    if (fits(p, d)) {
        if (ccol[d] == 4) { for (int col = 0; col < 4 && !found; col++) found = try_play(p, hs[p] - 1, col, g, limit); }
        else found = try_play(p, hs[p] - 1, -1, g, limit);
    }
    if (!found) {
        int s_cur = cur;
        cur = adv(p, 1);
        found = search(g + 1, limit);
        cur = s_cur;
    }
    hs[p]--; sp--;
    return found;
}

int main(int argc, char **argv) {
    n = 2; m = 7;
    long deals = 100, cap = 50000000;
    int limit_max = 40;
    uint64_t seed = 1;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-n")) n = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-m")) m = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-g")) deals = atol(argv[++i]);
        else if (!strcmp(argv[i], "-s")) seed = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "-L")) limit_max = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-C")) cap = atol(argv[++i]);
    }
    build_deck();
    rng_t rng; rseed(&rng, seed);
    for (long di = 0; di < deals; di++) {
        int deck[NCARDS];
        for (int i = 0; i < NCARDS; i++) deck[i] = i;
        for (int i = NCARDS - 1; i > 0; i--) { int j = rbelow(&rng, i + 1), t = deck[i]; deck[i] = deck[j]; deck[j] = t; }
        int k = 0;
        for (int p = 0; p < n; p++) hs[p] = 0;
        for (int r = 0; r < m; r++) for (int p = 0; p < n; p++) hand[p][hs[p]++] = deck[k++];
        /* flip the start card, sending any Wild Draw Four to the bottom */
        int start;
        for (;;) {
            start = deck[k];
            if (crank[start] != WD4) { k++; break; }
            memmove(deck + k, deck + k + 1, sizeof(int) * (NCARDS - k - 1));
            deck[NCARDS - 1] = start;
        }
        nstock = 0;
        for (int i = k; i < NCARDS; i++) stock[nstock++] = deck[i];
        sp = 0; dir = 1; cur = 0; topr = crank[start]; topc = ccol[start];
        int pre_turn = 0, wild_start = 0;
        switch (crank[start]) {
        case WILD: wild_start = 1; break;
        case SKIP: cur = 1 % n; break;
        case REV: cur = n - 1; if (n > 2) dir = -1; break;
        case D2: hand[0][hs[0]++] = stock[sp++]; hand[0][hs[0]++] = stock[sp++]; cur = 1 % n; break;
        }
        (void)pre_turn;
        int best = -1, who = -1;
        long tot_nodes = 0;
        for (int limit = bound(); limit <= limit_max && best < 0; limit++) {
            int cols = wild_start ? 4 : 1;
            for (int col = 0; col < cols && best < 0; col++) {
                if (wild_start) topc = col;   /* player 0 names the colour */
                nodes = 0; node_cap = cap;
                if (search(0, limit)) { best = limit; who = winner; }
                tot_nodes += nodes;
                if (nodes > node_cap) { limit = limit_max + 1; break; }
            }
        }
        printf("%ld %d %d %ld\n", di, best, who, tot_nodes);
        fflush(stdout);
    }
    return 0;
}
