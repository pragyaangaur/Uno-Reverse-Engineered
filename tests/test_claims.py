"""Checks that the claims in README.md and RESULTS.md still hold for the code."""
import json
import os
import subprocess
import sys
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "theory"))
import fluid  # noqa: E402

UNO = os.path.join(ROOT, "engine", "uno")


def run(*args):
    return json.loads(subprocess.run([UNO, *map(str, args)], capture_output=True, text=True, check=True).stdout)


def test_fluid_limits_are_the_stated_fractions():
    tau_free, _, _ = fluid.fluid(True)
    tau_off, x_end, _ = fluid.fluid(False)
    assert abs(tau_free - 27 / 19) < 1e-4, tau_free
    assert abs(tau_off - 26 / 23) < 1e-4, tau_off
    assert abs(x_end[fluid.D4] - 1 / 23) < 1e-4, x_end[fluid.D4]


def test_counting_argument():
    # R = (32/108)(1 + R) per unit of NM, so turns = 1 + R = 27/19
    R = Fraction(32, 108) / (1 - Fraction(32, 108))
    assert 1 + R == Fraction(27, 19)
    # official rule: Draw Fours held back, R = (16/108)(1 + R), plays = (104/108)(1 + R)
    R = Fraction(16, 108) / (1 - Fraction(16, 108))
    assert Fraction(104, 108) * (1 + R) == Fraction(26, 23)
    assert Fraction(4, 108) * (1 + R) == Fraction(1, 23)
    assert Fraction(26, 23) + Fraction(1, 46) == Fraction(53, 46)


def test_no_game_beats_the_turn_bounds():
    # the engine conserves all 108 cards and exits non-zero on a leak
    r = run("-n", 2, "-m", 7, "-g", 300000, "-s", 1)
    assert r["unfinished"] == 0
    assert r["min_turns"] >= 7
    r = run("-n", 4, "-m", 7, "-g", 300000, "-s", 1)
    assert r["min_turns"] >= 13


def test_seat_zero_has_the_edge_with_four_players():
    r = run("-n", 4, "-m", 7, "-g", 400000, "-s", 3)
    w = r["wins"]
    assert w[0] > w[3], w


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
