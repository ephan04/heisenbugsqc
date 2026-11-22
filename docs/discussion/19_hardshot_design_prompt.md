# Round 19: design review of the ML "hard-shot spotter" (version a). Answer in under 450 words. Do not run tools.

Context: Gross code, agreement gate over Relay-BP (see discussion/16). Current gate per basis decode: fast Relay-BP seed 0
(K=10 restarts cap) -> accept if solved in the first 80 iterations; no solution -> referee (kit Relay-BP R5); else seed 1
and accept if logicals agree, else referee. The remaining weaknesses vs Relay-BP: p99 1.03x at p=0.004, p90 1.01x at p=0.005,
and +16% failures (n.s.) at p=0.003.

Proposed ML: before decoding, a tiny classifier looks at the syndrome and predicts "the gate would escalate this decode"
(label = escalated). If the score is above a threshold, skip the fast runs and go straight to the referee. Wrong predictions
cost only time (skip on an easy shot = paying for the full referee), except that skipping replaces an accepted fast answer by the referee's.
Training data: 24,500 discovery pairs (data/adapt_p*.npz, p = 0.003-0.006), with per-decoder outcomes and timings recorded;
the syndromes are regenerated exactly from the seeds. Replay is used for the quick check, then a pre-registered fresh-seed confirmation.

Headroom (replay on discovery shots; ratios vs Relay-BP: mean / p90 / p99; perfect spotter = skip exactly the escalated decodes):
Perfect spotter: skip exactly the decodes the gate would escalate (same outcome, no wasted fast runs).
Also shown: skip every decode that is not solved in the first leg.

p=0.003  setting K=10 R5   escalated 0.6% of decodes
   gate as is        : fails   13 (RBP   12)  mean 0.40x  p90 0.16x  p99 0.75x
   perfect spotter   : fails   13 (RBP   12)  mean 0.37x  p90 0.16x  p99 0.50x
   skip if not first : fails   12 (RBP   12)  mean 0.42x  p90 0.16x  p99 0.92x
   best-of-both      : fails   13 (RBP   12)  mean 0.36x  p90 0.16x  p99 0.50x  (skip whenever it is faster and no worse)
p=0.004  setting K=10 R5   escalated 4.9% of decodes
   gate as is        : fails   60 (RBP   61)  mean 0.71x  p90 0.57x  p99 1.03x
   perfect spotter   : fails   60 (RBP   61)  mean 0.64x  p90 0.48x  p99 0.99x
   skip if not first : fails   63 (RBP   61)  mean 0.73x  p90 0.81x  p99 0.99x
   best-of-both      : fails   59 (RBP   61)  mean 0.63x  p90 0.45x  p99 0.99x  (skip whenever it is faster and no worse)
p=0.0045  setting K=10 R5   escalated 10.5% of decodes
   gate as is        : fails   83 (RBP   80)  mean 0.83x  p90 1.01x  p99 1.02x
   perfect spotter   : fails   83 (RBP   80)  mean 0.76x  p90 0.87x  p99 0.99x
   skip if not first : fails   81 (RBP   80)  mean 0.84x  p90 0.97x  p99 0.99x
   best-of-both      : fails   83 (RBP   80)  mean 0.75x  p90 0.87x  p99 0.99x  (skip whenever it is faster and no worse)
p=0.005  setting K=10 R5   escalated 20.6% of decodes
   gate as is        : fails  240 (RBP  241)  mean 0.90x  p90 1.01x  p99 1.00x
   perfect spotter   : fails  240 (RBP  241)  mean 0.84x  p90 0.97x  p99 0.96x
   skip if not first : fails  243 (RBP  241)  mean 0.89x  p90 0.98x  p99 1.00x
   best-of-both      : fails  240 (RBP  241)  mean 0.83x  p90 0.97x  p99 0.96x  (skip whenever it is faster and no worse)
p=0.0055  setting K=5 R2   escalated 39.6% of decodes
   gate as is        : fails  297 (RBP  286)  mean 0.71x  p90 0.94x  p99 0.83x
   perfect spotter   : fails  297 (RBP  286)  mean 0.67x  p90 0.92x  p99 0.81x
   skip if not first : fails  297 (RBP  286)  mean 0.68x  p90 0.92x  p99 0.81x
   best-of-both      : fails  297 (RBP  286)  mean 0.67x  p90 0.91x  p99 0.81x  (skip whenever it is faster and no worse)
p=0.006  setting K=5 R1   escalated 56.2% of decodes
   gate as is        : fails  376 (RBP  367)  mean 0.60x  p90 0.64x  p99 0.94x
   perfect spotter   : fails  376 (RBP  367)  mean 0.57x  p90 0.62x  p99 0.93x
   skip if not first : fails  382 (RBP  367)  mean 0.57x  p90 0.62x  p99 0.93x
   best-of-both      : fails  376 (RBP  367)  mean 0.57x  p90 0.62x  p99 0.93x  (skip whenever it is faster and no worse)

My planned features (per basis, before decoding): the basis alarm count, the count per cycle (13), the max per cycle, and
"clustering" from the detector adjacency A (detectors sharing an error mechanism): adjacent alarm pairs, isolated alarms,
largest cluster size; plus the noise estimate p_hat (alarm count over the last 10 pairs). Models: logistic regression and
HistGradientBoosting. Baseline to beat: a simple rule "skip if the basis alarm count is above T". Split: first 60% of each
discovery file for training/threshold, last 40% held out.

Questions:
1. Is this worth doing given the headroom? What is the realistic best case?
2. Better label? (escalated vs time saved vs "fast path took more than X iterations")
3. Feature suggestions that are cheap (microseconds) and plausibly predictive; anything likely useless?
4. How should the threshold be chosen (one global vs per p_hat bin), and what objective (mean, p99, both)?
5. What pre-registered pass criteria for the fresh-seed confirmation? Must the ML beat the simple rule by a margin?
6. Any leakage or bias traps in replaying on discovery data (the settings table was chosen on these shots)?
