"""Gate routed by a noise detector (alarm count, or MLP on a subset) vs kit BP-OSD and Relay-BP, same shots.

  python experiments/bposd_compare.py --p 0.004 --shots 6000 --seed 5040 --out data/compare_p0.004.npz

Pre-registered in docs/discussion/14_bposd_compare_prereg.md.
"""
import argparse
import pickle
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "kit"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from circuit import GROSS_CIRCUITS, dem_matrices, detector_ids, load_circuit, sample  # noqa: E402
from decoders import bposd_decoder, relay_decoder  # noqa: E402
from gate import AgreementGate  # noqa: E402
from noise_ml import TABLE, features  # noqa: E402

DECODERS = ["bposd", "relay", "gate_count", "gate_mlp"]
SETTINGS = sorted(set(TABLE.values()))
GRID = np.array(sorted(TABLE))
WINDOW = 10
CHUNKS_PER_WORKER = 6
DETECTOR = Path("data/noise_detector.pkl")


def train_detector():
    """Alarm-count calibration and the MLP, trained on seeds 9000+ (the same recipe as noise_ml.py)."""
    if DETECTOR.exists():
        return pickle.loads(DETECTOR.read_bytes())
    from sklearn.neural_network import MLPRegressor
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from noise_ml import shots
    train_p = np.round(np.linspace(0.002, 0.007, 41), 6)
    FX, FZ, y = [], [], []
    for i, p in enumerate(train_p):
        fx, fz = shots(p, 1500, 9000 + 10 * i)
        FX.append(fx); FZ.append(fz); y.append(np.full(len(fx), p))
    FX, FZ, y = np.vstack(FX), np.vstack(FZ), np.concatenate(y)
    tot = FX.sum(1) + FZ.sum(1)
    means = np.array([tot[y == p].mean() for p in train_p])
    mlp = make_pipeline(StandardScaler(), MLPRegressor(hidden_layer_sizes=(32, 16), max_iter=300, random_state=0,
                                                       early_stopping=True)).fit(np.hstack([FX, FZ]), np.log(y))
    det = dict(train_p=train_p, means=means, mlp=mlp)
    DETECTOR.write_bytes(pickle.dumps(det))
    return det


def trailing_mean(x, w):
    c = np.cumsum(x)
    out = c.copy()
    out[w:] = c[w:] - c[:-w]
    return out / np.minimum(np.arange(1, len(x) + 1), w)


def estimates(det, FX, FZ):
    count = np.interp(trailing_mean(FX.sum(1) + FZ.sum(1), WINDOW), det["means"], det["train_p"])
    mlp = np.exp(trailing_mean(det["mlp"].predict(np.hstack([FX, FZ])), WINDOW))
    return count, mlp


def setting_index(p_hat):
    return np.array([SETTINGS.index(TABLE[GRID[np.abs(GRID - q).argmin()]]) for q in p_hat], np.int8)


def work(job):
    basis, p, det, obs, s_count, s_mlp, use_mlp, chunk_seed = job
    H, L, priors = dem_matrices(load_circuit(GROSS_CIRCUITS[basis], p), basis)
    gates = [AgreementGate(H, L, priors, K=K, referee=ref) for K, ref in SETTINGS]
    gates_mlp = [AgreementGate(H, L, priors, K=K, referee=ref) for K, ref in SETTINGS]
    base = {"bposd": bposd_decoder(H, priors), "relay": relay_decoder(H, priors)}
    rng = np.random.default_rng(chunk_seed)
    n = len(det)
    out = dict(correct=np.ones((n, 4), bool), seconds=np.full((n, 4), np.nan))
    for k in range(n):
        decs = dict(base, gate_count=gates[s_count[k]])
        if use_mlp[k]:
            decs["gate_mlp"] = gates_mlp[s_mlp[k]]
        for name in rng.permutation(list(decs)):
            j = DECODERS.index(name)
            start = time.perf_counter()
            error = decs[name].decode(det[k])
            out["seconds"][k, j] = time.perf_counter() - start
            out["correct"][k, j] = (((L @ np.asarray(error, np.uint8)) % 2) == obs[k]).all()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=float, required=True)
    ap.add_argument("--shots", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    detector = train_detector()
    raw, feats = {}, {}
    for b, basis in enumerate("XZ"):
        circuit = load_circuit(GROSS_CIRCUITS[basis], args.p)
        d, o = sample(circuit, args.shots, args.seed + b)
        feats[basis] = features(d, basis)
        raw[basis] = (d[:, detector_ids(circuit, basis)], o)
    t = time.perf_counter()
    p_count, p_mlp = estimates(detector, feats["X"], feats["Z"])
    est_us = (time.perf_counter() - t) / args.shots * 1e6
    s_count, s_mlp = setting_index(p_count), setting_index(p_mlp)
    use_mlp = np.arange(args.shots) < args.shots // 3
    jobs = []
    for b, basis in enumerate("XZ"):
        det, obs = raw[basis]
        for c, idx in enumerate(np.array_split(np.arange(args.shots), args.workers * CHUNKS_PER_WORKER)):
            jobs.append((basis, args.p, det[idx], obs[idx], s_count[idx], s_mlp[idx], use_mlp[idx],
                         args.seed * 1000 + b * 100 + c))
    start = time.time()
    with Pool(args.workers) as pool:
        res = pool.map(work, jobs, chunksize=1)
    half = len(jobs) // 2
    arrays = {key: np.stack([np.concatenate([r[key] for r in res[:half]]),
                             np.concatenate([r[key] for r in res[half:]])], axis=1) for key in res[0]}
    np.savez_compressed(args.out, **arrays, p=args.p, shots=args.shots, seed=args.seed, decoders=DECODERS,
                        p_count=p_count, p_mlp=p_mlp, s_count=s_count, s_mlp=s_mlp, use_mlp=use_mlp,
                        settings=np.array(SETTINGS, dtype=object), estimate_us_per_pair=est_us)
    print(f"{args.out}: {args.shots} pairs at p={args.p} in {time.time() - start:.0f} s "
          f"(estimators {est_us:.1f} us per pair, batched)", flush=True)


if __name__ == "__main__":
    main()
