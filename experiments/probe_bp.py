"""Quick probe: how often does short BP converge, and is it right when it does?"""
import sys, time
sys.path.insert(0, "kit")
import numpy as np
from ldpc import BpDecoder
from circuit import GROSS_CIRCUITS, dem_matrices, detector_ids, load_circuit, sample

p, shots = float(sys.argv[1]), int(sys.argv[2])
c = load_circuit(GROSS_CIRCUITS["X"], p)
H, L, pri = dem_matrices(c, "X")
det, obs = sample(c, shots, 7)
det = det[:, detector_ids(c, "X")]
for iters in (10, 30, 80):
    bp = BpDecoder(H, error_channel=list(pri), max_iter=iters, bp_method="minimum_sum", ms_scaling_factor=1.0)
    conv = np.zeros(shots, bool); right = np.zeros(shots, bool); t = np.zeros(shots)
    for k in range(shots):
        s = time.perf_counter(); e = bp.decode(det[k]); t[k] = time.perf_counter() - s
        conv[k] = bp.converge; right[k] = not ((L @ e) % 2 != obs[k]).any()
    print(f"p={p} iters={iters:3d} converged {conv.mean():.3f}  wrong-given-converged {(~right[conv]).mean():.4f}  "
          f"mean {t.mean()*1e3:.2f} ms  conv-mean {t[conv].mean()*1e3:.2f} ms  syndrome wt {det.sum(1).mean():.0f}")
