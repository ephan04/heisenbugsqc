1. **Wrong:** “`\textbf{FAIL} if the gate has more than 1.2$\times$ the failures`”; “7 vs 5 … counts as FAIL under the count rule.”  
   **Correction:** The brief specifies PASS when the statistical upper bound is below 1.2. It supplies no raw-count FAIL rule; an observed ratio above 1.2 alone does not establish a statistically supported accuracy failure.

2. **Wrong:** “At `$p \in [0.004, 0.005]$`, accuracy criteria passed.”  
   **Correction:** Stage-2 accuracy at 0.004 was **inconclusive** (69 vs 61). Accuracy passed at 0.0045 and 0.005.

3. **Wrong:** “It matches Relay-BP's logical error rate within statistical resolution.”  
   **Correction:** Current accuracy is **inconclusive at 0.003 and 0.004**, and PASS at 0.005. Failure to resolve a difference does not establish matching accuracy or the registered noninferiority margin.

4. **Wrong:** “The gate has no trained parameters, so every shot is a test shot.”  
   **Correction:** Gate settings were selected on discovery data. Only the separate confirmation samples provide held-out evidence; having no learned parameters does not make discovery shots test shots.

5. **Wrong:** “Everything except the referee runs on almost every shot.”  
   **Correction:** At 0.003, 96.5% take the first-leg acceptance path and skip seed 1. Seed 1 runs only when seed 0 finds a solution after the deterministic first leg.

6. **Wrong:** “escalated shots were intrinsically corrupted beyond recovery.”  
   **Correction:** The tested referee choices produced no observed accuracy penalty at noise levels of at least 0.0055 because those shots failed either way. This does not establish that another decoder could not recover them.

7. **Wrong:** “parameterized machine learning classifiers (logistic regression, GBDTs, MLPs) underperformed when tasked with gating individual decoding shots.”  
   **Correction:** Logistic regression/GBDT were evaluated for acceptance gating. The MLP was evaluated for **noise estimation**, where it matched counting. The brief does not report an MLP acceptance-gating experiment.

8. **Wrong:** “simple physical counters serve as minimal sufficient statistics”; “structural ML feature extraction provided no incremental information.”  
   **Correction:** Alarm count was **nearly a sufficient statistic under the tested uniform noise model**, and the tested ML estimators provided no measured improvement. Neither mathematical sufficiency nor absence of additional information was established.

9. **Wrong:** “Capping the fast run at `$K=10$` restarts cut this excess to about `$3\%$`, but not below Relay-BP.”  
   **Correction:** The current observed p99 ratio is 1.03 at 0.004, but approximately **0.97 at 0.005** and **0.73 in the 0.003 100k run**. At 0.005, latency fails because of p90, not p99.

10. **Wrong:** “accuracy (bound)” entries “INCONCL. (1.29)” and “PASS (1.11)”; “Paired bootstrap (2,000 resamples)”; 100k-run mean times “77” and “30” ms.  
    **Correction:** These numerical details are absent from the brief. Retain the supplied verdicts, the 0.003 accuracy bound of 1.46, and the 100k mean-time ratio of 0.39; omit the unsupported values.

11. **Wrong:** MLP entries “6--8%” and “0.8--2.9%”; ridge entries “7--8%”, “1--4%”, and “60 μs”; “6,333-pair subset … 100%, 100% and 97.3%.”  
    **Correction:** These model-specific results and routing-agreement counts are not supplied. The brief gives single-shot error of 6–9%, approximately 0.8% over 100 shots, and ten-pair errors of 2–3% for count/MLP and 2–4% for ridge. It gives no ridge inference time or routing-agreement percentages.

12. **Wrong:** “the referee on about 21% with `$K=10$` (20.6% in discovery)”; “a 2-layer MLP with about 2,100 weights”; “roughly 4--5 hours of decoding.”  
    **Correction:** None of these resource measurements appears in the brief. Remove them. Supported resource facts include eight workers on one ten-core Apple-silicon Mac, serial gate stages, and the stated estimator costs.

13. **Wrong:** “Claims of architectural superiority … are unsupportable without sample sizes on the order of `$10^5\text{--}10^6$` shots.”  
    **Correction:** The brief establishes that 10k pairs were underpowered at 0.003 and that the 100k-pair accuracy comparison remained inconclusive for the 20% margin. It establishes no general required sample-size range.

14. **Wrong:** “A threshold of 4 rejected virtually all valid decodes.”  
    **Correction:** The median correct correction weight was 45, demonstrating that the threshold was unsuitable. A median alone does not establish that virtually all valid decodes exceeded four.

15. **Wrong:** “requiring independent, randomly initialized trajectories.”  
    **Correction:** The runs use different seeds for randomized **later legs**, but share the same deterministic first 80 iterations. They are not independently randomized from initialization, and their agreement does not establish independent error probabilities.
