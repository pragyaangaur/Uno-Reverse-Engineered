# Uno Reverse Engineered

How short can a game of Uno be, how long can it last, and how should you play it? This repo answers those questions for N players with M cards each, using a fast C engine for the official rules, an exact solver for the shortest game, and a small piece of new maths about very large hands.

The headline result is a counting law. When hands are large and every card is eventually played, a round lasts (27/19)·N·M turns, and the constant comes from the deck alone. Runs with up to 16000 cards each approach this value, but slowly, because the cards left in the losers' hands pull the count down and the last few turns of every game push it up. The official Wild Draw Four rule breaks the law in an interesting way. A Draw Four is legal only when you hold no card of the current colour, and a big hand always holds one, so every player quietly hoards M/23 Draw Fours and the game ends with players dumping them on neighbours who are skipped every time. For an even number of players this gives a limit of (53/46)·N·M turns, and games with up to 32000 cards each now agree with it. For an odd number of players the dumping pattern cannot close round the table, and the limit is a measured constant, about 1.1735·N·M for three players.

![Game length per card](figures/fluid_limit.png)

## What is in it

`RESULTS.md` is the full write-up, with every number and its caveats. In short:

- The fastest possible game takes at least M turns with two players and 2M − 1 with more. An exact IDA* solver shows that real 7 card deals almost never allow it. Two-player deals average 11.5 turns at best, and four-player deals average 17.6.
- There is no longest game under the official rules, because a player may always draw. With forced play the chance of a game lasting past t turns falls like e^(−0.048t) for four players, at the same rate for every hand size.
- With 7 cards each a random game lasts 47 turns for two players and 50 for four. The first seat keeps a small edge that does not fade as hands grow.
- Over 48 strategies the two-player Nash equilibrium is a single strategy: hold wilds, play action cards first, name your best colour, and attack a nearly empty hand. It beats random play 62.8% of the time. With four players a different strategy is stable.

## Run it

```bash
make
make test
```

`make test` checks the solver against an independent breadth-first search and checks the fractions in this README against the code. The experiments are `engine/e1_grid.py` to `engine/e8_free.py`, and the commands to regenerate every result are at the end of `RESULTS.md`. Everything runs offline. The runs at M = 32000 take about an hour on four cores.

The engine takes the number of players, the hand size, the number of games, a seed and a strategy for each seat, and prints one JSON object:

```bash
engine/uno -n 4 -m 7 -g 1000000 -s 1
engine/uno -n 2 -m 1000 -g 100 -I -W     # infinite deck, Draw Four always legal
engine/shortest -n 3 -m 7 -g 20 -s 1     # fastest possible game per deal
engine/endgame -n 3 -h 100000 -g 50      # the Draw Four endgame on its own
```

## Paper

The paper is `paper/uno.tex`, with a built copy in `paper/uno.pdf`. Version 1.0.0 of this repository is the version it cites. `submission/` holds the filing notes for Zenodo and arXiv.

## Licence

MIT
