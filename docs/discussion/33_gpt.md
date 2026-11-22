1. **Proposed layout**

Keep the executable code stable for this cleanup; group studies through short index pages linking to their scripts, results and preregistrations.

```text
README.md
PROMPTS.md                       # keep discoverable at root
challenge-1-ml-decoder-kit/       # organisers’ kit, unchanged
kit/                            # preserve until provenance is clear
experiments/
  gate.py                       # agreement-gate decoder
  *.py                          # existing scripts and shared helpers
  studies/
    agreement/README.md
    adaptive_noise/README.md
    bposd_comparison/README.md
    hard_shots/README.md
    routing/README.md
    estimated_priors/README.md
    hardware/README.md
ml_router/                      # Emma’s contribution, preserved
data/                           # all datasets and models, unchanged
results/                        # existing output paths, unchanged
  tail_latency/                 # rarepineapples’ benchmark
figures/                        # five headline figures
report/                         # PDF, TeX sources and report figures
docs/
  discussion/                   # numbered AI logs and SUMMARY.md
  plans/
    qubit_loss.md
    demo.md
```

Make the plans concise entry pages linking to the original numbered discussions, preserving their history. Keep `PROMPTS.md` at root as the reproducibility entry point. Update documentation links after moves.

Delete only confirmed junk: `.DS_Store`, the identified `.new` shell-history file, `__pycache__/`, and generated LaTeX/build logs. Add ignore rules. Keep every dataset, model, result, figure, report source and PDF; do not deduplicate either kit directory without inspection.

2. **Imports and paths**

The least-risk choice is **no Python, data or result moves in this pass**. Keep `gate.py` and all imported helpers at their existing paths. Study indexes provide organization without import shims or package changes.

Document that every command runs from the repository root. Preserve existing `sys.path` behavior and relative `data/` and `results/` paths. Physical script regrouping can follow a separate import/path audit. No tools or checks have been run here.

3. **Simple README outline**

- **Agreement Gate: Faster Gross-Code Decoding** — MidQWest 2026, Infleqtion Challenge 1. Explain that quantum error correction infers errors from measurements; the `[[144,12,12]]` code protects 12 logical qubits using 144 physical qubits.
- **The idea** — Explain syndrome, decoder and agreement gate in plain language, with one small flow diagram matching the implementation.
- **Results** — Figures **1** and **2**: 2.60×/1.37×/1.15× mean speedups; comparable accuracy at 0.004/0.005, inconclusive at 0.003. Figure **3**: unchanged p99. State laptop, paired shots, CPU-only, no training and +5.5 MB/process. Link figures **4–5** and the full report.
- **What we learned** — ML attempts did not beat simple rules under uniform noise; qubit loss is next.
- **Run it** — Verified installation and root-level smoke-test commands.
- **Repository map**
- **Team and credits** — Fernando and AI assistance; Emma Phan’s router; rarepineapples’ kit upload and benchmark; organisers.
