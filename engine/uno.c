/*
 * uno.c: a fast Monte Carlo engine for one round of Uno under the official
 * Mattel rules (108 card deck, one card per turn, no stacking, draw one and
 * play it if it fits, Reverse acts as Skip with two players, Wild Draw Four
 * only legal when the player holds no card of the current colour).
 *
 * Every seat runs a parametric strategy. The engine prints one JSON object
 * with the length distribution and the win count of every seat.
 *
 * Build: cc -O3 -o uno uno.c -lm
 * Usage: ./uno -n PLAYERS -m HANDSIZE -g GAMES -s SEED [-S spec] [-c CAP]
 *        [-t TRACEFILE] [-W]
 * A spec is "wildlast,action,colour,attack,switch" and may be given once for
 * every seat or as a ';' separated list, one per seat.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NCARDS 108
#define MAXP 16
#define HISTMAX 4096
#define HANDCAP 65536
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
    if (k != NCARDS) { fprintf(stderr, "deck size %d\n", k); exit(1); }
}

/* xoshiro256** */
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
static void shuffle(rng_t *r, int *a, int n) {
    for (int i = n - 1; i > 0; i--) { int j = rbelow(r, i + 1), t = a[i]; a[i] = a[j]; a[j] = t; }
}

typedef struct {
    int wild_last;  /* hold wilds while any coloured card fits */
    int action;     /* +1 dump action cards first, -1 save them, 0 neutral */
    int colour;     /* 0 random colour after a wild, 1 the colour I hold most of */
    int attack;     /* when the next player holds <= attack cards, hit them */
    int sw;         /* weight on landing in the colour I hold most of */
} strat_t;

typedef struct {
    int n, m;
    int hand[MAXP][HANDCAP], hs[MAXP];
    int draw[NCARDS], nd;
    int disc[NCARDS], ndisc;
    int topc, topr, dir, cur;
    long turns, plays, draws, reshuffles, passes, hoard_turn;
    int top_held;   /* the player on turn holds a card of the current colour */
    int wd4_free, infinite, overflow;
    strat_t st[MAXP];
    rng_t rng;
    FILE *trace;
} game_t;

static int draw_one(game_t *g, int p) {
    if (g->infinite) {
        if (g->hs[p] >= HANDCAP) { g->overflow = 1; return -1; }
        int c = rbelow(&g->rng, NCARDS);
        g->hand[p][g->hs[p]++] = c;
        g->draws++;
        return c;
    }
    if (g->nd == 0) {
        if (g->ndisc <= 1) return -1;
        int top = g->disc[g->ndisc - 1];
        memcpy(g->draw, g->disc, sizeof(int) * (g->ndisc - 1));
        g->nd = g->ndisc - 1;
        g->disc[0] = top; g->ndisc = 1;
        shuffle(&g->rng, g->draw, g->nd);
        g->reshuffles++;
    }
    int c = g->draw[--g->nd];
    g->hand[p][g->hs[p]++] = c;
    g->draws++;
    return c;
}

static int has_colour(const game_t *g, int p, int col) {
    for (int i = 0; i < g->hs[p]; i++) if (ccol[g->hand[p][i]] == col) return 1;
    return 0;
}

static int fits(const game_t *g, int p, int c) {
    if (crank[c] == WILD) return 1;
    (void)p;
    if (crank[c] == WD4) return g->wd4_free || !g->top_held;
    return ccol[c] == g->topc || crank[c] == g->topr;
}

static inline int adv(const game_t *g, int p, int k) { return ((p + g->dir * k) % g->n + g->n) % g->n; }

static int pick_colour(game_t *g, int p) {
    if (g->st[p].colour == 0 || g->hs[p] == 0) return rbelow(&g->rng, 4);
    int cnt[5] = {0};
    for (int i = 0; i < g->hs[p]; i++) cnt[ccol[g->hand[p][i]]]++;
    int best = -1, nb = 0, pick = 0;
    for (int c = 0; c < 4; c++) {
        if (cnt[c] > best) { best = cnt[c]; nb = 1; pick = c; }
        else if (cnt[c] == best && rbelow(&g->rng, ++nb) == 0) pick = c;
    }
    return pick;
}

