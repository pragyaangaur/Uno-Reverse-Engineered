# Uno

Started 7 October 2026 from the question of whether anyone has worked out the shortest, longest and typical Uno game for N players with M cards each. The answer was mostly no, so this folder computes it. `RESULTS.md` is the write-up and holds every number worth quoting.

## Where it got to

The engine, the exact shortest-game solver, eight experiments, a fluid-limit model, an endgame simulator and the figures are all done. The main result is a large-hand law. When hands are large and every card is eventually played, a game lasts (27/19)NM turns. Runs with the Draw Four always legal approach it to about 0.005 at M = 16000, from below for four players and after a dip below it for two. The official Wild Draw Four rule makes every hand hoard M/23 Draw Fours. For even N the endgame is a fixed pattern, which gives exactly 53/46, and full games up to M = 32000 agree with it within 0.7 standard errors when fitted with an M^(−1/2) correction. For odd N the dumping pattern cannot close round the table. The endgame constants were measured with `engine/endgame.c` (three players 1.1735, five 1.1657, seven 1.1604, nine 1.1582). On 8 October `theory/reduced_endgame.py --real` reproduced every one of them to within its own noise from the seating pattern alone: (N − 1)/2 dumpers at alternating seats, one pair of neighbouring absorbers, and the fastest dumper sets E. They are still computed constants with no closed form, and full games at M = 32000 are still 0.004 to 0.006 below them. The repo is github.com/pragyaangaur/Uno-Reverse-Engineered, public since 8 October 2026.

## Layout

`engine/uno.c` is the Monte Carlo engine. It takes `-n` players, `-m` cards, `-g` games, `-s` seed and `-S` a strategy spec `wildlast,action,colour,attack,steer`, either once or one per seat separated by `;`. `-I` switches to the infinite deck and `-W` makes the Draw Four legal at any time. It prints one JSON object. `engine/driver.py` splits runs across cores and merges them. `engine/endgame.c` plays only the Draw Four endgame, with hands stored as counts per card so the hoard h can reach millions. `engine/shortest.c` is the IDA* solver, and `engine/check_shortest.py` rebuilds the same deals in Python and checks it by breadth-first search. The scripts `e1` to `e8` are the experiments, and their output is in `results/`. `analysis/fit_official.py` fits the official-rule data against the endgame limits. `theory/fluid.py` integrates the fluid equations. `analysis/figures.py` draws `figures/`.

## Traps

The simulated players never draw by choice, so every length result is for forced play. The solver does allow the voluntary draw. The RNG is xoshiro256** seeded by splitmix64, and `check_shortest.py` copies it exactly, so changing either breaks the check. Recompiling `uno` while a background run is using it can kill that run. In infinite mode the hand capacity is `HANDCAP` (65536), and M is limited to half of it. A two-player game at M = 32000 takes about 10 seconds and a four-player game about 20. A shell loop that waits on `pgrep -f` for a run to finish did not start its follow-up job here, so start queued runs by hand. The five- and six-player shortest-game runs hit the node cap on many deals, so they are left out of the table and the figure.

## Next steps

Find a closed form for the odd-N endgame constants if one exists. The reduced model shows that the drifting make-up of the large hands is what has to be solved. Derive the M^(−1/2) finite-size correction, which probably comes from hands running out of coloured cards at times that differ by about √M turns. Run three players beyond M = 32000 to see whether T/(NM) keeps rising toward 1.1735. Replace the hand-built strategy family with a learned policy. Add the voluntary draw as a strategy choice.
