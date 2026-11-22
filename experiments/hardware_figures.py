"""Hardware and comparison figures: organisers' data vs ours, speed and accuracy.

  python experiments/hardware_figures.py      # -> figures/*.png and .pdf
"""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, NullFormatter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_figures import BLUE, GREEN, GRID, INK, MUTED, ORANGE, per_cycle  # noqa: E402  (also sets the style)

OUT = Path("figures")
OUT.mkdir(exist_ok=True)
PS = [0.003, 0.004, 0.005]
OURS = {"bposd": ("BP-OSD", ORANGE, "s"), "relay": ("Relay-BP", BLUE, "o"), "gate_count": ("Agreement gate", GREEN, "D")}
M = json.loads(Path("results/all_metrics.json").read_text())
KIT = {(r["p"], r["decoder"]): r for r in M["rows"] if r["source"].startswith("organisers")}
CMP = {row["p"]: row for row in json.loads(Path("results/bposd_compare.json").read_text())}


def load(p):
    d = np.load(f"data/compare_p{p}.npz", allow_pickle=True)
    names = list(d["decoders"])
    return ({n: (~d["correct"][..., j]).any(1) for j, n in enumerate(names)},
            {n: d["seconds"][..., j].sum(1) * 1e3 for j, n in enumerate(names)})


DATA = {p: load(p) for p in PS}


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=200)
    plt.close(fig)


def fig_accuracy():
    fig, ax = plt.subplots(figsize=(5.6, 3.8))
    for k, (name, label, color, marker) in enumerate([("BP-OSD", "BP-OSD", ORANGE, "s"), ("Relay-BP", "Relay-BP", BLUE, "o")]):
        r = [KIT[(p, name)] for p in PS]
        ax.errorbar(np.array(PS) * 1e3 - 0.06, [x["ler"] for x in r], yerr=[x["ler_err"] for x in r], color=color,
                    marker=marker, mfc="white", ls=":", lw=1.2, capsize=2, label=f"{label}: organisers")
    for k, (key, (label, color, marker)) in enumerate(OURS.items()):
        v = np.array([per_cycle(int(DATA[p][0][key].sum()), len(DATA[p][0][key])) for p in PS])
        ax.errorbar(np.array(PS) * 1e3 + 0.03 * k, v[:, 0], yerr=[v[:, 0] - v[:, 1], v[:, 2] - v[:, 0]], color=color,
                    marker=marker, capsize=2, markeredgecolor="white", markeredgewidth=0.8, label=f"{label}: ours")
    b = M["gate_100k_p0003"]
    for f, color, dx in [(b["gate_fails"], GREEN, 0.16), (b["relay_fails"], BLUE, 0.12)]:
        v = per_cycle(f, b["pairs"])
        ax.errorbar(3 + dx, v[0], yerr=[[v[0] - v[1]], [v[2] - v[0]]], color=color, marker="*", ms=9, capsize=2,
                    mec="white", mew=0.6)
    ax.annotate("100k-pair run", (3.16, per_cycle(b["gate_fails"], b["pairs"])[0]), xytext=(8, -14),
                textcoords="offset points", fontsize=7, color=MUTED)
    ax.set_yscale("log"); ax.set_xticks([3, 4, 5])
    ax.set_xlabel("physical error rate $p$ ($\\times 10^{-3}$)"); ax.set_ylabel("logical error rate per cycle")
    ax.set_title("Accuracy: organisers' reference vs our runs (95% intervals)", fontsize=9, color=INK)
    ax.legend(fontsize=7, loc="upper left", ncol=2)
    save(fig, "1_accuracy_vs_p")


