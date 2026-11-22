"""Simulate routing policies on a table from collect.py, scored as in the kit.

  python experiments/analyze.py data/p0.004_s11.npz

A pair (X shot k, Z shot k) fails when either fails; its time is the sum. Cascade time is
the light BP time plus the fallback's time when the shot is escalated (cold fallback).
The ML gate is trained on the first half of the pairs and evaluated on the second half.
"""
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

CYCLES = 12


def per_cycle(failed_pairs):
    P = failed_pairs.mean()
    hi = P + 1.96 * np.sqrt(max(P * (1 - P), 1 / len(failed_pairs)) / len(failed_pairs))
    return 1 - (1 - P) ** (1 / CYCLES), 1 - (1 - min(hi, 1)) ** (1 / CYCLES)


def pairs(a, basis):
    """Reshape a per-row array into (shot, basis)."""
    return np.stack([a[basis == 0], a[basis == 1]], axis=1)


def report(name, wrong, secs, escalated=None):
    fail = wrong.any(axis=1)
    ms = secs.sum(axis=1) * 1e3
    rate, hi = per_cycle(fail)
    esc = f"  escalated {escalated.mean():5.1%}" if escalated is not None else ""
    print(f"{name:34s} pair fails {fail.sum():4d}/{len(fail)}  LER/cycle {rate:.2e} (95% hi {hi:.1e})  "
          f"mean {ms.mean():7.1f} ms  p50 {np.median(ms):6.1f}  p99 {np.percentile(ms, 99):7.0f} ms{esc}")


def main(path):
    d = np.load(path, allow_pickle=True)
    tiers = list(d["tiers"])
    names = list(d["feature_names"])
    basis = d["basis"]
    C = {t: pairs(d["correct"][:, i], basis) for i, t in enumerate(tiers)}
    S = {t: pairs(d["seconds"][:, i], basis) for i, t in enumerate(tiers)}
    F = np.stack([d["features"][basis == 0], d["features"][basis == 1]], axis=1)  # shot, basis, feature
    conv = F[..., names.index("converged")] == 1
    corr_wt = F[..., names.index("correction_wt")]

    n = len(conv)
    test = np.arange(n) >= n // 2
    print(f"{path}: p={float(d['p'])}, {n} pairs; test half = {test.sum()} pairs\n")
    print(f"BP-80 converged: {conv.mean():.1%} of shots; wrong when converged: "
          f"{(~C['bp'][conv]).sum()} of {conv.sum()}")
    print(f"correction weight of converged BP: median {np.median(corr_wt[conv]):.0f}, "
          f"fraction <= 4: {(corr_wt[conv] <= 4).mean():.1%}\n")

    def cascade(accept, fallback):
        wrong = np.where(accept, ~C["bp"], ~C[fallback])
        secs = S["bp"] + np.where(accept, 0.0, S[fallback])
        return wrong, secs, ~accept

    # ML gate for escalated shots: predict whether relay_fast is enough, else full relay.
    X = np.concatenate([F.reshape(-1, F.shape[-1]), np.tile([[0], [1]], (n, 1))], axis=1)
    y = ~C["relay_fast"].reshape(-1) & C["relay"].reshape(-1)   # fast tier would hurt
    tr = np.repeat(~test, 2) & ~conv.reshape(-1)
    risk = np.zeros(2 * n)
    if y[tr].sum() >= 3:
        model = make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=2000))
        model.fit(X[tr], y[tr])
        risk = model.predict_proba(X)[:, 1]
    risk = risk.reshape(n, 2)
    print(f"training shots where relay_fast fails but relay succeeds: {int(y[tr].sum())}\n")

    for label, mask in [("ALL PAIRS", np.ones(n, bool)), ("TEST HALF", test)]:
        print(f"--- {label} ---")
        sel = lambda a: a[mask]  # noqa: E731
        for t in ["bposd", "relay", "relay_fast", "lsd"]:
            report(f"{t} alone", sel(~C[t]), sel(S[t]))
        for fb in ["relay", "relay_fast", "lsd"]:
            w, s, e = cascade(conv, fb)
            report(f"BP-80 conv-gate -> {fb}", sel(w), sel(s), sel(e))
        w, s, e = cascade(conv & (corr_wt <= 4), "relay")
        report("gate + weight<=4 rule -> relay", sel(w), sel(s), sel(e))
        # 3-tier: converged -> accept; else ML picks relay_fast or relay.
        for thr in (0.5, 0.2):
            heavy = ~conv & (risk >= thr)
            fast = ~conv & ~heavy
            wrong = np.where(conv, ~C["bp"], np.where(fast, ~C["relay_fast"], ~C["relay"]))
            secs = S["bp"] + np.where(fast, S["relay_fast"], 0) + np.where(heavy, S["relay"], 0)
            report(f"3-tier ML (thr {thr}) heavy {sel(heavy).mean():.0%}", sel(wrong), sel(secs), sel(~conv))
        oracle_fast = ~conv & C["relay_fast"]
        wrong = np.where(conv, ~C["bp"], np.where(oracle_fast, False, ~C["relay"]))
        secs = S["bp"] + np.where(oracle_fast, S["relay_fast"], np.where(conv, 0, S["relay"]))
        report("3-tier ORACLE router", sel(wrong), sel(secs), sel(~conv))
        print()


if __name__ == "__main__":
    main(sys.argv[1])