/* Choose which playable card to play. Returns an index into the hand. */
static int choose(game_t *g, int p, const int *idx, int k) {
    const strat_t *s = &g->st[p];
    int cnt[5] = {0}, maj = 0;
    for (int i = 0; i < g->hs[p]; i++) cnt[ccol[g->hand[p][i]]]++;
    for (int c = 1; c < 4; c++) if (cnt[c] > cnt[maj]) maj = c;
    int nextp = adv(g, p, 1), target = s->attack > 0 && g->hs[nextp] <= s->attack;
    double best = -1e18; int pick = idx[0];
    for (int j = 0; j < k; j++) {
        int c = g->hand[p][idx[j]], r = crank[c];
        double sc = (rnext(&g->rng) >> 11) * (1.0 / 9007199254740992.0);
        int wild = r == WILD || r == WD4;
        if (wild && s->wild_last) sc -= 100;
        if (r >= SKIP) sc += 10.0 * s->action;
        if (target && (r == D2 || r == WD4 || r == SKIP || (r == REV && g->n == 2)))
            sc += (r == D2 || r == WD4) ? 300 : 250;
        if (s->sw) sc += s->sw * (wild ? cnt[maj] : cnt[ccol[c]] - 1);
        if (sc > best) { best = sc; pick = idx[j]; }
    }
    return pick;
}

/* Play hand[p][i]. Returns 1 if p has won. */
static int play(game_t *g, int p, int i) {
    int c = g->hand[p][i];
    g->hand[p][i] = g->hand[p][--g->hs[p]];
    if (!g->infinite) g->disc[g->ndisc++] = c;
    g->plays++;
    g->topr = crank[c];
    g->topc = ccol[c] == 4 ? pick_colour(g, p) : ccol[c];
    if (g->hs[p] == 0) return 1;
    switch (crank[c]) {
    case SKIP: g->cur = adv(g, p, 2); break;
    case REV:
        if (g->n == 2) g->cur = p;
        else { g->dir = -g->dir; g->cur = adv(g, p, 1); }
        break;
    case D2: { int v = adv(g, p, 1); draw_one(g, v); draw_one(g, v); g->cur = adv(g, p, 2); break; }
    case WD4: { int v = adv(g, p, 1); for (int t = 0; t < 4; t++) draw_one(g, v); g->cur = adv(g, p, 2); break; }
    default: g->cur = adv(g, p, 1);
    }
    return 0;
}

/* Play one round. Returns the winning seat or -1 if the cap was hit. */
static int run_game(game_t *g, long cap) {
    int n = g->n;
    for (int i = 0; i < NCARDS; i++) g->draw[i] = i;
    shuffle(&g->rng, g->draw, NCARDS);
    g->nd = NCARDS; g->ndisc = 0;
    g->turns = g->plays = g->draws = g->reshuffles = g->passes = g->hoard_turn = 0;
    for (int p = 0; p < n; p++) g->hs[p] = 0;
    g->overflow = 0;
    for (int r = 0; r < g->m; r++)
        for (int p = 0; p < n; p++) g->hand[p][g->hs[p]++] = g->infinite ? (int)rbelow(&g->rng, NCARDS) : g->draw[--g->nd];
    long dealt_draws = 0;
    int c;
    for (;;) {
        c = g->infinite ? (int)rbelow(&g->rng, NCARDS) : g->draw[--g->nd];
        if (crank[c] != WD4) break;
        if (g->infinite) continue;
        g->draw[g->nd++] = c;           /* return it and reshuffle the stock */
        shuffle(&g->rng, g->draw, g->nd);
    }
    if (!g->infinite) g->disc[g->ndisc++] = c;
    g->topr = crank[c]; g->topc = ccol[c];
    g->dir = 1; g->cur = 0;
    switch (crank[c]) {
    case WILD: g->topc = pick_colour(g, 0); break;
    case SKIP: g->cur = 1 % n; break;
    case REV: g->cur = n - 1; if (n > 2) g->dir = -1; break;
    case D2: draw_one(g, 0); draw_one(g, 0); g->cur = 1 % n; break;
    }
    (void)dealt_draws;
    int idx[HANDCAP];
    while (g->turns < cap && !g->overflow) {
        int p = g->cur;
        g->turns++;
        if (g->trace) {
            fprintf(g->trace, "%ld", g->turns);
            for (int q = 0; q < n; q++) fprintf(g->trace, " %d", g->hs[q]);
            fputc('\n', g->trace);
        }
        /* A drawn card can only change this flag if it has the current colour, and then it fits anyway. */
        g->top_held = has_colour(g, p, g->topc);
        int k = 0, other = 0;
        for (int i = 0; i < g->hs[p]; i++) {
            if (fits(g, p, g->hand[p][i])) idx[k++] = i;
            other += crank[g->hand[p][i]] != WD4;
        }
        if (!g->hoard_turn && g->hs[p] > 0 && other == 0) g->hoard_turn = g->turns;
        if (k == 0) {
            int d = draw_one(g, p);
            if (d >= 0 && fits(g, p, d)) { if (play(g, p, g->hs[p] - 1)) return p; }
            else { g->passes++; g->cur = adv(g, p, 1); }
            continue;
        }
        if (play(g, p, choose(g, p, idx, k))) return p;
    }
    return -1;
}

