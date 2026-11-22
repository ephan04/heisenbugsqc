# Claude — round 1

## Measured data (500 X-basis shots per p, `experiments/probe_bp.py`)
| p | BP-30 converges | BP-80 converges | wrong when converged | BP-80 mean time |
|---|---|---|---|---|
| 0.003 | 59% | 87% | 0 / 437 | 4.7 ms |
| 0.004 | 35% | 64% | 0 / 318 | 6.9 ms |
| 0.005 | 9%  | 30% | 0 / 148 | 9.2 ms |

Baselines take ~150–850 ms per shot. **BP-80 is a ~50–70× cheaper stage that, when it converges, has been right every time so far.**
Relay-BP's first leg *is* an 80-iteration BP, but with `stop_nconv=5` it keeps running legs to find 5 solutions even on easy
shots, which is why its mean time is high. That is the opening.

## 1. Design
Keep the idea, simplify the first build: **2 tiers + a learned gate**, then add the middle tier only if it is measured to help.
- Tier 0: BP-80 (plain min-sum, same priors). If converged → candidate accept.
- Gate (ML): on converged shots, predict P(logical error). Accept unless risky. On non-converged shots, predict which fallback is needed.
- Tier 1 (optional): BP-LSD (order 0) or Relay-BP with `stop_nconv=1`.
- Tier 2: Relay-BP at full settings (optionally XYZ later).

## 2. Light stage
Accept/reject whole shots, not partial commits. Converged BP gives a full syndrome-consistent correction for free; partial commits
risk locking in a wrong hypothesis on a code with long-range checks, and the residual syndrome is not easier for Relay-BP in an
obvious way. Do pass BP's posteriors as features to the router.

## 3. Router
Features (all from BP-80, near-free): converged, iterations used, syndrome weight, weight of the correction, sum of
prior-weighted correction cost (−Σ log-likelihood), min |LLR| and count of |LLR| < τ, number of hard-decision flips across
iterations if cheap. Model: logistic regression or gradient-boosted trees (sklearn HistGradientBoosting). Labels: run tier 1 and
tier 2 on the training shots once and record correct/incorrect + time. Objective: pick the threshold that minimises mean latency
subject to LER ≤ LER(Relay-BP) × (1 + ε), and report the whole Pareto curve.

## 4. Traps
- Failures are rare: a router "always accept" can look 99% accurate and still double the LER. Evaluate on LER, not router accuracy.
- Same shots for every decoder; train/test seeds disjoint; tune thresholds on a validation split, not test.
- Count router + tier-0 time in latency; report mean and p99, single-threaded.
- Distribution shift across p: train on a mix of p or per-p.
- Relay-BP is the accuracy ceiling for this pipeline (unless XYZ). Sell it as speed at matched accuracy.

## 5. Loss
Worth a stretch slot only. Simplest correct route: add `HERALDED_ERASE(p_loss)` on data qubits each cycle, let Stim put the
herald bits in the measurement record, and for each shot raise the priors of mechanisms attached to heralded qubits (rebuild
priors per shot via `update_channel_probs`). Herald count is also a router feature.

## 6. First experiment (<15 min)
p=0.004, X basis, 2000 train + 1000 test shots. Run BP-80, BP-LSD, Relay-BP on all; save correctness and time. Report:
(a) "accept if converged else Relay-BP" — LER and mean/p99 vs Relay-BP alone; (b) oracle router upper bound; (c) a trained
gate on top. If (a) already gives ~3× mean speed-up at equal LER, the idea has legs.
