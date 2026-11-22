# 27 — Decoders built from the estimated noise level: pre-registration

**Question.** Until now every decoder was built from the true p. Does the gate still work when its decoders are built
from the program's own alarm-count estimate of p, so that nothing is told the true noise level?

**Shots.** The same pairs as `data/compare_p{0.003,0.004,0.005}.npz` (10,000 / 6,000 / 3,000 pairs; seeds 5030 / 5040 / 5050).

**Decoders, run live in one job, shuffled order per shot:**
- `gate_true`: the gate built from the true p, with settings chosen by the alarm-count estimate (the earlier `gate_count`).
  Sanity check: its failure counts must equal the earlier run's (7 / 53 / 262).
- `gate_est`: the same gate and settings, but with H, L and priors built from the circuit at p_hat. p_hat is the stored
  alarm-count estimate over the last 10 pairs (`p_count`), rounded to the nearest 0.0001.

**Verdicts per p, gate_est vs gate_true:**
- Accuracy: PASS if the `ratio_upper` failure-ratio bound is below 1.2. FAIL if gate_est has more than 1.2× gate_true's
  failures. Otherwise INCONCLUSIVE.
- Latency: PASS if the 95% bootstrap upper bounds of the mean, p90 and p99 ratios are all below 1.05.

Also reported: gate_est vs the stored Relay-BP (true p) failures, and the spread of p_hat.
