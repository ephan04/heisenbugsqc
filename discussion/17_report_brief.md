# Report brief: facts for the final report (Claude + GPT + Gemini). Use ONLY these facts; do not invent numbers.

Audience: hackathon judges and teammates. The team lead is learning QEC, so explain concepts plainly but correctly.
Output: LaTeX BODY ONLY (\section, \subsection, itemize, tabular with booktabs \toprule/\midrule/\bottomrule, $math$).
No preamble, no \begin{document}, no figures (Claude adds them). Use \textbf sparingly. Escape % and _ and &.

## The challenge (MidQWest 2026, Infleqtion "Qubits & Gradients", Challenge 1; repo github.com/Infleqtion/MidQWest-2026)
- ML-assisted decoding of the [[144,12,12]] Gross code (bivariate bicycle qLDPC code; Bravyi et al., Nature 627, 778 (2024)).
  It has 144 data qubits and 144 check qubits (288 total) and stores 12 logical qubits, with distance 12.
  A = x^3 + y + y^2, B = y^3 + x + x^2 on a 12x6 torus; each check touches 6 data qubits.
- Memory experiment: prepare |+> (X memory) or |0> (Z memory), 12 noisy syndrome cycles, then a noiseless final readout.
  Circuit-level depolarizing noise of strength p on every operation (CX, prep, measurement, idle). The kit uses stim.
- Per basis the decoder sees 936 detectors (alarms: a check whose value changed from the previous cycle) and must
  explain them with a set of 8,784 possible error mechanisms (matrix H, 936 x 8784; L maps mechanisms to the 12 logical observables).
  Full XYZ problem: 1728 detectors x ~68k mechanisms.
- Scoring: shot k of X memory is paired with shot k of Z memory; a pair fails if either basis predicts any logical wrong.
  LER per cycle = 1 - (1 - P_pair_fail)^(1/12).
- Required: sweep p in {0.003, 0.004, 0.005}; report LER, decoding latency, resources vs the baselines BP-OSD and Relay-BP; GitHub repo, plot, presentation.
  The bonus theme is qubit loss/heralding, but the kit does not simulate loss.
- Kit files: circuit.py (load_circuit, dem_matrices, sample, detector_ids), decoders.py (bposd_decoder CS-10, relay_decoder),
  baseline.py, make_dataset.py, make_circuit.py (also bb72/bb90/bb108 codes, any rounds), test_kit.py.
- Kit reference (10k shots/basis): BP-OSD 4.7e-4 / 4.4e-3 / 2.3e-2 per cycle at p = 0.003 / 0.004 / 0.005; Relay-BP 4.2e-5 (8.0e-5 with 100k) / 8.7e-4 / 6.9e-3.
  Relay-BP's mean is 0.38 s at 0.004 with a p99 of about 6 s; BP-OSD's is 0.33 s.

## Decoders (prerequisites)
- BP (belief propagation, min-sum): iterative message passing on the Tanner graph; fast but often fails to converge on quantum codes (degeneracy, short cycles, trapping sets).
- BP-OSD: BP followed by ordered-statistics decoding (Gaussian elimination on the most likely columns; CS-10 = combination sweep order 10). Always returns a syndrome-consistent answer and runs in roughly fixed time.
- Relay-BP (Mueller et al., arXiv:2506.01779; relay_bp 0.2.2): a first BP leg of 80 iterations ("pre_iter"),
  then legs of 60 iterations with random memory strengths gamma drawn from (-0.226, 0.622), each leg warm-started from the previous one.
  It collects solutions until stop_nconv=5 distinct solutions are found (or 300 legs) and returns the most likely one. Its accuracy is high, but its time per shot varies a lot (long tail).
  Its random generator has a seed, and its state carries over between decodes.
- Measured early (500 shots/p): converged BP-80 was never wrong (0/437, 0/318, 0/148 at p = .003/.004/.005), but it converges on only 87% / 64% / 30% of shots. BP-80 costs about 5-9 ms.

## Approaches considered (chronological)
1. Team idea (inspired by the hierarchical decoding survey arXiv:2611.16271): a light decoder removes easy errors, then an ML router
   sends harder shots to a fast medium decoder or a slow accurate heavy decoder.
