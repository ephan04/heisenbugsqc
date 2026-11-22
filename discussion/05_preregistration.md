# Pre-registered criteria for the agreement gate (written before the sweep results were read)

Merged from GPT (04_gpt.md) and Gemini (04_gemini.md); Claude arbitrated.

**Primary policy.** Agreement → full Relay-BP (kit settings), with serial timing (fast_s0 + fast_s1 + relay when escalated).
- A shot is accepted only if **both** fast runs report success **and** their full 12-bit logical vectors agree.
- Escalation is per basis: an X escalation does not rerun Z.
- Agreement → relay_nconv2 and parallel timing (max of the two fast runs) are secondary and labelled as such. Parallel timing is hypothetical.

**Accuracy (non-inferiority).**
- The margin is a **20% relative increase in pair-failure probability** vs Relay-BP on the same shots (GPT).
- PASS at a noise level if the one-sided 95% upper bound of the paired failure-probability ratio is < 1.2.
- FAIL if the point estimate is > 1.2.
- Otherwise INCONCLUSIVE. With roughly 10–60 failures per run, this is expected, and it will be reported as such rather than spun.
- A secondary pooled check (Gemini): total gate pair failures ≤ total Relay-BP pair failures across all runs.

**Latency.**
- PASS at a noise level if the paired-bootstrap 95% upper bound of mean(gate)/mean(relay) is ≤ 0.8 (GPT; Gemini proposed 0.7).
- p50, p95, p99 and max are reported. A tail improvement is claimed only if its bootstrap upper bound is < 1.

**Robustness checks reported.**
- Escalation rate split into "no solution" vs "valid disagreement".
- Agreed-but-wrong counts with denominators, split by basis and by first-leg (both runs ≤ 80 iterations) vs later.
- The two p = 0.004 seeds compared (Fisher exact test on failures and escalations).
- Prefix results (first 1000/2000 pairs) are descriptive only.
- Seed check: on hard shots, how often the two seeds give different logical vectors, not only different iteration counts.
- Timing confounds: fixed decoder order and 8 workers. A separate single-worker timing run with randomised decoder order checks the latency ratio.
- Pair failure is a synthetic union of independently sampled X and Z shots paired by index, as in the kit.
- LER/cycle = 1 − (1 − P)^(1/12), with the CI mapped through the same monotone transform.
