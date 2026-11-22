### 1. Architecture: Cut to 2 Tiers First

**Cut the 3-tier cascade to a clean 2-tier design.** In a 1–2 day hackathon with Python orchestration, multi-tier routing overhead (dispatching, intermediate data structures, and feature extraction) will cannibalize your latency gains.

* **Tier 1 (Fast Gate):** Short-run BP ($\sim 25$ iterations).
* **Tier 2 (Heavy Finisher):** Full Relay-BP.
* **Why drop the middle tier (BP-LSD / BP-OSD-0)?**
  At $p=0.004$, BP-OSD is barely faster than Relay-BP (0.33 s vs 0.38 s) while having $5\times$ higher logical error rate (LER). Trimming Relay-BP (e.g., fewer sets) or running order-0 OSD creates a messy Pareto frontier that requires fine-tuning multiple routing thresholds. 
* **The winning play:** At $p=0.004$, roughly $80\text{--}85\%$ of shots are clean or low-weight errors. If Tier 1 finishes in $<10\text{ ms}$ on $80\%$ of shots and passes the remaining $20\%$ to Relay-BP, mean latency immediately drops from $\sim 380\text{ ms}$ to $\sim 85\text{ ms}$ with **zero LER penalty**. Only add a middle tier if Relay-BP’s p99 tail remains unacceptable.

---

### 2. Light Stage: Whole-Shot Accept/Reject

* **Algorithm & Budget:** Min-sum BP (`ldpc.BpDecoder`), 20–30 iterations max, scaled min-sum ($\alpha \approx 0.8\text{--}0.9$).
* **Acceptance Rule:** 
  $$\text{Accept } \iff H\hat{e} = s \quad \text{AND} \quad \|\hat{e}\|_0 \le w_{\text{max}} \quad \text{AND} \quad \min |LLR_{\text{post}}| > \theta$$
  For the Gross code ($d=12$), set $w_{\text{max}} = 3$ or $4$.
* **Reject Partial Commits:** Do **not** commit confident bits and pass a residual. 
  1. Correlated trapping sets in bivariate bicycle codes mean confident check/bit nodes can be wrong together.
  2. Submatrix slicing and re-instantiating CSR matrices in Python per shot adds 5–10 ms of overhead, destroying the speed advantage. Whole-shot accept/reject is branchless, zero-copy, and fast.

---

### 3. Router: Lightweight GBDT / Heuristic Gate

* **Features (must compute in $<0.5\text{ ms}$ in NumPy):**
  1. Syndrome Hamming weight $\|s\|_0$ (`syndrome.sum()`).
  2. BP convergence status (`converged` bool).
  3. Decoded error weight $\|\hat{e}\|_0$.
  4. Soft metrics: mean, variance, and $\min$ of absolute post-BP LLRs.
* **Model:** A depth-3 Decision Tree or shallow LightGBM classifier. In fact, a **hard threshold heuristic** on `(converged, weight <= 4, min_LLR > threshold)` will capture 95% of the ML model's utility with microsecond execution latency.
* **Labeling & Objective:**
  * Label $y=0$ if Tier 1 decoded correctly (observable parity matches ground truth); $y=1$ if Tier 1 failed or didn't converge.
  * **Objective:** Minimize mean + tail latency subject to zero LER inflation:
    $$\min_\tau \; \mathbb{E}[\text{Latency}(\tau)] \quad \text{s.t.} \quad \text{LER}(\tau) \le \text{LER}_{\text{Relay}} + \epsilon$$
    Calibrate the router threshold $\tau$ (predicting $P(\text{Tier 1 fails})$) so the false-negative rate (classifying a failing shot as "easy") is $\approx 0$.

---

### 4. Failure Modes & Evaluation Traps

1. **The Degeneracy / Undetected Logical Error Trap:** BP can converge ($H\hat{e} = s$) to a valid codeword that differs from the true error by a logical operator. If the router accepts based solely on $H\hat{e}=s$, your LER will explode to BP levels ($4.4 \times 10^{-3}$). The weight bound ($\|\hat{e}\|_0 \le 4$) is vital because minimum logical weight is 12.
2. **Unmeasured Routing Latency:** All feature extraction, matrix multiplications, and model inferences must be timed inside `score()`'s per-shot clock. If routing takes 5 ms, you cannot afford it on shots that take 2 ms to decode.
3. **Cross-$p$ Generalization Trap:** A classifier trained at $p=0.004$ will mispredict syndrome density at $p=0.005$. Either train separate thresholds per $p$, or include $p$ as an explicit feature.
4. **Independent X/Z Pairing Trap:** The kit scores pairs $(X, Z)$. If your router is overly conservative on Z, optimizing X latency yields diminishing returns for the pair's wall-clock time.

---

### 5. Qubit Loss / Heralding: Day 2 Bonus Only

* **Hackathon strategy:** Do not touch this until the 2-tier pipeline works and is benchmarked on Pauli noise.
* **Simplest correct implementation:**
  1. Add `HERALDED_ERASE(p_erase)` to data/ancilla idling in Stim circuits (`make_circuit.py`).
  2. When an erasure fires, the detector error model mechanisms associated with that location lose their biased prior: their prior is set to $p=0.5$ (prior $LLR = 0$).
  3. Pass the shot-specific priors to `BpDecoder(H, error_channel=shot_priors)`. Min-sum BP natively solves erasures when input LLRs are zeroed.

---

### 6. Minimal First Experiment (< 15 min on 10 cores)

**Goal:** Prove the Tier 1 gate correctly filters $\ge 75\%$ of shots with 0 added logical errors.

* **Configuration:**
  * $p = 0.004$, 2,000 shots of X and Z.
  * Parallelize across 10 workers using Python's `multiprocessing`.
* **Script Logic:**
  1. Run pure BP (`max_iter=30`) on each shot.
  2. Apply rule: If converged AND $\|\hat{e}\|_0 \le 4$, accept; else pass to `relay_decoder`.
* **Success Criteria (to establish that the idea has legs):**
  * Tier 1 accepts $\ge 75\%$ of shots.
  * Tier 1 logical failures among accepted shots is exactly 0.
  * Mean time per shot drops from $\sim 380\text{ ms} \to < 120\text{ ms}$.
* If this succeeds, the pipeline is viable, and you can proceed to train the ML router for the borderline cases.
