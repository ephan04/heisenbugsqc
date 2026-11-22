"""Run every candidate tier on the same shots and save per-shot correctness, time and BP features.

  python experiments/collect.py --p 0.004 --shots 1500 --seed 11 --out data/p0.004_s11.npz

One row per (basis, shot). Downstream scripts simulate any routing policy from this table
without re-decoding.
"""
import argparse
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "kit"))
from ldpc import BpDecoder, BpLsdDecoder  # noqa: E402

from circuit import GROSS_CIRCUITS, dem_matrices, detector_ids, load_circuit, sample  # noqa: E402
from decoders import bposd_decoder, relay_decoder  # noqa: E402

LIGHT_ITERS = 80
TIERS = ["bp", "lsd", "bposd", "relay_fast", "relay"]


def build(H, priors):
    common = dict(error_channel=list(priors), bp_method="minimum_sum", ms_scaling_factor=1.0)
    return {
        "bp": BpDecoder(H, max_iter=LIGHT_ITERS, **common),
        "lsd": BpLsdDecoder(H, max_iter=LIGHT_ITERS, lsd_order=0, **common),
        "bposd": bposd_decoder(H, priors),
        "relay_fast": relay_decoder(H, priors, stop_nconv=1, num_sets=50),
        "relay": relay_decoder(H, priors),
    }


def features(bp, H, priors, syndrome, error):
    llr = np.asarray(bp.log_prob_ratios)
    abs_llr = np.abs(llr)
    weights = np.log((1 - priors) / priors)
    return [
        float(bp.converge), float(bp.iter), float(syndrome.sum()), float(error.sum()),
        float(weights @ error), float(abs_llr.min()), float((abs_llr < 1).sum()),
        float((abs_llr < 3).sum()), float(((H @ error) % 2 != syndrome).sum()),
    ]


BP_FEATURES = ["converged", "iters", "syndrome_wt", "correction_wt", "correction_cost",
               "min_abs_llr", "n_llr_lt1", "n_llr_lt3", "residual_wt"]
RELAY_FEATURES = ["rf_success", "rf_iters", "rf_weight", "rf_cost", "rf_min_abs_post", "rf_n_post_lt1"]
FEATURE_NAMES = BP_FEATURES + RELAY_FEATURES
N_BP = len(BP_FEATURES)


def relay_features(result, priors, error):
    """Diagnostics of the fast Relay-BP run: did it stop on a solution, how long it searched, how costly it is."""
    post = np.abs(np.log(np.clip(np.asarray(result.posterior_ratios, float), 1e-300, None)))
    weights = np.log((1 - priors) / priors)
    return [float(result.success), float(result.iterations), float(error.sum()), float(weights @ error),
            float(post.min()), float((post < 1).sum())]


def work(job):
    basis, p, det, obs = job
    circuit = load_circuit(GROSS_CIRCUITS[basis], p)
    H, L, priors = dem_matrices(circuit, basis)
    decs = build(H, priors)
    n = len(det)
    correct = np.zeros((n, len(TIERS)), bool)
    seconds = np.zeros((n, len(TIERS)))
    feats = np.zeros((n, len(FEATURE_NAMES)))
    for k in range(n):
        for j, name in enumerate(TIERS):
            start = time.perf_counter()
            if name == "relay_fast":
                result = decs[name].decode_detailed(det[k])
                error = np.asarray(result.decoding, np.uint8)
            else:
                error = np.asarray(decs[name].decode(det[k]), np.uint8)
            seconds[k, j] = time.perf_counter() - start
            correct[k, j] = not ((L @ error) % 2 != obs[k]).any()
            if name == "bp":
                feats[k, :N_BP] = features(decs["bp"], H, priors, det[k], error)
            elif name == "relay_fast":
                feats[k, N_BP:] = relay_features(result, priors, error)
    return correct, seconds, feats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=float, default=0.004)
    ap.add_argument("--shots", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    jobs, basis_col = [], []
    for b, basis in enumerate("XZ"):
        circuit = load_circuit(GROSS_CIRCUITS[basis], args.p)
        det, obs = sample(circuit, args.shots, args.seed + b)
        det = det[:, detector_ids(circuit, basis)]
        for chunk in np.array_split(np.arange(args.shots), args.workers):
            jobs.append((basis, args.p, det[chunk], obs[chunk]))
            basis_col.append(np.full(len(chunk), b))
    start = time.time()
    with Pool(args.workers) as pool:
        results = pool.map(work, jobs)
    correct, seconds, feats = (np.concatenate(x) for x in zip(*results))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.out, correct=correct, seconds=seconds, features=feats,
                        basis=np.concatenate(basis_col), tiers=TIERS, feature_names=FEATURE_NAMES,
                        p=args.p, shots=args.shots, seed=args.seed)
    print(f"{args.out}: {len(correct)} rows in {time.time() - start:.0f} s")
    for j, name in enumerate(TIERS):
        print(f"  {name:10s} wrong {(~correct[:, j]).sum():4d}  mean {seconds[:, j].mean() * 1e3:7.1f} ms  "
              f"p99 {np.percentile(seconds[:, j], 99) * 1e3:7.0f} ms")


if __name__ == "__main__":
    main()
