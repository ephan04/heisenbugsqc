1. **The pattern is plausible, but “harmless” is relative.** At high noise, R5 may already fail on most shots that weaker referees cannot solve, leaving little additional damage. A large baseline failure rate also compresses relative differences: at 0.006, 376 versus 367 is only +2.5%, despite nine extra failures. Shared failures are a hypothesis requiring the paired contingency tables. Also, R1 does **not** qualify at 0.003 or 0.0055; R2 does. The intermediate regime may contain more difficult but recoverable shots where extra referee effort matters.

2. **Selection stability and confirmation are different.** Small discordant counts make the precise winning setting unstable, but strongly shared failures can make paired noninferiority easier to establish. Marginal counts alone cannot determine the bounds.

   Tentative stage-2 predictions, assuming comparable sample sizes:

   | Noise | Accuracy | Joint latency |
   |---|---|---|
   | 0.003 | INCONCLUSIVE | PASS |
   | 0.004 | Likely PASS* | FAIL or INCONCLUSIVE |
   | 0.0045 | Likely PASS* | FAIL or INCONCLUSIVE |
   | 0.005 | Likely PASS* | FAIL or INCONCLUSIVE |
   | 0.0055 | Likely PASS | PASS or INCONCLUSIVE |
   | 0.006 | Likely PASS | PASS or INCONCLUSIVE |

   *Conditional on few discordances. Middle-noise p99 regressions threaten latency; at 0.005, p90 also does. At 0.0055, p90 is the concern; at 0.006, p99. Here FAIL means demonstrated regression; merely missing a PASS bound can remain INCONCLUSIVE.

3. **Yes: mean-only selection mismatches the eventual latency criterion.** For the next preregistration, minimize mean time subject to accuracy eligibility **and explicit p90/p99 constraints**, preferably uncertainty-aware with prespecified margins. Include baseline fallback when nothing qualifies, and define tie-breaking using unrounded values. Keep these frozen picks unchanged.

4. **Misrouting can erase accuracy gains.** A true 0.004 shot sent to K=5,R2 gives:

   - Versus baseline: 77 versus 61 failures, **+26.2%**, or **+0.267 percentage points**.
   - Versus its intended K=50,R5: 77 versus 59, **+30.5%**, or **+0.300 points**, saving approximately **35 ms** mean time.

   If 4% of true-0.004 shots take that wrong route, expected added failure probability is **0.012 percentage points** versus intended routing. This assumes misclassified shots have representative difficulty. Overall classification accuracy cannot establish routing cost: use the confusion matrix and conditional decoder losses, including window lag near noise changes.
