### 1. Verdict per Noise Level & Overall Claim

* **$p=0.003$**: **PASS** (Accuracy: fail ratio 0.90, upper 1.00; Latency: mean ratio 0.48, upper 0.53).
* **$p=0.004$**: **PASS / INCONCLUSIVE** (Latency passes at ~0.70; Accuracy passes in s401 [ratio 0.93], inconclusive in s101 [ratio 1.17, upper 1.36]; pooled replication passes).
* **$p=0.005$**: **FAIL** on speedup (Accuracy PASS [ratio 0.95, McNemar $p<0.01$]; Latency FAIL [ratio 0.96, upper 0.99 > 0.80]).

**Claim**: The agreement gate is **effective strictly as a low-to-moderate noise accelerator ($p \le 0.004$)**, delivering a $1.3\times$–$2.1\times$ mean speedup while preserving logical accuracy. It is **ineffective** as a universal threshold decoder: at $p=0.005$, the speedup vanishes entirely, and tail latency ($p_{99}$) degrades across all $p \ge 0.004$ (+13% to +23%).

---

### 2. Explanation of $p=0.005$ & Seed Discrepancy

* **$p=0.005$ accuracy win without speedup**: High noise causes an 11.2% escalation rate. Escalation acts as an ensemble fallback: when the fast seeds disagree or fail, Relay-BP explores a fresh decoder state/trajectory, rescuing errors Relay-BP alone missed (14 wins vs. 2 losses). However, paying for two fast attempts *plus* a full Relay-BP decode on >11% of shots erases mean latency gains ($0.96\times$).
* **Seed 101 vs. 401 (35 vs. 26 fails)**: Not suspicious. At $\sim30$ events in 3,000 pairs, Poisson noise yields $\sigma \approx \sqrt{30} \approx 5.5$; 26 and 35 are within $\pm 1\sigma$ (Fisher $p=0.30$). Persistent RNG state across chunks introduces minor intra-run correlation, but the difference is standard finite-sample variance.

---

### 3. Single-Worker vs. 8-Worker Timing

**Quote the single-worker ratio (0.79, 95% upper 0.92)** as the primary reported speedup, mentioning 8-worker (0.70) as parallel throughput. Multi-worker benchmarks suffer from thread/cache contention and uneven core scaling that artificially penalize memory-heavy baseline decodes. The randomized, pinned single-worker measurement isolates the true algorithmic latency gain.

---

### 4. Most Valuable Next Change

**Asymmetric fast-path escalation**: If Seed 1 finds *no solution*, escalate immediately to Relay-BP without running Seed 2. 

At $p=0.005$, no-solution events outnumber disagreements 7:1 (591 vs. 81). Running a second fast seed when the first has already failed wastes cycles on doomed shots. Eliminating Seed 2 on initial failure cuts wasted overhead and restores speedup at high noise.
