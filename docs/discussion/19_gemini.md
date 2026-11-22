### 1. Headroom & Realistic Best Case
**Marginal value.** Headroom is narrow: a perfect spotter saves only 3–7% mean latency. However, it successfully resolves the tail inversions at $p=0.004$ (p99 $1.03\times \to 0.99\times$) and $p=0.0045/0.005$ (p90 $1.01\times \to 0.87/0.97\times$). A realistic model capturing ~50% of headroom yields ~2–3% mean speedup and shaves ~2% off tails. It is only worth doing if eliminating the tail inversion is a strict requirement and feature extraction plus inference overhead is $\le 5\,\mu\text{s}$.

### 2. Better Label
**Use Cost-Sensitive Time Delta ($\Delta t = t_{\text{gate}} - t_{\text{referee}}$).** 
"Escalated" treats an immediate fast-leg rejection the same as a shot that runs two full legs before escalating. The tail latency blowup is driven entirely by the latter. Either train a regressor directly on $\Delta t > 0$ or weight binary escalation loss by wasted fast iterations ($t_{\text{wasted\_fast}}$).

### 3. Features: Cheap vs. Useless
* **Keep / Add (Microsecond ops):** Basis bit-count/`popcount` (dominates signal), temporal alarm distribution across 3-cycle windows, and **opposite-basis alarm count** (correlated $Y$ errors make the other basis predictive of hard shots).
* **Drop (Too slow / low yield):** Graph clustering on adjacency $A$ (connected components, BFS/DFS cluster size). Traversing the graph costs $10\text{--}50\,\mu\text{s}$, erasing your single-digit percentage gains. Avoid HistGradientBoosting at inference; use logistic regression or a quantized linear dot product.

### 4. Threshold & Objective
* **Threshold per $\hat{p}$ (or $K, R$ regime):** Mandatory. Escalation rates vary from 0.6% to 56%, and gate parameters switch at $p=0.0055$. A single global threshold will over-skip at low $p$ and under-skip at high $p$.
* **Objective:** Constrained tail optimization: minimize p99 latency subject to $\text{mean}(t) \le t_{\text{gate}}$ and no degradation in logical error rate.

### 5. Pre-Registered Confirmation Criteria
Evaluate on fresh seeds with full wall-clock accounting (including ML inference):
1. **Tail constraint:** $\text{p99} \le 1.00\times \text{Relay-BP}$ across all $p \in [0.003, 0.006]$.
2. **Margin over heuristic:** ML must outperform the simple rule ("skip if count $> T(\hat{p})$") by $\ge 2\%$ mean speedup or $\ge 3\%$ p99. Otherwise, adopt the simple rule.
3. **Accuracy:** Logical error count within $1\sigma$ of Relay-BP.

### 6. Leakage & Bias Traps
* **Inference accounting:** Replay uses zero-cost predictions. Real feature extraction must be measured inline.
* **Temporal dependency in $\hat{p}$:** Do not shuffle discovery shots across files when computing the rolling 10-pair window; maintain strict temporal order.
* **Co-adaptation:** The gate’s $(K, R)$ settings were tuned on discovery data. Optimizing threshold curves on the same discovery shots risks compounding selection bias on edge cases. Hold out entirely un-tuned seed sets.