def fig_speed():
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.6))
    ax = axes[0]
    w = 0.17
    x = np.arange(3)
    for k, (name, key, color) in enumerate([("BP-OSD", "bposd", ORANGE), ("Relay-BP", "relay", BLUE)]):
        ax.bar(x + (2 * k - 2) * w, [KIT[(p, name)]["mean_ms"] for p in PS], w * 0.92, color="white", edgecolor=color,
               hatch="///", lw=1, label=f"{name}: organisers")
        ax.bar(x + (2 * k - 1) * w, [DATA[p][1][key].mean() for p in PS], w * 0.92, color=color, label=f"{name}: ours")
    gate = [DATA[p][1]["gate_count"].mean() for p in PS]
    ax.bar(x + 2 * w, gate, w * 0.92, color=GREEN, label="gate: ours")
    for xi, p, g in zip(x, PS, gate):
        vs_relay, vs_bposd = DATA[p][1]["relay"].mean() / g, DATA[p][1]["bposd"].mean() / g
        top = max(KIT[(p, "Relay-BP")]["mean_ms"], KIT[(p, "BP-OSD")]["mean_ms"])
        ax.text(xi, top * 1.12, f"{vs_relay:.2f}x vs Relay-BP\n{vs_bposd:.2f}x vs BP-OSD", ha="center",
                va="bottom", fontsize=7, color=GREEN, fontweight="bold", linespacing=1.3)
    ax.set_yscale("log"); ax.set_ylim(15, 6000); ax.set_xticks(x, [f"{p:g}" for p in PS]); ax.set_xlabel("$p$")
    ax.set_ylabel("mean ms per X+Z pair"); ax.grid(axis="x", visible=False)
    ax.set_title("Mean decode time; green = gate speed-up on our machine", fontsize=9, color=INK)
    ax.legend(fontsize=6.5, loc="upper left", ncol=3, bbox_to_anchor=(0, -0.18))
    ax = axes[1]
    for stat, color, marker in [("mean", GREEN, "D"), ("p90", "#7d55c7", "^"), ("p99", INK, "v")]:
        r = np.array([CMP[p]["gate_count_vs_relay"]["latency"][stat] for p in PS])
        ax.errorbar(np.array(PS) * 1e3, r[:, 0], yerr=[np.zeros(3), r[:, 1] - r[:, 0]], color=color, marker=marker,
                    capsize=2, label=f"{stat} (bar = 95% upper bound)")
        if stat == "mean":
            for xp, v in zip(np.array(PS) * 1e3, r[:, 0]):
                ax.annotate(f"{1 / v:.2f}x faster", (xp, v), xytext=(0, 10 if xp < 4.5 else -16), textcoords="offset points",
                            ha="center", fontsize=7, color=GREEN, fontweight="bold")
    ax.axhline(1, color=BLUE, lw=1); ax.text(2.95, 1.02, "Relay-BP = 1", color=BLUE, fontsize=7, va="bottom")
    ax.set_xticks([3, 4, 5]); ax.set_xlabel("$p$ ($\\times 10^{-3}$)"); ax.set_ylabel("time / Relay-BP (same machine)")
    ax.set_ylim(0, 1.25)
    ax.set_title("Gate time relative to Relay-BP, same shots", fontsize=9, color=INK)
    ax.legend(fontsize=6.5, loc="lower right")
    fig.tight_layout()
    save(fig, "2_speed")


def fig_survival():
    fig, axes = plt.subplots(1, 3, figsize=(8.4, 2.9), sharey=True)
    for ax, p in zip(axes, PS):
        for key, (label, color, _) in OURS.items():
            t = np.sort(DATA[p][1][key])
            ax.step(t, 1 - np.arange(len(t)) / len(t), where="post", color=color, lw=1.6,
                    label=f"{label} (median {np.median(t):.0f} ms)")
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(1e-3, 1.05)
        ax.axhline(0.01, color=GRID, lw=0.8, ls="--")
        ax.set_title(f"p = {p:g}  ({len(DATA[p][1]['relay']):,} pairs)", fontsize=9, color=INK)
        ax.set_xlabel("ms per X+Z pair"); ax.legend(fontsize=6, loc="lower left")
    axes[0].set_ylabel("share of pairs at least this slow")
    axes[0].text(1.2, 0.012, "slowest 1%", fontsize=6.5, color=MUTED)
    fig.tight_layout()
    save(fig, "3_latency_distribution")


