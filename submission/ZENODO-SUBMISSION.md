# Zenodo record

Do this before the arXiv submission, because the arXiv comments field should carry the DOI that Zenodo gives you. Create one new record at https://zenodo.org/uploads/new that holds both the paper and the code.

## Files to upload

Upload both files from `submission/zenodo/`.

- `uno-preprint.pdf` is the paper, 8 pages, built on 8 October 2026 from `paper/uno.tex`. Its text is identical to the arXiv build.
- `Uno-Reverse-Engineered-v1.0.0.zip` is the repository at tag `v1.0.0`, made with `git archive`. It holds 64 files. It was unpacked into an empty folder, and `make test` built the engine and passed every test there.

Set the PDF as the default preview if Zenodo asks.

## Fields

**Resource type**

Publication, subtype Preprint.

**Title**

```
How long is a game of Uno? A counting law for large hands and the Wild Draw Four hoard
```

**Creators**

```
Gaur, Pragyaan
```

Add your ORCID if you have one.

**Publication date**

```
2026-10-08
```

**Version**

```
1.0.0
```

**Description**

```
This paper studies the length of one round of Uno under the official rules, for N players who each start with M cards.

The fastest possible round takes at least M turns with two players and at least 2M-1 turns with three or more, and both bounds are attained for small M. An exact search over random deals shows that real deals rarely allow them. Under the official rules a round has no maximum length, and under forced play the probability that a round lasts more than t turns decays exponentially in t at a rate that does not depend on M.

The main result concerns very large hands. If every card a player ever holds is eventually played, a round lasts (27/19)NM turns to first order, and the constant depends only on the composition of the deck. The official rule that a Wild Draw Four may only be played by a player who holds no card of the current colour breaks this law. Every large hand hoards Wild Draw Fours, M/23 of them per player, and the round ends with a dumping endgame. For an even number of players this gives (53/46)NM turns. For an odd number of players the endgame settles into a seating pattern whose turn rate is computed numerically. Simulations with up to 32,000 cards per hand support these limits.

The paper also solves a small strategy game. With two players the Nash equilibrium over a family of 48 strategies is a single pure strategy that wins 62.8% of rounds against uniformly random play.

The record holds the preprint and version 1.0.0 of the code and data: a C engine for the official rules, an exact solver for the shortest round, an endgame simulator, the experiment scripts with their raw output, and the figure scripts. The code is under the MIT licence and is developed at https://github.com/pragyaangaur/Uno-Reverse-Engineered.
```

**License**

Creative Commons Attribution 4.0 International (CC BY 4.0). This matches the licence to choose on arXiv. The code inside the zip keeps its own MIT licence in its `LICENSE` file, which the description states.

**Keywords**

```
Uno
card games
game length
conservation law
fluid limit
Markov chain
Nash equilibrium
recreational mathematics
```

**Related works**

| Relation | Identifier | Resource type |
| --- | --- | --- |
| is supplemented by | `https://github.com/pragyaangaur/Uno-Reverse-Engineered` | Software |
| references | `10.1016/j.tcs.2013.11.023` | Journal article |

**Languages**

English.

## After publishing

1. Copy the DOI Zenodo shows, which looks like `10.5281/zenodo.NNNNNNNN`. It goes in the arXiv comments field.
2. When arXiv announces the paper, edit this record and add one more related work: relation "is identical to", identifier `arXiv:YYMM.NNNNN`, resource type Preprint. Zenodo lets you edit metadata after publishing without a new version.
3. Add the DOI badge to `README.md` and note the DOI in `AGENTS.md`.
