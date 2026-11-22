"""Memory and build-time cost of each decoder, one process, p = 0.004 X memory.

  python experiments/hardware_probe.py
"""
import json
import resource
import sys
import time
from pathlib import Path

import os
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "kit"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from circuit import GROSS_CIRCUITS, dem_matrices, detector_ids, load_circuit, sample  # noqa: E402
from decoders import bposd_decoder, relay_decoder  # noqa: E402
from gate import AgreementGate  # noqa: E402

mb = lambda: int(subprocess.check_output(["ps", "-o", "rss=", "-p", str(os.getpid())])) / 1024  # noqa: E731
out = {"rss_after_imports_mb": mb()}
t = time.perf_counter()
circuit = load_circuit(GROSS_CIRCUITS["X"], 0.004)
H, L, priors = dem_matrices(circuit, "X")
out["dem_build_s"], out["rss_after_dem_mb"] = time.perf_counter() - t, mb()
out["H_shape"], out["H_nnz"] = list(H.shape), int(H.nnz)
for name, build in [("relay", lambda: relay_decoder(H, priors)), ("bposd", lambda: bposd_decoder(H, priors)),
                    ("gate", lambda: AgreementGate(H, L, priors, K=10, referee="R5"))]:
    before, t = mb(), time.perf_counter()
    dec = build()
    out[f"{name}_build_s"] = time.perf_counter() - t
    det, obs = sample(circuit, 50, 7)
    det = det[:, detector_ids(circuit, "X")]
    for s in det:
        dec.decode(s)
    out[f"{name}_added_mb"] = mb() - before
    globals()[f"keep_{name}"] = dec
out["peak_rss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20
print(json.dumps(out, indent=1))
Path("results/hardware_probe.json").write_text(json.dumps(out, indent=1))
