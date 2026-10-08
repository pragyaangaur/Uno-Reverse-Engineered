/*
 * endgame.c: the hoard endgame of Uno under the official Draw Four rule.
 *
 * In the large-hand limit every player reaches the end of the main phase
 * holding about h = M/23 Wild Draw Fours and almost nothing else. This
 * program starts there: every seat holds h Draw Fours plus k random other
 * cards, the top card is a random coloured card, and seat 0 is on turn.
 * It then plays to the end with the same rules and the same uniformly random
 * strategy as uno.c. A hand is stored as a count for each of the 108 cards,
 * so a turn costs the same for any hand size and h can be in the millions.
 *
 * Build: cc -O3 -o endgame endgame.c -lm
 * Usage: ./endgame -n PLAYERS -h HOARD -k OTHER -g GAMES -s SEED
 * Prints one JSON object with the mean length of the endgame and the mean
 * number of cards each loser holds at the end, both divided by h.
 */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NCARDS 108
#define MAXP 16
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

static int n, topc, topr, dir, cur;
static long cnt[MAXP][NCARDS], tot[MAXP];
static rng_t rng;

static void give(int p) { cnt[p][rbelow(&rng, NCARDS)]++; tot[p]++; }

static inline int adv(int p, int k) { return ((p + dir * k) % n + n) % n; }

/* Play one card of type c. Returns 1 if p has won. */
static int play(int p, int c) {
    cnt[p][c]--; tot[p]--;
    topr = crank[c];
    topc = ccol[c] == 4 ? (int)rbelow(&rng, 4) : ccol[c];
    if (tot[p] == 0) return 1;
    switch (topr) {
    case SKIP: cur = adv(p, 2); break;
    case REV:
        if (n == 2) cur = p;
        else { dir = -dir; cur = adv(p, 1); }
        break;
    case D2: { int v = adv(p, 1); give(v); give(v); cur = adv(p, 2); break; }
    case WD4: { int v = adv(p, 1); for (int t = 0; t < 4; t++) give(v); cur = adv(p, 2); break; }
    default: cur = adv(p, 1);
    }
    return 0;
}

static int fits(int c, int held) {
    if (crank[c] == WD4) return !held;
    return crank[c] == WILD || ccol[c] == topc || crank[c] == topr;
}

int main(int argc, char **argv) {
    long h = 1000, games = 1000;
    int k = 0;
    uint64_t seed = 1;
    n = 2;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-n")) n = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-h")) h = atol(argv[++i]);
        else if (!strcmp(argv[i], "-k")) k = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-g")) games = atol(argv[++i]);
        else if (!strcmp(argv[i], "-s")) seed = strtoull(argv[++i], NULL, 10);
        else { fprintf(stderr, "unknown flag %s\n", argv[i]); return 2; }
    }
    if (n < 2 || n > MAXP || h < 1 || k < 0) { fprintf(stderr, "bad arguments\n"); return 2; }
    build_deck();
    rseed(&rng, seed);
    double st = 0, st2 = 0, sleft = 0;
    double seatwin[MAXP] = {0}, seatleft[MAXP] = {0};
    for (long gi = 0; gi < games; gi++) {
        for (int p = 0; p < n; p++) {
            memset(cnt[p], 0, sizeof cnt[p]);
            cnt[p][NCARDS - 1] = h; tot[p] = h;
            for (int j = 0; j < k; j++) give(p);
        }
        int c;
        do c = rbelow(&rng, NCARDS); while (ccol[c] == 4);
        topc = ccol[c]; topr = crank[c]; dir = 1; cur = 0;
        long turns = 0;
        int winner;
        for (;;) {
            int p = cur, held = 0;
            long legal = 0;
            turns++;
            for (int i = 0; i < NCARDS; i++) held |= cnt[p][i] > 0 && ccol[i] == topc;
            for (int i = 0; i < NCARDS; i++) if (cnt[p][i] && fits(i, held)) legal += cnt[p][i];
            if (legal == 0) {
                int d = rbelow(&rng, NCARDS);
                cnt[p][d]++; tot[p]++;
                if (fits(d, held)) { if (play(p, d)) { winner = p; break; } }
                else cur = adv(p, 1);
                continue;
            }
            /* every playable card is equally likely, as with strategy 0,0,0,0,0 in uno.c */
            long r = (long)((rnext(&rng) >> 11) * (1.0 / 9007199254740992.0) * legal);
            for (c = 0; c < NCARDS; c++) {
                if (!cnt[p][c] || !fits(c, held)) continue;
                if (r < cnt[p][c]) break;
                r -= cnt[p][c];
            }
            if (play(p, c)) { winner = p; break; }
        }
        st += turns; st2 += (double)turns * turns;
        seatwin[winner]++;
        for (int p = 0; p < n; p++) { sleft += tot[p]; seatleft[p] += tot[p]; }
    }
    double mean = st / games;
    printf("{\"n\":%d,\"h\":%ld,\"k\":%d,\"games\":%ld,\"seed\":%llu,\"turns_per_h\":%.6f,\"sd_turns_per_h\":%.6f,"
           "\"left_per_loser_per_h\":%.6f,\"wins\":[", n, h, k, games, (unsigned long long)seed, mean / h,
           (st2 / games - mean * mean > 0 ? sqrt(st2 / games - mean * mean) : 0) / h, sleft / games / (n - 1) / h);
    for (int p = 0; p < n; p++) printf("%s%.0f", p ? "," : "", seatwin[p]);
    printf("],\"left_per_h\":[");
    for (int p = 0; p < n; p++) printf("%s%.6f", p ? "," : "", seatleft[p] / games / h);
    printf("]}\n");
    return 0;
}
