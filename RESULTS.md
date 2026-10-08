# Uno: how short, how long, and how to play

This folder asks the question from 7 October 2026. Given N players who each start with M cards, what can be said about the shortest game, the longest game and the typical game, and what does game theory say about how to play? Everything here was computed on a laptop with a C engine that plays one round of Uno under the official Mattel rules. Every number below can be regenerated with the commands at the end.

The most interesting finding is in section 4. The length of a game with large hands follows an exact rational law, and the official rule for the Wild Draw Four changes that law in a way that is easy to see once you look for it.

## Rules used

The deck is the standard 108 cards. Each colour has one 0, two each of 1 to 9, and two each of Skip, Reverse and Draw Two, and there are four Wilds and four Wild Draw Fours. A player plays one matching card per turn or draws one card, and plays the drawn card at once if it fits. A Draw Two or Draw Four makes the next player draw and lose their turn. A Reverse acts as a Skip with two players. The Wild Draw Four is legal only when the player holds no card of the current colour, and the engine enforces that instead of modelling challenges. There is no stacking. The starting card is flipped and acts on the first player, and a Wild Draw Four flipped at the start goes back into the stock. When the stock runs out the discard pile is reshuffled. A game ends when the first player goes out, and "turns" counts every turn a player actually takes.

The official rules let a player draw instead of playing a card that fits. The simulated players never do this. They always play when they can, so the simulations describe forced play. The shortest-game solver does allow the voluntary draw.

## 1. The shortest game

**The bound.** A player has to play all M cards, one per turn, so the winner takes at least M turns. With two players, every Skip, Reverse, Draw Two and Draw Four gives the turn straight back, so a first player holding M − 1 of them and any last card can win in M turns. With three or more players every play passes the turn to someone else, so at least one other turn falls between two plays by the same player. The winner then needs at least 2M − 1 turns, and the bound is reached when the neighbours relay the turn back with Reverses or Skips.

**What a real deal allows.** The solver in `engine/shortest.c` takes a random deal with every hand and the order of the stock known. It lets all players cooperate to end the round as fast as possible, with any player allowed to be the winner, and finds the exact minimum by iterative deepening A* search. A plain breadth-first search in `engine/check_shortest.py` agrees with it on all 145 test deals.

| Players | Cards | Deals | Bound | Mean fastest finish | Range | Share at the bound |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 3 | 4000 | 3 | 7.08 | 3 to 27 | 2.9% |
| 2 | 5 | 4000 | 5 | 8.95 | 5 to 28 | 0.65% |
| 2 | 7 | 4000 | 7 | 11.47 | 8 to 19 | none |
| 3 | 3 | 4000 | 5 | 7.16 | 5 to 33 | 11.1% |
| 3 | 5 | 2000 | 9 | 10.94 | 9 to 17 | 7.8% |
| 3 | 7 | 2000 | 13 | 14.95 | 13 to 19 | 8.1% |
| 4 | 3 | 4000 | 5 | 8.03 | 5 to 25 | 1.0% |
| 4 | 5 | 1000 | 9 | 12.94 | 9 to 19 | 0.1% |
| 4 | 7 | 1000 | 13 | 17.59 | 14 to 22 | none |

With seven cards and two players the bound of 7 never happened in 4000 deals, because it needs six turn-repeating cards in one hand. Three players reach their bound far more often than two or four. Two neighbours who relay the turn back make it easy, and a three-player deal reaches 2M − 1 in 8% to 11% of cases for every M tested. With five and six players the search hit its node limit on 44 of 400 and 75 of 200 deals, so those results are left out of the table. The solved five-player deals all needed at least 16 turns.

![Fastest finish](figures/shortest.png)

## 2. The longest game

Under the official rules there is no longest game. Any player may draw instead of playing and the discard pile is reshuffled into the stock, so the players can keep a round going for as long as they like.

Forced play is the more interesting case. All 58 million games in the length experiments ended. The length distribution has an exponential tail, so the chance that a game runs past t turns falls like e^(−λt). With four players λ is about 0.048 per turn, one factor of e every 21 turns, and it stays the same for every starting hand from M = 1 to M = 15. The tail belongs to the endgame, when hands are small. A long game is a game stuck in that endgame, so how many cards were dealt does not matter. With seven cards λ is 0.030 for two players and between 0.041 and 0.051 for three to ten.

![Tail](figures/tail.png)

## 3. The typical game

