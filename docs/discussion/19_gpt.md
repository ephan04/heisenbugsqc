**Worth a small experiment, with modest expectations.** The oracle saves 0.03–0.07 baseline-time units in mean latency. At the weak points, p=0.004 p99 reaches only 0.99x, and p=0.005 p90 reaches 0.97x—before feature/inference overhead. A practical model will capture a fraction of this. Escalation spotting cannot repair the gate’s existing failure excess; false-positive skips can change correctness.

1. **Label:** Start with “escalated,” but select policies using measured **net time saved**, not classification accuracy or AUROC. Define Δt = gate time − direct-referee time; subtract feature/inference overhead on **every** decode. Escalation classification ignores heterogeneous savings and false-positive costs. Compare it with Δt regression or cost-weighted classification. “More than X iterations” is a weaker proxy unless it demonstrably predicts savings better.

2. **Features:** Alarm count, cycle profile, adjacent pairs, and isolated alarms are sensible. Add cheap temporal concentration, consecutive-cycle overlap, and adjacency-normalized pair density. Raw pair counts largely track alarm count; normalization may reveal additional structure. Largest-cluster computation deserves an ablation: it may cost more than it contributes. Check whether “max per cycle” is redundant with the 13 counts. Precompute adjacency lists and benchmark the entire feature path. Treat p_hat as optional: ten pairs may be noisy and mostly duplicate syndrome weight.

3. **Threshold:** Begin with one global threshold on a score conditioned on p_hat, basis, and decoder configuration. Separate p_hat-bin thresholds invite overfitting, especially at 0.6% escalation prevalence. Choose thresholds on a validation subset, separate from fitting and the final 40%. Optimize mean net latency subject to explicit tail and correctness constraints; empirical p99 alone is unstable.

4. **Fresh-seed pass criteria:** Freeze features, models, settings, thresholds, sample sizes, and analysis. Compare ML, the tuned alarm-count rule, unchanged gate, and Relay-BP on paired shots. Require:
   - A predeclared, practically meaningful net-latency improvement over the rule.
   - Confidence bounds meeting the targeted tail requirements, including overhead.
   - Failure-rate noninferiority within a predeclared margin, assessed against both gate and Relay-BP.

   Power the correctness check using discordant paired outcomes; “not significant” is insufficient. Predeclare per-p requirements and multiplicity handling. If ML cannot clearly beat the rule, keep the rule.

5. **Leakage:** Split by whole shot/pair, keeping both bases together. Compute p_hat causally from preceding pairs and reproduce deployment initialization. Verify regenerated syndromes, referee seeds, and replay equivalence. Discovery-selected settings make the held-out discovery results exploratory, not independent confirmation. Keep fresh seeds untouched by all tuning; validate replay timing with actual executions.
