"""Stage 1 scoring: evaluate all 12 gate settings per noise level and freeze the selection.

  python experiments/adaptive_select.py data/adapt_p*.npz

Capped runs (K < 50) are derived from the uncapped run: solved within K restarts if it needed
<= 80 + 60 K iterations; time scaled by iterations otherwise (approximate; stage 2 runs them for real).
Selection rule (discussion/09_noise_adaptive_prereg.md): among settings with failure ratio <= 1.05
vs the baseline, the lowest mean time; if none qualifies, K=50 with the R5 referee.
"""
import json
import sys
from pathlib import Path

import numpy as np

FIRST_LEG, LEG = 80, 60
KS = [5, 10, 20, 50]
REFEREES = ["R5", "R2", "R1"]
MAX_FAIL_RATIO = 1.05


def capped(ok, it, secs, K):
    cap = FIRST_LEG + LEG * K
    solved = (ok == 1) & (it <= cap)
    t = np.where(it <= cap, secs, secs * cap / np.maximum(it, 1))
    return solved, t


def policy(d, K, ref):
    idx = {name: i for i, name in enumerate(d["decoders"])}
    ok, it, S, C, L = d["success"], d["iterations"], d["seconds"], d["correct"], d["logical"]
    s0, s1, r = idx["s0"], idx["s1"], idx[ref]
    first = (ok[..., s0] == 1) & (it[..., s0] <= FIRST_LEG)
    ok0, t0 = capped(ok[..., s0], it[..., s0], S[..., s0], K)
    ok1, t1 = capped(ok[..., s1], it[..., s1], S[..., s1], K)
    agree = ok0 & ok1 & (L[..., s0, :] == L[..., s1, :]).all(-1)
    esc = ~ok0 | (~first & ~agree)
    wrong = np.where(esc, ~C[..., r], ~C[..., s0])
    secs = t0 + np.where(ok0 & ~first, t1, 0.0) + np.where(esc, S[..., r], 0.0)
    return wrong.any(1), secs.sum(1), esc


def summary(fail, secs, base_fail, base_secs, esc=None):
    q = lambda a, x: float(np.percentile(a, x))  # noqa: E731
    out = dict(fails=int(fail.sum()), fail_ratio=float(fail.sum() / max(base_fail.sum(), 1)),
               mean_ms=float(secs.mean() * 1e3), mean_ratio=float(secs.mean() / base_secs.mean()),
               p90_ratio=q(secs, 90) / q(base_secs, 90), p99_ratio=q(secs, 99) / q(base_secs, 99))
    if esc is not None:
        out["escalated"] = float(esc.mean())
    return out


def main():
    table, selected = [], {}
    for path in sorted(sys.argv[1:], key=lambda f: float(np.load(f)["p"])):
        d = dict(np.load(path, allow_pickle=True))
        d["decoders"] = list(d["decoders"])
        p, pairs = float(d["p"]), int(d["shots"])
        r5 = d["decoders"].index("R5")
        base_fail, base_secs = (~d["correct"][..., r5]).any(1), d["seconds"][..., r5].sum(1)
        print(f"\np = {p}  ({pairs} pairs)  baseline R5: {base_fail.sum()} failed pairs, "
              f"mean {base_secs.mean()*1e3:.0f} ms, p90 {np.percentile(base_secs, 90)*1e3:.0f}, "
              f"p99 {np.percentile(base_secs, 99)*1e3:.0f}")
        print(f"   {'K':>3s} {'ref':>4s} {'fails':>6s} {'ratio':>6s} {'mean':>6s} {'p90':>6s} {'p99':>6s} {'esc':>6s}")
        rows = []
        for K in KS:
            for ref in REFEREES:
                fail, secs, esc = policy(d, K, ref)
                s = summary(fail, secs, base_fail, base_secs, esc) | dict(K=K, referee=ref)
                rows.append(s)
                print(f"   {K:3d} {ref:>4s} {s['fails']:6d} {s['fail_ratio']:6.2f} {s['mean_ratio']:6.2f} "
                      f"{s['p90_ratio']:6.2f} {s['p99_ratio']:6.2f} {s['escalated']:6.1%}")
        ok = [r for r in rows if r["fail_ratio"] <= MAX_FAIL_RATIO]
        pick = min(ok, key=lambda r: r["mean_ratio"]) if ok else next(r for r in rows if r["K"] == 50 and r["referee"] == "R5")
        print(f"   SELECTED: K={pick['K']} referee={pick['referee']}"
              f"{'' if ok else ' (fallback: no setting met the accuracy rule)'}")
        selected[str(p)] = dict(K=pick["K"], referee=pick["referee"], qualified=bool(ok))
        table.append(dict(p=p, pairs=pairs, baseline=summary(base_fail, base_secs, base_fail, base_secs),
                          settings=rows, selected=selected[str(p)]))
    Path("results").mkdir(exist_ok=True)
    Path("results/adaptive_discovery.json").write_text(json.dumps(table, indent=1))
    Path("results/adaptive_selected.json").write_text(json.dumps(selected, indent=1))
    print("\nfrozen selection -> results/adaptive_selected.json")


if __name__ == "__main__":
    main()
