# GPT — round 2

1. **Mostly agree: the opportunity is selective escalation on hard shots.** BP→Relay saves only 4.5% mean latency; the ML .5 policy saves 37%, with four additional observed pair failures. That is a promising tradeoff, not demonstrated matched reliability. Report paired harmful substitutions and rescues, with uncertainty on excess failure probability; identical failure counts need not mean identical failed pairs. The truth-assisted oracle demonstrates complementarity, not deployable performance or a strict latency optimum.

   Two corrections: LSD is **not dominated** by Relay-Fast: its mean/p99 are 41/158 ms versus 53/728 ms, albeit with much worse LER. Drop it for the near-Relay accuracy objective, not because it is slower. Also, 0/4923 accepted-BP failures does not establish “zero leakage”; the approximate one-sided 95% binomial upper bound is 0.061% per accepted decode, not per cycle.

   Code audit: current `analyze.py` feeds **all** saved features into direct routing. With the new `rf_*` columns, that uses Relay-Fast outputs without charging its execution on heavy shots. Restrict direct routing to BP features; verify which schema produced the quoted table. Feature extraction/inference are also outside recorded decoder times. Ten-worker, fixed-order timings are contention-affected service measurements, not isolated runtime or queue latency.

2. **Next hour: Relay-Fast→full Relay, with no separate BP pass initially.** Its existing initial BP work makes the extra tier questionable; retain BP→Relay as a baseline. Use saved diagnostics; no new expensive experiment is needed while collection runs.

   Features: success plus explicit syndrome consistency, iterations, prior-weighted correction cost, correction weight, syndrome weight, posterior-confidence summaries, basis, and p if pooling noise levels. Verify what `iterations` and `posterior_ratios` actually represent; iterations are not automatically perturbation legs. Mandatory fallback on invalid candidates. Compare success-only escalation, a small iterations/cost threshold grid, and regularized logistic regression. Balanced-class logistic scores are not calibrated failure probabilities.

   Keep pair-level train/validation/test splits; choose thresholds only on validation under a predeclared excess-LER allowance, then evaluate once. Validation count parity alone is not noninferiority. Charge `T_fast + I(escalate)*T_full` plus diagnostics/gating; measure conditional costs rather than using unconditional medians.

   Before running `escalate.py`, fix `iters[train & succ]` to `iters[train[:, None] & succ]`: the existing masks have incompatible shapes. Handle empty successful subsets/feasible grids and single-class training. Its ML policy currently lacks mandatory unsuccessful-output escalation. Keep its exported test threshold curve descriptive, never a selection set.

3. **Pitch measured results, with the cascade explicitly pending.** Subject to confirming the table used BP-only routing features: “At p=0.004, selective routing reduced mean pair decode time from 266 to 167 ms; failures increased from 19 to 23/2000. Confidence-based escalation is the next test.” Plot LER versus mean latency and p99, with paired uncertainty, standalone baselines, validation-selected policies, and clearly labeled oracle references. Extend across all three p values before generalizing.

   **Gemini:** agree on withdrawing weight≤4 and testing simple thresholds. But a 12-ms unconditional median cannot price selected hard-shot overhead; the claimed 11% fallback, 140-ms matched-LER result, and tail protection are unmeasured. The current ML p99 remains 3.78 seconds.
