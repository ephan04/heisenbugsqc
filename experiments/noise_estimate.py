"""Can the decoder tell the noise level from the alarms alone?

Calibrate mean alarm count (X-basis detectors) against p, then estimate p from fresh shots:
from a single shot, and from running averages over windows of shots.

  python experiments/noise_estimate.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "kit"))
from circuit import GROSS_CIRCUITS, detector_ids, load_circuit, sample  # noqa: E402

GRID = np.round(np.arange(0.0010, 0.0071, 0.0005), 4)
circuit0 = load_circuit(GROSS_CIRCUITS["X"])
ids = detector_ids(circuit0, "X")


def weights(p, shots, seed):
    det, _ = sample(load_circuit(GROSS_CIRCUITS["X"], p), shots, seed)
    return det[:, ids].sum(1).astype(float)


# 1. Calibration curve (seed 1) and a fresh test set (seed 2).
calib = {p: weights(p, 20000, 1) for p in GRID}
mean = np.array([calib[p].mean() for p in GRID])
sd = np.array([calib[p].std() for p in GRID])
print("p        mean alarms  sd    (per X-basis shot, 936 detectors)")
for p, m, s in zip(GRID, mean, sd):
    print(f"{p:.4f}   {m:9.1f}  {s:5.1f}")
fit = np.polyfit(GRID, mean, 2)
invert = lambda w: np.interp(w, mean, GRID)  # noqa: E731  (mean is monotone in p)
print(f"\nquadratic fit: alarms ~ {fit[0]:.3g} p^2 + {fit[1]:.4g} p + {fit[2]:.3g}")

# 2. Estimate p from windows of fresh shots.
print("\nestimating p from the average alarm count over a window of fresh shots")
print(f"{'true p':>7s} " + " ".join(f"{('N=' + str(n)):>14s}" for n in [1, 10, 100, 1000]))
for p in [0.003, 0.004, 0.005]:
    w = weights(p, 20000, 2)
    cells = []
    for n in [1, 10, 100, 1000]:
        est = invert(w[: (len(w) // n) * n].reshape(-1, n).mean(1))
        cells.append(f"{np.mean(np.abs(est - p)) / p:6.1%} err")
    print(f"{p:7.4f} " + " ".join(f"{c:>14s}" for c in cells))

# 3. Single shot: which of the three challenge noise levels is it?
print("\nsingle shot, classify as p=0.003 / 0.004 / 0.005 (nearest calibrated mean):")
levels = np.array([0.003, 0.004, 0.005])
centres = np.interp(levels, GRID, mean)
for p in levels:
    w = weights(p, 20000, 3)
    guess = levels[np.abs(w[:, None] - centres[None]).argmin(1)]
    print(f"  true {p}: correct {np.mean(guess == p):.0%}")
