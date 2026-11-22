"""Stage 2 report: pre-registered verdicts for the confirmation runs.

  python experiments/adaptive_report.py data/confirm_p*.npz

Accuracy: PASS if the one-sided upper bound of the paired failure ratio (gate / Relay-BP) is < 1.2 at
99.2% (Bonferroni over 6 noise levels). The bound conditions on the discordant pairs: with b pairs only
the gate fails and c only Relay-BP fails, a Clopper-Pearson bound on b / (b + c) gives the ratio bound
(a + n_d * t) / (a + n_d * (1 - t)), where a counts pairs both fail. This stays valid when b = 0.
Latency: PASS if paired-bootstrap 95% upper bounds of the mean, p90 and p99 time ratios are all < 1.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import beta

CYCLES, MARGIN, CONF, BOOT = 12, 1.2, 1 - 0.05 / 6, 2000
EXPLORATORY = {0.0055, 0.006}
rng = np.random.default_rng(0)


def ratio_upper(gf, rf):
    a, b, c = int((gf & rf).sum()), int((gf & ~rf).sum()), int((~gf & rf).sum())
    nd = b + c
    if nd == 0:
        return 1.0, a, b, c
    t = beta.ppf(CONF, b + 1, c) if c > 0 else 1.0
    denom = a + nd * (1 - t)
    return (a + nd * t) / denom if denom > 0 else np.inf, a, b, c


def boot_upper(g, r, stat):
    idx = rng.integers(0, len(g), (BOOT, len(g)))
    return float(np.quantile(stat(g[idx]) / stat(r[idx]), 0.975))


def main():
    rows = []
    for path in sorted(sys.argv[1:], key=lambda f: float(np.load(f)["p"])):
        d = np.load(path, allow_pickle=True)
        p, n = float(d["p"]), int(d["shots"])
        gf, rf = (~d["correct"][..., 0]).any(1), (~d["correct"][..., 1]).any(1)
        gt, rt = d["seconds"][..., 0].sum(1), d["seconds"][..., 1].sum(1)
        up, a, b, c = ratio_upper(gf, rf)
        mean = lambda x: x.mean(axis=-1)  # noqa: E731
        q = lambda pct: (lambda x: np.percentile(x, pct, axis=-1))  # noqa: E731
        lat = {name: (float(f(gt) / f(rt)), boot_upper(gt, rt, f)) for name, f in
               [("mean", mean), ("p90", q(90)), ("p99", q(99))]}
        acc = "PASS" if up < MARGIN else ("FAIL" if gf.sum() > MARGIN * rf.sum() else "INCONCLUSIVE")
        latv = "PASS" if all(u < 1 for _, u in lat.values()) else "FAIL"
        paths = np.bincount(d["path"].ravel(), minlength=4) / d["path"].size
        row = dict(p=p, pairs=n, K=int(d["K"]), referee=str(d["referee"]), gate_fails=int(gf.sum()),
                   relay_fails=int(rf.sum()), both=a, gate_only=b, relay_only=c, fail_ratio_upper=float(up),
                   gate_ler=1 - (1 - gf.mean()) ** (1 / CYCLES), relay_ler=1 - (1 - rf.mean()) ** (1 / CYCLES),
                   gate_mean_ms=float(gt.mean() * 1e3), relay_mean_ms=float(rt.mean() * 1e3),
                   latency={k: dict(ratio=v[0], upper95=v[1]) for k, v in lat.items()},
                   paths=dict(zip([str(x) for x in d["paths"]], paths.round(4).tolist())),
                   accuracy=acc, latency_verdict=latv, exploratory=p in EXPLORATORY)
        rows.append(row)
        tag = " (exploratory)" if row["exploratory"] else ""
        print(f"\np = {p}{tag}: {n} pairs, gate K={row['K']} referee {row['referee']}")
        print(f"  failed pairs gate {row['gate_fails']} vs Relay-BP {row['relay_fails']}  (only gate {b}, only Relay-BP {c})"
              f"  ratio upper bound {up:.2f} -> accuracy {acc}")
        print(f"  LER/cycle gate {row['gate_ler']:.2e} vs Relay-BP {row['relay_ler']:.2e}")
        print("  time ratio " + "  ".join(f"{k} {v[0]:.2f} (<= {v[1]:.2f})" for k, v in lat.items())
              + f"  -> latency {latv}   [mean {row['gate_mean_ms']:.0f} vs {row['relay_mean_ms']:.0f} ms]")
        print("  paths: " + ", ".join(f"{k} {v:.1%}" for k, v in row["paths"].items()))
    Path("results/adaptive_confirm.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
