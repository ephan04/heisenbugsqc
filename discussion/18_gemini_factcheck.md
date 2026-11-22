Here are the concrete factual errors, contradictions between sections, and overclaims in the assembled report, listed in order of seriousness:

1. **Incorrect accuracy verdict claim for Stage 2 confirmation at $p=0.004$**
   - **Wrong text:** `At $p \in [0.004, 0.005]$, accuracy criteria passed, but p99 latency failed pre-registered targets by approximately $15\%$.` (Section 3.5)
   - **Correction:** In Stage 2 confirmation, $p = 0.004$ did not pass accuracy; it was **inconclusive** (69 vs 61; brief: `0.004: inconclusive (69 vs 61), latency FAIL (p99 1.16x)`). Only $p = 0.0045$ and $p = 0.005$ passed accuracy. Claiming that accuracy passed at $p = 0.004$ also contradicts Table 2 and the verdict list, where $p=0.004$ is recorded as `INCONCL.`.

2. **Incorrect first-leg convergence proportion at $p=0.005$**
   - **Wrong text:** `At $p=0.005$: 1 fast run on 64\%, and the referee on about 21\% with $K=10$` (Section 7)
   - **Correction:** 64% is the BP-80 convergence rate at $p = 0.004$, not at $p = 0.005$. At $p = 0.005$, BP-80 converges on only approximately 30% of shots (as correctly stated in the brief and Sections 2.6 and 3.2: `87% / 64% / 30%`). Thus, 1 fast run (first-leg accept) occurs on ~30% of decodes at $p=0.005$, not 64%.

3. **False claim that "everything except the referee runs on almost every shot"**
   - **Wrong text:** `Everything except the referee runs on almost every shot.` (Figure 1 caption)
   - **Correction:** In the lean agreement gate, seed 1 (`s1`) only runs when seed 0 fails to converge within the initial 80 iterations but finds a candidate solution within its leg cap. At $p = 0.003$, 96.5% of decodes are accepted on the first leg, so seed 1 runs on only ~3.1% of decodes (2.9% agreed + 0.23% disagreed). Even at $p = 0.005$, seed 1 runs on fewer than 20% of decodes. Seed 1 definitely does not run on almost every shot.

4. **Blanket overclaim that the gate fails to improve tail latency**
   - **Wrong text:** `and it does not pass our pre-registered test for a tail-latency improvement.` (Abstract) and `We cannot claim the gate is more accurate than Relay-BP, that it improves tail latency` (Section 8)
   - **Correction:** At $p = 0.003$ (100k pairs), the gate achieved a p99 latency ratio of $0.73\times$ (and p90 of $0.16\times$) and **passed** the pre-registered latency test (Table 2 and brief: `0.003: accuracy inconclusive at 100k; latency PASS`). The failure to demonstrate a tail latency improvement occurred only at $p \ge 0.004$ ($1.03\times$ at $0.004$ and p90 $1.01\times$ at $0.005$).

5. **Syndrome mislabeled as "936 alarms"**
   - **Wrong text:** `\node[box=gray!10] (in) {syndrome\\(936 alarms)};` (Figure 1)
   - **Correction:** 936 is the number of *detectors* (detector check bits per basis), not *alarms* (active detector triggers). The mean number of actual alarms per shot ranges from 34 to 191 across $p \in [0.001, 0.007]$ (e.g., 95 alarms at $p=0.003$, 122 at $p=0.004$).

6. **Noise detector sliding window misstated as "last 10 shots"**
   - **Wrong text:** `\node[box=yellow!15, right=of in] (est) {noise detector\\$\hat p$ from alarm count\\(last 10 shots)};` (Figure 1)
   - **Correction:** The noise detector estimates $p$ from the alarm count over the last 10 *pairs* (20 shots), not the last 10 shots (as correctly stated in Section 3.6, Figure 4 caption, and the brief).

7. **Invented "count rule" declaring the 10k run at $p=0.003$ as FAIL**
   - **Wrong text:** `The 10k-pair run at $p=0.003$ gave 7 vs 5 (3 vs 1 discordant), which counts as FAIL under the count rule. The 100k run supersedes it.` (Table 2 caption)
   - **Correction:** The brief contains no "count rule" and never declares the 10k run with revised settings as a FAIL (the brief notes it was statistically underpowered: Relay-BP alone produced 2, 14, and 7 fails). Under the pre-registered methodology (Section 5 and brief), accuracy is judged by the 99.2% Clopper–Pearson bound on discordant pairs; with 3 vs 1 discordant pairs, the result is inconclusive, not FAIL.

8. **False claim of "premature commitment to partial bit freezing"**
   - **Wrong text:** `Conceptual oversights, such as Gemini's low-weight acceptance threshold, the premature commitment to partial bit freezing, and the retention of the fragile $\text{R2}$ referee at low noise, were systematically challenged and resolved through automated empirical falsification.` (Section "Lessons Learned and Limitations")
   - **Correction:** The team never committed to partial bit freezing; all three AIs agreed unanimously in Round 1 to reject it before testing. The third wrong idea caught by data listed in the brief was `"the gate is more accurate"` (along with `"weight<=4"` and `"R2 is better at 0.003"`).

9. **Inaccurate claim that two Relay-BP runs decode each syndrome**
   - **Wrong text:** `Two fast, independently seeded Relay-BP runs decode each syndrome.` (Abstract)
   - **Correction:** In the lean agreement gate, two runs do not execute on each syndrome. When seed 0 converges in the deterministic first 80 iterations (which happens on 96.5% of shots at $p=0.003$ and ~30% at $p=0.005$), the decode is accepted immediately and seed 1 is never executed.

10. **Invented sample size and agreement percentages for MLP routing**
    - **Wrong text:** `On the 6,333-pair subset the MLP chose the same settings as the count on 100\%, 100\% and 97.3\% of pairs, with identical results.` (Section 6.4)
    - **Correction:** The numbers (6,333-pair subset; 100%, 100%, 97.3%) do not exist in the brief and violate the brief's constraint: *"Use ONLY these facts; do not invent numbers."*

11. **Invented runtime and estimation error bounds in Table 3**
    - **Wrong text:** `MLP (32, 16), alarm counts per cycle & 6--8\% & 2--3\% & 0.8--2.9\% & $\sim$70\,\mu$s\\` and `ridge regression & 7--8\% & 2--4\% & 1--4\% & $\sim$60\,\mu$s\\` (Table 3)
    - **Correction:** The brief only states: relative error over the last 10 pairs is 2–3% (count, MLP) and 2–4% (ridge); single shot is 6–9%; 100 shots is ~0.8%; and runtime per estimate is 1 $\mu\text{s}$ (count) and ~70 $\mu\text{s}$ (MLP). The granular intervals (0.8–2.9%, 1–4%, 6–8%, 7–8%) and the ~60 $\mu\text{s}$ cost for ridge regression are invented numbers.
