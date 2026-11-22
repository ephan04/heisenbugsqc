### 1. Requirements & Deliverables Scorecard

* **Set up baselines & reproduce performance:** **MET** — BP-OSD and Relay-BP fully replicated, paired, and profiled at scale.
* **Simulate memory experiments with noise (use heralding/loss):** **PARTLY** — Simulated depolarizing circuit noise thoroughly, but completely omitted loss and heralding.
* **Build ML-assisted decoder:** **NOT MET** — The deployed system is 100% heuristic (agreement gate + scalar alarm-count routing); tested ML models were abandoned.
* **Compare decoder against baselines under same noise:** **MET** — Rigorous, pre-registered paired testing on identical shots.
* **Sweep physical error rates `[0.003, 0.004, 0.005]`:** **MET** — Covered with up to 100k pairs and rigorous bounds.
* **Report LER, latency, and resource requirements:** **MET** — Reported paired LER, mean/p90/p99 latency bootstrap, and CPU/memory footprint.
* **Deliverable: Codebase on GitHub:** **MET** — Documented, reproducible repository with scripts.
* **Deliverable: Comparison plot:** **MET** — 21-page report with 7 plots.
* **Deliverable: Short presentation / demo:** **NOT MET** — "No slides yet."

---

### 2. Is our decoder "ML-Assisted"?

**No.** A skeptical judge will say you submitted a classical heuristic algorithm to an ML challenge. 

While you trained ML models (MLP for noise detection, GBDT/logistic for hard-shot spotting), **every production path runs purely on classical heuristics** (alarm counts and seed-agreement). Proving that ML is unnecessary because an alarm count is a sufficient statistic is great science, but Challenge 1 explicitly asked for an *ML-assisted decoder*. If your final artifact has zero weights and zero inference, you will score poorly on the core rubric unless you frame your submission as a rigorous ML benchmark/ablation study.

---

### 3. How central is qubit loss?

**Extremely central.** The challenge description mentions loss four times:
> *"This challenge focuses on using machine learning to improve decoding, especially in the presence of qubit loss..."*
> *"The goal is to see whether your decoder can outperform the baseline, particularly when loss information is available."*

Skipping loss strips away the exact neutral-atom physical motivation the organizers designed the problem around. Without loss, your work is a generic depolarizing-noise benchmark on the Gross code.

---

### 4. Priority Plan for the Final 6–10 Hours

Do **not** try to build a full `clifft` loss pipeline now. Implementing loss-detection flags, rewiring priors, and training a new ML decoder in 6 hours will produce buggy, unverified results and destroy your presentation.

**1. Priority 1: Slides & Presentation Polish (3–4 hours) [CRITICAL]**
* You cannot win without the required presentation deliverable.
* **Frame the narrative honestly:** "Empirical bounds on ML routing for the Gross code." Position your work as an engineering ablation: you built ML decoders/routers (show the MLP and GBDT ROC curves, inference overheads, and feature separabilities) and proved why a deterministic agreement gate beats them in tail latency.

**2. Priority 2: Toy/Synthetic ML Heralded Loss Demo (2–3 hours)**
* If you want to claim "loss" and "ML", create a small, self-contained demonstration: simulate random erasure flags on physical qubits, train a small GNN/MLP or learned prior updater to reweight check priors before BP, and show it on 1,000 shots. 
* Even as an exploratory extension, this checks the "handles loss" and "ML-assisted" boxes in the presentation.

**3. Priority 3: Noise-aware priors under non-uniform noise (Drop)**
* Non-uniform noise without loss still ignores the central challenge prompt. Do not spend time here.
