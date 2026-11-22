"""Figures for report/report.tex, built from the saved runs in data/.

  python experiments/report_figures.py
"""
import json
import pickle
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.stats import beta  # noqa: E402

OUT = Path("report/figures")
OUT.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, GREEN, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, MUTED, GRID = "#1f2328", "#59636e", "#e6e8eb"
STYLE = {"bposd": ("BP-OSD", ORANGE, "s"), "relay": ("Relay-BP", BLUE, "o"), "gate": ("Agreement gate", GREEN, "D")}
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                     "lines.linewidth": 2, "lines.markersize": 6, "savefig.bbox": "tight"})
CYCLES = 12


def per_cycle(k, n):
    """LER per cycle and its 95% Clopper-Pearson interval from k failed pairs of n."""
    f = lambda P: 1 - (1 - P) ** (1 / CYCLES)  # noqa: E731
    lo = beta.ppf(0.025, k, n - k + 1) if k > 0 else 0.0
    hi = beta.ppf(0.975, k + 1, n - k)
    return f(k / n), f(lo), f(hi)


def load_compare():
    rows = {}
    for p in [0.003, 0.004, 0.005]:
        d = np.load(f"data/compare_p{p}.npz", allow_pickle=True)
        names = list(d["decoders"])
        fail = {n: (~d["correct"][..., j]).any(1) for j, n in enumerate(names)}
        secs = {n: d["seconds"][..., j].sum(1) for j, n in enumerate(names)}
        rows[p] = dict(fail={"bposd": fail["bposd"], "relay": fail["relay"], "gate": fail["gate_count"]},
                       secs={"bposd": secs["bposd"], "relay": secs["relay"], "gate": secs["gate_count"]})
    big = np.load("data/large_p0.003.npz", allow_pickle=True)
    rows["big"] = dict(fail={"gate": (~big["correct"][..., 0]).any(1), "relay": (~big["correct"][..., 1]).any(1)},
                       path=big["path"], paths=list(big["paths"]))
    return rows


def fig_ler(rows):
    fig, ax = plt.subplots(figsize=(4.6, 3.3))
    ps = [0.003, 0.004, 0.005]
    for k, (key, (label, color, marker)) in enumerate(STYLE.items()):
        vals = []
        for p in ps:
            f = rows["big"]["fail"][key] if (p == 0.003 and key != "bposd") else rows[p]["fail"][key]
            vals.append(per_cycle(int(f.sum()), len(f)))
        v = np.array(vals)
        x = np.array(ps) * 1e3 + (k - 1) * 0.02
        ax.errorbar(x, v[:, 0], yerr=[v[:, 0] - v[:, 1], v[:, 2] - v[:, 0]], color=color, marker=marker,
                    label=label, capsize=2, markeredgecolor="white", markeredgewidth=0.8)
    ax.set_yscale("log")
    ax.set_xlabel("physical error rate $p$ ($\\times 10^{-3}$)")
    ax.set_ylabel("logical error rate per cycle")
    ax.set_xticks([3, 4, 5])
    ax.legend(loc="upper left")
    fig.savefig(OUT / "ler_vs_p.pdf")


def fig_latency(rows):
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.9), sharey=True)
    ps = [0.003, 0.004, 0.005]
    for ax, (stat, title) in zip(axes, [(np.mean, "mean time per pair"), (lambda x: np.percentile(x, 99), "slowest 1% (p99)")]):
        for key, (label, color, marker) in STYLE.items():
            ax.plot([p * 1e3 for p in ps], [stat(rows[p]["secs"][key]) * 1e3 for p in ps], color=color,
                    marker=marker, label=label, markeredgecolor="white", markeredgewidth=0.8)
        ax.set_yscale("log"); ax.set_title(title, fontsize=9, color=INK); ax.set_xticks([3, 4, 5])
        ax.set_xlabel("$p$ ($\\times 10^{-3}$)")
    axes[0].set_ylabel("milliseconds (X + Z shot)")
    axes[0].legend(loc="upper left")
    fig.savefig(OUT / "latency_vs_p.pdf")


def fig_paths():
    ps = [0.003, 0.004, 0.0045, 0.005, 0.0055, 0.006]
    labels = {"first_leg": "solved in first 80 iterations", "agreed": "two seeds agreed",
              "no_solution": "no solution $\\rightarrow$ referee", "disagreed": "disagreed $\\rightarrow$ referee"}
    colors = [GREEN, BLUE, ORANGE, YELLOW]
    shares = []
    for p in ps:
        d = np.load(f"data/confirm_p{p}.npz", allow_pickle=True)
        shares.append(np.bincount(d["path"].ravel(), minlength=4) / d["path"].size)
    shares = np.array(shares)
    fig, ax = plt.subplots(figsize=(5.6, 2.8))
    bottom = np.zeros(len(ps))
    for j, (name, c) in enumerate(zip(labels, colors)):
        ax.bar([f"{p:g}" for p in ps], shares[:, j] * 100, bottom=bottom, color=c, label=labels[name],
               edgecolor="white", linewidth=1.5, width=0.7)
        bottom += shares[:, j] * 100
    ax.set_ylabel("share of basis decodes (%)"); ax.set_xlabel("physical error rate $p$")
    ax.set_ylim(0, 100); ax.grid(axis="x", visible=False); ax.set_axisbelow(True)
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=8)
    fig.savefig(OUT / "gate_paths.pdf")


