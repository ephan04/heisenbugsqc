### 1. Referee Pattern & High-Noise Resilience
In the transition regime ($p \in [0.004, 0.005]$), errors are hard enough to trigger escalation (5–26%), but structured enough that R5's deeper search (`stop_nconv=5`) succeeds where R1/R2 stall, yielding a 15–39% failure penalty. 
At $p=0.003$, escalation is negligible ($\le 1.2\%$), making referee strength statistically invisible. At $p \ge 0.0055$, noise exceeds the code's practical decoding capacity: escalated shots are uncorrectable graph trapping sets where Relay-BP fails regardless of depth. Because baseline R5 fails on virtually the same instances as R1/R2, cheaper referees are harmless.

---

### 2. Stage 2 Verdict Predictions
* **$p = 0.003$ ($K=5, \text{R2}$): INCONCLUSIVE.** With only 10–12 failures across 10,000 pairs, Poisson shot noise will inflate the 99.2% upper confidence bound of the failure ratio past 1.2 despite the 0.83 point estimate.
* **$p = 0.004, 0.0045, 0.005$ ($K=50, \text{R5}$): FAIL (Latency).** Accuracy will PASS ($\text{ratio} \le 1.00$), but latency will FAIL because empirical p99 ratios are 1.07–1.17, preventing the 95% bootstrap upper bound from being $< 1$.
* **$p = 0.0055$ ($K=5, \text{R2}$): BORDERLINE / INCONCLUSIVE.** Accuracy PASSes; latency is fragile because p90 is 0.94 (bootstrap UB may cross 1.0).
* **$p = 0.006$ ($K=5, \text{R1}$): PASS.** Tight failure bounds on 370+ events ensure accuracy PASS; latency metrics (mean 0.60, p90 0.64, p99 0.94) will clear the $< 1.0$ bootstrap bounds.

---

### 3. Selection Rule Critique & Follow-up Rule
The current rule ignores tail latency, selecting $K=50$ which adds fast-gate leg overhead onto full R5 decodes, blowing out p99 ($> 1$).

**Proposed follow-up rule:**  
> *"Among configurations with paired failure ratio $\le 1.05$ and empirical $p90 < 0.90$ and $p99 < 0.95$, select the minimum mean time."*  
(At $p=0.004$, this naturally picks $K=5, \text{R5}$ or $K=10, \text{R5}$, preserving tail latency).

---

### 4. Cost of Noise Misrouting
From the $p=0.004$ table, routing a true $0.004$ shot to the $0.003$ policy ($K=5, \text{R2}$) increases failures from 59 ($K=50, \text{R5}$) to 77—a **+30.5% failure increase** (ratio 1.26 vs baseline), instantly failing the $\text{UB} < 1.2$ accuracy gate. 

Because underestimating noise carries a severe accuracy penalty while overestimating noise only incurs modest latency overhead (e.g. running R5 unnecessarily), the noise classifier must be calibrated with an asymmetric, risk-averse loss function biased toward the higher noise bin.
