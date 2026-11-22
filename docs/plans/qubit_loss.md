# Loss plan: synthesis of round 23 (Claude, GPT, Gemini)

> Copied from `docs/discussion/` (the original discussion file), kept here as an easy entry point.

## Agreed
- Stage 1: immediate, perfectly heralded erasure after every CX (stim HERALDED_ERASE), described as a proxy for atom loss. Defer clifft and missed/false flags.
- Stage 2: coarse heralds. The decoder learns the qubit and cycle of a loss but not which CX. The location ambiguity is where ML has a real job.
- Decoding: raise per-shot priors of existing DEM columns. ldpc BpOsdDecoder.update_channel_probs for BP-OSD; rebuild Relay-BP per shot (1.8 ms); feed both into the gate.
- Comparison ladder on identical shots: herald-blind -> flat coarse priors -> ML coarse priors -> exact-herald oracle. Include the no-erasure case.

## Decisions on the disagreements
- Erasure rate: additive (GPT), keeping the kit's DEPOLARIZE2(p) unchanged, with q = alpha * p, so the required p sweep stays comparable with the earlier baselines.
  Pilot alpha in {0.5, 1} (Gemini's 50% split corresponds to alpha = 1 on top); freeze one alpha before confirmation.
- Prior semantics (GPT): an erasure is two fair generators, X and Z. Per-basis decoding sees one of them (Z errors in X memory, X errors in Z memory),
  so the flagged generator's column gets prior 1/2, combined with any base prior by r = (1 - prod(1 - 2 r_i)) / 2. Clamp at 0.499 (Gemini).
- Herald bookkeeping: renumber detector and observable rec targets to absolute indices (GPT). Verify zero-loss equivalence with the kit circuit bit for bit.
- ML (Gemini's formulation, GPT's rigor): a per-herald model predicts which CX in the flagged cycle the erasure hit, from the local syndrome
  (the detectors adjacent to that qubit in cycles c and c+1). Its output spreads the 1/2 prior over the candidate columns.
  The baselines it must beat are the flat spread (uniform over the ~7 CX) and the exact-herald oracle as the ceiling.
  Risk: BP may already infer the location from flat priors, so the ML gain may be small. That is the honest test.

## Sanity checks (do before any comparison)
1. With alpha = 0 the renumbered circuit gives identical detectors to the kit circuit for the same seed.
2. Herald rate equals the expected number of locations x q; the flip rate given a herald is 1/2 per relevant generator.
3. Erasure-only circuit (p = 0): herald-aware decoding should be near perfect at moderate q; herald-blind clearly worse.
4. Exact-herald-aware must beat herald-blind by a large factor at p = 0.005; if not, suspect the location -> column map.

## Timeline (about 6 h)
0-2 h stage 1 + sanity checks; 2-3 h coarse heralds + flat baseline; 3-5 h ML location model + replay; 5-6 h pre-registered fresh-seed run and report.
