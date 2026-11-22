"""Version (a) of the ML router: a hard-shot spotter that sends a shot straight to the referee.

  python experiments/hardshot.py headroom     # what a perfect spotter could save (no ML)
  python experiments/hardshot.py check        # train on 60% of discovery shots, replay on the other 40%

Per basis decode, the gate (revised table) either runs normally, or skips the fast runs and goes straight to
the referee. Skipping can only change time, plus the outcome on the shots the gate would have accepted
(where the referee's answer replaces the fast answer). Outcomes are replayed from the recorded per-decoder
results in data/adapt_p*.npz; the fast runs' capped times are derived from the uncapped ones, as in adaptive_select.py.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "kit"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from adaptive_select import FIRST_LEG, capped  # noqa: E402
from noise_ml import DISCOVERY, LEVELS, TABLE  # noqa: E402


def basis_outcomes(d, K, ref):
    """Per (pair, basis): wrong and seconds for the normal gate path, and for skipping to the referee."""
    idx = {name: i for i, name in enumerate(d["decoders"])}
    ok, it, S, C, L = d["success"], d["iterations"], d["seconds"], d["correct"], d["logical"]
    s0, s1, r = idx["s0"], idx["s1"], idx[ref]
    first = (ok[..., s0] == 1) & (it[..., s0] <= FIRST_LEG)
    ok0, t0 = capped(ok[..., s0], it[..., s0], S[..., s0], K)
    ok1, t1 = capped(ok[..., s1], it[..., s1], S[..., s1], K)
    agree = ok0 & ok1 & (L[..., s0, :] == L[..., s1, :]).all(-1)
    esc = ~ok0 | (~first & ~agree)
    gate_wrong = np.where(esc, ~C[..., r], ~C[..., s0])
    gate_secs = t0 + np.where(ok0 & ~first, t1, 0.0) + np.where(esc, S[..., r], 0.0)
    return dict(gate_wrong=gate_wrong, gate_secs=gate_secs, skip_wrong=~C[..., r], skip_secs=S[..., r],
                esc=esc, first=first, base_wrong=~C[..., idx["R5"]], base_secs=S[..., idx["R5"]])


def load(p):
    d = dict(np.load(f"data/adapt_p{p}.npz", allow_pickle=True))
    d["decoders"] = list(d["decoders"])
    return d


def evaluate(o, skip):
    """Pair-level failures and time for a per-(pair, basis) skip mask."""
    wrong = np.where(skip, o["skip_wrong"], o["gate_wrong"]).any(1)
    secs = np.where(skip, o["skip_secs"], o["gate_secs"]).sum(1)
    return wrong, secs


def summary(wrong, secs, o):
    bw, bs = o["base_wrong"].any(1), o["base_secs"].sum(1)
    q = lambda x, k: np.percentile(x, k)  # noqa: E731
    return (f"fails {wrong.sum():4d} (RBP {bw.sum():4d})  mean {secs.mean() / bs.mean():.2f}x  "
            f"p90 {q(secs, 90) / q(bs, 90):.2f}x  p99 {q(secs, 99) / q(bs, 99):.2f}x")


def headroom():
    print("Perfect spotter: skip exactly the decodes the gate would escalate (same outcome, no wasted fast runs).")
    print("Also shown: skip every decode that is not solved in the first leg.\n")
    for p in LEVELS:
        o = basis_outcomes(load(p), *TABLE[p])
        print(f"p={p}  setting K={TABLE[p][0]} {TABLE[p][1]}   escalated {o['esc'].mean():.1%} of decodes")
        print(f"   gate as is        : {summary(*evaluate(o, np.zeros_like(o['esc'])), o)}")
        print(f"   perfect spotter   : {summary(*evaluate(o, o['esc']), o)}")
        print(f"   skip if not first : {summary(*evaluate(o, ~o['first']), o)}")
        best = (o["skip_secs"] < o["gate_secs"]) & (o["skip_wrong"] <= o["gate_wrong"])
        print(f"   best-of-both      : {summary(*evaluate(o, best), o)}  (skip whenever it is faster and no worse)")




# ---------------------------------------------------------------- quick check (discussion/19)
import pickle  # noqa: E402
import time  # noqa: E402

import scipy.sparse as sp  # noqa: E402
from circuit import GROSS_CIRCUITS, dem_matrices, detector_ids, load_circuit, sample  # noqa: E402

CHECKS = 72
FEATURES = ["alarms", "other_alarms", "adj_pairs", "pair_density", "isolated", "repeat_same_check", "max_cycle",
            "p_hat"] + [f"cycle_{c}" for c in range(13)]


class FeatureMaker:
    """Microsecond features of one basis syndrome (936 bits) plus the other basis's alarm count."""

    def __init__(self, basis):
        c = load_circuit(GROSS_CIRCUITS[basis], 0.004)
        H, _, _ = dem_matrices(c, basis)
        A = (H.astype(np.int32) @ H.T.astype(np.int32)).tocsr()
        A.setdiag(0); A.eliminate_zeros(); A.data[:] = 1
        self.A = A.astype(np.float32)
        self.ids = detector_ids(c, basis)
        self.other = np.setdiff1d(np.arange(c.num_detectors), self.ids)

    def __call__(self, det_full, p_hat):
        s = det_full[:, self.ids].astype(np.float32)
        n = s.sum(1)
        As = np.asarray((self.A @ s.T).T)
        pairs = (s * As).sum(1) / 2
        isolated = ((s > 0) & (As == 0)).sum(1)
        cyc = s.reshape(len(s), -1, CHECKS)
        repeat = (cyc[:, 1:] * cyc[:, :-1]).sum((1, 2))
        per_cycle = cyc.sum(2)
        return np.column_stack([n, det_full[:, self.other].sum(1), pairs, pairs / np.maximum(n, 1), isolated, repeat,
                                per_cycle.max(1), p_hat * 1e3, per_cycle])


