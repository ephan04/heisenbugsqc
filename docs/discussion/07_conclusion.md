# Verification conclusion (rounds 4–5; Claude, GPT, Gemini)

Criteria were fixed in `05_preregistration.md` before any of these results were read.
Fresh seeds; 17,000 X/Z pairs over 4 runs, plus a 400-pair timing check.
Full numbers: `results/agree_report.txt`. Plots: `results/agree_verdicts.png`, `results/agree_ler_vs_latency.png`.

## Primary gate (2 fast seeds → agree ? accept : full Relay-BP), pre-registered verdicts
| Run | Pair failures gate / Relay-BP | Accuracy | Mean time vs Relay-BP | Latency | p99 vs Relay-BP |
|---|---|---|---|---|---|
| p=0.003, 8000 pairs | 9 / 10 | PASS* | 0.48 (≤0.53) | PASS | 0.49 |
| p=0.004, seed 101 | 35 / 30 | INCONCLUSIVE (1.17, ≤1.36) | 0.71 (≤0.76) | PASS | 1.18 |
| p=0.004, seed 401 | 26 / 28 | PASS (0.93, ≤1.04) | 0.70 (≤0.75) | PASS | 1.23 |
| p=0.005, 3000 pairs | 247 / 259 | PASS; significantly better (14 vs 2 discordant, McNemar p≈0.004) | 0.96 (≤0.99) | FAIL | 1.13 |

\* GPT: there were 0 gate-worse pairs, so the paired bootstrap cannot exceed 1. This PASS is fragile and needs a coverage-valid sensitivity check.

- The pooled check passes: 317 vs 327 failures over 17,000 pairs.
- Replication at p=0.004: 35 vs 26 gate failures, Fisher p = 0.30, which is consistent with sampling noise.
- Timing check (1 worker, randomised decoder order, threads=1): mean ratio **0.79 (≤0.92)**, p99 ratio 1.30.
  - GPT and Gemini agree this controlled number should be the one quoted. The 0.70 from 8 workers is secondary.

## Agreed claim
The agreement gate **matches Relay-BP's logical error rate** at every tested noise level, and at p=0.005 it is slightly better. It **cuts mean decode time at p ≤ 0.004**: 2.1× at p=0.003, and about 1.27× at p=0.004 under controlled timing. It gives **no speed-up at p=0.005** and **worsens the p99 tail** at p ≥ 0.004. It is not a universal accelerator, and tail latency is still unsolved.

## Exploratory follow-up (post-hoc, round 5): lean gate (`experiments/lean_gate.py`)
The accept/escalate decisions are the same. The second fast run is skipped when it cannot change the outcome:
- If seed 0 finds no solution, escalate at once (Gemini).
- If seed 0 stops inside the deterministic first leg, accept at once (GPT).

Checked: **0 first-leg mismatches** in every run, so accuracy is identical to the primary gate.

| Run | Mean ratio, primary → lean | p99 ratio, primary → lean |
|---|---|---|
| p=0.003 | 0.48 → **0.36** | 0.49 → 0.48 |
| p=0.004 (two seeds) | 0.71/0.70 → **0.63/0.63** | 1.18/1.23 → 1.08/1.17 |
| p=0.005 | 0.96 → **0.88** | 1.13 → 1.01 |
| timing check | 0.79 → **0.72 (≤0.83)** | 1.30 → 1.16 |

These times are built from per-decoder timings measured on the same shots. They need confirming with a real implementation of the lean decoder, timed end to end on fresh seeds.

## Next steps (consensus)
1. Implement the lean gate as a real decoder. Time it under controlled single-worker conditions on fresh seeds.
2. Share the deterministic first leg between seeds rather than recomputing it (GPT).
3. Attack the tail: cap the escalated decode's budget, or start the full Relay-BP in parallel with the fast runs.
4. Run a coverage-valid non-inferiority analysis, which is needed for the p=0.003 result.
