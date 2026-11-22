"""Time Relay-BP, BP-OSD, the ML router and the agreement gate on identical fresh shots.

  python tail_bench.py --p 0.004 --models X.joblib Z.joblib --out tail_p0.004.npz
Same shots as evaluate_router.py (seed 1000 for X, 1001 for Z). Decoder order is shuffled per shot.
Saves per-shot seconds and failures, shape (shots, 2 bases), for each decoder, plus gate and router paths.
"""
import argparse
import random
import time

import joblib
import numpy as np

from circuit import GROSS_CIRCUITS, dem_matrices, detector_ids, load_circuit, sample
from decoders import bposd_decoder, relay_decoder
from evaluate_router import RoutedDecoder
from gate import AgreementGate, settings_for

NAMES = ["relay", "bposd", "router", "gate"]

parser = argparse.ArgumentParser()
parser.add_argument("--p", type=float, required=True)
parser.add_argument("--shots", type=int, default=1000)
parser.add_argument("--seed", type=int, default=1000)
parser.add_argument("--t", type=float, default=0.7)
parser.add_argument("--models", nargs=2, required=True)
parser.add_argument("--table", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

K, referee = settings_for(args.p, args.table)
print(f"p={args.p}: gate K={K} referee={referee}, router t={args.t}", flush=True)
secs = {n: np.zeros((args.shots, 2)) for n in NAMES}
fail = {n: np.zeros((args.shots, 2), bool) for n in NAMES}
gate_path = np.empty((args.shots, 2), dtype=object)
order_rng = random.Random(12345)

for j, (basis, model_path) in enumerate(zip("XZ", args.models)):
    circuit = load_circuit(GROSS_CIRCUITS[basis], args.p)
    H, L, priors = dem_matrices(circuit, basis)
    det, obs = sample(circuit, args.shots, args.seed + j)
    det = det[:, detector_ids(circuit, basis)]
    dec = {"relay": relay_decoder(H, priors), "bposd": bposd_decoder(H, priors),
           "router": RoutedDecoder(H, priors, joblib.load(model_path), args.t),
           "gate": AgreementGate(H, L, priors, K=K, referee=referee)}
    for k, (syndrome, truth) in enumerate(zip(det, obs)):
        names = NAMES[:]
        order_rng.shuffle(names)
        for n in names:
            start = time.perf_counter()
            error = dec[n].decode(syndrome)
            secs[n][k, j] = time.perf_counter() - start
            fail[n][k, j] = ((L @ np.asarray(error, np.uint8)) % 2 != truth).any()
        gate_path[k, j] = dec["gate"].last_path
        if (k + 1) % 100 == 0:
            print(f"[{basis}] {k + 1}/{args.shots}", flush=True)
    print(f"[{basis}] router paths {dec['router'].counts}", flush=True)

np.savez(args.out, **{f"{n}_secs": secs[n] for n in NAMES}, **{f"{n}_fail": fail[n] for n in NAMES},
         gate_path=gate_path.astype(str), p=args.p, K=K, referee=referee, t=args.t)
for n in NAMES:
    ms = secs[n].sum(axis=1) * 1e3
    P = fail[n].any(axis=1).mean()
    print(f"{n:7s} fails {fail[n].sum(axis=0)} pairs {fail[n].any(axis=1).sum():4d} "
          f"LER {1 - (1 - P) ** (1 / 12):.2e}  mean {ms.mean():7.1f}  p50 {np.median(ms):7.1f}  "
          f"p90 {np.percentile(ms, 90):7.1f}  p99 {np.percentile(ms, 99):7.0f}  max {ms.max():7.0f} ms")
