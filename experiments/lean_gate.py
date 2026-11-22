"""Exploratory (post-hoc, suggested in round 5): the same accept/escalate decisions as the agreement gate,
but skipping the second fast run when it cannot change the decision.

  - seed 0 finds no solution        -> escalate at once (Gemini): the gate would escalate anyway
  - seed 0 stops in the first leg   -> accept at once (GPT): seed 1 runs the same deterministic leg

Accuracy is identical to the primary gate only if seed 1 always reproduces seed 0 when seed 0 stops in the
first leg; this script checks that before reporting latency.

  python experiments/lean_gate.py data/agree_*.npz
"""
import sys

import numpy as np

FIRST_LEG = 80
for path in sys.argv[1:]:
    d = np.load(path)
    names = list(d["decoders"])
    i0, i1, ir = names.index("fast_s0"), names.index("fast_s1"), names.index("relay")
    ok, it, L, S, C = d["success"], d["iterations"], d["logical"], d["seconds"], d["correct"]
    agree = ok[..., i0] & ok[..., i1] & (L[..., i0, :] == L[..., i1, :]).all(-1)
    first = ok[..., i0] & (it[..., i0] <= FIRST_LEG)
    mismatch = int((first & ~agree).sum())           # must be 0 for identical accuracy
    s0, s1, sr = S[..., i0], S[..., i1], S[..., ir]
    primary = s0 + s1 + np.where(agree, 0, sr)
    lean = s0 + np.where(~ok[..., i0], sr, np.where(first, 0, s1 + np.where(agree, 0, sr)))
    rel = sr.sum(1).mean()
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(sr), (2000, len(sr)))
    ratio = lean.sum(1)[idx].mean(1) / sr.sum(1)[idx].mean(1)
    p99 = lambda a: np.percentile(a.sum(1), 99)  # noqa: E731
    print(f"{path}: first-leg mismatches {mismatch} | mean ratio vs Relay-BP: primary {primary.sum(1).mean() / rel:.2f}"
          f" -> lean {lean.sum(1).mean() / rel:.2f} (95% upper {np.quantile(ratio, 0.975):.2f}) | "
          f"p99 ratio primary {p99(primary) / p99(sr):.2f} -> lean {p99(lean) / p99(sr):.2f} | "
          f"second run skipped on {(~ok[..., i0] | first).mean():.0%} of shots")