def fig_discovery():
    table = json.loads(Path("results/adaptive_discovery.json").read_text())
    refs = {"R5": (BLUE, "o"), "R2": (ORANGE, "s"), "R1": (YELLOW, "^")}
    fig, axes = plt.subplots(2, 3, figsize=(7.0, 4.4), sharex=True)
    for ax, row in zip(axes.ravel(), table):
        for ref, (c, m) in refs.items():
            pts = [s for s in row["settings"] if s["referee"] == ref]
            ax.plot([s["mean_ratio"] for s in pts], [s["fail_ratio"] for s in pts], color=c, marker=m, lw=1,
                    label=f"referee {ref}", markeredgecolor="white", markeredgewidth=0.6)
            for s in pts:
                if s["K"] in (5, 50):
                    ax.annotate(f"K{s['K']}", (s["mean_ratio"], s["fail_ratio"]), fontsize=6, color=MUTED,
                                xytext=(3, 2), textcoords="offset points")
        sel = row["selected"]
        pick = next(s for s in row["settings"] if s["K"] == sel["K"] and s["referee"] == sel["referee"])
        ax.plot(pick["mean_ratio"], pick["fail_ratio"], marker="o", ms=12, mfc="none", mec=INK, mew=1)
        ax.axhline(1.05, color=MUTED, lw=0.8, ls="--")
        ax.axhline(1.0, color=GRID, lw=0.8)
        ax.set_title(f"p = {row['p']:g}  (Relay-BP: {row['baseline']['fails']} fails)", fontsize=8, color=INK)
    for ax in axes[1]:
        ax.set_xlabel("mean time / Relay-BP")
    for ax in axes[:, 0]:
        ax.set_ylabel("failures / Relay-BP")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.legend(h, l, loc="lower center", ncol=3, fontsize=8)
    fig.savefig(OUT / "discovery.pdf")


def fig_noise():
    det = pickle.loads(Path("data/noise_detector.pkl").read_bytes())
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.8))
    ax = axes[0]
    ax.plot(det["train_p"] * 1e3, det["means"], color=BLUE, marker="o", ms=3)
    ax.set_xlabel("$p$ ($\\times 10^{-3}$)"); ax.set_ylabel("mean alarms per pair (X + Z shot)")
    ax.set_title("calibration: alarms rise with noise", fontsize=9, color=INK)
    ax = axes[1]
    for p, c in zip([0.003, 0.004, 0.005], [GREEN, BLUE, ORANGE]):
        d = np.load(f"data/compare_p{p}.npz", allow_pickle=True)
        ax.hist(d["p_count"] * 1e3, bins=np.linspace(2.5, 5.7, 65), color=c, alpha=0.75, label=f"true p = {p:g}")
    ax.axvline(5.25, color=MUTED, ls="--", lw=0.8)
    ax.text(5.2, ax.get_ylim()[1] * 0.8, "switch to\ncheap referee", fontsize=7, color=MUTED, ha="right")
    ax.set_xlabel("estimated $p$ from last 10 pairs ($\\times 10^{-3}$)"); ax.set_ylabel("pairs")
    ax.set_title("alarm-count estimate", fontsize=9, color=INK); ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "noise_detector.pdf")


def fig_big(rows):
    big = rows["big"]
    g, r = big["fail"]["gate"], big["fail"]["relay"]
    # per-basis discordance by path
    d = np.load("data/large_p0.003.npz", allow_pickle=True)
    gb, rb = ~d["correct"][..., 0], ~d["correct"][..., 1]
    names = ["first_leg", "agreed", "no_solution", "disagreed"]
    nice = ["first 80\niterations", "seeds\nagreed", "no solution\n(referee)", "disagreed\n(referee)"]
    go = [int((gb & ~rb & (d["path"] == i)).sum()) for i in range(4)]
    ro = [int((rb & ~gb & (d["path"] == i)).sum()) for i in range(4)]
    fig, ax = plt.subplots(figsize=(4.8, 2.8))
    x = np.arange(4)
    ax.bar(x - 0.18, go, 0.34, color=GREEN, label="only the gate failed", edgecolor="white")
    ax.bar(x + 0.18, ro, 0.34, color=BLUE, label="only Relay-BP failed", edgecolor="white")
    for xi, a, b in zip(x, go, ro):
        ax.text(xi - 0.18, a + 0.3, str(a), ha="center", fontsize=7, color=INK)
        ax.text(xi + 0.18, b + 0.3, str(b), ha="center", fontsize=7, color=INK)
    ax.set_xticks(x, nice, fontsize=7.5); ax.set_ylabel("basis decodes"); ax.grid(axis="x", visible=False)
    ax.set_title(f"p = 0.003, 100,000 pairs: {int(g.sum())} vs {int(r.sum())} failed pairs", fontsize=9, color=INK)
    ax.legend(fontsize=7.5)
    fig.savefig(OUT / "p0003_discordance.pdf")


def main():
    rows = load_compare()
    fig_ler(rows); fig_latency(rows); fig_paths(); fig_discovery(); fig_noise(); fig_big(rows)
    for f in ["agree_ler_vs_latency.png", "agree_verdicts.png"]:
        (OUT / f).write_bytes(Path("results", f).read_bytes())
    print("figures ->", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
