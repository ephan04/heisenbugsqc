**Use immediate perfect-herald erasure first, then delayed heralds.** This is a credible study of decoding with loss information, provided you describe erasure as a proxy for physical atom loss.

**1. Staged plan: cap this at six hours.**

- **Hours 0–2:** implement immediate erasure, verify record bookkeeping and conditional priors, demonstrate a herald-aware baseline.
- **Hours 2–3:** expose only qubit-and-cycle flags while keeping exact locations hidden. This models delayed information about transient erasures, not persistent loss.
- **Hours 3–5:** train and evaluate ML-assisted decoder selection.
- **Hour 6:** held-out evaluation and robustness checks, optionally including missed/false flags.

Defer clifft unless someone already has a validated example. Installation, persistent-loss gate semantics, replacement policy, and decoder compatibility make it too risky for the critical path.

**2. Preserve the required noise sweep.**

Keep every existing `DEPOLARIZE2(p)` unchanged for \(p\in\{0.003,0.004,0.005\}\). Add independent erasures after CX on each participating qubit, with probability \(q=\alpha p\).

Pilot \(\alpha=0,0.02,0.1\); increase only if flags barely affect performance. These are **additional erasure hazards**, not fractions of a fixed total error budget. Report \(p,q\), mean heralds per shot, and logical failure. Select one nonzero \(\alpha\) using validation shots, then freeze it across the required sweep.

Initially omit idle and measurement loss: they introduce additional exposure and readout conventions. A fixed-total-noise comparison can be supplementary, but cannot silently replace the kit’s \(p\) sweep.

**3. Condition the decoder correctly.**

A perfect herald means a uniformly random Pauli: represent it as **two independent fair binary generators, X and Z**, propagated from that location into detector **and logical-observable** signatures. Y is their combination. Do not assign probability \(1/4\) independently to X, Y, and Z columns.

Match generator signatures to existing DEM columns, checking observable signatures as well as detector signatures. A matching flagged generator makes its combined binary-column prior \(1/2\). For independent contributions merged into one column, use
\[
r_{\mathrm{combined}}=\frac{1-\prod_i(1-2r_i)}2.
\]
Start from the original Pauli-noise DEM; with perfect flags, unflagged locations contribute no erasure noise. Validate any approximation inherited from the base DEM.

Update BP-OSD probabilities per shot; rebuild Relay-BP with the same probabilities. Feed these conditioned candidates into your agreement gate.

For coarse flags, distribute posterior location probability using the known hazard and eligible locations. **Do not mark every location in the cycle fully erased.** Independent marginal priors approximate correlated location uncertainty; label that approximation.

Gaussian elimination on flagged-generator columns is a useful diagnostic and possible hybrid: eliminate their syndrome contribution before decoding residual noise. Pure peeling may stall, and syndrome consistency alone cannot resolve logical ambiguity.

**4. Give ML a specific opportunity.**

Immediate perfect heralds mostly favor physics rules. Target **candidate selection under coarse heralds and loopy decoding**.

Train a small gradient-boosted classifier on decoder-disagreement shots:

- **Inputs:** cyclewise flag counts, local flag/syndrome overlap, BP confidence summaries, iteration counts, residual checks, and each candidate’s conditioned likelihood score.
- **Output:** which decoder’s logical prediction to select.
- **Labels:** simulator logical truth; identify which candidate succeeds. Handle both-correct/both-wrong cases explicitly.

Beat the best individual conditioned decoder, your fixed agreement gate, and a tuned physics-likelihood selector. Freeze thresholds on validation data. Report end-to-end failure reduction; disagreement accuracy alone is insufficient.

**5. Evaluate paired comparisons.**

Use identical shots for herald-blind, perfect-aware, coarse-aware, and ML-assisted decoding. Include the original no-erasure experiment. Report per-basis and joint logical failure, paired confidence intervals, runtime, and flag counts. Large improvements are plausible, not guaranteed.

**6. Catch bugs early.**

Renumber **all** measurement-record references, including observables and feedback. Check zero-loss equivalence, injected X/Z/Y signatures, conditional flip rates, and prior restoration between shots. Test erasure-only cases before mixed noise. Keep exact locations and logical truth out of ML inputs; split independent shots before tuning.
