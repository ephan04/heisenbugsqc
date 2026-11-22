# 32 — Hardware facts and figures (synthesis of Claude, 31_gpt.md, 31_gemini.md)

Data: results/all_metrics.{json,md} (experiments/metrics_summary.py), results/hardware_probe.json
(experiments/hardware_probe.py). Figures: figures/1-5 (experiments/hardware_figures.py).

Corrections to the draft facts after review:
- Chip is Apple M5 (system_profiler), not a typo as Gemini suggested.
- Throughput "8 / mean time" checked against wall clock: 7.3-7.75 of 8 workers busy (3-9% optimistic), not the
  20-35% Gemini estimated. Decode times were measured under full 8-worker load, so they already include the efficiency cores.
- The gate's extra state is several Relay-BP instances (+5.5 MB), not "only a second seed" (GPT).
- Cross-machine speed: say "our runs were 1.3-1.8x faster", not "our hardware is faster"; conditions differ (GPT).
- Tail latency is not uniformly better; accuracy verdicts are FAIL / INCONCLUSIVE / PASS (both reviewers).
- The teammate's tail run used the old K = 50 setting; excluded from current-setting figures (GPT).
- Gemini's "strictly dominates" and "maintains accuracy across all noise levels" are not used.
