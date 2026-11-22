# Round 22: does our project satisfy Challenge 1? Be blunt and concrete. Under 600 words. Do not run tools.

## The official challenge text (verbatim)
# Challenge 1: ML-Assisted QEC Decoding

## Challenge

QEC decoders must identify and correct errors quickly. They must also stay accurate. Powerful decoders can be computationally expensive. Simpler decoders may be faster but less accurate.

For this challenge, teams will work with the Gross code, a quantum low-density parity-check (qLDPC) code in the bivariate bicycle family. Its parameters are `[[144, 12, 12]]` — 12 logical qubits in 144 data qubits, with a code distance of 12.

This challenge focuses on using machine learning to improve decoding, especially in the presence of qubit loss in addition to conventional Pauli errors. These error mechanisms are relevant to neutral-atom hardware where information about loss may be available to the decoder.

## Task

Build an ML-assisted decoder that improves an existing QEC decoder. Start with the BP-OSD and relay-BP decoders as baselines and examine whether a machine-learning approach can improve its accuracy, speed, or ability to handle loss.

**We have provided a possible scaffolding for this decoder comparison [here](challenge-1-ml-decoder-kit.zip). Download the zip file and follow its setup instructions before implementing your decoder.**

One approach is hierarchical decoding: use a fast first-stage decoder for simpler error patterns and pass harder cases to a stronger decoder. Machine learning could help identify likely errors, make use of loss information, or decide when a result should be passed to the next stage.

The goal is to see whether your decoder can outperform the baseline, particularly when loss information is available.

## Requirements

- Set up the code and baseline decoders. Download the [decoder kit](challenge-1-ml-decoder-kit.zip) and run the BP-OSD and relay-BP decoders, then reproduce their baseline performance before making changes.
- Simulate memory experiments with noise. Use heralding information, such as loss-detection flags, where available.
- Build your ML-assisted decoder. Use syndrome information and, where applicable, loss information. You can build a standalone decoder or add a learned component to an existing decoding pipeline.
- Compare your decoder against the baseline approaches under the same noise conditions.

## Possible Approaches

Some possible directions:

- **[Learned predecoders](https://github.com/NVIDIA/ising-decoding):** Train a model to recognize common error patterns and resolve them before passing the remaining syndrome to a stronger decoder.
- **Confidence-based routing:** Predict whether a decoding result is reliable enough to accept or should be sent to a stronger decoder.
- **Belief propagation:** Use BP as a partial decoder, resolving confident corrections before passing the remaining syndrome onward.
- **CNNs or graph neural networks:** Use neural networks to identify patterns in syndrome data, potentially using the structure of the code or its Tanner graph.
- **Leakage tracking:** Use temporal models, such as hidden Markov models, to identify leakage events and inform decoding.

> **Note:** You do not need to implement a hierarchical decoder. These are possible ways to approach the problem, not a required set of methods.

## Experiments and Metrics

Compare your decoder with the BP-OSD and relay-BP baselines using the same test data and noise conditions. While more experiments are encouraged for a more thorough analysis, we *require* one for this challenge:

- A sweep of your decoder across the physical error rates `[0.003, 0.004, 0.005]`.

Required metrics to report include logical error rate, decoding latency*, and decoder resource requirements. In your evaluation, discuss where your approach works well and where it falls short.

\*This is where hierarchical decoding approaches really shine!

## Deliverables

- A working decoder, the code used to generate training and test data, and the script for reproducing evaluation results on GitHub.
- A comparison of your decoder to the baselines, including at least one plot of logical error rate or decoding time.
- A short presentation or demo explaining the approach and results.

## Stretch Goals

- Train a router to decide when to accept a first-stage result or invoke a stronger decoder.
- Test the approach on a second QEC code or code family.
- Run the decoder on sliding syndrome windows.
- Study how performance changes with code distance.
- Estimate the hardware cost of the decoder, such as GPU resource usage or latency.

## Recommended Tools

A few open-source tools may be useful for this Challenge:

- **[qLDPC](https://github.com/qLDPCOrg/qLDPC):** A library for working with quantum error-correcting codes. It can be used for code construction and related QEC workflows.
- **[clifft](https://github.com/unitaryfoundation/clifft/releases/tag/v0.13.0):** A non-Clifford simulation tool extended from [Stim](https://github.com/quantumlib/stim) for quantum error correction and decoding workflows that support leakage, loss, etc.

---

# Shared Expectations

- Be prepared to explain why you chose your approach and what role quantum computing or machine learning plays in it.
- Results should be clear and reproducible, and the corresponding GitHub codebase should follow best coding practices.
- You can use existing libraries and tools rather than implementing everything from scratch.
- AI use is encouraged — but be prepared to explain your implementation!

## What we have (facts)
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

## Since then
# Hard-shot spotter (ML version a): conclusion

Design: discussion/19 (with GPT and Gemini). Result: results/hardshot_check.txt and hardshot_separability.txt. Review: discussion/20.

- Ceiling (perfect spotter, discovery replay): mean -3 to -7 points; p99 at 0.004 1.03 -> 0.99; p90 at 0.005 1.01 -> 0.97.
- Models: logistic and GBDT on pre-decode syndrome features, plus a GBDT on time saved. Inference cost per decode: rule 2 us, logistic 112 us, GBDT 0.7-2.8 ms.
- Held out (last 30% of each discovery file): every policy, including the simple alarm-count rule, chose to skip almost nothing, with results equal to the plain gate.
- Separability of "the gate would escalate": AUC 0.67-0.74 for the alarm count and 0.69-0.74 for logistic. Top-1% precision is 2% at 0.003 and 39% at 0.004.
- Decision (pre-agreed decision point; GPT and Gemini agree): stop; no fresh-seed confirmation.
- Wording (GPT): pre-decode syndrome summaries moderately predict escalation, but the tested routing policies yield no convincing net latency benefit under the tail-latency objective, the failure constraint and the inference costs.
- Next (both): use early in-flight decoder state (for example, unsatisfied checks after the first 80-iteration leg) to decide early escalation, rather than syndrome summaries alone. This needs instrumenting Relay-BP.
- Hardware cost estimate done: CPU only, one core per decode, ~100 MB per process (gate adds ~1 MB; BP-OSD +67 MB); gate 22/191/1164 ms per pair at p=.003/.004/.005 on an Apple M5.
- Repo: github.com/ephan04/heisenbugsqc, branch noise-adaptive-gate: gate code, data generation scripts, evaluation/report scripts, raw data, a 21-page PDF report with 7 figures, PROMPTS.md. No slides yet.
- Loss/heralding: NOT done. The kit circuits have no loss; the challenge suggests clifft (a Stim extension with loss/leakage).
- The deployed decoder routes with an alarm count (not ML); the MLP noise detector chose the same settings 97-100% of the time; the ML hard-shot spotter was dropped.
- Candidate next step proposed by Claude: an ML noise-rate estimator under non-uniform noise (measurement != gate noise) that rebuilds the decoder priors.

## Questions
1. Go through every Requirement, the required Experiment/Metrics, and each Deliverable: mark MET / PARTLY / NOT MET, each with one line of why.
2. Is our decoder 'ML-assisted' in a way judges will accept? Be honest.
3. How central is qubit loss to this challenge (judge's view)? Is skipping it a serious problem?
4. Given limited hackathon time (assume ~6-10 hours left), what should we do next, in priority order? Compare: (a) loss + heralding with an ML component that uses loss flags, (b) noise-aware priors under non-uniform noise, (c) slides/presentation polish, (d) anything else.