The grid in `results/e1_grid.txt` covers N = 2 to 10 and M = 1 to 15 with 400,000 games of uniformly random legal play per point. With seven cards the mean is 47 turns for two players, 50 for four and 83 for ten. Beyond the first few cards the mean grows linearly in M. The slope is about 2.6 turns per card for two players and 5.4 for four. The standard deviation hardly moves with M, from about 34 to 35 for two players over the whole range, because most of the randomness comes from the endgame.

Seat order matters and the edge does not wear off as M grows. With four players and seven cards the first player wins 26.0% and the last 24.3%. With ten players it is 11.1% against 9.3%. With small hands the dealer, who sits last, does better than the seat before, because a Reverse flipped at the start gives the dealer the first turn. With ten players and one card each the dealer wins 4.5% against 3.4% for the seat before.

![Length grid](figures/length_grid.png)

## 4. The large-hand law and the Draw Four hoard

To study large hands the engine has an infinite deck mode in which every card dealt or drawn is an independent random card with the deck's proportions. This removes the 108 card ceiling so that M can grow to thousands.

**The law.** Suppose every player's hand is large, so every turn is a play, and suppose every card a player ever holds is eventually played. Each card held is a Draw Two with probability 8/108 and a Draw Four with probability 4/108. If the players between them receive R penalty cards, then the cards played contain on average (8/108)(NM + R) Draw Twos and (4/108)(NM + R) Draw Fours, and those hand out exactly R cards:

R = 2 · (8/108)(NM + R) + 4 · (4/108)(NM + R) = (8/27)(NM + R).

So R = 8NM/19 and the number of turns is NM + R = (27/19) NM. The constant depends on the deck alone. It holds for every N and for every strategy that plays the hand down evenly.

**The test.** With the Draw Four made legal at any time, so that the assumption holds, the mean of T/(NM) at M = 1000 is 1.4213 ± 0.0008 for two players, against 27/19 = 1.4211. Larger hands show that this close match is partly luck. `engine/e8_free.py` runs M = 500, 1000, 2000, 4000, 8000 and 16000. For two players T/(NM) is 1.4403, 1.4225, 1.4144, 1.4130, 1.4138 and 1.4164, so it falls below 27/19 and then turns up again near M = 4000. For four players it is 1.3946, 1.3947, 1.3977, 1.4024, 1.4062 and 1.4110, and it rises the whole way. The standard errors are below 0.0018.

Three corrections account for this shape. The first is negative. The cards the losers still hold at the end are never played, and the leftover per loser falls as 0.042, 0.033, 0.026, 0.021, 0.016 and 0.011 of M for two players. Its local slope on a log-log plot steepens from about −0.35 to about −0.47 over this range, so the earlier estimate of M^(−0.37) was too shallow, and the slope may be heading to −1/2. The second is positive. Every game has about 14 turns in which a player draws and cannot play, for every M and for both N, and these add 14/(NM). The third is positive and smaller. Even after the leftover cards are counted as if they had been played, the count comes out above 27/19 by 0.0029 for two players and 0.0025 for four at M = 16000, and this excess shrinks as M grows. The leftover share goes to zero, so the counting argument still gives 27/19 as the limit. The runs agree with it to about 0.005 at M = 16000, and the agreement at M = 1000 should not be read as a four-digit confirmation. Three and six players sit at 1.409 and 1.380 at M = 1000. A strategy that names its best colour or dumps its action cards first gives 1.41 to 1.43 at M = 1000 as well.

**What the official rule does.** Under the official rule a large hand always holds a card of the current colour, so a Draw Four can never be played and every one a player receives stays in the hand. The same counting with Draw Fours left out gives R = (4/27)(M + R) per player. So each player plays 26M/23 cards in the main phase of the game and ends it holding a hoard of M/23 Draw Fours. The fluid equations in `theory/fluid.py` give exactly these values, and a traced two-player game with M = 1000 shows the winner reaching 41 cards, nearly all Draw Fours, against the predicted 43.

The hoard decides the endgame. Once a player is down to Draw Fours they have no card of the current colour, so each Draw Four is legal, and it makes the next player draw four and miss their turn. With two players the hoarder plays every Draw Four in a row. With an even number of players the players two seats apart take turns dumping, and the players between them are skipped every time and only collect cards. Adding M/23 dumping turns for every two players gives a predicted limit of T/(NM) = 26/23 + 1/46 = 53/46 ≈ 1.152 for every even N.

**The endgame on its own.** A full game at M = 32000 takes several seconds, so the endgame was also played by itself. `engine/endgame.c` gives every seat h Draw Fours and nothing else, turns up a random coloured card and plays to the end with the same rules and the same random strategy. It stores a hand as a count for each of the 108 cards, so a turn costs the same for any hand and h can reach a million. If the endgame lasts E·h turns, then with h = M/23 the official limit is T/(NM) = 26/23 + E/(23N).

