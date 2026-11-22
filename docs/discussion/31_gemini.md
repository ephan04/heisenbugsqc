### Fact-Check & Flags

1. **Hardware specs (Fact 1):** Flag **"Apple M5"** as an apparent typo (likely Apple M4, which features 10 cores: 4P + 6E). Because 4 workers must run on slower efficiency cores, core throughput is non-uniform.
2. **Memory & Build (Facts 2 & 3):** **Accurate.** Memory footprints match expectations (BP-OSD needs dense linear algebra buffers; Relay-BP graph is lightweight).
3. **Throughput Scaling (Fact 4):** **Overclaimed.** Calculating throughput as $8 / \text{mean}$ assumes linear scaling across symmetric cores. Since E-cores run at ~half the throughput of P-cores and memory bandwidth can saturate, true multi-worker throughput will be 20–35% lower.
4. **Platform Comparison & State (Facts 5 & 6):** **Accurate and honest.** Normalizing runtimes on identical shots rather than raw wall-clock times is methodologically sound.
5. **Speed vs Relay-BP (Fact 7):** **Partially overclaimed.** While mean time is faster (0.38×, 0.73×, 0.87×), **tail latency is not uniformly faster**: at $p=0.004$, p99 is **1.03× slower** (4415 vs 4279 ms), because fallback shots execute both seeds plus Relay-BP.

---

### Figure Proposals

#### Fig 1: Logical Error Rate vs. Physical Error Rate ($p$)
* **Axes:** X: Noise rate $p$ ($0.003, 0.004, 0.005$); Y: LER / cycle ($\log_{10}$ scale).
* **Rows:** Organisers (Relay-BP, BP-OSD) vs. Ours (Relay-BP, Agreement Gate, ML Router, BP-OSD).
* **Message:** Agreement gate maintains Relay-BP’s superior accuracy across all noise levels (~10× better LER than BP-OSD).
* **Caveat:** Organisers’ numbers report upper-bound $X+Z$ sums; on 100k shots ($p=0.003$), the gate has slightly more failures (86 vs. 74) due to statistical edge cases.

#### Fig 2: Normalized Runtime Relative to Relay-BP
* **Axes:** X: Physical error rate $p$; Y: Runtime relative to Relay-BP baseline ($1.0\times$).
* **Rows:** Ours (Gate, Relay-BP, BP-OSD, Router) on identical shots.
* **Message:** Gate delivers a $2.6\times$ speedup ($0.38\times$ runtime) in the operating regime ($p=0.003$) and remains 13–27% faster at higher noise.
* **Caveat:** Speedups narrow as $p$ rises because the fast-path solve rate drops from 96.5% ($p=0.003$) to frequent fallback cascades.

#### Fig 3: Latency Distribution: Typical (p50) vs. Tail (p99 / Max)
* **Axes:** X: Decoders grouped by $p=0.004, 0.005$; Y: Latency (ms, $\log_{10}$ scale) showing p50, p90, p99, and Max.
* **Rows:** Teammate 1k tail-latency runs.
* **Message:** Gate slashes typical latency dramatically (p50: $13.6\text{ ms}$ vs. Relay-BP $98.3\text{ ms}$ at $p=0.004$).
* **Caveat:** Tail latency suffers: gate maximum latency is higher than Relay-BP (7.3 s vs. 6.1 s) due to sequential fallback iterations.

#### Fig 4: Speed–Accuracy Pareto Frontier
* **Axes:** X: Mean decode time per pair (ms, inverted $\log_{10}$); Y: LER / cycle ($\log_{10}$).
* **Rows:** All decoders across $p=0.003, 0.004, 0.005$.
* **Message:** Gate strictly dominates Relay-BP on the Pareto frontier, capturing near-BP-OSD speed with Relay-BP accuracy at $p=0.003$.
* **Caveat:** Assumes ideal batch scheduling without E-core thread contention.
