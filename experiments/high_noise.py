"""Exploratory: high-noise variants of the skip gate, scored offline on stored agree_*.npz runs.

Levers: (1) cap the fast runs at K restarts instead of 50, (2) a cheaper referee
(Relay-BP stop_nconv=2 instead of the kit's stop_nconv=5).
A capped run is treated as 'no solution' if it needed more than K restarts; its time is estimated
by scaling the measured time to the iterations it would have run (80 + 60 K). Approximate.

  python experiments/high_noise.py data/agree_p0.005_s301.npz data/agree_p0.004_s401.npz
"""
import sys

import numpy as np

CYCLES = 12
for path in sys.argv[1:]:
    d = np.load(path)
    ok, it, L, S, C = d["success"], d["iterations"], d["logical"], d["seconds"], d["correct"]
    base_t, base_f = S[..., 3].sum(1), (~C[..., 3]).any(1)
    print(f"\n{path}: Relay-BP {base_f.sum()} failed pairs, mean {base_t.mean()*1e3:.0f} ms, "
          f"p90 {np.percentile(base_t, 90)*1e3:.0f}, p99 {np.percentile(base_t, 99)*1e3:.0f}")
    print(f"{'restart cap K':>14s} {'referee':>9s} {'fails':>6s} {'vs base':>8s} {'mean':>6s} {'p90':>6s} {'p99':>6s}  escalated")
    for K in [50, 20, 10, 5, 2]:
        cap = 80 + 60 * K
        okK = ok[..., :2] & (it[..., :2] <= cap)
        tK = np.where(it[..., :2] <= cap, S[..., :2], S[..., :2] * cap / np.maximum(it[..., :2], 1))
        first = okK[..., 0] & (it[..., 0] <= 80)
        agree = okK[..., 0] & okK[..., 1] & (L[..., 0, :] == L[..., 1, :]).all(-1)
        for ref, j in [("relay", 3), ("nconv2", 2)]:
            esc = ~okK[..., 0] | (~first & ~agree)
            wrong = np.where(esc, ~C[..., j], ~C[..., 0])
            secs = tK[..., 0] + np.where(okK[..., 0] & ~first, tK[..., 1], 0) + np.where(esc, S[..., j], 0)
            f, t = wrong.any(1), secs.sum(1)
            print(f"{K:14d} {ref:>9s} {f.sum():6d} {f.sum()/base_f.sum():8.2f} "
                  f"{t.mean()/base_t.mean():6.2f} {np.percentile(t, 90)/np.percentile(base_t, 90):6.2f} "
                  f"{np.percentile(t, 99)/np.percentile(base_t, 99):6.2f}  {esc.mean():6.1%}")
