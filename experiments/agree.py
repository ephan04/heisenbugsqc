"""Agreement-based escalation: two cheap Relay-BP runs with different seeds; escalate to full Relay-BP
only when they disagree on the logical outcome (or either finds no solution).

  python experiments/agree.py --p 0.004 --shots 3000 --seed 101 --out data/agree_p0.004_s101.npz

Every decoder runs on every shot, so any policy can be scored offline on identical shots
(experiments/agree_report.py). No learned parameters, so every shot is a test shot.
"""
import argparse
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "kit"))
from circuit import GROSS_CIRCUITS, dem_matrices, detector_ids, load_circuit, sample  # noqa: E402
from decoders import relay_decoder  # noqa: E402

FAST = dict(stop_nconv=1, num_sets=50)
DECODERS = ["fast_s0", "fast_s1", "relay_nconv2", "relay"]
CHUNKS_PER_WORKER = 6   # small chunks so slow shots don't leave one worker as a straggler


def work(job):
    basis, p, det, obs, shuffle = job
    order_rng = np.random.default_rng(len(det) * 7919 + int(det.sum()))
    H, L, priors = dem_matrices(load_circuit(GROSS_CIRCUITS[basis], p), basis)
    decs = [relay_decoder(H, priors, seed=0, **FAST), relay_decoder(H, priors, seed=1, **FAST),
            relay_decoder(H, priors, stop_nconv=2), relay_decoder(H, priors)]
    n, m = len(det), len(decs)
    out = dict(correct=np.zeros((n, m), bool), seconds=np.zeros((n, m)), success=np.zeros((n, m), bool),
               iterations=np.zeros((n, m), np.int32), logical=np.zeros((n, m, L.shape[0]), np.uint8))
    for k in range(n):
        order = order_rng.permutation(m) if shuffle else range(m)   # timing check: randomise decoder order
        for j in order:
            dec = decs[j]
            start = time.perf_counter()
            res = dec.decode_detailed(det[k])
            out["seconds"][k, j] = time.perf_counter() - start
            pred = (L @ np.asarray(res.decoding, np.uint8)) % 2
            out["logical"][k, j] = pred
            out["correct"][k, j] = (pred == obs[k]).all()
            out["success"][k, j] = bool(res.success)
            out["iterations"][k, j] = res.iterations
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=float, default=0.004)
    ap.add_argument("--shots", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=101)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", required=True)
    ap.add_argument("--shuffle-order", action="store_true", help="run the decoders in a random order per shot")
    args = ap.parse_args()
    jobs = []
    chunks = args.workers * CHUNKS_PER_WORKER
    for b, basis in enumerate("XZ"):
        circuit = load_circuit(GROSS_CIRCUITS[basis], args.p)
        det, obs = sample(circuit, args.shots, args.seed + b)
        det = det[:, detector_ids(circuit, basis)]
        jobs += [(basis, args.p, det[c], obs[c], args.shuffle_order) for c in np.array_split(np.arange(args.shots), chunks)]
    start = time.time()
    with Pool(args.workers) as pool:
        res = pool.map(work, jobs, chunksize=1)
    half = len(jobs) // 2
    arrays = {key: np.stack([np.concatenate([r[key] for r in res[:half]]),
                             np.concatenate([r[key] for r in res[half:]])], axis=1)   # pair, basis, ...
              for key in res[0]}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.out, **arrays, decoders=DECODERS, p=args.p, shots=args.shots, seed=args.seed,
                        workers=args.workers)
    print(f"{args.out}: {args.shots} pairs at p={args.p} in {time.time() - start:.0f} s")


if __name__ == "__main__":
    main()
