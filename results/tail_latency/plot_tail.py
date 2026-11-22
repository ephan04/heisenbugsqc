"""Tail-latency chart: fraction of X/Z pairs slower than t, per decoder, one panel per noise level.

  python plot_tail.py out.png tail_p0.004.npz tail_p0.005.npz
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np

# Reference categorical palette (light mode), fixed slot order; color follows the decoder.
SERIES = [("relay", "Relay-BP", "#2a78d6"), ("bposd", "BP-OSD", "#eb6834"),
          ("router", "ML router", "#1baf7a"), ("gate", "Agreement gate", "#eda100")]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

out, files = sys.argv[1], sys.argv[2:]


def fmt(ms):
    return f"{ms / 1000:.1f} s" if ms >= 1000 else f"{ms:.0f} ms"


def tick(x, _):
    return {1: "1 ms", 10: "10 ms", 100: "100 ms", 1000: "1 s", 10000: "10 s"}.get(round(x), "")
plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK})
fig, axes = plt.subplots(1, len(files), figsize=(6.2 * len(files), 4.6), sharey=True,
                         facecolor=SURFACE)
axes = np.atleast_1d(axes)

for ax, f in zip(axes, files):
    d = np.load(f, allow_pickle=True)
    ax.set_facecolor(SURFACE)
    n = len(d["relay_secs"])
    ends = []
    for key, label, color in SERIES:
        ms = np.sort(d[f"{key}_secs"].sum(axis=1) * 1e3)
        surv = 1 - np.arange(n) / n          # fraction of pairs taking >= this long
        P = d[f"{key}_fail"].any(axis=1).mean()
        ler = 1 - (1 - P) ** (1 / 12)
        stats = f"{label}\np99 {fmt(np.percentile(ms, 99))} · mean {fmt(ms.mean())} · LER {ler:.1e}"
        ax.step(ms, surv, where="post", color=color, lw=2, label=stats)
        p99 = np.percentile(ms, 99)
        ax.plot([p99], [0.01], "o", ms=8, color=color, mec=SURFACE, mew=2, zorder=5)
        ends.append((ms[-1], label, color))
    for frac, txt in [(0.5, "median"), (0.1, "p90"), (0.01, "p99")]:
        ax.axhline(frac, color=GRID, lw=1, zorder=0)
        ax.text(1.0, frac, f" {txt}", transform=ax.get_yaxis_transform(), va="center",
                ha="left", fontsize=8, color=INK2)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_ylim(0.8 / n, 1.05)
    ax.set_xlabel("decode time per X+Z pair (log scale)")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(tick))
    ax.legend(loc="lower left", frameon=False, fontsize=8, labelspacing=0.9, handlelength=1.6)
    ax.grid(True, which="major", axis="x", color=GRID, lw=0.8)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    K, ref, t = int(d["K"]), str(d["referee"]), float(d["t"])
    ax.set_title(f"p = {float(d['p'])}   ({n:,} pairs; gate K={K}, {ref} referee; router t={t})",
                 fontsize=10, color=INK, loc="left")
axes[0].set_ylabel("fraction of pairs at least this slow (log scale)")
axes[0].set_yticks([1, 0.5, 0.1, 0.01, 0.001], ["100%", "50%", "10%", "1%", "0.1%"])
fig.suptitle("Tail latency on identical shots: a curve further left is faster; dots mark each decoder's p99",
             x=0.01, ha="left", fontsize=11, color=INK)
fig.text(0.01, 0.01, "All four decoders ran on the same fresh shots (seeds 1000/1001), one process per noise level, decoder order shuffled per shot. "
         "Absolute times are inflated by the shared harness; compare decoders within a panel.", fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(out, dpi=170, facecolor=SURFACE)
print("saved", out)