2. Round 1 (3 AIs): all agreed on whole-shot accept/escalate. No partial "commit confident bits", because BB checks are long-range and frozen bits can lock in the wrong logical class.
   Start with 2 tiers. Judge on paired LER and latency (mean, p99), never on router accuracy. Defer loss.
3. Measured at p=0.004:
   - Gemini's "accept if weight <= 4" is wrong: the median correct correction weight is 45.
   - A BP gate in front of Relay-BP barely helps (254 vs 266 ms); the cost is in the hard ~38% of shots and the tail.
   - BP-LSD as a middle tier: 9.5e-3 LER, worse than BP-OSD, so it was cut.
   - Single-run confidence gates: the best was 13 vs 12 fails at only ~14% faster; an ML acceptance gate (logistic/GBDT on BP diagnostics) gave +5 fails.
   - Oracle headroom: a perfect gate would get 8 fails at 128 ms vs Relay-BP's 12 fails at 361 ms.
4. Agreement gate (the winner): run fast Relay-BP (stop_nconv=1, 50 legs) with seeds 0 and 1; accept if both succeed with the same
   12-bit logical answer, else send the shot to the "referee" (full kit Relay-BP). It has no learned parameters.
   - Lean version: if seed 0 solves within the deterministic first 80 iterations, accept (seed 1 would be identical; 0 mismatches in about 34k shots).
     If seed 0 finds no solution, escalate immediately. Otherwise run seed 1 and compare.
5. Pre-registered verification (doc 05), 17,000 fresh pairs:
   - Matches Relay-BP accuracy (pooled 317 vs 327). At p=0.005 it is significantly better (14 vs 2 discordant pairs, McNemar p~0.004).
   - Mean time 0.48x at 0.003, 0.70x at 0.004 (0.79x single-worker controlled); 0.96x at 0.005 (FAIL); p99 worse by 13-30% at p >= 0.004.
   - Lean gate (same accuracy): mean 0.36x / 0.63x / 0.88x; single-worker 0.72x.
6. Noise-adaptive gate (no ML; the noise level is given): settings = restart cap K (fast run may use 80 + 60K iterations) and referee
   R5 (kit Relay-BP), R2 (stop_nconv=2) or R1 (stop_nconv=1, 300 legs).
   - Stage 1 discovery: 12 settings x 6 noise levels (0.003-0.006), 24,500 pairs. Rule: lowest mean time among settings with failure ratio <= 1.05.
     Picks: 0.003 K5/R2; 0.004-0.005 K50/R5; 0.0055 K5/R2; 0.006 K5/R1.
     Cheap referees cost 15-39% accuracy at 0.004-0.005 but are harmless at >= 0.0055 (those shots fail either way).
   - Stage 2 confirmation (fresh seeds):
     - 0.003: FAIL accuracy (9 vs 2; R2 caused it), latency PASS (0.31x).
     - 0.004: inconclusive (69 vs 61), latency FAIL (p99 1.16x).
     - 0.0045 and 0.005: accuracy PASS, latency FAIL (p99 ~1.15x).
     - 0.0055 and 0.006: accuracy PASS, latency FAIL narrowly; mean 0.67x / 0.60x.
   - Ablation at 0.003 with R5: K5 gave 15 vs 14 (inconclusive) and K50 gave 10 vs 7. Lesson: 0.003 is underpowered at 10k pairs; Relay-BP alone gave 2, 14 and 7 fails in three 10k runs.
   - Revised table: K=10 with R5 for p <= 0.005; K5/R2 at 0.0055; K5/R1 at 0.006.
