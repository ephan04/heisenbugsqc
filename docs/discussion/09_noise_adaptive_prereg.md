# Pre-registration: noise-adaptive gate settings (written before any data in this round)

Plan merged from `08_gpt.md` and `08_gemini.md` by Claude. No ML is built: the noise level is given.
The output is a lookup table, noise level → best settings, which a later noise detector would use.

## Policy family (skip gate)
- Seed 0: fast Relay-BP with at most K restarts. If it is solved within the deterministic first 80 iterations, accept.
- Seed 0 no solution: go to the referee.
- Otherwise run seed 1 (also capped at K). If the two logical vectors agree, accept; if not, go to the referee.
- K ∈ {5, 10, 20, 50}.
- Referee ∈ {**R5**: kit Relay-BP (stop_nconv=5, 300 sets), **R2**: stop_nconv=2, **R1**: stop_nconv=1, 300 sets}.
- 12 policies, plus the baseline (R5 alone on every shot).

## Stage 1: discovery (choose settings)
- Fresh seeds 1000+.
- Pairs per noise level: p = 0.003: 10,000 · 0.004: 6,000 · 0.0045: 3,000 · 0.005: 3,000 · 0.0055: 1,500 · 0.006: 1,000.
- Every shot gets seed 0 (50 restarts) and the baseline R5.
- Shots not solved in seed 0's first leg also get seed 1, R2 and R1.
  - Seed 1 on first-leg shots is skipped: it gave identical results on all 34,000 shots checked before.
- Results for capped runs (K < 50) are derived from the uncapped run's iteration count, with times scaled by iterations. This is approximate, because Relay-BP's random state carries over between shots, so a real capped decoder is statistically equivalent but not bit-identical. That is why stage 2 runs the real thing.
- Selection rule, per noise level:
  - Among the 12 policies, keep those with discovery failure ratio ≤ 1.05 vs baseline.
  - Of those, choose the lowest mean time.
  - If none qualifies, choose baseline-equivalent behaviour (R5 referee, K = 50).
- The selected table is frozen to `results/adaptive_selected.json` before stage 2 starts.

## Stage 2: confirmation (real decoder, fresh seeds 2000+)
- The frozen setting for each noise level runs as a real decoder (real caps, real referee), next to the baseline, on the same shots. Decoder order is randomised per shot.
- Pairs: p = 0.003: 10,000 · 0.004: 6,000 · 0.0045: 3,000 · 0.005: 3,000 · 0.0055: 1,000 · 0.006: 800.
- **Claims, per noise level:**
  - Accuracy: PASS if the one-sided upper bound of the paired failure ratio is < 1.2, at 99.2% (Bonferroni over 6 levels).
  - Latency: PASS if the 95% upper bounds of the mean, p90 and p99 time ratios are each < 1.
  - Anything else is reported as INCONCLUSIVE or FAIL. Nothing is re-tuned on confirmation data.
- p = 0.0055 and 0.006 are exploratory: few pairs, so any claim there is labelled as such.

## Excluded (agreed by GPT and Gemini)
- XYZ referee (too slow for this budget).
- BP-OSD (no value for choosing settings; already reported in earlier runs).
- ML of any kind.
