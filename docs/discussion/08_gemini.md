### 1. Noise Levels & Pair Allocation (Budget: 57,600 s)

Test across 4 noise points spanning from low-noise to the breakdown regime:

| $p$ | Cost / Pair | Pairs | Worker-s | Expected Relay Fails | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0.003** | 0.15 s | 15,000 | 2,250 s | ~15 | Confirm zero-regression floor & fast-path dominance |
| **0.004** | 0.50 s | 20,000 | 10,000 s | ~200 | Resolve seed ambiguity with statistical significance |
| **0.005** | 3.00 s | 8,000 | 24,000 s | ~670 | High-power evaluation of referee & tail mitigation |
| **0.006** | 9.00 s | 2,200 | 19,800 s | ~350 | Measure regime boundary where skip gate collapses |
| **Total** | — | **45,200** | **56,050 s** | — | **97.3% of 2-hr budget** |

---

### 2. Direct Measurements vs. Offline Derivation

* **Measure directly on every shot**:
  1. **Fast Seed 0 & 1** (up to $K=50$): log runtime, exact iteration count, restart index at convergence, syndrome validation, and logical flip prediction.
  2. **Referee Baseline**: Full Relay-BP (`nconv=5`, 300 sets).
  3. **Referee Candidate**: Cheap Relay-BP (`nconv=2`, 300 sets).
* **Derivation trustworthiness**: Decimation and restart loops are strictly sequential and deterministic given the seed. Truncating at $K < 50$ produces the exact bit-level trajectory of an actual run capped at $K$. 
* **Timing calibration**: To guarantee wall-clock validity beyond iteration scaling, calibrate the linear runtime model against a 500-shot pilot directly executing $K \in \{10, 20\}$. All gate variants ($K \in \{5, 10, 15, 20, 50\} \times \text{Referee}$) are then synthesized offline.

---

### 3. BP-OSD & XYZ Referee

* **BP-OSD**: **Exclude**. OSD-$w$ on degenerate graphs is prohibitively slow for an agreement referee and adds no architectural value to an online gate.
* **XYZ Referee**: **Exclude**. At 1,728 detectors and ~68k columns, XYZ Relay-BP is $>5\times$ slower than standard Relay-BP. Including it would cut shot counts by $>60\%$, destroying statistical power at $p=0.004$.

---

### 4. Output Deliverables & Pass Criteria

* **Deliverable Table**: 
  * Columns: $p$ | Best Config ($K$, Referee) | Mean Speedup | p90 / p99 Speedup | Failure Ratio (Point Estimate & 95% Wilson CI).
* **Deliverable Plots**: 
  1. *Pareto Frontier*: Mean latency vs. Failure ratio for each $p$.
  2. *Tail Scaling*: p90 and p99 latency vs. $p$ across candidate configurations.
* **Pass Criteria**:
  1. **Accuracy**: Failure ratio $\le 1.02\times$ Relay-BP (upper bound of 95% CI $< 1.05\times$).
  2. **Mean Latency**: $\le 0.70\times$ Relay-BP across all $p \le 0.005$.
  3. **Tail Latency**: p90 latency $\le 1.00\times$ Relay-BP at $p \ge 0.004$.
