"""The teammate's ML router (t = 0.7) vs BP-OSD and Relay-BP at 10,000 pairs per noise level.

  python experiments/router_eval_report.py data/router_compare_p0.003.npz data/router_eval_p0.004.npz data/router_eval_p0.005.npz
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bposd_compare_report import stats, verdict  # noqa: E402

NAMES = {"bposd": "BP-OSD", "relay": "Relay-BP", "router": "ML router (t=0.7)"}


def main():
    lines, out = [], []
    for path in sorted(sys.argv[1:], key=lambda f: float(np.load(f)["p"])):
        d = np.load(path, allow_pickle=True)
        p, names = float(d["p"]), list(d["decoders"])
        fail = {n: (~d["correct"][..., j]).any(1) for j, n in enumerate(names)}
        secs = {n: d["seconds"][..., j].sum(1) for j, n in enumerate(names)}
        perb = {n: (~d["correct"][..., j]).sum(0) for j, n in enumerate(names)}
        lines += [f"p = {p}: {int(d['shots'])} pairs, seeds {int(d['seed'])}/{int(d['seed']) + 1} (X/Z), file {path}",
                  f"  {'decoder':20s} {'fails [X Z]':>12s} {'pairs':>6s} {'LER/cycle':>10s} {'mean ms':>8s} {'p90 ms':>7s} {'p99 ms':>7s}"]
        row = dict(p=p, stats={})
        for n in NAMES:
            s = stats(fail[n], secs[n]); s["per_basis"] = perb[n].tolist(); row["stats"][n] = s
            lines.append(f"  {NAMES[n]:20s} {str(perb[n].tolist()):>12s} {s['fails']:6d} {s['ler']:10.2e} "
                         f"{s['mean_ms']:8.1f} {s['p90_ms']:7.0f} {s['p99_ms']:7.0f}")
        route = d["route"].ravel()
        share = {r: float((route == i).mean()) for i, r in enumerate(d["routes"])}
        fails_by = {r: int((~d["correct"][..., names.index("router")] & (d["route"] == i)).sum())
                    for i, r in enumerate(d["routes"])}
        lines.append("  router sent basis decodes to: " + ", ".join(
            f"{r} {share[r]:.1%} ({fails_by[r]} failed)" for r in share))
        v = verdict(fail["router"], fail["relay"], secs["router"], secs["relay"])
        lat = "  ".join(f"{k} {r:.2f} (95% upper {u:.2f})" for k, (r, u) in v["latency"].items())
        lines.append(f"  router vs Relay-BP: only router {v['only_gate']}, only Relay-BP {v['only_relay']}, ratio upper "
                     f"{v['ratio_upper']:.2f} -> accuracy {v['accuracy']};  {lat} -> latency {v['latency_verdict']}")
        vb = verdict(fail["router"], fail["bposd"], secs["router"], secs["bposd"])
        latb = "  ".join(f"{k} {r:.2f}" for k, (r, u) in vb["latency"].items())
        lines.append(f"  router vs BP-OSD:   {fail['router'].sum() / max(fail['bposd'].sum(), 1):.2f}x the failures "
                     f"(only router {vb['only_gate']}, only BP-OSD {vb['only_relay']});  time {latb}\n")
        row.update(routes=share, fails_by_route=fails_by, vs_relay=v, vs_bposd=vb)
        out.append(row)
    text = "\n".join(lines)
    print(text)
    Path("results/router_eval.txt").write_text(text)
    Path("results/router_eval.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
