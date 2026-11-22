**1. Yes—stop this branch without fresh-seed confirmation.** No learned policy delivers a convincing net improvement under the specified objective and failure constraint. Fresh seeds would confirm a promising candidate; none emerged here. This supports stopping this feature/policy approach, not ruling out ML. Correct the “held-out 40%” versus “last 30%” reporting inconsistency.

**2. The proposed information claim is too strong.** AUC 0.69–0.74 indicates moderate discrimination, not little information. Logistic exceeds alarm count by 0.05 at p=0.004 and 0.0045; without uncertainty estimates, “the same” is unwarranted. High-p top-score precision also shows useful enrichment, although those subsets are small.

The defensible conclusion is: **these features did not produce a useful routing policy under the tested objective, constraints, and measured implementation costs.**

Distinguish prediction from policy:

- Thresholds, the latency objective, and inference charges do not explain the reported AUC. They can explain why discrimination fails to translate into net savings.
- Optimizing mean/p90/p99 jointly can reject mean-saving policies that worsen tails; the failure constraint can further restrict routing. Near-zero skipping alone does not establish absent signal.
- Charging inference on every decode is appropriate if deployment requires it. The 2.828 ms GBDT charge is substantial; the 112 µs logistic charge is much smaller. Neither supports a general claim that ML is intrinsically too expensive.
- Escalation is a proxy for routing benefit. The negative median “loss” on non-escalated cases at high p makes that mismatch explicit. The time-saved model addresses it partially, but its failure does not establish that benefit is unpredictable.

The oracle shows modest mean headroom, with a larger low-p p99 opportunity. Median savings/losses cannot establish expected break-even precision.

**3. Report sentences**

**Lesson:** “Pre-decode syndrome summaries moderately predict escalation, but the tested routing policies yield no convincing net latency benefit under the specified tail-latency objective, failure constraint, and inference costs.”

**Next:** “ML should next target conditional routing benefit using inexpensive early decoder-state signals, where evidence of stalled progress may be more actionable than syndrome summaries alone.”
