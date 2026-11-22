# Brief: ML-assisted hierarchical decoder for the Gross code (MidQWest 2026, Infleqtion Challenge 1)

Three AI agents (Claude, GPT via Codex, Gemini via Antigravity) are discussing the approach before building a prototype. Please read this, then answer the questions at the bottom.

## The challenge
- Code: [[144,12,12]] Gross code (bivariate bicycle). Memory experiments, 12 noisy cycles, X and Z basis.
- Kit is in `kit/` (read `kit/README.md`, `kit/decoders.py`, `kit/circuit.py`, `kit/baseline.py`).
- Per-basis decoding problem: H is 936 detectors x 8784 mechanisms (`dem_matrices(circuit, "X")`). Full XYZ problem: 1728 x ~68k (`dem_matrices(circuit)`).
- Baselines: BP-OSD (CS-10, 80 iters) and Relay-BP (relay-bp 0.2.2). At p=0.004: BP-OSD ~4.4e-3/cycle, 0.33 s mean; Relay-BP ~8.7e-4/cycle, 0.38 s mean, p99 ~6 s.
- Required: sweep p in {0.003, 0.004, 0.005}; report logical error rate per cycle, decode latency (mean + tail), resources. Compare on the same shots.
- Bonus: use qubit *loss* / heralding info. The kit does NOT simulate loss; would need to be added (e.g. Stim HERALDED_ERASE).
- Environment: Python 3.12 venv at `.venv` with stim, ldpc 2.4.1 (BpDecoder, BpOsdDecoder, BpLsdDecoder), relay_bp, numpy, scipy, scikit-learn. 10 CPU cores, Apple Silicon, no GPU. Hackathon timescale (~1-2 days).

## The team's proposed approach
1. **Light decoder** pass: cheap, removes quick/easy errors (e.g. short BP run, keep confident bits / or accept if converged).
2. **ML router** looks at the residual / BP diagnostics and routes each shot:
   - easy -> accept light result
   - moderately hard -> fast decoder, slightly lower accuracy (candidates: BP-LSD, BP-OSD order 0, trimmed Relay-BP)
   - hard -> slow, accurate decoder (Relay-BP, possibly XYZ-Relay-BP on the full 1728-detector problem)

Related work: hierarchical decoding survey arXiv:2611.16271 (Sec. III-B predecoding cascades); BP partial decoder; lazy predecoder; GARI-NMS (2510.14060); qDither-BP (2611.07144); greedy peeling for BB codes (2604.11352); BP convergence prediction (2604.07995).

## Questions (answer concisely, be concrete and critical)
1. Is this 3-tier design the best use of 1-2 days? What would you change, cut or add? Is the middle tier worth it?
2. Light stage: what exactly (algorithm, iteration count, accept rule)? Is partial "commit confident bits, pass residual" a good idea for this code, or just accept/reject whole shots?
3. Router: features, model, and how to get labels cheaply. What is the routing objective (e.g. minimize mean/p99 latency subject to LER <= Relay-BP + epsilon)?
4. Where could the ML router realistically fail or mislead? What are the evaluation traps?
5. Loss: worth doing in the hackathon? If yes, simplest correct way.
6. Propose a minimal first experiment (small shot count, runs in < 15 min on 10 cores) that tells us whether the idea has legs.

Write your answer to the file named in your prompt. Do not modify `kit/`.
