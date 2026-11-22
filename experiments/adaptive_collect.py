"""Stage 1 (discovery) of the noise-adaptive study: per-shot data for every gate setting.

  python experiments/adaptive_collect.py --p 0.005 --shots 3000 --seed 1050 --out data/adapt_p0.005.npz

Every shot: fast Relay-BP seed 0 (50 restarts) and the baseline referee R5 (kit Relay-BP).
Shots seed 0 does not solve in its deterministic first leg also get: seed 1 (50 restarts),
R2 (stop_nconv=2) and R1 (stop_nconv=1, 300 sets). Decoders after seed 0 run in random order.
Missing entries are marked with success = -1. See docs/discussion/09_noise_adaptive_prereg.md.
"""
import argparse
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "kit"))
from circuit import GROSS_CIRCUITS, dem_matrices, detector_ids, load_circuit, sample  # noqa: E402
from decoders import relay_decoder  # noqa: E402

FIRST_LEG = 80
DECODERS = ["s0", "s1", "R5", "R2", "R1"]
SETTINGS = {
    "s0": dict(stop_nconv=1, num_sets=50, seed=0),
    "s1": dict(stop_nconv=1, num_sets=50, seed=1),
    "R5": dict(),                               # kit settings
    "R2": dict(stop_nconv=2),
    "R1": dict(stop_nconv=1, num_sets=300),
}
CHUNKS_PER_WORKER = 6


def work(job):
    basis, p, det, obs, chunk_seed = job
    H, L, priors = dem_matrices(load_circuit(GROSS_CIRCUITS[basis], p), basis)
    decs = {name: relay_decoder(H, priors, **SETTINGS[name]) for name in DECODERS}
    rng = np.random.default_rng(chunk_seed)
    n, m, k = len(det), len(DECODERS), L.shape[0]
    out = dict(success=np.full((n, m), -1, np.int8), correct=np.zeros((n, m), bool), seconds=np.zeros((n, m)),
               iterations=np.zeros((n, m), np.int32), logical=np.zeros((n, m, k), np.uint8),
               weight=det.sum(1).astype(np.int32))

    def run(k_shot, name):
        j = DECODERS.index(name)
        start = time.perf_counter()
        res = decs[name].decode_detailed(det[k_shot])
        out["seconds"][k_shot, j] = time.perf_counter() - start
        pred = (L @ np.asarray(res.decoding, np.uint8)) % 2
        out["logical"][k_shot, j] = pred
        out["correct"][k_shot, j] = (pred == obs[k_shot]).all()
        out["success"][k_shot, j] = int(res.success)
        out["iterations"][k_shot, j] = res.iterations
        return res

    for k_shot in range(n):
        first = run(k_shot, "s0")
        easy = first.success and first.iterations <= FIRST_LEG
        rest = ["R5"] if easy else ["s1", "R5", "R2", "R1"]
        for name in rng.permutation(rest):
            run(k_shot, name)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=float, required=True)
    ap.add_argument("--shots", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    jobs = []
    chunks = args.workers * CHUNKS_PER_WORKER
    for b, basis in enumerate("XZ"):
        circuit = load_circuit(GROSS_CIRCUITS[basis], args.p)
        det, obs = sample(circuit, args.shots, args.seed + b)
        det = det[:, detector_ids(circuit, basis)]
        for c, idx in enumerate(np.array_split(np.arange(args.shots), chunks)):
            jobs.append((basis, args.p, det[idx], obs[idx], args.seed * 1000 + b * 100 + c))
    start = time.time()
    with Pool(args.workers) as pool:
        res = pool.map(work, jobs, chunksize=1)
    half = len(jobs) // 2
    arrays = {key: np.stack([np.concatenate([r[key] for r in res[:half]]),
                             np.concatenate([r[key] for r in res[half:]])], axis=1)
              for key in res[0]}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.out, **arrays, decoders=DECODERS, p=args.p, shots=args.shots, seed=args.seed,
                        workers=args.workers)
    print(f"{args.out}: {args.shots} pairs at p={args.p} in {time.time() - start:.0f} s", flush=True)


if __name__ == "__main__":
    main()
