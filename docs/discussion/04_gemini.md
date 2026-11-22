### 1. Pre-Registered Pass/Fail Criteria
- **Accuracy (Non-inferiority)**: 
  - Paired two-sided McNemar test vs. full Relay-BP has $p > 0.05$ across each dataset individually.
  - Total pooled pair failures across all 17,000 pairs must be $\le$ full Relay-BP.
  - "Agreed-but-wrong" pairs must constitute $< 20\%$ of total gate failure events and $< 0.15\%$ of total pairs.
- **Latency & Escalation**:
  - Serial mean pair time $\le 0.70\times$ Relay-BP; parallel ($\max(s_0, s_1)$) mean $\le 0.45\times$ across all $p$.
  - Escalation rate stays strictly $< 3.0\%$ at all tested noise levels ($p \in [0.003, 0.005]$).

---

### 2. Missing Checks & Plan Corrections
- **Per-basis vs. Pair escalation**: Escalation should trigger per basis ($X$ and $Z$ independently). Document if an $X$ escalation triggers $Z$ escalation or only its own rerun.
- **Trigger decomposition**: Separate escalation rates into:
  1. *Convergence failure* (`success == False` on either seed).
  2. *Valid disagreement* (both converged to valid syndromes, but differing logicals).
- **Tail latency reality check**: Serial escalation incurs $t_{s0} + t_{s1} + t_{\text{relay}}$. Ensure p95/p99/max timing explicitly sums these for escalated shots rather than substituting the raw relay duration.
- **Replication validation**: Formal equivalence check between the two $p=0.004$ runs (seeds 101 and 401) via Fisher's exact test on failure and escalation counts.

---

### 3. Confounders to Watch / Fix
- **Deterministic first-leg inflation**: Shots finishing within the shared deterministic phase ($\le 80$ iterations) are mathematically guaranteed to agree (agreement = 1.0). Report escalation and agreement metrics both *overall* and *conditioned on iterations $> 80$* to isolate actual multi-seed consensus power.
- **Execution order bias**: In `work()`, `fast_s0` always runs first and `relay` always runs fourth. Cache cold-starts favor later decoders, while thermal throttling penalizes them. Randomizing decoder order per shot eliminates systematic timing skew.
- **CPU oversubscription**: If Relay-BP relies on OpenMP or multithreaded BLAS, 8 parallel workers will contend for CPU threads and distort `perf_counter` readings. Verify `OMP_NUM_THREADS=1` / `MKL_NUM_THREADS=1` in worker processes.
