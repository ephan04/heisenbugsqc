"""Quick viability test of a light ML noise detector that picks the gate's settings.

  python experiments/noise_ml.py

1. Train: shots at p uniform in [0.002, 0.007] (fresh seeds). Features per basis shot: alarm
   counts per (cycle, check type), 24 numbers. Models predict log p.
   Baseline: invert the mean total alarm count (no learning beyond a calibration curve).
2. Estimate p on held-out shots: single shot, and averaged over the last W shots.
3. Routing replay: the discovery shots (data/adapt_p*.npz) are regenerated from their seeds and
   routed by the estimated p, using the per-shot outcomes already recorded for every setting.
   Settings were chosen on these same shots, so absolute numbers are optimistic; the comparison
   that matters is estimated p vs true p.
4. Drift: a stream whose noise level changes every 300 pairs.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "kit"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from circuit import GROSS_CIRCUITS, load_circuit, sample  # noqa: E402
from adaptive_select import policy  # noqa: E402

LEVELS = [0.003, 0.004, 0.0045, 0.005, 0.0055, 0.006]
DISCOVERY = {0.003: (10000, 1030), 0.004: (6000, 1040), 0.0045: (3000, 1045), 0.005: (3000, 1050),
             0.0055: (1500, 1055), 0.006: (1000, 1060)}
# Revised table (discussion/13): full referee up to 0.005 with a small cap, cheap referees above.
TABLE = {0.003: (10, "R5"), 0.004: (10, "R5"), 0.0045: (10, "R5"), 0.005: (10, "R5"),
         0.0055: (5, "R2"), 0.006: (5, "R1")}
WINDOWS = [1, 10, 100]


def block_index(circuit):
    """Feature column of every detector: its check type and its cycle (count of earlier same-type detectors // 72)."""
    coords = circuit.get_detector_coordinates()
    seen, cols = {0: 0, 1: 0}, []
    for d in range(circuit.num_detectors):
        t = int(coords[d][0])
        cols.append((t, seen[t] // 72))
        seen[t] += 1
    keys = sorted(set(cols))
    return np.array([keys.index(c) for c in cols]), len(keys)


CIRCUIT0 = {b: load_circuit(GROSS_CIRCUITS[b]) for b in "XZ"}
BLOCKS = {b: block_index(CIRCUIT0[b]) for b in "XZ"}


def features(det, basis):
    idx, n = BLOCKS[basis]
    out = np.zeros((len(det), n))
    for k in range(n):
        out[:, k] = det[:, idx == k].sum(1)
    return out


def shots(p, n, seed):
    """Features of n pair-shots: X half and Z half, sampled like the kit (seed for X, seed + 1 for Z)."""
    return [features(sample(load_circuit(GROSS_CIRCUITS[b], p), n, seed + k)[0], b) for k, b in enumerate("XZ")]


def main():
    rng = np.random.default_rng(0)
    # ---- 1. training and test data (seeds 9000+ never used elsewhere)
    t0 = time.time()
    train_p = np.round(np.linspace(0.002, 0.007, 41), 6)
    Xtr = {b: [] for b in "XZ"}; ytr = []
    for i, p in enumerate(train_p):
        fx, fz = shots(p, 1500, 9000 + 10 * i)
        Xtr["X"].append(fx); Xtr["Z"].append(fz); ytr.append(np.full(len(fx), p))
    Xtr = {b: np.vstack(v) for b, v in Xtr.items()}; ytr = np.concatenate(ytr)
    print(f"training data: {len(ytr)} pair-shots at {len(train_p)} noise levels in {time.time() - t0:.0f} s")

    def calib_counter():
        tot = Xtr["X"].sum(1) + Xtr["Z"].sum(1)
        means = np.array([tot[ytr == p].mean() for p in train_p])
        return lambda FX, FZ: np.interp(FX.sum(1) + FZ.sum(1), means, train_p), means

    count_est, means = calib_counter()
    Xboth = np.hstack([Xtr["X"], Xtr["Z"]])
    models = {
        "ridge": make_pipeline(StandardScaler(), Ridge(1.0)),
        "mlp": make_pipeline(StandardScaler(), MLPRegressor(hidden_layer_sizes=(32, 16), max_iter=300, random_state=0, early_stopping=True)),
    }
    for name, m in models.items():
        t = time.time(); m.fit(Xboth, np.log(ytr)); print(f"  trained {name} in {time.time() - t:.1f} s")
    est = {"count": count_est}
    for name, m in models.items():
        est[name] = (lambda m: lambda FX, FZ: np.exp(m.predict(np.hstack([FX, FZ]))))(m)

    # ---- 2. accuracy of the estimate on fresh shots
    print("\nrelative error of the estimated p (mean |p_hat - p| / p), fresh shots, window = last W pairs")
    print(f"  {'true p':>7s} {'method':>6s} " + " ".join(f"{'W=' + str(w):>8s}" for w in WINDOWS))
    acc = {}
    for j, p in enumerate(LEVELS):
        FX, FZ = shots(p, 3000, 9800 + 10 * j)
        for name, f in est.items():
            single = f(FX, FZ)
            cells = []
            for w in WINDOWS:
                # average in log space over the trailing window (the count method averages counts first)
                if name == "count":
                    tot = np.convolve(FX.sum(1) + FZ.sum(1), np.ones(w) / w, "valid")
                    e = np.interp(tot, means, train_p)
                else:
                    e = np.exp(np.convolve(np.log(single), np.ones(w) / w, "valid"))
                cells.append(float(np.mean(np.abs(e - p)) / p))
            acc[(p, name)] = cells
            print(f"  {p:7.4f} {name:>6s} " + " ".join(f"{c:8.1%}" for c in cells))

    # ---- latency of one estimate
    FX1, FZ1 = shots(0.004, 1, 9999)
    for name, f in est.items():
        t = time.perf_counter()
        for _ in range(200):
            f(FX1, FZ1)
        print(f"  {name}: {(time.perf_counter() - t) / 200 * 1e6:.0f} us per estimate (python, one shot)")

    # ---- 3. routing replay on the discovery shots
    data = {p: dict(np.load(f"data/adapt_p{p}.npz", allow_pickle=True)) for p in LEVELS}
    for d in data.values():
        d["decoders"] = list(d["decoders"])
    outcome = {p: {s: policy(data[p], *s)[:2] for s in set(TABLE.values())} for p in LEVELS}
    feats = {p: shots(p, *DISCOVERY[p]) for p in LEVELS}
    base = {p: ((~data[p]["correct"][..., data[p]["decoders"].index("R5")]).any(1),
                data[p]["seconds"][..., data[p]["decoders"].index("R5")].sum(1)) for p in LEVELS}
    grid = np.array(sorted(TABLE))

    def route(p, p_hat, bias=1.0):
        setting = [TABLE[grid[np.abs(grid - q * bias).argmin()]] for q in p_hat]
        wrong = np.array([outcome[p][s][0][k] for k, s in enumerate(setting)])
        secs = np.array([outcome[p][s][1][k] for k, s in enumerate(setting)])
        return wrong, secs, np.mean([s == TABLE[p] for s in setting])

    def windowed(f, FX, FZ, w):
        if w == 1:
            return f(FX, FZ)
        lg = np.log(f(FX, FZ)) if f is not count_est else None
        if f is count_est:
            tot = FX.sum(1) + FZ.sum(1)
            c = np.concatenate([np.cumsum(tot)[:w] / np.arange(1, w + 1), np.convolve(tot, np.ones(w) / w, "valid")[1:]])
            return np.interp(c, means, train_p)
        c = np.concatenate([np.cumsum(lg)[:w] / np.arange(1, w + 1), np.convolve(lg, np.ones(w) / w, "valid")[1:]])
        return np.exp(c)

    print("\nrouting replay on discovery shots: failed pairs and mean time vs the kit's Relay-BP (R5)")
    print("  'oracle' = settings for the true p; others route each pair by its estimated p")
    routes = [("oracle", None, 0, 1.0)] + [(f"{n} W={w}", est[n], w, 1.0) for n in ["count", "mlp"] for w in WINDOWS] \
        + [("mlp W=1 +10%", est["mlp"], 1, 1.10), ("count W=10 +5%", est["count"], 10, 1.05)]
    replay = {}
    for p in LEVELS:
        bf, bs = base[p]
        print(f"\n  p={p}  Relay-BP {bf.sum()} failed pairs of {len(bf)}, mean {bs.mean() * 1e3:.0f} ms")
        for label, f, w, bias in routes:
            if f is None:
                wrong, secs = outcome[p][TABLE[p]]; right = 1.0
            else:
                wrong, secs, right = route(p, windowed(f, *feats[p], w), bias)
            replay[(p, label)] = (int(wrong.sum()), float(secs.mean() / bs.mean()), float(right))
            print(f"    {label:>15s}: fails {wrong.sum():4d} ({wrong.sum() / max(bf.sum(), 1):.2f}x)  "
                  f"time {secs.mean() / bs.mean():.2f}x  p99 {np.percentile(secs, 99) / np.percentile(bs, 99):.2f}x  "
                  f"right setting {right:.0%}")

    # ---- 4. drift: noise changes every 300 pairs
    order = [0.003, 0.005, 0.004, 0.006, 0.0045, 0.0055, 0.003]
    used = {p: 0 for p in LEVELS}; seg = []
    for p in order:
        n = min(300, len(outcome[p][TABLE[p]][0]) - used[p])
        seg.append((p, used[p], used[p] + n)); used[p] += n
    print("\ndrift stream: noise changes every 300 pairs, " + " -> ".join(str(p) for p, _, _ in seg))
    for label, f, w in [("oracle", None, 0), ("count W=10", est["count"], 10), ("count W=100", est["count"], 100),
                        ("mlp W=10", est["mlp"], 10)]:
        tot_w = tot_b = 0; t_g = t_b = 0.0; ok = []
        if f is not None:
            FX = np.vstack([feats[p][0][a:b] for p, a, b in seg]); FZ = np.vstack([feats[p][1][a:b] for p, a, b in seg])
            p_hat = windowed(f, FX, FZ, w)
        k = 0
        for p, a, b in seg:
            for i in range(a, b):
                s = TABLE[p] if f is None else TABLE[grid[np.abs(grid - p_hat[k]).argmin()]]
                tot_w += outcome[p][s][0][i]; t_g += outcome[p][s][1][i]
                tot_b += base[p][0][i]; t_b += base[p][1][i]; ok.append(s == TABLE[p]); k += 1
        print(f"  {label:>11s}: fails {tot_w} vs Relay-BP {tot_b}  time {t_g / t_b:.2f}x  right setting {np.mean(ok):.0%}")

    Path("results/noise_ml.json").write_text(json.dumps(
        {"estimate_error": {f"{p}|{n}": v for (p, n), v in acc.items()},
         "replay": {f"{p}|{n}": v for (p, n), v in replay.items()}}, indent=1))


if __name__ == "__main__":
    main()
