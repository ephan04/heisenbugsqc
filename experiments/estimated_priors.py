"""Gate built from the estimated noise level vs the gate built from the true p, live on the same shots.

  python experiments/estimated_priors.py data/compare_p0.003.npz --out data/estprior_p0.003.npz

Pre-registered in discussion/27_estimated_priors_prereg.md.
"""
import argparse
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "kit"))
sys.path.insert(0, str(ROOT / "experiments"))
from circuit import GROSS_CIRCUITS, dem_matrices, detector_ids, load_circuit, sample  # noqa: E402
from gate import AgreementGate  # noqa: E402

DECODERS = ["gate_true", "gate_est"]
CHUNKS_PER_WORKER = 6
_cache = {}


def gate(basis, p, setting):
    """One gate per (basis, p, setting), built once per worker."""
    key = (basis, p, setting)
    if key not in _cache:
        if (basis, p) not in _cache:
            _cache[(basis, p)] = dem_matrices(load_circuit(GROSS_CIRCUITS[basis], p), basis)
        H, L, priors = _cache[(basis, p)]
        _cache[key] = AgreementGate(H, L, priors, K=setting[0], referee=setting[1])
    return _cache[key]


def work(job):
    basis, p, det, obs, p_est, settings, chunk_seed = job
    rng = np.random.default_rng(chunk_seed)
    n = len(det)
    out = dict(correct=np.ones((n, 2), bool), seconds=np.zeros((n, 2)))
    for k in range(n):
        decs = {"gate_true": gate(basis, p, settings[k]), "gate_est": gate(basis, p_est[k], settings[k])}
        L = _cache[(basis, p)][1]
        for name in rng.permutation(DECODERS):
            j = DECODERS.index(name)
            start = time.perf_counter()
            error = decs[name].decode(det[k])
            out["seconds"][k, j] = time.perf_counter() - start
            out["correct"][k, j] = (((L @ np.asarray(error, np.uint8)) % 2) == obs[k]).all()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("compare", help="a data/compare_p*.npz run: its shots, estimates and settings are reused")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    c = np.load(args.compare, allow_pickle=True)
    p, shots, seed = float(c["p"]), int(c["shots"]), int(c["seed"])
    settings = [tuple((int(K), str(r))) for K, r in c["settings"]]
    s = [settings[i] for i in c["s_count"]]
    p_est = np.round(c["p_count"], 4)
    jobs = []
    for b, basis in enumerate("XZ"):
        circuit = load_circuit(GROSS_CIRCUITS[basis], p)
        det, obs = sample(circuit, shots, seed + b)
        det = det[:, detector_ids(circuit, basis)]
        for i, idx in enumerate(np.array_split(np.arange(shots), args.workers * CHUNKS_PER_WORKER)):
            jobs.append((basis, p, det[idx], obs[idx], p_est[idx], [s[k] for k in idx], seed * 1000 + b * 100 + i))
    start = time.time()
    with Pool(args.workers) as pool:
        res = pool.map(work, jobs, chunksize=1)
    half = len(jobs) // 2
    arrays = {key: np.stack([np.concatenate([r[key] for r in res[:half]]),
                             np.concatenate([r[key] for r in res[half:]])], axis=1) for key in res[0]}
    np.savez_compressed(args.out, **arrays, p=p, shots=shots, seed=seed, decoders=DECODERS, p_est=p_est)
    print(f"{args.out}: {shots} pairs at p={p} in {time.time() - start:.0f} s", flush=True)


if __name__ == "__main__":
    main()
