"""Report for bposd_compare.py runs (pre-registered in docs/discussion/14).

  python experiments/bposd_compare_report.py data/compare_p*.npz
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adaptive_report import MARGIN, boot_upper, ratio_upper  # noqa: E402

CYCLES = 12
NAMES = {"bposd": "BP-OSD", "relay": "Relay-BP", "gate_count": "gate (alarm count)", "gate_mlp": "gate (MLP)"}


def stats(fail, secs):
    return dict(fails=int(fail.sum()), pairs=len(fail), ler=float(1 - (1 - fail.mean()) ** (1 / CYCLES)),
                mean_ms=float(secs.mean() * 1e3), p90_ms=float(np.percentile(secs, 90) * 1e3),
                p99_ms=float(np.percentile(secs, 99) * 1e3))


def verdict(gf, rf, gt, rt):
    up, a, b, c = ratio_upper(gf, rf)
    acc = "PASS" if up < MARGIN else ("FAIL" if gf.sum() > MARGIN * rf.sum() else "INCONCLUSIVE")
    lat = {k: (float(f(gt) / f(rt)), boot_upper(gt, rt, f)) for k, f in
           [("mean", lambda x: x.mean(-1)), ("p90", lambda x: np.percentile(x, 90, axis=-1)),
            ("p99", lambda x: np.percentile(x, 99, axis=-1))]}
    latv = "PASS" if all(u < 1 for _, u in lat.values()) else "FAIL"
    return dict(only_gate=b, only_relay=c, both=a, ratio_upper=float(up), accuracy=acc, latency=lat, latency_verdict=latv)


def table(rows, title):
    print(f"  {title}")
    print(f"    {'decoder':20s} {'fails':>6s} {'LER/cycle':>10s} {'mean ms':>8s} {'p90 ms':>7s} {'p99 ms':>7s}")
    for name, s in rows.items():
        print(f"    {NAMES[name]:20s} {s['fails']:6d} {s['ler']:10.2e} {s['mean_ms']:8.0f} {s['p90_ms']:7.0f} {s['p99_ms']:7.0f}")


def show(v, label):
    lat = "  ".join(f"{k} {r:.2f} (95% upper {u:.2f})" for k, (r, u) in v["latency"].items())
    print(f"    {label}: only gate {v['only_gate']}, only Relay-BP {v['only_relay']}, ratio upper {v['ratio_upper']:.2f}"
          f" -> accuracy {v['accuracy']};  time {lat} -> latency {v['latency_verdict']}")


def main():
    out = []
    for path in sorted(sys.argv[1:], key=lambda f: float(np.load(f)["p"])):
        d = np.load(path, allow_pickle=True)
        p, names = float(d["p"]), list(d["decoders"])
        fail = {n: (~d["correct"][..., j]).any(1) for j, n in enumerate(names)}
        secs = {n: d["seconds"][..., j].sum(1) for j, n in enumerate(names)}
        sub = d["use_mlp"]
        print(f"\np = {p}: {int(d['shots'])} pairs (MLP subset: first {int(sub.sum())})")
        full = {n: stats(fail[n], secs[n]) for n in ["bposd", "relay", "gate_count"]}
        table(full, "all shots")
        v_count = verdict(fail["gate_count"], fail["relay"], secs["gate_count"], secs["relay"])
        show(v_count, "gate (alarm count) vs Relay-BP")
        vs_bposd = dict(fail_ratio=full["gate_count"]["fails"] / max(full["bposd"]["fails"], 1),
                        mean_time_ratio=full["gate_count"]["mean_ms"] / full["bposd"]["mean_ms"],
                        p99_time_ratio=full["gate_count"]["p99_ms"] / full["bposd"]["p99_ms"])
        print(f"    gate (alarm count) vs BP-OSD: {vs_bposd['fail_ratio']:.2f}x the failures, "
              f"{vs_bposd['mean_time_ratio']:.2f}x mean time, {vs_bposd['p99_time_ratio']:.2f}x p99 time")
        subset = {n: stats(fail[n][sub], secs[n][sub]) for n in names}
        table(subset, "MLP subset (exploratory)")
        v_mlp = verdict(fail["gate_mlp"][sub], fail["relay"][sub], secs["gate_mlp"][sub], secs["relay"][sub])
        show(v_mlp, "gate (MLP) vs Relay-BP")
        settings = [tuple(s) for s in d["settings"]]
        share = lambda s: {f"K={K} {r}": float(np.mean(s == i)) for i, (K, r) in enumerate(settings)}  # noqa: E731
        differ = float(np.mean(d["s_count"][sub] != d["s_mlp"][sub]))
        print(f"    settings chosen, alarm count: {share(d['s_count'])};  MLP (subset): {share(d['s_mlp'][sub])};"
              f"  the two differ on {differ:.1%} of subset pairs")
        print(f"    estimate error (mean |p_hat - p| / p): alarm count {np.mean(np.abs(d['p_count'] - p)) / p:.1%},"
              f" MLP {np.mean(np.abs(d['p_mlp'] - p)) / p:.1%};  estimator cost {float(d['estimate_us_per_pair']):.1f} us/pair (batched)")
        out.append(dict(p=p, all=full, subset=subset, gate_count_vs_relay=v_count, gate_mlp_vs_relay=v_mlp,
                        gate_count_vs_bposd=vs_bposd, settings_count=share(d["s_count"]),
                        settings_mlp=share(d["s_mlp"][sub]), settings_differ=differ))
    Path("results/bposd_compare.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
