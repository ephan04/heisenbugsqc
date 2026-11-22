"""The teammate's ML router (ml_router/) vs BP-OSD, Relay-BP and our gate, live on the same shots.

  python experiments/router_compare.py --p 0.003 --shots 10000 --seed 5030 --out data/router_compare_p0.003.npz

Pre-registered in discussion/25_router_compare_prereg.md.
"""
import argparse
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "kit"))
sys.path.insert(0, str(ROOT / "ml_router"))
sys.path.insert(0, str(ROOT / "experiments"))
from circuit import GROSS_CIRCUITS, dem_matrices, detector_ids, load_circuit, sample  # noqa: E402
from decoders import bposd_decoder, relay_decoder  # noqa: E402
from evaluate_router import RoutedDecoder  # noqa: E402
from fast_bp import fast_decoder  # noqa: E402
from gate import AgreementGate  # noqa: E402

DECODERS = ["bposd", "relay", "gate", "router", "bp_relay"]
CHUNKS_PER_WORKER = 6


class BpThenRelay:
    """The router pipeline with the router switched off: fast BP, then Relay-BP if BP did not converge."""

    def __init__(self, H, priors):
        self.bp, self.relay = fast_decoder(H, priors), relay_decoder(H, priors)

    def decode(self, syndrome):
        error = self.bp.decode(syndrome)
        return error if self.bp.converge else self.relay.decode(syndrome)


def work(job):
    basis, p, det, obs, model_path, t, K, ref, chunk_seed, names = job
    H, L, priors = dem_matrices(load_circuit(GROSS_CIRCUITS[basis], p), basis)
    build = {"bposd": lambda: bposd_decoder(H, priors), "relay": lambda: relay_decoder(H, priors),
             "gate": lambda: AgreementGate(H, L, priors, K=K, referee=ref),
             "router": lambda: RoutedDecoder(H, priors, joblib.load(model_path), t),
             "bp_relay": lambda: BpThenRelay(H, priors)}
    decs = {name: build[name]() for name in names}
    rng = np.random.default_rng(chunk_seed)
    n = len(det)
    out = dict(correct=np.ones((n, len(names)), bool), seconds=np.zeros((n, len(names))),
               route=np.zeros(n, np.int8))
    for k in range(n):
        for name in rng.permutation(names):
            j = names.index(name)
            before = dict(decs["router"].counts)
            start = time.perf_counter()
            error = decs[name].decode(det[k])
            out["seconds"][k, j] = time.perf_counter() - start
            out["correct"][k, j] = (((L @ np.asarray(error, np.uint8)) % 2) == obs[k]).all()
            if name == "router":
                out["route"][k] = ["bp", "relay", "bposd"].index(
                    next(r for r in before if decs["router"].counts[r] != before[r]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=float, required=True)
    ap.add_argument("--shots", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--t", type=float, default=0.7)
    ap.add_argument("--K", type=int, default=10)
    ap.add_argument("--referee", default="R5")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--decoders", nargs="+", default=DECODERS, choices=DECODERS)
    ap.add_argument("--model-dir", default="ml_router/result")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    jobs = []
    for b, basis in enumerate("XZ"):
        circuit = load_circuit(GROSS_CIRCUITS[basis], args.p)
        det, obs = sample(circuit, args.shots, args.seed + b)
        det = det[:, detector_ids(circuit, basis)]
        model = ROOT / args.model_dir / f"route_{basis}_p{args.p}_safe_logistic.joblib"
        for c, idx in enumerate(np.array_split(np.arange(args.shots), args.workers * CHUNKS_PER_WORKER)):
            jobs.append((basis, args.p, det[idx], obs[idx], str(model), args.t, args.K, args.referee,
                         args.seed * 1000 + b * 100 + c, args.decoders))
    start = time.time()
    with Pool(args.workers) as pool:
        res = pool.map(work, jobs, chunksize=1)
    half = len(jobs) // 2
    arrays = {key: np.stack([np.concatenate([r[key] for r in res[:half]]),
                             np.concatenate([r[key] for r in res[half:]])], axis=1) for key in res[0]}
    np.savez_compressed(args.out, **arrays, p=args.p, shots=args.shots, seed=args.seed, decoders=args.decoders,
                        t=args.t, routes=["bp", "relay", "bposd"])
    print(f"{args.out}: {args.shots} pairs at p={args.p} in {time.time() - start:.0f} s", flush=True)


if __name__ == "__main__":
    main()