def fig_tradeoff():
    fig, axes = plt.subplots(1, 3, figsize=(8.4, 3.0))
    for ax, p in zip(axes, PS):
        fail, secs = DATA[p]
        for key, (label, color, marker) in OURS.items():
            v = per_cycle(int(fail[key].sum()), len(fail[key]))
            ax.errorbar(secs[key].mean(), v[0], yerr=[[v[0] - v[1]], [v[2] - v[0]]], color=color, marker=marker,
                        ms=8, capsize=2, mec="white", mew=0.8, ls="none", label=label)
        ax.set_xscale("log"); ax.set_yscale("log")
        for axis in (ax.xaxis, ax.yaxis):
            axis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
            axis.set_minor_formatter(NullFormatter())
        lo, hi = min(secs[k].mean() for k in OURS), max(secs[k].mean() for k in OURS)
        ax.set_xticks(np.round(np.geomspace(lo, hi, 3), -1 if hi < 1000 else -2))
        ax.set_xlim(lo / 1.3, hi * 1.3)
        ax.set_title(f"p = {p:g}", fontsize=9, color=INK); ax.set_xlabel("mean ms per pair (this laptop)")
    axes[0].set_ylabel("logical error rate per cycle")
    axes[0].legend(fontsize=7, loc="upper right")
    fig.suptitle("Speed vs accuracy on the same shots: lower-left is better", fontsize=9, color=INK)
    fig.tight_layout()
    save(fig, "4_speed_vs_accuracy")


def fig_hardware():
    hw = M["hardware"]["probe_p0.004_X"]
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.0))
    ax = axes[0]
    base = hw["rss_after_dem_mb"]
    items = [("Relay-BP", hw["relay_added_mb"], BLUE), ("Agreement gate", hw["gate_added_mb"], GREEN),
             ("BP-OSD", hw["bposd_added_mb"], ORANGE)]
    for i, (name, add, color) in enumerate(items):
        ax.barh(i, base, color=GRID, edgecolor="white")
        ax.barh(i, add, left=base, color=color, edgecolor="white")
        ax.text(base + add + 2, i, f"+{add:.1f} MB", va="center", fontsize=7, color=INK)
    ax.set_yticks(range(3), [n for n, _, _ in items]); ax.set_xlabel("memory per worker process (MB)")
    ax.set_xlim(0, 190); ax.grid(axis="y", visible=False)
    ax.text(base / 2, 0, f"Python + problem\n{base:.0f} MB", ha="center", va="center", fontsize=6.5, color=MUTED)
    ax.set_title("Memory (one process, p = 0.004)", fontsize=9, color=INK)
    ax = axes[1]
    x, w = np.arange(3), 0.26
    for k, (key, (label, color, _)) in enumerate(OURS.items()):
        tput = [8e3 / DATA[p][1][key].mean() for p in PS]
        ax.bar(x + (k - 1) * w, tput, w * 0.92, color=color, label=label)
        for xi, t in zip(x + (k - 1) * w, tput):
            ax.text(xi, t * 1.08, f"{t:.0f}", ha="center", fontsize=6.5, color=INK)
    ax.set_yscale("log"); ax.set_xticks(x, [f"{p:g}" for p in PS]); ax.set_xlabel("$p$")
    ax.set_ylabel("pairs per second, 8 workers"); ax.grid(axis="x", visible=False); ax.legend(fontsize=7)
    ax.set_title("Throughput on a MacBook Air (M5, CPU only)", fontsize=9, color=INK)
    fig.tight_layout()
    save(fig, "5_hardware")


if __name__ == "__main__":
    fig_accuracy(); fig_speed(); fig_survival(); fig_tradeoff(); fig_hardware()
    print(sorted(f.name for f in OUT.iterdir()))
