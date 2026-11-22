"""Stage 2 (confirmation): the real gate with frozen settings vs the kit's Relay-BP, on fresh shots.

  python experiments/adaptive_confirm.py --p 0.005 --shots 3000 --seed 2050 --out data/confirm_p0.005.npz

Both decoders run on every shot in random order per shot. Settings come from
results/adaptive_selected.json, frozen before this stage (docs/discussion/09_noise_adaptive_prereg.md).
"""
import argparse
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "kit"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from circuit import GROSS_CIRCUITS, dem_matrices, detector_ids, load_circuit, sample  # noqa: E402
from decoders import relay_decoder  # noqa: E402
from gate import PATHS, AgreementGate, settings_for  # noqa: E402

CHUNKS_PER_WORKER = 6


def work(job):
    basis, p, K, referee, det, obs, chunk_seed = job
    H, L, priors = dem_matrices(load_circuit(GROSS_CIRCUITS[basis], p), basis)
    decs = {"gate": AgreementGate(H, L, priors, K=K, referee=referee), "relay": relay_decoder(H, priors)}
    rng = np.random.default_rng(chunk_seed)
    n = len(det)
    out = dict(correct=np.zeros((n, 2), bool), seconds=np.zeros((n, 2)), path=np.zeros(n, np.int8))
    for k in range(n):
        for name in rng.permutation(["gate", "relay"]):
            j = 0 if name == "gate" else 1
            start = time.perf_counter()
            error = decs[name].decode(det[k])
            out["seconds"][k, j] = time.perf_counter() - start
            out["correct"][k, j] = (((L @ np.asarray(error, np.uint8)) % 2) == obs[k]).all()
        out["path"][k] = PATHS.index(decs["gate"].last_path)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=float, required=True)
    ap.add_argument("--shots", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", required=True)
    ap.add_argument("--table", default="results/adaptive_selected.json", help="frozen settings per noise level")
    args = ap.parse_args()
    K, referee = settings_for(args.p, args.table)
    jobs = []
    chunks = args.workers * CHUNKS_PER_WORKER
    for b, basis in enumerate("XZ"):
        circuit = load_circuit(GROSS_CIRCUITS[basis], args.p)
        det, obs = sample(circuit, args.shots, args.seed + b)
        det = det[:, detector_ids(circuit, basis)]
        for c, idx in enumerate(np.array_split(np.arange(args.shots), chunks)):
            jobs.append((basis, args.p, K, referee, det[idx], obs[idx], args.seed * 1000 + b * 100 + c))
    start = time.time()
    with Pool(args.workers) as pool:
        res = pool.map(work, jobs, chunksize=1)
    half = len(jobs) // 2
    arrays = {key: np.stack([np.concatenate([r[key] for r in res[:half]]),
                             np.concatenate([r[key] for r in res[half:]])], axis=1)
              for key in res[0]}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.out, **arrays, p=args.p, shots=args.shots, seed=args.seed, K=K, referee=referee,
                        paths=PATHS, workers=args.workers)
    print(f"{args.out}: {args.shots} pairs at p={args.p} (K={K}, referee {referee}) in {time.time() - start:.0f} s",
          flush=True)


if __name__ == "__main__":
    main()
