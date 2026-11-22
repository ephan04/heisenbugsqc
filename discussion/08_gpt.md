1. **Noise grid and allocation.** Target these pair counts, split equally between discovery and fresh-seed confirmation:

   | Noise \(p\) | Pairs |
   |---|---:|
   | 0.003 | 100,000 |
   | 0.004 | 6,000 |
   | 0.0045 | 2,000 |
   | 0.005 | 3,000 |
   | 0.0055 | 300 |
   | 0.006 | 200 |

   Budget **35,000 worker-seconds** for core decoding, **17,000** for cap validation and direct policy timing, and **5,600** contingency. These are targets, not guaranteed costs: intermediate-noise costs and extra executions need a throughput pilot. Freeze any revised allocation using runtime measurements before inspecting comparative failures.

   Low-\(p\) accuracy is the limitation: even 100,000 pairs yields only roughly 100 baseline failures. Splitting reduces confirmation precision further. Tight failure-ratio equivalence may remain unresolved. The highest-noise points are exploratory; concentrate additional boundary sampling near 0.004–0.005.

2. **Measure versus derive.** Run Relay-BP on every shot. During discovery, collect both fast seeds’ restart traces and compare **K = 10, 20, 50**, with referees **nconv5/300, nconv2, nconv1/300**. Referees need execution only on the union of shots routed to them by candidate policies.

   Treat prefix equivalence as a hypothesis. Audit real caps against uncapped prefixes on **1,000 stratified pairs**, including cap hits and no-solution cases. Require identical restart states, stopping decisions, and corrections; inspect whether caps alter RNG consumption or scheduling. Any mismatch invalidates replay. Even exact replay establishes outcomes, not wall-clock latency. On confirmation shots, execute the frozen selected policy directly, including actual caps, and time the baseline separately under matched conditions.

3. **Other decoders.** Exclude XYZ from this budget. Include BP-OSD only if required for challenge reporting; give it a separate **2,000-worker-second ceiling drawn from contingency**, using representative paired subsets. Neither should displace accuracy confirmation.

4. **Deliverable and acceptance.** Produce a per-noise table with selected configuration, failures, paired discordant outcomes, failure ratio and confidence interval, mean/p90/p99 latency ratios, and escalation rate. Plot accuracy–latency frontiers and selected settings versus noise.

   Pre-register selection: fastest mean among policies whose confirmation **one-sided 95% upper failure-ratio bound ≤1.20**, with multiplicity adjustment across claimed noise levels, and **upper confidence bounds below 1 for mean, p90, and p99 latency ratios**. Otherwise retain Relay-BP and label evidence insufficient.
