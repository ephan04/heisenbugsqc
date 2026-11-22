"""Report for router_compare.py (pre-registered in discussion/25).

  python experiments/router_compare_report.py data/router_compare_p0.003.npz
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bposd_compare_report import stats, verdict  # noqa: E402

NAMES = {"bposd": "BP-OSD", "relay": "Relay-BP", "gate": "our gate (K10 R5)",
         "router": "ML router (t=0.7)", "bp_relay": "fast BP -> Relay-BP"}


def main():
    d = np.load(sys.argv[1], allow_pickle=True)
    names, p = list(d["decoders"]), float(d["p"])
    fail = {n: (~d["correct"][..., j]).any(1) for j, n in enumerate(names)}
    secs = {n: d["seconds"][..., j].sum(1) for j, n in enumerate(names)}
    old = np.load(f"data/compare_p{p}.npz", allow_pickle=True)
    old_fail = {n: int((~old["correct"][..., j]).any(1).sum()) for j, n in enumerate(old["decoders"])}
    lines = [f"p = {p}: {int(d['shots'])} pairs, seed {int(d['seed'])}, same shots as data/compare_p{p}.npz",
             f"  {'decoder':22s} {'fails':>6s} {'LER/cycle':>10s} {'mean ms':>8s} {'p90 ms':>7s} {'p99 ms':>7s}"]
    out = dict(p=p, stats={}, vs_relay={}, vs_bposd={})
    for n in names:
        s = stats(fail[n], secs[n]); out["stats"][n] = s
        lines.append(f"  {NAMES[n]:22s} {s['fails']:6d} {s['ler']:10.2e} {s['mean_ms']:8.1f} {s['p90_ms']:7.0f} {s['p99_ms']:7.0f}")
    route = d["route"].ravel()
    share = {r: float((route == i).mean()) for i, r in enumerate(d["routes"])}
    lines.append("  router sent basis decodes to: " + ", ".join(f"{r} {v:.1%}" for r, v in share.items()))
    out["router_routes"] = share
    lines.append("  vs Relay-BP:")
    for n in ["gate", "router", "bp_relay"]:
        v = verdict(fail[n], fail["relay"], secs[n], secs["relay"]); out["vs_relay"][n] = v
        lat = "  ".join(f"{k} {r:.2f} (95% upper {u:.2f})" for k, (r, u) in v["latency"].items())
        lines.append(f"    {NAMES[n]:22s} only it {v['only_gate']}, only Relay-BP {v['only_relay']}, ratio upper "
                     f"{v['ratio_upper']:.2f} -> accuracy {v['accuracy']};  {lat} -> latency {v['latency_verdict']}")
    lines.append("  vs BP-OSD:")
    for n in ["gate", "router", "bp_relay"]:
        r = dict(fails=fail[n].sum() / max(fail["bposd"].sum(), 1), mean=secs[n].mean() / secs["bposd"].mean(),
                 p99=np.percentile(secs[n], 99) / np.percentile(secs["bposd"], 99))
        out["vs_bposd"][n] = {k: float(x) for k, x in r.items()}
        lines.append(f"    {NAMES[n]:22s} {r['fails']:.2f}x the failures, {r['mean']:.2f}x mean time, {r['p99']:.2f}x p99 time")
    same = {n: (int(fail[n].sum()), old_fail[m]) for n, m in [("bposd", "bposd"), ("relay", "relay"), ("gate", "gate_count")]}
    lines.append("  sanity (deterministic decoders, fails now vs earlier run): "
                 + ", ".join(f"{n} {a} vs {b}" for n, (a, b) in same.items()))
    out["sanity"] = same
    text = "\n".join(lines)
    print(text)
    Path(f"results/router_compare_p{p}.txt").write_text(text + "\n")
    Path(f"results/router_compare_p{p}.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