static int parse_strat(const char *s, strat_t *out) {
    return sscanf(s, "%d,%d,%d,%d,%d", &out->wild_last, &out->action, &out->colour, &out->attack, &out->sw) == 5;
}

int main(int argc, char **argv) {
    int n = 4, m = 7, wd4_free = 0, infinite = 0;
    long games = 100000, cap = 100000;
    uint64_t seed = 1;
    const char *spec = "0,0,0,0,0", *tracef = NULL;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-n")) n = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-m")) m = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-g")) games = atol(argv[++i]);
        else if (!strcmp(argv[i], "-s")) seed = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "-S")) spec = argv[++i];
        else if (!strcmp(argv[i], "-c")) cap = atol(argv[++i]);
        else if (!strcmp(argv[i], "-t")) tracef = argv[++i];
        else if (!strcmp(argv[i], "-W")) wd4_free = 1;
        else if (!strcmp(argv[i], "-I")) infinite = 1;
        else { fprintf(stderr, "unknown flag %s\n", argv[i]); return 2; }
    }
    if (n < 2 || n > MAXP || m < 1 || (!infinite && n * m > NCARDS - 1) || m > HANDCAP / 2) { fprintf(stderr, "bad n or m\n"); return 2; }
    build_deck();
    static game_t g;
    memset(&g, 0, sizeof g);
    g.n = n; g.m = m; g.wd4_free = wd4_free; g.infinite = infinite;
    rseed(&g.rng, seed);
    char buf[4096]; strncpy(buf, spec, sizeof buf - 1);
    int ns = 0;
    for (char *tok = strtok(buf, ";"); tok && ns < MAXP; tok = strtok(NULL, ";"))
        if (!parse_strat(tok, &g.st[ns++])) { fprintf(stderr, "bad spec %s\n", tok); return 2; }
    for (int p = ns; p < n; p++) g.st[p] = g.st[ns - 1];
    if (tracef) g.trace = fopen(tracef, "w");

    static long hist[HISTMAX + 1];
    long wins[MAXP] = {0}, unfinished = 0, minturns = 1L << 60, maxturns = 0;
    double st = 0, st2 = 0, sp = 0, sd = 0, sr = 0, sh = 0;
    for (long gi = 0; gi < games; gi++) {
        int w = run_game(&g, cap);
        if (w < 0) { unfinished++; continue; }
        wins[w]++;
        long t = g.turns;
        hist[t < HISTMAX ? t : HISTMAX]++;
        st += t; st2 += (double)t * t; sp += g.plays; sd += g.draws; sr += g.reshuffles;
        sh += g.hoard_turn ? g.hoard_turn : t;
        if (t < minturns) minturns = t;
        if (t > maxturns) maxturns = t;
        if (infinite) continue;
        int tot = g.nd + g.ndisc;
        for (int p = 0; p < n; p++) tot += g.hs[p];
        if (tot != NCARDS) { fprintf(stderr, "card leak %d\n", tot); return 1; }
    }
    if (g.trace) fclose(g.trace);
    long done = games - unfinished;
    double mean = done ? st / done : 0;
    printf("{\"n\":%d,\"m\":%d,\"games\":%ld,\"seed\":%llu,\"spec\":\"%s\",\"wd4_free\":%d,"
           "\"infinite\":%d,\"unfinished\":%ld,\"mean_turns\":%.6f,\"var_turns\":%.6f,\"mean_plays\":%.6f,"
           "\"mean_draws\":%.6f,\"mean_reshuffles\":%.6f,\"mean_hoard_turn\":%.6f,\"min_turns\":%ld,\"max_turns\":%ld,\"wins\":[",
           n, m, games, (unsigned long long)seed, spec, wd4_free, infinite, unfinished, mean,
           done ? st2 / done - mean * mean : 0, done ? sp / done : 0, done ? sd / done : 0,
           done ? sr / done : 0, done ? sh / done : 0, minturns, maxturns);
    for (int p = 0; p < n; p++) printf("%s%ld", p ? "," : "", wins[p]);
    printf("],\"hist\":[");
    int last = HISTMAX;
    while (last > 0 && hist[last] == 0) last--;
    for (int t = 0; t <= last; t++) printf("%s%ld", t ? "," : "", hist[t]);
    printf("]}\n");
    return 0;
}
