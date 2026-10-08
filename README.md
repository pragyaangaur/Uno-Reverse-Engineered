# Uno Reverse Engineered

How short can a game of Uno be, how long can it last, and how should you play it? This repo answers those questions for N players with M cards each, using a fast C engine for the official rules, an exact solver for the shortest game, and a small piece of new maths about very large hands.

The headline result is a counting law. When hands are large and every card is eventually played, a round lasts (27/19)·N·M turns, and the constant comes from the deck alone. At two players and 1000 cards each the simulation gives 1.4213 ± 0.0008 against 27/19 = 1.4211. The official Wild Draw Four rule breaks the law in an interesting way. A Draw Four is legal only when you hold no card of the current colour, and a big hand always holds one, so every player quietly hoards M/23 Draw Fours and the game ends with one player dumping them on a neighbour who is skipped every time.

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

`make test` checks the solver against an independent breadth-first search and checks the fractions in this README against the code. The experiments are `engine/e1_grid.py` to `engine/e5_shortest.py`, and the commands to regenerate every result are at the end of `RESULTS.md`. Everything runs offline on a laptop.

The engine takes the number of players, the hand size, the number of games, a seed and a strategy for each seat, and prints one JSON object:

```bash
engine/uno -n 4 -m 7 -g 1000000 -s 1
engine/uno -n 2 -m 1000 -g 100 -I -W     # infinite deck, Draw Four always legal
engine/shortest -n 3 -m 7 -g 20 -s 1     # fastest possible game per deal
```

## Licence

MIT