def regime(p_hat):
    """0: full-referee settings (K=10 R5); 1: cheap-referee settings. Same lookup as the gate."""
    grid = np.array(sorted(TABLE))
    near = grid[np.abs(grid[None] - p_hat[:, None]).argmin(1)]
    return (near >= 0.0055).astype(int)


def p_hat_stream(totals, det):
    """Causal alarm-count estimate from the last 10 pairs, including the current one, in shot order."""
    c = np.cumsum(totals); w = 10
    m = c.copy(); m[w:] = c[w:] - c[:-w]
    m = m / np.minimum(np.arange(1, len(totals) + 1), w)
    return np.interp(m, det["means"], det["train_p"])


def build():
    det = pickle.loads(Path("data/noise_detector.pkl").read_bytes())
    fm = {b: FeatureMaker(b) for b in "XZ"}
    rows = []
    for p in LEVELS:
        shots, seed = DISCOVERY[p]
        full = {b: sample(load_circuit(GROSS_CIRCUITS[b], p), shots, seed + k)[0] for k, b in enumerate("XZ")}
        ph = p_hat_stream(full["X"].sum(1) + full["Z"].sum(1), det)
        d = load(p)
        assert (d["weight"][:, 0] == full["X"][:, fm["X"].ids].sum(1)).all(), "regenerated shots differ"
        o_main = basis_outcomes(d, *TABLE[0.004])
        o_cheap = basis_outcomes(d, *TABLE[0.0055]), basis_outcomes(d, *TABLE[0.006])
        reg = regime(ph)
        rows.append(dict(p=p, X=np.stack([fm[b](full[b], ph) for b in "XZ"], 1), p_hat=ph, regime=reg,
                         o=dict(main=o_main, cheap55=o_cheap[0], cheap60=o_cheap[1])))
    return rows, fm


def outcomes_for(row):
    """Outcome arrays for the setting the gate would actually use on each pair (by its p_hat)."""
    grid = np.array(sorted(TABLE))
    near = grid[np.abs(grid[None] - row["p_hat"][:, None]).argmin(1)]
    pick = np.where(near >= 0.006, "cheap60", np.where(near >= 0.0055, "cheap55", "main"))
    keys = ["gate_wrong", "gate_secs", "skip_wrong", "skip_secs", "esc", "base_wrong", "base_secs"]
    return {k: np.where((pick[:, None] == "main"), row["o"]["main"][k],
                        np.where(pick[:, None] == "cheap55", row["o"]["cheap55"][k], row["o"]["cheap60"][k])) for k in keys}


def metrics(o, skip, idx, overhead=0.0):
    wrong = np.where(skip, o["skip_wrong"], o["gate_wrong"])[idx].any(1)
    secs = (np.where(skip, o["skip_secs"], o["gate_secs"])[idx] + overhead).sum(1)
    bs = o["base_secs"][idx].sum(1)
    q = lambda x, k: np.percentile(x, k)  # noqa: E731
    return dict(fails=int(wrong.sum()), base_fails=int(o["base_wrong"][idx].any(1).sum()),
                mean=secs.mean() / bs.mean(), p90=q(secs, 90) / q(bs, 90), p99=q(secs, 99) / q(bs, 99),
                skip=float(skip[idx].mean()))


