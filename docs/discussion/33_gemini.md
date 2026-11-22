### 1. Proposed Folder Layout

```text
├── README.md
├── kit/                         # Unmodified organizer kit
├── ml_router/                   # Emma Phan's ML router
├── experiments/                 # Core decoder & study scripts (run from root)
├── data/                        # Frozen shot data & models (.npz, .pkl)
├── results/                     # Logs & JSON metrics
│   └── tail_latency/            # rarepineapples' benchmark
├── figures/                     # Headline plots (Figs 1–5, PNG & PDF)
├── report/                      # report.pdf & paper LaTeX source
└── docs/
    ├── plans/                   # 24_loss_plan.md, 30_demo_plan.md
    ├── prompts/                 # PROMPTS.md & prompt iteration logs
    └── discussion/              # 00–33 AI logs & SUMMARY.md
```

**Junk to delete:** `__pycache__/`, `report/*.log`, `report/*.aux`, `report/build.log`, `.DS_Store`, and any temporary `.new` shell history files. Keep all `.npz`, `.pkl`, `.json`, and `.txt` files in `data/` and `results/`.

---

### 2. Safely Preserving Imports & Relative Paths

To avoid breaking relative file operations (`data/`, `results/`) and module imports without modifying 30+ scripts:

1. **Keep `experiments/` flat**: Moving scripts into nested subdirectories breaks both relative file paths (`open("data/...")`) and local imports (`import gate`).
2. **Execution rule**: Run all scripts from repo root using either:
   ```bash
   PYTHONPATH=experiments python experiments/agree.py
   # OR
   python -m experiments.agree
   ```
3. **One-line root guard** (optional, zero-risk): Prepend to `experiments/gate.py`:
   ```python
   import sys, os; sys.path.insert(0, os.path.abspath("experiments"))
   ```
   This ensures any script importing `gate` immediately gains visibility into helper modules (`adaptive_report`, `report_figures`, etc.).

---

### 3. README Outline (Judge-Centric & Accessible)

1. **Title & Executive Summary**
   - *Agreement Gate Decoder for the [[144,12,12]] Gross Code*.
   - Headline metrics: **2.60× / 1.37× / 1.15× speedup** over Relay-BP at $p=0.003/0.004/0.005$ with **statistically identical logical error rate**, **3–8× lower failure rate than BP-OSD**, and **zero trained weights** (+5.5 MB RAM).
2. **Intuition & Concept (Non-Expert Friendly)**
   - Explain Gross code decoding complexity.
   - The *Agreement Gate* idea: run two fast, independent BP passes; accept immediately if they agree, escalate only on disagreement.
3. **Key Findings & Headline Figures**
   - **Throughput & Speedup**: Mean latency gains across error rates (`figures/2_speed.png`).
   - **Accuracy**: Logical error rate comparison against Relay-BP & BP-OSD (`figures/1_accuracy_vs_p.png`).
   - **Tail Latency & Trade-offs**: P99 stability (`figures/3_latency_distribution.png`, `figures/4_speed_vs_accuracy.png`).
   - **Hardware Footprint**: CPU-only memory profile (`figures/5_hardware.png`).
   - **Negative ML Results**: Why learned routers and noise classifiers failed to beat rule-based gating under uniform noise (and why ML pivots to qubit loss).
4. **Reproducibility & Quickstart**
   - Step-by-step shell commands to run smoke checks and reproduce benchmark tables from root.
   - Direct link to `report/report.pdf` for the complete research paper.
5. **Repository Guide**
   - Quick roadmap to `experiments/`, `report/`, `ml_router/`, `kit/`, and `docs/plans/`.
6. **Team & Attribution**
   - **Fernando** (+ Claude, GPT-4, Gemini 2.0): Agreement Gate architecture, verification, and report.
   - **Emma Phan**: Machine learning router (`ml_router/`).
   - **rarepineapples**: Organizer kit integration & tail latency benchmarking (`results/tail_latency/`).
