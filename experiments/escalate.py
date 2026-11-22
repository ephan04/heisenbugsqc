"""Confidence-based escalation: fast Relay-BP first, a learned gate decides whether to also run full Relay-BP.

  python experiments/escalate.py data/v2_p0.004.npz [more files...]

Policy per shot: run relay_fast (its first leg is an 80-iteration BP, so easy shots stop there).
A logistic-regression gate on its diagnostics predicts P(relay_fast is wrong). Above the threshold
the shot is escalated to full Relay-BP, whose answer replaces it; the time is relay_fast + relay.

Pairs are split 50 / 25 / 25 into train / validation / test. The threshold is chosen on validation as
the fastest one whose pair-failure count is within `--slack` of Relay-BP alone; test numbers are reported.
"""
import argparse
import json

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

CYCLES = 12
GATE_FEATURES = ["rf_success", "rf_iters", "rf_weight", "rf_cost", "rf_min_abs_post", "rf_n_post_lt1",
                 "syndrome_wt"]


def per_cycle(fail):
    return 1 - (1 - fail.mean()) ** (1 / CYCLES)


def by_pair(a, basis):
    return np.stack([a[basis == 0], a[basis == 1]], axis=1)


def summary(wrong, secs):
    fail = wrong.any(axis=1)
    ms = secs.sum(axis=1) * 1e3
    return dict(fails=int(fail.sum()), n=len(fail), ler=per_cycle(fail), mean_ms=ms.mean(),
                p50_ms=float(np.median(ms)), p99_ms=float(np.percentile(ms, 99)))


def line(name, s, extra=""):
    return (f"{name:30s} fails {s['fails']:4d}/{s['n']}  LER/cycle {s['ler']:.2e}  mean {s['mean_ms']:7.1f} ms  "
            f"p50 {s['p50_ms']:6.1f}  p99 {s['p99_ms']:6.0f}{extra}")


def analyse(path, slack):
    d = np.load(path, allow_pickle=True)
    tiers, names, basis = list(d["tiers"]), list(d["feature_names"]), d["basis"]
    C = {t: by_pair(d["correct"][:, i], basis) for i, t in enumerate(tiers)}
    S = {t: by_pair(d["seconds"][:, i], basis) for i, t in enumerate(tiers)}
    F = np.stack([d["features"][basis == 0], d["features"][basis == 1]], axis=1)
    n = F.shape[0]
    X = np.concatenate([F[..., [names.index(f) for f in GATE_FEATURES]],
                        np.broadcast_to(np.array([0.0, 1.0])[None, :, None], (n, 2, 1))], axis=2)
    split = np.arange(n) * 4 // n            # 0,1 train; 2 validation; 3 test
    train, val, test = split <= 1, split == 2, split == 3

    y = ~C["relay_fast"]
    model = make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", C=0.5, max_iter=5000))
    if len(np.unique(y[train])) < 2:
        risk = np.zeros((n, 2))                       # nothing to learn: success-only escalation
    else:
        model.fit(X[train].reshape(-1, X.shape[-1]), y[train].reshape(-1))
        risk = model.predict_proba(X.reshape(-1, X.shape[-1]))[:, 1].reshape(n, 2)

    def policy(escalate):
        wrong = np.where(escalate, ~C["relay"], ~C["relay_fast"])
        secs = S["relay_fast"] + np.where(escalate, S["relay"], 0.0)
        return wrong, secs

    thresholds = np.r_[0.0, np.quantile(risk[train], np.linspace(0.5, 0.999, 60)), 1.01]
    curve, target = [], (~C["relay"][val]).any(axis=1).sum() + slack
    succ = F[..., names.index("rf_success")] == 1
    for thr in thresholds:
        w, s = policy(~succ | (risk >= thr))          # an unsuccessful fast run always escalates
        curve.append(dict(thr=float(thr), val=summary(w[val], s[val]), test=summary(w[test], s[test]),
                          escalated=float((~succ[test] | (risk[test] >= thr)).mean())))
    ok = [c for c in curve if c["val"]["fails"] <= target] or curve[:1]   # thr 0 = always escalate
    chosen = min(ok, key=lambda c: c["val"]["mean_ms"])

    # Gemini's deterministic alternative: escalate unless it succeeded within K iterations and cost <= W.
    iters, cost = F[..., names.index("rf_iters")], F[..., names.index("rf_cost")]
    grid = []
    for K in np.unique(np.quantile(iters[train[:, None] & succ], np.linspace(0.5, 1, 11))):
        for W in np.quantile(cost[train], np.linspace(0.5, 1, 11)):
            w, s = policy(~succ | (iters > K) | (cost > W))
            grid.append(dict(K=float(K), W=float(W), val=summary(w[val], s[val]), test=summary(w[test], s[test])))
    grid_ok = [g for g in grid if g["val"]["fails"] <= target] or [min(grid, key=lambda g: g["val"]["fails"])]
    det_rule = min(grid_ok, key=lambda g: g["val"]["mean_ms"])

    oracle_w, oracle_s = policy(y & C["relay"])            # escalate exactly the shots relay would fix
    rule_w, rule_s = policy(F[..., names.index("rf_success")] == 0)
    p = float(d["p"])
    out = {"p": p, "relay": summary(~C["relay"][test], S["relay"][test]),
           "bposd": summary(~C["bposd"][test], S["bposd"][test]),
           "relay_fast": summary(~C["relay_fast"][test], S["relay_fast"][test]),
           "rule": summary(rule_w[test], rule_s[test]), "oracle": summary(oracle_w[test], oracle_s[test]),
           "ml": chosen["test"], "ml_thr": chosen["thr"], "ml_escalated": chosen["escalated"],
           "det_rule": det_rule["test"], "det_rule_KW": [det_rule["K"], det_rule["W"]],
           "curve": [dict(thr=c["thr"], escalated=c["escalated"], **c["test"]) for c in curve]}

    print(f"\n{path}  p={p}  test pairs={test.sum()}  (gate trained on {train.sum()} pairs)")
    print(line("BP-OSD (kit)", out["bposd"]))
    print(line("Relay-BP (kit)", out["relay"]))
    print(line("Relay-fast alone", out["relay_fast"]))
    print(line("rule: escalate if no solution", out["rule"]))
    print(line("ML gate", out["ml"], f"  thr {chosen['thr']:.3f} escalated {chosen['escalated']:.1%}"))
    print(line("rule: iters<=K & cost<=W", out["det_rule"], f"  K={det_rule['K']:.0f} W={det_rule['W']:.0f}"))
    print(line("oracle gate", out["oracle"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--slack", type=int, default=0, help="extra validation pair failures allowed vs Relay-BP")
    ap.add_argument("--json", default="results/escalate.json")
    args = ap.parse_args()
    results = [analyse(f, args.slack) for f in args.files]
    import os
    os.makedirs(os.path.dirname(args.json), exist_ok=True)
    with open(args.json, "w") as fh:
        json.dump(results, fh, indent=1)
    print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