def check():
    from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    rows, fm = build()
    for r in rows:
        r["oo"] = outcomes_for(r)
        n = len(r["p_hat"])
        r["split"] = np.where(np.arange(n) < 0.5 * n, 0, np.where(np.arange(n) < 0.7 * n, 1, 2))  # train/valid/hold
    cat = lambda f, part: np.concatenate([f(r)[r["split"] == part] for r in rows])  # noqa: E731
    Xtr = cat(lambda r: r["X"].reshape(-1, len(FEATURES)) if False else r["X"], 0).reshape(-1, len(FEATURES))
    esc_tr = cat(lambda r: r["oo"]["esc"], 0).ravel()
    dt_tr = cat(lambda r: r["oo"]["gate_secs"] - r["oo"]["skip_secs"], 0).ravel()
    print(f"training decodes {len(esc_tr)}, escalated {esc_tr.mean():.1%}")
    models = {
        "logistic (escalated)": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=1.0)).fit(Xtr, esc_tr),
        "GBDT (escalated)": HistGradientBoostingClassifier(max_depth=3, max_iter=200, learning_rate=0.05,
                                                           random_state=0).fit(Xtr, esc_tr),
        "GBDT (time saved)": HistGradientBoostingRegressor(max_depth=3, max_iter=200, learning_rate=0.05,
                                                           random_state=0).fit(Xtr, dt_tr),
    }

    def scorer(name):
        if name == "alarm-count rule":
            return lambda X: X[..., 0]
        m = models[name]
        if hasattr(m, "predict_proba"):
            return lambda X: m.predict_proba(X.reshape(-1, len(FEATURES)))[:, 1].reshape(X.shape[:-1])
        return lambda X: m.predict(X.reshape(-1, len(FEATURES))).reshape(X.shape[:-1])

    # inference cost per decode (features + model, one syndrome at a time, python)
    one = sample(load_circuit(GROSS_CIRCUITS["X"], 0.004), 200, 777)[0]
    cost = {}
    for name in ["alarm-count rule"] + list(models):
        f = scorer(name); t = time.perf_counter()
        for k in range(200):
            x = fm["X"](one[k:k + 1], np.array([0.004])) if name != "alarm-count rule" else one[k:k + 1, fm["X"].ids].sum(1)
            if name != "alarm-count rule":
                f(x[None])
        cost[name] = (time.perf_counter() - t) / 200
    print("inference cost per basis decode: " + ", ".join(f"{k} {v * 1e6:.0f} us" for k, v in cost.items()))

    def choose(name, reg):
        """Threshold per settings regime on the validation slice: minimise the mean of (mean, p90, p99) ratios
        averaged over the noise levels in that regime, with failures <= gate failures + 1 per level."""
        f = scorer(name)
        lv = [r for r in rows if np.mean(r["regime"] == reg) > 0.5]
        scores = np.concatenate([f(r["X"])[r["split"] == 1].ravel() for r in lv])
        best = (np.inf, np.inf)
        for t in np.unique(np.quantile(scores, np.linspace(0.3, 1.0, 71))):
            J, ok = 0.0, True
            for r in lv:
                idx = r["split"] == 1
                skip = f(r["X"]) > t
                m = metrics(r["oo"], skip, idx, cost[name])
                g = metrics(r["oo"], np.zeros_like(skip), idx)
                ok &= m["fails"] <= g["fails"] + 1
                J += (m["mean"] + m["p90"] + m["p99"]) / 3 / len(lv)
            if ok and J < best[0]:
                best = (J, t)
        return best[1]

    print("\nheld-out: last 30% of each discovery file (train 50%, thresholds on the next 20%)")
    names = ["alarm-count rule"] + list(models)
    thr = {(n, reg): choose(n, reg) for n in names for reg in (0, 1)}
    for r in rows:
        idx = r["split"] == 2
        o = r["oo"]
        print(f"\n p={r['p']}  ({idx.sum()} held-out pairs)")
        g = metrics(o, np.zeros_like(o["esc"]), idx)
        print(f"   {'gate as is':22s} fails {g['fails']:3d} (RBP {g['base_fails']:3d})  mean {g['mean']:.2f}  p90 {g['p90']:.2f}  p99 {g['p99']:.2f}")
        m = metrics(o, o["esc"], idx)
        print(f"   {'perfect spotter':22s} fails {m['fails']:3d}            mean {m['mean']:.2f}  p90 {m['p90']:.2f}  p99 {m['p99']:.2f}  skip {m['skip']:.1%}")
        for n in names:
            t = np.where(r["regime"][:, None] == 1, thr[(n, 1)], thr[(n, 0)])
            skip = scorer(n)(r["X"]) > t
            m = metrics(o, skip, idx, cost[n])
            print(f"   {n:22s} fails {m['fails']:3d}            mean {m['mean']:.2f}  p90 {m['p90']:.2f}  p99 {m['p99']:.2f}  skip {m['skip']:.1%}")
    Path("data/hardshot_models.pkl").write_bytes(pickle.dumps(dict(models=models, thresholds=thr, features=FEATURES)))
    if hasattr(models["GBDT (escalated)"], "feature_importances_"):
        pass
    lr = models["logistic (escalated)"][-1]
    order = np.argsort(-np.abs(lr.coef_[0]))[:8]
    print("\nlogistic top features (standardised coefficients): " +
          ", ".join(f"{FEATURES[i]} {lr.coef_[0][i]:+.2f}" for i in order))


if __name__ == "__main__":
    {"headroom": headroom, "check": check}[sys.argv[1]]()