With an even number of players the endgame follows a fixed pattern. Seat 0 dumps on seat 1. Seat 2 holds no card of the named colour, so it dumps on seat 3, and this goes on round the table. The even seats dump and the odd seats only collect. Every even seat has h cards to dump, so the endgame takes (N/2)h turns and E = N/2. The runs give exactly this for N = 2, 4, 6 and 8, and so T/(NM) = 26/23 + 1/46 = 53/46 for every even N. Each collecting seat ends with its own h Draw Fours and 4h new cards, so a loser holds on average 5N/(46(N − 1)) of M at the end. This is 5/23 = 0.217 for two players and 10/69 = 0.145 for four.

With an odd number of players the dumping seats cannot alternate all the way round the table. The runs settle into (N − 1)/2 dumping seats, each with one collecting seat after it, and one place where two seats that do not dump sit next to each other. The second seat of that pair plays an ordinary card in every round, and its Draw Twos, Skips and Reverses break the pattern from time to time. A clean pattern would need (N + 1)/2 turns per dumped card. The measured E is larger by 0.97 for three players, 1.05 for five, 0.82 for seven and 0.74 for nine. I have not found a closed form for these constants, and they do not look like simple fractions.

| Players | E, endgame turns per hoarded card | Hoard h in the run | Predicted T/(NM) | Predicted leftover per loser, share of M |
| --- | --- | --- | --- | --- |
| 2 | 1 | 10^6 | 53/46 = 1.15217 | 5/23 = 0.2174 |
| 3 | 2.9717 ± 0.0003 | 10^6 | 1.17350 | 0.0949 |
| 4 | 2 | 10^6 | 53/46 = 1.15217 | 10/69 = 0.1449 |
| 5 | 4.0550 ± 0.0003 | 10^6 | 1.16570 | 0.1012 |
| 6 | 3 | 10^6 | 53/46 = 1.15217 | 0.1304 |
| 7 | 4.8164 ± 0.0004 | 10^5 | 1.16035 | 0.1015 |
| 8 | 4 | 10^5 | 53/46 = 1.15217 | 0.1242 |
| 9 | 5.7399 ± 0.0003 | 10^5 | 1.15816 | 0.1028 |

For three players E is 3.197, 2.993, 2.973 and 2.972 at h = 10^3, 10^4, 10^5 and 10^6, so the value has settled. Starting every seat with k = 10 or 300 random cards beside the Draw Fours changes E by about 3k/h, which goes to zero as h grows. These runs are in `results/e7_endgame.txt`.

**Full games up to M = 32000.** `engine/e6_official.py` and `engine/e6b_odd.py` play full games under the official rule with the infinite deck. Each point has between 100 and 800 games, and the standard errors are 0.0002 to 0.0016.

| M | N = 2 | N = 3 | N = 4 | N = 5 |
| --- | --- | --- | --- | --- |
| 1000 | 1.1306 | 1.1805 | 1.1350 | 1.1438 |
| 2000 | 1.1362 | 1.1728 | 1.1390 | 1.1489 |
| 4000 | 1.1410 | 1.1687 | 1.1433 | 1.1523 |
| 8000 | 1.1441 | 1.1684 | 1.1455 | 1.1555 |
| 16000 | 1.1465 | 1.1692 | 1.1477 | 1.1582 |
| 32000 | 1.1482 | 1.1699 | 1.1489 | 1.1603 |
| predicted limit | 1.1522 | 1.1735 | 1.1522 | 1.1657 |

For even N the data now agree with 53/46. A fit of T/(NM) = L + a·M^(−p) with all three numbers free gives L = 1.1527 ± 0.0015 and p = 0.46 ± 0.07 for two players, and L = 1.1527 ± 0.0014 and p = 0.45 ± 0.08 for four. With p fixed at 1/2 the fit gives L = 1.15192 ± 0.00034 for two players and 1.15201 ± 0.00029 for four, which are 0.7 and 0.6 standard errors from 53/46 = 1.15217, with chi-square 0.7 and 2.8 on 4 degrees of freedom. The gap to 53/46 shrinks by a factor close to √2 every time M doubles. The two-player loser holds 0.251, 0.244, 0.235, 0.231, 0.228 and 0.224 of M from M = 1000 to 32000, and this also moves toward 5/23 = 0.217 at roughly the same rate. These fits assume one power-law correction, so they confirm the limit only within that assumption. The script is `analysis/fit_official.py`.

