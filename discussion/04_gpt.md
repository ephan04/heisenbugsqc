### 1. Pre-register effectiveness

- **Primary policy:** agreement→Relay, with **serial** timing. Treat agreement→nconv2 and other policies as secondary.
- **Accuracy:** propose a noninferiority margin of **20% relative increase in pair-failure probability**, fixed before inspecting results. Pass only if the paired one-sided confidence bound excludes that increase at every noise level. Require both p=0.004 replications to support the conclusion. A nonsignificant McNemar test does **not** establish equivalence; insufficient precision means **inconclusive**.
- **Latency:** require the upper confidence bound for the mean-time ratio to be **≤0.8** at every noise level. Report tails separately; claim tail improvement only with supporting uncertainty estimates.
- Use simultaneous bounds for the primary comparisons. These sample sizes may leave accuracy inconclusive, especially at p=0.003.

### 2. Report safeguards

- Freeze the gate: accept only when **both fast decoders succeed and their entire logical vectors agree**. Otherwise use the designated fallback. Count terminal no-solution as operational failure even if its logical prediction happens to match; report logical mismatch separately.
- Include paired discordance counts, paired uncertainty for accuracy differences/ratios, and paired bootstrap intervals for latency ratios.
- Report agreed-but-wrong **numerators and denominators**, by basis and first-leg category. Matching logical outputs can reflect correlated mistakes.
- Prefix results are descriptive, nested checks—not independent replications or opportunities to select a favorable stopping point.
- Define pair failure explicitly. X/Z samples here are independently generated and paired by index; their union is a synthetic endpoint, not an observed joint physical trial.
- Explain the assumptions converting pair failure into LER/cycle. Clopper–Pearson applies directly to a binomial failure probability, not automatically to that conversion.

### 3. Setup confounds

- Fixed decoder order confounds timing with cache, thermal, and scheduling effects. Counterbalance order in a separate timing validation; record thread counts, hardware, and contention.
- `max(fast_s0, fast_s1)` is hypothetical parallel latency; serial measurements do not demonstrate it.
- Each chunk reconstructs decoders with repeated seeds. Verify RNG/reset behavior and record chunk boundaries; chunking may affect outcomes and invalidate shot-independent uncertainty assumptions.
- Different iteration counts do not establish seed independence. Verify actual seed use and prediction diversity on hard shots.
