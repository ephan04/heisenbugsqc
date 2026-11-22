"""All headline metrics and hardware facts in one place: results/all_metrics.{json,md}.

  python experiments/metrics_summary.py
"""
import json
import platform
import subprocess
from importlib.metadata import version
from pathlib import Path

import numpy as np

R = Path("results")
WORKERS = 8
# The organisers' reference table (kit/README.md): 10,000 pairs, their 8-core machine, mean time per X+Z pair.
KIT = {0.003: {"bposd": (56, 4.7e-4, 0.6e-4, 140), "relay": (5, 4.2e-5, 1.9e-5, 100)},
       0.004: {"bposd": (522, 4.4e-3, 0.2e-3, 330), "relay": (105, 8.7e-4, 0.9e-4, 380)},
       0.005: {"bposd": (2588, 2.3e-2, 0.05e-2, 590), "relay": (825, 6.9e-3, 0.2e-3, 1700)}}
# Wall-clock time of three 8-worker runs, as printed at the end of each run (results/wall_clock_runs.txt).
WALL_CLOCK = {"data/router_compare_p0.003.npz": 402, "data/router_eval_p0.004.npz": 971,
              "data/router_eval_p0.005.npz": 3335}


def parallel_efficiency():
    """How many of the 8 workers were busy on average: total decode time / wall-clock time."""
    rows = []
    for path, wall in WALL_CLOCK.items():
        d = np.load(path, allow_pickle=True)
        busy = float(d["seconds"].sum())
        rows.append(dict(run=path, p=float(d["p"]), pairs=int(d["shots"]), decoders=list(d["decoders"]),
                         decode_seconds=busy, wall_seconds=wall, busy_workers=busy / wall,
                         efficiency=busy / wall / WORKERS))
    return rows


def sh(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def hardware():
    hw = dict(machine=sh("system_profiler SPHardwareDataType | sed -n 's/.*Model Name: //p'"),
              chip=sh("sysctl -n machdep.cpu.brand_string"),
              cores=sh("system_profiler SPHardwareDataType | sed -n 's/.*Total Number of Cores: //p'"),
              memory_gb=int(sh("sysctl -n hw.memsize")) / 2**30, os=f"macOS {platform.mac_ver()[0]}",
              python=platform.python_version(), workers=WORKERS, gpu_used=False)
    hw["libraries"] = {k: version(k) for k in ["stim", "ldpc", "relay-bp", "numpy", "scipy", "scikit-learn"]}
    hw["probe_p0.004_X"] = json.loads((R / "hardware_probe.json").read_text())
    return hw


def main():
    compare = {row["p"]: row for row in json.loads((R / "bposd_compare.json").read_text())}
    router = {row["p"]: row for row in json.loads((R / "router_eval.json").read_text())}
    big = json.loads((R / "large_p0.003.json").read_text())
    big = big[0] if isinstance(big, list) else big
    rows = []
    for p in [0.003, 0.004, 0.005]:
        c = compare[p]["all"]
        for name, key in [("BP-OSD", "bposd"), ("Relay-BP", "relay"), ("agreement gate", "gate_count")]:
            s = c[key]
            rows.append(dict(p=p, decoder=name, source="ours, same shots", pairs=s["pairs"], fails=s["fails"],
                             ler=s["ler"], mean_ms=s["mean_ms"], p90_ms=s["p90_ms"], p99_ms=s["p99_ms"],
                             pairs_per_s_8w=WORKERS * 1e3 / s["mean_ms"]))
        for key, name in [("bposd", "BP-OSD"), ("relay", "Relay-BP")]:
            f, ler, err, ms = KIT[p][key]
            rows.append(dict(p=p, decoder=name, source="organisers (kit README)", pairs=10000, fails=f, ler=ler,
                             ler_err=err, mean_ms=ms))
        s = router[p]["stats"]["router"]
        rows.append(dict(p=p, decoder="ML router (Emma, t=0.7)", source="ours, 10k pairs", pairs=s["pairs"],
                         fails=s["fails"], ler=s["ler"], mean_ms=s["mean_ms"], p90_ms=s["p90_ms"], p99_ms=s["p99_ms"]))
    rows.append(dict(p=0.003, decoder="agreement gate", source="ours, 100k pairs", pairs=big["pairs"],
                     fails=big["gate_fails"], ler=big["gate_ler"], mean_ms=big["gate_mean_ms"]))
    rows.append(dict(p=0.003, decoder="Relay-BP", source="ours, 100k pairs", pairs=big["pairs"],
                     fails=big["relay_fails"], ler=big["relay_ler"], mean_ms=big["relay_mean_ms"]))
    verdicts = {p: dict(vs_relay=compare[p]["gate_count_vs_relay"], vs_bposd=compare[p]["gate_count_vs_bposd"])
                for p in compare if p in (0.003, 0.004, 0.005)}
    eff = parallel_efficiency()
    out = dict(hardware=hardware(), parallel_efficiency=eff, rows=rows, gate_verdicts=verdicts, gate_100k_p0003=big)
    (R / "all_metrics.json").write_text(json.dumps(out, indent=1, default=float))
    md = ["| p | decoder | source | pairs | failed pairs | LER / cycle | mean ms/pair | p90 | p99 | pairs/s (8 workers) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    fmt = lambda v, f: "" if v is None else format(v, f)  # noqa: E731
    for r in sorted(rows, key=lambda r: (r["p"], r["decoder"], r["source"])):
        md.append(f"| {r['p']} | {r['decoder']} | {r['source']} | {r['pairs']} | {r['fails']} | {r['ler']:.2e} | "
                  f"{r['mean_ms']:.0f} | {fmt(r.get('p90_ms'), '.0f')} | {fmt(r.get('p99_ms'), '.0f')} | "
                  f"{fmt(r.get('pairs_per_s_8w'), '.0f')} |")
    md += ["", "Parallel efficiency: how many of the 8 workers were busy on average (total decode time / wall-clock time).",
           "The pairs-per-second column assumes all 8 are busy, so it is optimistic by the gap shown here.", "",
           "| run | p | pairs | decoders | decode time (s) | wall clock (s) | busy workers | efficiency |",
           "|---|---|---|---|---|---|---|---|"]
    md += [f"| `{e['run']}` | {e['p']} | {e['pairs']} | {', '.join(e['decoders'])} | {e['decode_seconds']:.0f} | "
           f"{e['wall_seconds']} | {e['busy_workers']:.2f} of {WORKERS} | {e['efficiency']:.0%} |" for e in eff]
    (R / "all_metrics.md").write_text("\n".join(md) + "\n")
    print(json.dumps(out["hardware"], indent=1)); print("\n".join(md))


if __name__ == "__main__":
    main()
