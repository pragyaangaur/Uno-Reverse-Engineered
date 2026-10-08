"""Run the C engine over many configurations in parallel and merge results."""
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "uno")
WORKERS = os.cpu_count() or 4


def run_one(n, m, games, seed, spec="0,0,0,0,0", cap=100000, wd4_free=False, infinite=False):
    args = [BIN, "-n", str(n), "-m", str(m), "-g", str(games), "-s", str(seed), "-S", spec, "-c", str(cap)]
    if wd4_free:
        args.append("-W")
    if infinite:
        args.append("-I")
    out = subprocess.run(args, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def merge(parts):
    """Combine several runs of the same configuration into one result."""
    d = dict(parts[0])
    done = [p["games"] - p["unfinished"] for p in parts]
    tot = sum(done)
    d["games"] = sum(p["games"] for p in parts)
    d["unfinished"] = sum(p["unfinished"] for p in parts)
    for k in ("mean_turns", "mean_plays", "mean_draws", "mean_reshuffles"):
        d[k] = sum(p[k] * w for p, w in zip(parts, done)) / tot
    second = sum((p["var_turns"] + p["mean_turns"] ** 2) * w for p, w in zip(parts, done)) / tot
    d["var_turns"] = second - d["mean_turns"] ** 2
    d["min_turns"] = min(p["min_turns"] for p in parts)
    d["max_turns"] = max(p["max_turns"] for p in parts)
    d["wins"] = [sum(p["wins"][i] for p in parts) for i in range(len(parts[0]["wins"]))]
    L = max(len(p["hist"]) for p in parts)
    d["hist"] = [sum(p["hist"][i] for p in parts if i < len(p["hist"])) for i in range(L)]
    d.pop("seed", None)
    return d


def run_many(configs, games, chunks=WORKERS, base_seed=1000):
    """configs: list of dicts with n, m and optional spec, cap, wd4_free.
    Each config is split into `chunks` independent seeds."""
    jobs = []
    for ci, c in enumerate(configs):
        per = games // chunks
        for k in range(chunks):
            jobs.append((ci, dict(n=c["n"], m=c["m"], games=per, seed=base_seed + 1000 * ci + k,
                                  spec=c.get("spec", "0,0,0,0,0"), cap=c.get("cap", 100000),
                                  wd4_free=c.get("wd4_free", False), infinite=c.get("infinite", False))))
    with ThreadPoolExecutor(WORKERS) as ex:
        outs = list(ex.map(lambda j: (j[0], run_one(**j[1])), jobs))
    grouped = {}
    for ci, o in outs:
        grouped.setdefault(ci, []).append(o)
    return [merge(grouped[ci]) for ci in range(len(configs))]
