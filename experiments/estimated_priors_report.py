"""Report for estimated_priors.py runs (pre-registered in docs/discussion/27).

  python experiments/estimated_priors_report.py data/estprior_p*.npz
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adaptive_report import MARGIN, boot_upper, ratio_upper  # noqa: E402
from bposd_compare_report import stats  # noqa: E402

STATS = [("mean", lambda x: x.mean(-1)), ("p90", lambda x: np.percentile(x, 90, axis=-1)),
         ("p99", lambda x: np.percentile(x, 99, axis=-1))]
EARLIER = {0.003: 7, 0.004: 53, 0.005: 262}


def main():
    lines, out = [], []
    for path in sorted(sys.argv[1:], key=lambda f: float(np.load(f)["p"])):
        d = np.load(path, allow_pickle=True)
        p = float(d["p"])
        fail = {n: (~d["correct"][..., j]).any(1) for j, n in enumerate(d["decoders"])}
        secs = {n: d["seconds"][..., j].sum(1) for j, n in enumerate(d["decoders"])}
        c = np.load(f"data/compare_p{p}.npz", allow_pickle=True)
        relay = (~c["correct"][..., list(c["decoders"]).index("relay")]).any(1)
        up, a, b, cc = ratio_upper(fail["gate_est"], fail["gate_true"])
        g, t = fail["gate_est"].sum(), fail["gate_true"].sum()
        acc = "PASS" if up < MARGIN else ("FAIL" if g > MARGIN * t else "INCONCLUSIVE")
        lat = {k: (float(f(secs["gate_est"]) / f(secs["gate_true"])), boot_upper(secs["gate_est"], secs["gate_true"], f))
               for k, f in STATS}
        latv = "PASS" if all(u < 1.05 for _, u in lat.values()) else "FAIL"
        pe = d["p_est"]
        lines += [f"p = {p}: {int(d['shots'])} pairs;  p_hat range {pe.min():.4f}-{pe.max():.4f}, "
                  f"mean |p_hat - p| / p = {np.abs(pe - p).mean() / p:.1%}",
                  f"  {'decoder':26s} {'fails':>6s} {'LER/cycle':>10s} {'mean ms':>8s} {'p90 ms':>7s} {'p99 ms':>7s}"]
        rows = {"gate, true p": stats(fail["gate_true"], secs["gate_true"]),
                "gate, estimated p": stats(fail["gate_est"], secs["gate_est"])}
        for name, s in rows.items():
            lines.append(f"  {name:26s} {s['fails']:6d} {s['ler']:10.2e} {s['mean_ms']:8.1f} {s['p90_ms']:7.0f} {s['p99_ms']:7.0f}")
        lines.append(f"  {'Relay-BP, true p (stored)':26s} {int(relay.sum()):6d}")
        lines.append(f"  estimated vs true: only estimated {b}, only true {cc}, ratio upper {up:.2f} -> accuracy {acc};  "
                     + "  ".join(f"{k} {r:.3f} (95% upper {u:.3f})" for k, (r, u) in lat.items()) + f" -> latency {latv}")
        lines.append(f"  sanity: gate (true p) fails {int(t)} vs earlier run {EARLIER[p]}\n")
        out.append(dict(p=p, rows=rows, relay_fails=int(relay.sum()), only_est=b, only_true=cc, ratio_upper=float(up),
                        accuracy=acc, latency=lat, latency_verdict=latv, p_hat_rel_error=float(np.abs(pe - p).mean() / p)))
    text = "\n".join(lines)
    print(text)
    Path("results/estimated_priors.txt").write_text(text)
    Path("results/estimated_priors.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
