# Noise-adaptive agreement gate: conclusion (no ML; the noise level is given)

Data: discovery `results/adaptive_discovery.txt`, confirmation `results/adaptive_confirm.txt`, ablation
`results/ablation_k5.txt` and `results/ablation_k50.txt`. Pre-registrations: 09 and 12. Reviews: 10, 11 (GPT, Gemini).

## Confirmed results (fresh seeds; real gate vs kit Relay-BP on the same shots)
| p | setting | failed pairs gate vs RBP | accuracy | mean time | p90 | p99 | latency |
|---|---|---|---|---|---|---|---|
| 0.003 | K5 R2 | 9 vs 2 | FAIL | 0.31 | 0.16 | 0.57 | PASS |
| 0.003* | K5 R5 | 15 vs 14 | INCONCL. | 0.42 | 0.16 | 0.87 | PASS |
| 0.003* | K50 R5 | 10 vs 7 | FAIL (by count rule; upper bound 2.8) | 0.35 | 0.15 | 0.52 | PASS |
| 0.004 | K50 R5 | 69 vs 61 | INCONCL. (upper bound 1.41) | 0.66 | 0.51 | 1.16 | FAIL (p99) |
| 0.0045 | K50 R5 | 90 vs 94 | PASS | 0.78 | 0.51 | 1.15 | FAIL (p99) |
| 0.005 | K50 R5 | 233 vs 234 | PASS | 0.87 | 1.16 | 1.14 | FAIL (p90, p99) |
| 0.0055 (expl.) | K5 R2 | 171 vs 181 | PASS | 0.67 | 0.94 | 0.84 | FAIL (p99 upper bound 1.01) |
| 0.006 (expl.) | K5 R1 | 281 vs 259 | PASS (upper bound 1.18) | 0.60 | 0.69 | 1.01 | FAIL (p99) |
*Addendum 12. Latency FAIL means the 95% upper bound was >= 1. The printed "(<= x)" is that bound, not the criterion.

## What we learned
1. The cheap referee R2 at low noise was a discovery artifact. In stage 2 its extra failures sat on the no_solution path (R2 decides there). With R5, that path's discordance is symmetric (6 vs 5): Relay-BP's own randomness.
2. p = 0.003 is underpowered. Relay-BP gave 2, 14 and 7 failed pairs in three 10k runs. Proving parity within 20% needs roughly 10x more shots.
3. The gate saves 13-69% of mean time at every level. Its p99 is 0-16% worse whenever K=50 (seed 0 runs long and then escalates serially). Small K (5) keeps p99 <= 1 at low and high noise.
4. At high noise (>= 0.0055), half the decodes find no solution and escalate; cheap referees then cost little extra accuracy and give a 30-40% speed-up.
5. For a future noise estimator: under-estimating the noise is costly (a true 0.004 shot given the 0.003 cheap settings fails about 26-30% more often). Over-estimating costs only time. Bias the estimate upward.

## Recommended table for the next pre-registration (not yet confirmed)
Use R5 everywhere up to 0.005 and K=5 or 10 (tail-safe). At >= 0.0055, K=5 with R2. The selection rule should constrain p90/p99, not only the mean.