The likely source of the M^(−1/2) correction is the main phase. Hands do not run out of coloured cards at the same moment, because the fluctuations in a hand of size M are of order √M. A hand that is nearly out of coloured cards often lacks the current colour and plays a Draw Four early, and the other hands still hold some coloured cards when the first hand becomes a pure hoard. Each of these effects changes the game by a number of turns of order √M, which is of order M^(−1/2) after division by NM. This explanation is a heuristic and has not been derived.

For odd N the data are consistent with the endgame prediction, but they do not confirm it. Five players rise steadily, and the free fit gives L = 1.1708 ± 0.0040 against the predicted 1.1657, but the approach is slower than M^(−1/2) over this range and a fit with p fixed at 1/2 is poor. Three players are not monotone. T/(NM) falls to 1.1684 at M = 8000 and then rises, and at M = 32000 it is still 0.0036 below the prediction. The three-player leftover share gives better support, because it falls steadily as 0.117, 0.113, 0.108, 0.105, 0.102 and 0.100 toward the predicted 0.095. The endgame seen inside full games also matches. Counted from the first turn at which some player holds only Draw Fours, it lasts 2.95·M/23 turns for three players at M = 32000, against E = 2.97 from the endgame runs, and 4.11·M/23 turns for five against E = 4.06. The remaining gap for odd N is mostly in the main phase, where the even case shows the same slow approach.

A strategy that holds back a class of cards builds a hoard of the same kind. A strategy that holds wilds and saves action cards gives T/(NM) = 0.87 at M = 1000 with the Draw Four free, which is even shorter than the official rule. So the law describes play that keeps the hand balanced, and the Draw Four rule is the one place where the official rules force a hoard on everybody.

![Fluid limit](figures/fluid_limit.png)

![Official limit](figures/official_limit.png)

## 5. Game theory

The strategy family has five settings: whether to hold wilds back while a coloured card fits, whether to play action cards first or last, whether to name a random colour or the colour held most, whether to hit the next player with Draw Twos, Draw Fours and Skips when they hold two cards or fewer, and whether to prefer cards that keep play in the colour held most. Together they give 48 strategies, including uniform random play.

**Two players.** Every pair was played 80,000 times with seats swapped half the time, which gives a symmetric zero-sum matrix game. Its Nash equilibrium found by linear programming is pure: hold wilds, play action cards first, name your best colour and attack when the opponent is low. It beats random play 62.8% of the time. Playing action cards first matters because with two players every action card is a free extra turn. The single most valuable setting is the colour choice, which on average lifts a strategy from 51% to 58% against random play.

**Four players.** Each strategy was played as a single deviant against a field of three copies of every other strategy, 20,000 games per pair over all four seats. One field is stable: hold wilds, treat action cards like any other card, name your best colour, attack and steer towards your colour. The best deviant against it wins 25.04%, which is a fair share. The two-player equilibrium is not stable here, because it wins only 23.6% as a deviant in that field. Against three random players the stable strategy wins 32.8%. Steering towards your colour helps with four players and costs a little with two.

![Tournament](figures/tournament.png)

## Limitations

The simulated players always play when they can, so the length results describe forced play. The strategy family is small and hand built, and a learned policy could do better. The large-hand law is proved for the fluid limit and checked by simulation. The official limits rest on the fluid main phase plus the endgame runs. For even N the full games agree with 53/46 under a one-power-law fit, and for odd N the endgame constants are measured, not derived, and the full games have not yet reached them. The finite-size corrections are fitted and not derived. The infinite deck is an idealisation, and on the real deck M cannot pass 107/N. The shortest-game solver assumes full information and full cooperation, so it measures what a deal allows, not what happens at a table.

## Reproduce

```bash
cd engine && cc -O3 -o uno uno.c -lm && cc -O3 -o shortest shortest.c
python3 e1_grid.py 400000 > ../results/e1_grid.txt
python3 e2_infinite.py 200000 > ../results/e2_infinite.txt
python3 e3_bigm.py > ../results/e3_bigm.txt
python3 e3b_hugem.py > ../results/e3b_hugem.txt
python3 e4_tournament.py 20000 5000 > ../results/e4_tournament.txt
python3 e5_shortest.py > ../results/e5_shortest.txt
python3 e6_official.py > ../results/e6_official.txt
python3 e6b_odd.py > ../results/e6b_odd.txt
cc -O3 -o endgame endgame.c -lm && python3 e7_endgame.py > ../results/e7_endgame.txt
python3 e8_free.py > ../results/e8_free.txt
python3 check_shortest.py
cd .. && python3 theory/fluid.py && python3 analysis/fit_official.py && python3 analysis/figures.py
```
