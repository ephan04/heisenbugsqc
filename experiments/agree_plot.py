"""Plot LER per cycle vs mean pair decode time, one panel per run, from results/agree_report.json.

  python experiments/agree_plot.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SERIES = [  # (policy key, label, colour, marker) - fixed categorical order, validated palette
    ("Relay-BP (kit)", "Relay-BP (baseline)", "#2a78d6", "o"),
    ("fast Relay-BP alone", "fast Relay-BP alone", "#eb6834", "^"),
    ("AGREEMENT -> Relay-BP (primary)", "agreement gate", "#1baf7a", "D"),
    ("agreement -> Relay-BP, parallel*", "agreement gate, 2 cores*", "#eda100", "s"),
]
INK, MUTED, GRID, SURFACE = "#1f1f1e", "#6b6a63", "#e6e5df", "#fcfcfb"

runs = json.load(open("results/agree_report.json"))
runs.sort(key=lambda r: (r["p"], r["seed"]))
fig, axes = plt.subplots(1, len(runs), figsize=(4.2 * len(runs), 4.2), sharey=True, facecolor=SURFACE)
for ax, run in zip(axes, runs):
    ax.set_facecolor(SURFACE)
    for key, label, colour, marker in SERIES:
        e = run["policies"][key]
        lo, hi = e["ler_ci"]
        ax.errorbar(e["mean"], e["ler"], yerr=[[e["ler"] - lo], [hi - e["ler"]]], fmt=marker, ms=8, color=colour,
                    mec=SURFACE, mew=1.5, elinewidth=2, capsize=0, label=label, zorder=3)
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.xaxis.set_minor_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}" if str(int(v))[0] in "25" else ""))
    ax.set_yscale("log")
    ax.set_title(f"p = {run['p']}  ·  {run['pairs']} pairs  ·  seed {run['seed']}", fontsize=10, color=INK)
    ax.set_xlabel("mean decode time per X+Z pair (ms, log)", fontsize=9, color=MUTED)
    ax.grid(True, which="major", color=GRID, lw=0.8)
    ax.tick_params(colors=MUTED, labelsize=8)
    for s in ax.spines.values():
        s.set_color(GRID)
axes[0].set_ylabel("logical error rate per cycle (log, 95% CI)", fontsize=9, color=MUTED)
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, fontsize=9, labelcolor=INK)
fig.suptitle("Agreement gate vs Relay-BP on the Gross code (same shots per panel)", fontsize=12, color=INK)
fig.text(0.5, 0.005, "* 2 cores: the two fast runs in parallel (time = slower of the two); hypothetical, not measured",
         ha="center", fontsize=7.5, color=MUTED)
fig.tight_layout(rect=(0, 0.08, 1, 0.95))
fig.savefig("results/agree_ler_vs_latency.png", dpi=160, facecolor=SURFACE)
print("wrote results/agree_ler_vs_latency.png")

# Verdict chart: ratios to Relay-BP on the same shots, with the pre-registered bounds.
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6), facecolor=SURFACE)
names = [f"p={r['p']} (seed {r['seed']})" for r in runs]
ys = list(range(len(runs)))[::-1]
gate = "AGREEMENT -> Relay-BP (primary)"
for ax, key, upper, bound, title in [
        (a1, "fail_ratio", "fail_ratio_upper95", 1.2, "Pair failures vs Relay-BP\n(one-sided 95% upper bound; pass if < 1.2)"),
        (a2, "lat_ratio", "lat_ratio_upper95", 0.8, "Mean decode time vs Relay-BP\n(95% upper bound; pass if <= 0.8)")]:
    ax.set_facecolor(SURFACE)
    for y, r in zip(ys, runs):
        pr = r["policies"][gate]["paired"]
        ok = pr[upper] < bound if key == "fail_ratio" else pr[upper] <= bound
        ax.plot([pr[key], pr[upper]], [y, y], color="#1baf7a", lw=2, zorder=2)
        ax.plot(pr[key], y, "D", ms=8, color="#1baf7a", mec=SURFACE, mew=1.5, zorder=3)
        ax.annotate(f"{pr[key]:.2f}  ({'pass' if ok else 'fail' if key == 'lat_ratio' or pr[key] > bound else 'inconclusive'})",
                    (max(pr[key], pr[upper]), y), xytext=(8, -3), textcoords="offset points", fontsize=8, color=INK)
    ax.axvline(1.0, color=MUTED, lw=1, ls=":")
    ax.axvline(bound, color="#eb6834", lw=1.5, ls="--")
    ax.set_yticks(ys, names, fontsize=8, color=INK)
    ax.set_xlim(0.3, 1.75)
    ax.set_title(title, fontsize=9, color=INK)
    ax.set_xlabel("ratio to Relay-BP (1 = same)", fontsize=8, color=MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(True, axis="x", color=GRID, lw=0.8)
    for sp in ax.spines.values():
        sp.set_color(GRID)
fig.suptitle("Agreement gate: pre-registered verdicts per run", fontsize=11, color=INK)
fig.tight_layout()
fig.savefig("results/agree_verdicts.png", dpi=160, facecolor=SURFACE)
print("wrote results/agree_verdicts.png")
