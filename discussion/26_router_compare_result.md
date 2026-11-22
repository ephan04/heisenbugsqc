# 26 — Teammate's ML router vs our decoders at p = 0.003: result

Pre-registered in 25. Full numbers: `results/router_compare_p0.003.txt`. 10,000 fresh pairs, the same shots as
`data/compare_p0.003.npz`. The sanity check passed: BP-OSD, Relay-BP and the gate gave the same failure counts as the
earlier run (55 / 5 / 7).

| decoder | failed pairs | LER / cycle | mean ms | p99 ms |
|---|---|---|---|---|
| BP-OSD | 55 | 4.6e-4 | 99 | 597 |
| Relay-BP | 5 | 4.2e-5 | 60 | 419 |
| our gate (K10 R5) | 7 | 5.8e-5 | **23** | **335** |
| ML router (t = 0.7) | 41 | 3.4e-4 | 61 | 391 |
| fast BP → Relay-BP (router off) | 6 | 5.0e-5 | 52 | 382 |

- **The prediction held.** The router at t = 0.7 is about 8× worse than Relay-BP (accuracy FAIL, upper bound 13.7) and no
  faster on average (1.02×). It is still better than BP-OSD: 0.75× the failures, 0.61× the mean time.
- **Why:** 40 of its 41 failures come from the 5.7% of basis decodes it sends to BP-OSD. At p = 0.003, BP-OSD is both
  slower *and* less accurate than Relay-BP, so every shot routed there is a loss. Even the training-replay oracle could
  not beat "fast BP → Relay-BP". The router's idea pays off only where BP-OSD is the faster decoder (p ≥ 0.004).
- **Its first stage is free.** Fast BP solved 58.8% of basis decodes with zero failures. This matches our gate's
  first-leg finding.
- **Our gate is fastest:** 0.38× Relay-BP's mean time, 0.80× its p99. This run's p99 upper bound was 1.01, a hair over
  the PASS line (it was 0.99 in the earlier run). Accuracy: 7 vs 5 is FAIL under the observed-count rule; the 100k-pair
  run was INCONCLUSIVE (86 vs 74).
- **Their README's p = 0.003 row** can now be filled in from this run; timings are from this machine, not theirs.
