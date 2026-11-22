"""Train a router that decides, for each hard shot, whether to use relay-BP or BP-OSD,
and compare routing policies on held-out shots. Saves a trade-off plot.

  python train_router.py route_X_p0.004.npz --label safe --model logistic
"""
import argparse
import time

import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------- options
parser = argparse.ArgumentParser()
parser.add_argument("data", help="file made by make_routing_data.py")
parser.add_argument("--slow-pct", type=float, default=90,
                    help="'slow' = relay-BP time above this percentile of the hard training shots")
parser.add_argument("--label", choices=["slow", "safe"], default="safe",
                    help="slow: relay-BP is slow. safe: relay-BP is slow AND BP-OSD gets it right")
parser.add_argument("--model", choices=["logistic", "boosting"], default="logistic")
args = parser.parse_args()

# ---------------------------------------------------------------- load the recorded results
d = {key: value for key, value in np.load(args.data).items()}
F, conv = d["features"], d["converged"]   # clues from fast BP, and whether fast BP converged
n = len(conv)

# Hold out 40% of shots as a test set. The classifier never sees them.
test = np.random.default_rng(0).random(n) < 0.4
train = ~test


# ---------------------------------------------------------------- labels
# Only hard shots (fast BP did not converge) reach the router, so train on those.
hard_train = train & ~conv
cut = np.percentile(d["relay_time"][hard_train], args.slow_pct)
slow = d["relay_time"] > cut              # relay-BP takes longer than the cut-off
safe = slow & d["bposd_ok"]               # ...and BP-OSD gets the shot right
target = safe if args.label == "safe" else slow

print(f"{n} shots ({test.sum()} test). Fast BP converged on {conv.mean():.1%}. "
      f"'slow' = relay-BP over {cut * 1e3:.0f} ms")
print(f"training label '{args.label}': {target[hard_train].sum()} positive examples, model: {args.model}")

# ---------------------------------------------------------------- train the classifier
if args.model == "logistic":
    model = make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=1000))
else:
    model = HistGradientBoostingClassifier(max_iter=200, random_state=0)
model.fit(F[hard_train], target[hard_train])
prob = model.predict_proba(F)[:, 1]       # model's confidence that the shot should go to BP-OSD

# Time of one classifier call. It is added to every hard shot's latency.
start = time.perf_counter()
for _ in range(200):
    model.predict_proba(F[:1])
clf_time = (time.perf_counter() - start) / 200
print(f"classifier: {clf_time * 1e3:.2f} ms per call")

hard_test = test & ~conv
caught = (prob >= 0.5)[hard_test & target].mean()
false_alarm = (prob >= 0.5)[hard_test & ~target].mean()
print(f"at t=0.5: flags {caught:.0%} of '{args.label}' test shots, "
      f"false alarms on {false_alarm:.0%} of the others\n")

# ---------------------------------------------------------------- evaluate routing policies
results = []   # (name, fail %, mean ms, p99 ms), used for the plot


def evaluate(name, to_osd, gate=True, extra=0.0):
    """Replay one policy on the test shots using the recorded times and outcomes.

    to_osd: for each shot, True = send to BP-OSD, False = send to relay-BP.
    gate:   run fast BP first, and accept its answer when it converged.
    extra:  time added to each hard shot (the classifier's own cost).
    """
    strong_time = np.where(to_osd, d["bposd_time"], d["relay_time"])
    strong_ok = np.where(to_osd, d["bposd_ok"], d["relay_ok"])
    if gate:
        total = d["bp_time"] + np.where(conv, 0.0, strong_time + extra)
        ok = np.where(conv, d["bp_ok"], strong_ok)
        sent = (to_osd & ~conv)[test].mean()
    else:
        total, ok, sent = strong_time, strong_ok, to_osd[test].mean()
    ms, ok = total[test] * 1e3, ok[test]
    print(f"{name:34s} {(~ok).sum():5d} {(~ok).mean():7.2%} {ms.mean():9.1f} "
          f"{np.percentile(ms, 99):9.0f} {sent:8.1%}")
    results.append((name, (~ok).mean() * 100, ms.mean(), np.percentile(ms, 99)))


none, every = np.zeros(n, bool), np.ones(n, bool)
print(f"{'policy':34s} {'fails':>5s} {'fail %':>7s} {'mean ms':>9s} {'p99 ms':>9s} {'to OSD':>8s}")
evaluate("relay-BP only", none, gate=False)
evaluate("BP-OSD only", every, gate=False)
evaluate("BP gate -> relay-BP", none)
evaluate("BP gate -> BP-OSD", every)
for t in [0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99]:
    evaluate(f"BP gate -> router (t={t})", prob >= t, extra=clf_time)
evaluate("BP gate -> perfect router (slow)", slow)    # cheats: knows the true answer
evaluate("BP gate -> perfect router (safe)", safe)    # cheats: knows the true answer

# ---------------------------------------------------------------- plot
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
router = [r for r in results if "-> router" in r[0]]
markers = [("relay-BP only", "s", "tab:green"),
           ("BP-OSD only", "s", "tab:red"),
           ("BP gate -> perfect router (slow)", "*", "tab:orange"),
           ("BP gate -> perfect router (safe)", "*", "tab:purple")]

for ax, col, xlabel in [(axes[0], 2, "mean time per shot (ms)"),
                        (axes[1], 3, "p99 time per shot (ms)")]:
    ax.plot([r[col] for r in router], [r[1] for r in router], "o-", color="tab:blue",
            label=f"ML router ({args.model}, varying t)")
    for r in router:
        ax.annotate(r[0].split("(")[1].rstrip(")"), (r[col], r[1]),
                    textcoords="offset points", xytext=(5, 5), fontsize=8)
    for name, marker, color in markers:
        r = next(r for r in results if r[0] == name)
        ax.plot(r[col], r[1], marker, color=color, markersize=13, label=name)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("failure rate per shot (%)")
    ax.set_xscale("log")
    ax.grid(alpha=0.3)

axes[0].legend(fontsize=8)
axes[0].set_title("accuracy vs. average speed")
axes[1].set_title("accuracy vs. worst-case speed")
fig.suptitle(f"Routing between relay-BP and BP-OSD ({args.data}, label: {args.label})")
fig.tight_layout()
out = args.data.replace(".npz", f"_{args.label}_{args.model}_tradeoff.png")
fig.savefig(out, dpi=150)
print(f"\nplot saved to {out}")

import joblib
model_file = args.data.replace(".npz", f"_{args.label}_{args.model}.joblib")
joblib.dump(model, model_file)
print(f"model saved to {model_file}")
