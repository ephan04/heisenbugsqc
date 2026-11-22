"""Run fast BP, relay-BP and BP-OSD on every shot. Save per-shot clues, times and outcomes.

  python make_routing_data.py --basis X --p 0.004 --shots 2000 --seed 1 --out route_X_p0.004.npz
"""
import argparse
import os
import time
from multiprocessing import Pool

import numpy as np

from circuit import GROSS_CIRCUITS, dem_matrices, detector_ids, load_circuit, sample
from decoders import bposd_decoder, relay_decoder
from fast_bp import fast_decoder, features, is_correct

_worker = {}   # decoders built once inside each worker process


def init_worker(basis, p):
    circuit = load_circuit(GROSS_CIRCUITS[basis], p)
    H, L, priors = dem_matrices(circuit, basis)
    _worker.update(L=L, bp=fast_decoder(H, priors),
                   relay=relay_decoder(H, priors), bposd=bposd_decoder(H, priors))


def timed(decode, syndrome):
    start = time.perf_counter()
    error = decode(syndrome)
    return error, time.perf_counter() - start


def run_shot(job):
    """All three decoders on one shot."""
    syndrome, truth = job
    w = _worker
    error, bp_time = timed(w["bp"].decode, syndrome)
    clues, converged = features(syndrome, w["bp"], error), bool(w["bp"].converge)   # read before next decode
    bp_ok = is_correct(w["L"], error, truth)
    error, relay_time = timed(w["relay"].decode, syndrome)
    relay_ok = is_correct(w["L"], error, truth)
    error, bposd_time = timed(w["bposd"].decode, syndrome)
    bposd_ok = is_correct(w["L"], error, truth)
    return clues, converged, bp_time, bp_ok, relay_time, relay_ok, bposd_time, bposd_ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--basis", choices=["X", "Z"], default="X")
    parser.add_argument("--p", type=float, default=0.004)
    parser.add_argument("--shots", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--workers", type=int, default=max(1, os.cpu_count() // 2))
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    circuit = load_circuit(GROSS_CIRCUITS[args.basis], args.p)
    det, obs = sample(circuit, args.shots, args.seed)
    det = det[:, detector_ids(circuit, args.basis)]

    print(f"{args.shots} shots, {args.workers} workers: running BP, relay-BP and BP-OSD on each ...", flush=True)
    rows = []
    with Pool(args.workers, initializer=init_worker, initargs=(args.basis, args.p)) as pool:
        for k, row in enumerate(pool.imap(run_shot, zip(det, obs), chunksize=10), 1):
            rows.append(row)
            if k % max(1, args.shots // 10) == 0:
                print(f"  {k}/{args.shots} done", flush=True)

    clues, converged, bp_time, bp_ok, relay_time, relay_ok, bposd_time, bposd_ok = map(np.array, zip(*rows))
    np.savez(args.out, features=clues, converged=converged, bp_time=bp_time, bp_ok=bp_ok,
             relay_time=relay_time, relay_ok=relay_ok, bposd_time=bposd_time, bposd_ok=bposd_ok)
    print(f"saved {args.out}: BP converged on {converged.mean():.1%}, "
          f"relay-BP right on {relay_ok.mean():.1%}, BP-OSD right on {bposd_ok.mean():.1%}")


if __name__ == "__main__":
    main()
