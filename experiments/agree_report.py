"""Score the agreement gate against Relay-BP using the pre-registered criteria
(discussion/05_preregistration.md).

  python experiments/agree_report.py data/agree_p0.004_s101.npz data/agree_p0.003_s201.npz ...

Writes results/agree_report.json and prints one block per run.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import beta, binomtest, fisher_exact

CYCLES = 12
FIRST_LEG = 80          # pre_iter of Relay-BP: both seeds run this deterministic leg identically
BOOT = 2000
MARGIN, LAT_BOUND = 1.2, 0.8
rng = np.random.default_rng(0)


def per_cycle(P):
    return 1 - (1 - P) ** (1 / CYCLES)


def clopper_pearson(k, n):
    lo = beta.ppf(0.025, k, n - k + 1) if k else 0.0
    hi = beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return lo, hi


def load(path):
    d = np.load(path, allow_pickle=True)
    names = list(d["decoders"])
    get = lambda key: {name: d[key][..., i] for i, name in enumerate(names)}  # noqa: E731
    logical = {name: d["logical"][..., i, :] for i, name in enumerate(names)}
    return dict(p=float(d["p"]), seed=int(d["seed"]), C=get("correct"), S=get("seconds"), ok=get("success"),
                it=get("iterations"), L=logical, n=int(d["shots"]))


def policies(r):
    C, S, ok, L = r["C"], r["S"], r["ok"], r["L"]
    agree = ok["fast_s0"] & ok["fast_s1"] & (L["fast_s0"] == L["fast_s1"]).all(-1)     # (pair, basis)
    single = ok["fast_s0"]
    fast2 = S["fast_s0"] + S["fast_s1"]
    pol = {
        "Relay-BP (kit)": (~C["relay"], S["relay"], np.zeros_like(agree)),
        "fast Relay-BP alone": (~C["fast_s0"], S["fast_s0"], np.zeros_like(agree)),
        "1 seed, escalate if no solution": (np.where(single, ~C["fast_s0"], ~C["relay"]),
                                            S["fast_s0"] + np.where(single, 0, S["relay"]), ~single),
        "AGREEMENT -> Relay-BP (primary)": (np.where(agree, ~C["fast_s0"], ~C["relay"]),
                                            fast2 + np.where(agree, 0, S["relay"]), ~agree),
        "agreement -> Relay-BP, parallel*": (np.where(agree, ~C["fast_s0"], ~C["relay"]),
                                             np.maximum(S["fast_s0"], S["fast_s1"]) + np.where(agree, 0, S["relay"]),
                                             ~agree),
        "agreement -> nconv2": (np.where(agree, ~C["fast_s0"], ~C["relay_nconv2"]),
                                fast2 + np.where(agree, 0, S["relay_nconv2"]), ~agree),
    }
    return pol, agree


def timing(secs):
    ms = secs.sum(1) * 1e3
    return {q: float(v) for q, v in zip(["mean", "p50", "p95", "p99", "max"],
                                        [ms.mean(), *np.percentile(ms, [50, 95, 99]), ms.max()])}


def paired(gate_fail, relay_fail, gate_ms, relay_ms):
    """Failure-probability ratio and mean-latency ratio with paired bootstrap bounds."""
    n = len(gate_fail)
    idx = rng.integers(0, n, size=(BOOT, n))
    gf, rf = gate_fail[idx].sum(1), relay_fail[idx].sum(1)
    fail_ratio = np.where(rf > 0, gf / np.maximum(rf, 1), np.where(gf > 0, 1e9, 1.0))  # 0/0 counts as equal
    lat_ratio = gate_ms[idx].mean(1) / relay_ms[idx].mean(1)
    b = int((gate_fail & ~relay_fail).sum())    # gate fails, relay right
    c = int((~gate_fail & relay_fail).sum())    # gate right, relay fails
    return dict(
        fail_ratio=float(gate_fail.sum() / max(relay_fail.sum(), 1)),
        fail_ratio_upper95=float(np.quantile(fail_ratio, 0.95)),
        gate_worse=b, gate_better=c,
        mcnemar_p=float(binomtest(b, b + c, 0.5).pvalue) if b + c else 1.0,
        lat_ratio=float(gate_ms.mean() / relay_ms.mean()),
        lat_ratio_upper95=float(np.quantile(lat_ratio, 0.975)),
        p99_ratio=float(np.percentile(gate_ms, 99) / np.percentile(relay_ms, 99)),
        p99_ratio_upper95=float(np.quantile(
            np.percentile(gate_ms[idx], 99, axis=1) / np.percentile(relay_ms[idx], 99, axis=1), 0.975)),
    )


def verdicts(pr):
    if pr["fail_ratio_upper95"] < MARGIN:
        acc = "PASS"
    elif pr["fail_ratio"] > MARGIN:
        acc = "FAIL"
    else:
        acc = "INCONCLUSIVE"
    return acc, "PASS" if pr["lat_ratio_upper95"] <= LAT_BOUND else "FAIL"


def analyse(path):
    r = load(path)
    pol, agree = policies(r)
    relay_fail = pol["Relay-BP (kit)"][0].any(1)
    relay_ms = pol["Relay-BP (kit)"][1].sum(1)
    out = dict(file=path, p=r["p"], seed=r["seed"], pairs=r["n"], policies={})
    print(f"\n=== {path}: p={r['p']}, {r['n']} pairs, seed {r['seed']} ===")
    print(f"{'policy':36s} {'fails':>6s} {'LER/cycle [95% CI]':>28s} {'esc':>6s} "
          f"{'mean':>7s} {'p50':>6s} {'p95':>6s} {'p99':>7s} {'max':>7s}  (ms per pair)")
    for name, (wrong, secs, esc) in pol.items():
        fail = wrong.any(1)
        k = int(fail.sum())
        lo, hi = clopper_pearson(k, r["n"])
        t = timing(secs)
        entry = dict(fails=k, ler=per_cycle(k / r["n"]), ler_ci=[per_cycle(lo), per_cycle(hi)],
                     escalated=float(esc.mean()), **t)
        if name != "Relay-BP (kit)":
            entry["paired"] = paired(fail, relay_fail, secs.sum(1), relay_ms)
        out["policies"][name] = entry
        print(f"{name:36s} {k:6d} {entry['ler']:9.2e} [{entry['ler_ci'][0]:.1e}, {entry['ler_ci'][1]:.1e}] "
              f"{esc.mean():6.1%} {t['mean']:7.1f} {t['p50']:6.1f} {t['p95']:6.0f} {t['p99']:7.0f} {t['max']:7.0f}")

    pr = out["policies"]["AGREEMENT -> Relay-BP (primary)"]["paired"]
    acc, lat = verdicts(pr)
    out["verdict"] = dict(accuracy=acc, latency=lat)
    print(f"\nprimary vs Relay-BP: failure ratio {pr['fail_ratio']:.2f} (one-sided 95% upper {pr['fail_ratio_upper95']:.2f})"
          f"  gate-worse {pr['gate_worse']} / gate-better {pr['gate_better']}  McNemar p={pr['mcnemar_p']:.2f}")
    print(f"                     mean-latency ratio {pr['lat_ratio']:.2f} (95% upper {pr['lat_ratio_upper95']:.2f})"
          f"  p99 ratio {pr['p99_ratio']:.2f} (95% upper {pr['p99_ratio_upper95']:.2f})")
    print(f"                     VERDICT accuracy: {acc}   latency: {lat}")

    # Diagnostics on the gate itself (per basis shot).
    ok, L, it, C = r["ok"], r["L"], r["it"], r["C"]
    no_solution = ~(ok["fast_s0"] & ok["fast_s1"])
    disagree = ~no_solution & ~agree
    first_leg = (it["fast_s0"] <= FIRST_LEG) & (it["fast_s1"] <= FIRST_LEG)
    wrong_agree = agree & ~C["fast_s0"]
    hard = it["fast_s0"] > FIRST_LEG
    diag = dict(
        shots=int(agree.size), escalated_no_solution=int(no_solution.sum()), escalated_disagree=int(disagree.sum()),
        agreed=int(agree.sum()), agreed_wrong=int(wrong_agree.sum()),
        agreed_wrong_first_leg=int((wrong_agree & first_leg).sum()), agreed_first_leg=int((agree & first_leg).sum()),
        agreed_wrong_later=int((wrong_agree & ~first_leg).sum()), agreed_later=int((agree & ~first_leg).sum()),
        agreed_wrong_by_basis=[int(wrong_agree[:, b].sum()) for b in (0, 1)],
        hard_shots=int(hard.sum()),
        hard_logical_differ=int((hard & (L["fast_s0"] != L["fast_s1"]).any(-1)).sum()),
        hard_iterations_differ=int((hard & (it["fast_s0"] != it["fast_s1"])).sum()),
    )
    out["gate"] = diag
    print(f"gate: escalated {diag['escalated_no_solution']} no-solution + {diag['escalated_disagree']} disagreement "
          f"of {diag['shots']} basis-shots; agreed-but-wrong {diag['agreed_wrong']}/{diag['agreed']} "
          f"(first leg {diag['agreed_wrong_first_leg']}/{diag['agreed_first_leg']}, later "
          f"{diag['agreed_wrong_later']}/{diag['agreed_later']}; X/Z {diag['agreed_wrong_by_basis']})")
    print(f"seeds: of {diag['hard_shots']} shots past the first leg, iterations differ on "
          f"{diag['hard_iterations_differ']}, logical vectors differ on {diag['hard_logical_differ']}")

    # Prefix stability (descriptive only).
    wrong, secs, _ = pol["AGREEMENT -> Relay-BP (primary)"]
    out["prefix"] = []
    for m in sorted({1000, 2000, r["n"]}):
        if m <= r["n"]:
            g, rl = wrong[:m].any(1).sum(), relay_fail[:m].sum()
            out["prefix"].append(dict(pairs=m, gate_fails=int(g), relay_fails=int(rl),
                                      lat_ratio=float(secs[:m].sum(1).mean() / relay_ms[:m].mean())))
    print("prefix (descriptive): " + "; ".join(f"{x['pairs']} pairs: {x['gate_fails']} vs {x['relay_fails']} fails, "
                                               f"latency x{x['lat_ratio']:.2f}" for x in out["prefix"]))
    return out


def replication(results):
    by_p = {}
    for r in results:
        by_p.setdefault(r["p"], []).append(r)
    for p, runs in by_p.items():
        if len(runs) < 2:
            continue
        a, b = runs[:2]
        rows = []
        for name in ["Relay-BP (kit)", "AGREEMENT -> Relay-BP (primary)"]:
            fa, fb = a["policies"][name]["fails"], b["policies"][name]["fails"]
            pval = fisher_exact([[fa, a["pairs"] - fa], [fb, b["pairs"] - fb]])[1]
            rows.append(f"{name}: {fa} vs {fb} fails (Fisher p={pval:.2f})")
        ea = round(a["policies"]["AGREEMENT -> Relay-BP (primary)"]["escalated"] * a["pairs"] * 2)
        eb = round(b["policies"]["AGREEMENT -> Relay-BP (primary)"]["escalated"] * b["pairs"] * 2)
        pval = fisher_exact([[ea, 2 * a["pairs"] - ea], [eb, 2 * b["pairs"] - eb]])[1]
        rows.append(f"escalations {ea} vs {eb} (Fisher p={pval:.2f})")
        print(f"\nreplication at p={p} (seeds {a['seed']} vs {b['seed']}): " + "; ".join(rows))


def main():
    results = [analyse(f) for f in sys.argv[1:]]
    replication(results)
    gf = sum(r["policies"]["AGREEMENT -> Relay-BP (primary)"]["fails"] for r in results)
    rf = sum(r["policies"]["Relay-BP (kit)"]["fails"] for r in results)
    print(f"\npooled over {sum(r['pairs'] for r in results)} pairs: gate {gf} vs Relay-BP {rf} pair failures "
          f"-> pooled check {'PASS' if gf <= rf else 'FAIL'}")
    Path("results").mkdir(exist_ok=True)
    Path("results/agree_report.json").write_text(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
