### 1. Recommended Staged Loss Model (~5–7 h timeline)
* **Stage 1 (Hours 0–3, Must-Have): Immediate Heralded Erasure (Stim).** Place `HERALDED_ERASE(p_erase)` after each CX. The herald pinpoints $(q, t)$. This establishes the herald-aware performance ceiling and integrates cleanly with the existing DEM.
* **Stage 2 (Hours 3–5, Hackathon Sweet Spot): Coarse/Delayed Heralding.** In neutral atoms, loss is typically read out only at cycle boundaries. Model this by aggregating heralds: the decoder is told *"qubit $q$ was lost in cycle $c$,"* but not during which of the ~7 CX gates on $q$. This is realistic, technically sound, and creates the exact ambiguity where ML excels.
* **Cut / De-prioritize:**
  * *(iv) `clifft`:* **Too risky.** Compiling, binding, and re-extracting DEMs across 84 layers in 5 h invites project-ending build blockers.
  * *(iii) False alarms:* Unnecessary complication before Stage 2 works.

---

### 2. Parameterization & Noise Sweep
* **Partitioning:** Fix total physical error per CX at $p \in \{0.003, 0.004, 0.005\}$. Set $p_{CX} = p_{depol} + p_{erase}$ with an erasure fraction $f_{erase} = 0.5$ ($p_{erase} = 0.5p$, $p_{depol} = 0.5p$). This reflects atom loss conversion regimes (e.g., Rydberg leakage converted to ground erasure) while preserving the required $p$-sweep.
* **Locations:** Apply erasures strictly **after 2Q CX gates** (where 90%+ of physical error occurs across the 84 layers). Keeping idle and 1Q loss at zero ensures **zero new columns are added to the DEM**—loss maps directly onto the pre-existing single-qubit Pauli columns of `DEPOLARIZE2`.

---

### 3. Decoder Integration & Prior Updates
* **Mechanism Map:** Precompute an offline dictionary:
  $$\text{herald}(q, \text{layer}) \longrightarrow \{\text{DEM column indices for } X, Y, Z \text{ on } q\}.$$
* **Prior Assignment:**
  * For BP-OSD, update the channel priors via `BpOsdDecoder.update_channel_probs(p_vec)`.
  * For columns flagged by an erasure, clamp the prior to $p_j = 0.499$ (avoid $0.5$ exactly to prevent $\text{LLR} = \ln((1-p)/p) = 0$ division-by-zero or NaN stalls in BP).
  * For Relay-BP, re-instantiate when an erasure occurs (1.8 ms is negligible; erasures only hit a subset of shots).
* **Peeling/GE vs BP-OSD:** Pure peeling/Gaussian elimination struggles with hypergraph Gross codes under residual Pauli background noise. Soft-prior BP-OSD natively implements generalized erasure decoding: setting $p_j \approx 0.5$ makes OSD pivot on erased columns with zero penalty.

---

### 4. Where ML Genuinely Beats Simple Rules
Setting priors to $0.5$ on known gates is statistically optimal—ML cannot beat physics there. **ML wins under Coarse / Delayed Heralds (Stage 2):**
* **The Problem:** When atom $q$ is lost in cycle $c$, it could have failed at any of $K \approx 7$ CX gates. The physics rule assigns a flat prior ($p/K$) across all $K$ candidates.
* **ML Formulation (Local Candidate Classifier):**
  * **Input:** The local syndrome neighborhood (detectors adjacent to $q$ in cycles $c$ and $c+1$, $\sim 16$ binary bits) + candidate gate indices.
  * **Output:** Soft distribution $(\pi_1, \dots, \pi_K)$ over the $K$ CX mechanisms.
  * **Model:** A compact 2-layer MLP or LightGBM (ultra-fast inference, trains in 2 minutes on $50\text{k}$ shots).
  * **Baseline to beat:** Uniform spreading rule ($p_k = p_{erase}/K$). ML correlates the observed syndrome with the exact fault location, sharpening priors into near-deterministic erasures for BP-OSD.

---

### 5. Baselines, Metrics, & Sanity Checks
* **Metrics:** Logical Error Rate (LER) across the $p \in \{0.003, 0.004, 0.005\}$ sweep, evaluated on identical paired Monte Carlo seeds ($N \ge 2{,}000$ shots).
* **Comparison Ladder:**
  1. *Blind Baseline:* Standard BP-OSD ignoring heralds.
  2. *Flat-Prior Baseline:* Uniform distribution of coarse heralds.
  3. *ML-Enhanced Decoder:* ML-focused prior distribution.
  4. *Oracle Upper Bound:* Stage 1 exact-gate heralding.
* **Sanity Checks:**
  * At $f_{erase} = 0$, LER matches Round 22 baselines identically.
  * Oracle erasure-aware LER must beat Blind LER by $>2\times$ to $5\times$ at $p=0.005$.

---

### 6. Critical Risks & Immediate Mitigations
1. **Stim `rec[-k]` Index Desynchronization:** `HERALDED_ERASE` creates measurement records, silently invalidating downstream relative detector indices.
   * *Mitigation:* Do not let Stim record herald measurements. Simulate erasures by drawing the erasure mask in Python from binomial seeds, then inject corresponding single-qubit errors directly into Stim, or manually offset detector records by the cumulative herald count.
2. **BP Saturation:** Over-confident priors ($p=0.5$) freeze BP graph marginals. Keep priors clamped at $[10^{-6}, 0.499]$.
