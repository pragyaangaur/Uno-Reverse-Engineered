# Uno

Started 7 October 2026 from the question of whether anyone has worked out the shortest, longest and typical Uno game for N players with M cards each. The answer was mostly no, so this folder computes it. `RESULTS.md` is the write-up and holds every number worth quoting.

## Where it got to

The engine, the exact shortest-game solver, five experiments, a fluid-limit model and the figures are all done. The main result is a large-hand law. When hands are large and every card is eventually played, a game lasts (27/19)NM turns, and this is confirmed to four digits at M = 1000. The official Wild Draw Four rule makes every hand hoard Draw Fours, M/23 of them, which changes the predicted limit to 53/46 for even N. The data is still rising toward 53/46 at M = 4000, so that limit is supported and not yet confirmed. The odd-N official limit is open. The repo is github.com/pragyaangaur/Uno-Reverse-Engineered, public since 8 October 2026.

## Layout

`engine/uno.c` is the Monte Carlo engine. It takes `-n` players, `-m` cards, `-g` games, `-s` seed and `-S` a strategy spec `wildlast,action,colour,attack,steer`, either once or one per seat separated by `;`. `-I` switches to the infinite deck and `-W` makes the Draw Four legal at any time. It prints one JSON object. `engine/driver.py` splits runs across cores and merges them. `engine/shortest.c` is the IDA* solver, and `engine/check_shortest.py` rebuilds the same deals in Python and checks it by breadth-first search. The scripts `e1` to `e5` are the experiments, and their output is in `results/`. `theory/fluid.py` integrates the fluid equations. `analysis/figures.py` draws `figures/`.

## Traps

The simulated players never draw by choice, so every length result is for forced play. The solver does allow the voluntary draw. The RNG is xoshiro256** seeded by splitmix64, and `check_shortest.py` copies it exactly, so changing either breaks the check. Recompiling `uno` while a background run is using it can kill that run. In infinite mode the hand capacity is `HANDCAP` (16384), and M is limited to half of it. The five- and six-player shortest-game runs hit the node cap on many deals, so they are left out of the table and the figure.

## Next steps

Run M = 8000 and beyond for two and four players to see whether the official limit reaches 53/46. Work out the odd-N endgame. Derive the finite-size corrections, which look like a power of M near −0.37. Replace the hand-built strategy family with a learned policy. Add the voluntary draw as a strategy choice.
