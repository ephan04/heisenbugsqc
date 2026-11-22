# Noise detector, BP-OSD comparison and the 100k-pair run at p = 0.003

Data: `results/noise_ml.txt`, `results/bposd_compare.txt`, `results/large_p0.003.txt`. Pre-registrations: 14, 15.

## Noise detector (experiments/noise_ml.py)
- Estimating p from the last 10 pairs: the alarm count is 2-3% off, the MLP (alarm counts per cycle) 2-3% off, and ridge 2-4% off.
  With one uniform noise strength, the total alarm count carries nearly all the information.
- Routing replay and a drift stream (p changes every 300 pairs): count W=10 gives 203 failures vs 207 for the oracle, at the oracle's time.
- With the revised table, under-estimating is the safe direction; a +10% upward bias cost 11-18% extra failures at 0.0045-0.005.
- Verdict: the routing works; ML adds nothing over counting in this simulation.

## Gate (alarm-count routing, K=10 R5 up to 0.005) vs BP-OSD and Relay-BP, the same fresh shots
| p | BP-OSD fails | Relay-BP fails | gate fails | gate mean (vs RBP) | gate p99 (vs RBP) | vs Relay-BP |
|---|---|---|---|---|---|---|
| 0.003 (10k) | 55 | 5 | 7 | 22 ms (0.38x) | 0.76x | accuracy FAIL by count rule (3 vs 1 discordant); latency PASS |
| 0.004 (6k) | 336 | 55 | 53 | 191 ms (0.73x) | 1.03x | accuracy INCONCLUSIVE; latency FAIL |
| 0.005 (3k) | 726 | 262 | 262 | 1164 ms (0.87x) | 0.97x (p90 1.01x) | accuracy PASS; latency FAIL |
- Against BP-OSD: 3-8x fewer failures; mean time 0.23x / 0.68x / 2.0x; p99 5-7x worse at 0.004-0.005 (Relay-BP's tail).
- The MLP picked the same setting as the count on 100% / 100% / 97.3% of the subset pairs.
- The revised cap (K=10) cut the p99 excess from about 15% to about 3%; it is not yet below Relay-BP.

## p = 0.003, 100,000 pairs (seed 6030)
- Gate 86 vs Relay-BP 74 failed pairs (LER/cycle 7.2e-5 vs 6.2e-5; the authors report 6.0e-5).
  The ratio upper bound is 1.46 -> accuracy INCONCLUSIVE. Latency PASS: mean 0.39x, p90 0.16x, p99 0.73x.
- The largest discordance is on the agreed path (9 gate-only vs 4): both fast seeds agree on a wrong answer. This is a target for a per-shot ML predictor.