7. Noise detector (user's design: "when there is an alarm, the ML model detects the noise level and applies its effect"):
   - Mean X-basis alarms: 34/66/95/122/147/170/191 at p = 0.001...0.007.
   - Training: 61,500 pair-shots, 41 noise levels in [0.002, 0.007]. Features: alarm counts per (cycle, check type) = 24 per basis.
   - Estimate error over the last 10 pairs: alarm count 2-3%, MLP (32,16) 2-3%, ridge 2-4%. Single shot 6-9%; 100 shots ~0.8%.
     Cost: count 1 us, MLP ~70 us per single estimate; under 1 us per pair batched.
   - Routing replay plus a drift stream (p changes every 300 pairs): count W=10 gives 203 fails vs the oracle's 207 vs Relay-BP's 207, at 0.67x time.
   - Conclusion: routing works, but ML adds nothing over counting, because with uniform noise the total alarm count is nearly a sufficient statistic.
     With the revised table, under-estimating is the safe direction (a +10% upward bias cost 11-18% extra failures at 0.0045-0.005).

## Current results (fresh seeds; the gate uses alarm-count routing and the revised table; same shots for all decoders)
| p | pairs | BP-OSD fails | Relay-BP fails | gate fails | BP-OSD LER | Relay LER | gate LER | mean ms BP-OSD/Relay/gate | p99 ms BP-OSD/Relay/gate |
| 0.003 | 10k | 55 | 5 | 7 | 4.6e-4 | 4.2e-5 | 5.8e-5 | 94/57/22 | 565/404/307 |
| 0.004 | 6k | 336 | 55 | 53 | 4.8e-3 | 7.7e-4 | 7.4e-4 | 282/262/191 | 849/4279/4415 |
| 0.005 | 3k | 726 | 262 | 262 | 2.3e-2 | 7.6e-3 | 7.6e-3 | 578/1335/1164 | 1138/7835/7603 |
- p = 0.003 with 100k pairs: gate 86 vs Relay-BP 74 (LER 7.2e-5 vs 6.2e-5; the authors report 6.0e-5); ratio upper bound 1.46, so INCONCLUSIVE.
  Time 0.39x mean, 0.16x p90, 0.73x p99: PASS. Paths: first leg 96.5%, agreed 2.9%, no solution 0.35%, disagreed 0.23%.
  The largest gate-only excess is on the agreed path (9 vs 4).
- Gate vs BP-OSD: 3-8x fewer failures; mean time 0.23x / 0.68x / 2.0x; p99 5-7x worse at 0.004-0.005 (Relay-BP-family tail).
- Verdicts vs Relay-BP:
  - 0.003: accuracy inconclusive at 100k; latency PASS.
  - 0.004: inconclusive (53 vs 55); latency FAIL (p99 1.03x, upper bound 1.09).
  - 0.005: accuracy PASS (262 vs 262); latency FAIL (p90 1.01x).

## Methodology
- Pre-registration before each confirmation (docs 05, 09, 12, 14, 15). Discovery and confirmation use disjoint seeds.
- Paired comparisons on identical shots, with a random decoder order per shot.
- Accuracy: one-sided 99.2% (Bonferroni over 6) conditional Clopper-Pearson bound on the discordant pairs; PASS if the failure-ratio upper bound is < 1.2.
- Latency: paired bootstrap 95% upper bounds of the mean, p90 and p99 ratios; PASS if all are < 1.
- 8 workers on one Apple-silicon Mac (10 cores). Ratios are the claim; absolute ms are machine-specific. 8 workers overstate speed-ups slightly (single-core 0.79 vs 0.70).
- Three AIs (Claude via Claude Code, GPT via codex, Gemini via agy) discussed and critiqued each round; their disagreements were resolved by data.
  Wrong ideas caught by data: the weight<=4 rule, "the gate is more accurate", and "R2 is better at 0.003".

## Limitations
Simulation only, with uniform depolarizing noise and no loss; one machine; Python orchestration overhead; serial execution of the gate's stages; p=0.003 underpowered for a 20% margin; settings were selected on discovery data.

## Next steps
1. A per-shot ML difficulty predictor: send shots likely to defeat the fast decoder straight to the referee, which targets the tail and the agreed-but-wrong shots; training data exists (24.5k discovery pairs).
2. Run the stages in parallel (seeds 0 and 1 and the referee on separate cores), so latency is the max of the stages, not their sum.
3. Non-uniform or drifting noise (measurement != gate noise), where a learned detector could beat counting.
4. Loss/heralding (stim HERALDED_ERASE).
5. Other codes (bb72) to test generality.
