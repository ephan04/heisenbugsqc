# 25 — Teammate's ML router (branch `ml-router`) vs our decoders at p = 0.003: pre-registration

Written after training, before any evaluation on the test shots.

**Code.** `ml_router/` is copied unchanged from `origin/ml-router` (author: Emma Phan). It is run with
`PYTHONPATH=kit:ml_router` so it uses the same kit files.

**Training (their recipe, unchanged).** `make_routing_data.py` at p = 0.003, 3000 shots per basis, seeds 1 (X) and 2 (Z),
on this machine. `train_router.py --label safe --model logistic`. Output: `results/router_train_p0.003.txt`.

**Test shots.** The same 10,000 pairs as `data/compare_p0.003.npz` (seed 5030 for X, 5031 for Z), which the router never saw.

**Decoders, all run live in one job with a shuffled order per shot (same method as bposd_compare.py):**
- `bposd`, `relay`: the kit baselines.
- `gate`: our agreement gate at its p = 0.003 setting (K = 10, referee R5).
- `router`: their RoutedDecoder at **t = 0.7** (the threshold they report). This is the primary router result.
- `bp_relay`: their pipeline with the router switched off (fast BP, then Relay-BP if BP did not converge).
  Added because their replay at p = 0.003 shows this beats every router threshold. Secondary.

**Report.** The same verdicts as discussion/14 against Relay-BP: accuracy PASS / FAIL / INCONCLUSIVE from
`ratio_upper` with a margin of 1.2, and latency PASS if the 95% upper bounds of the mean, p90 and p99 ratios are all
below 1. Also failures and time vs BP-OSD. A sanity check: bposd, relay and gate are deterministic, so their failure
counts must equal those in `data/compare_p0.003.npz` (55 / 5 / 7).

**Prediction from the training replay:** router t = 0.7 has more failures than Relay-BP and no mean-time gain.
`bp_relay` is faster than Relay-BP at the same accuracy, but slower than our gate.
