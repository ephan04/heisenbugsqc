# Round 23: how should we simulate qubit loss and use it in decoding? Independent design. Under 700 words. Do not run tools.

Context: the Challenge 1 text (discussion/22) says "This challenge focuses on using machine learning to improve decoding,
especially in the presence of qubit loss... relevant to neutral-atom hardware where information about loss may be available
to the decoder", and "The goal is to see whether your decoder can outperform the baseline, particularly when loss information
is available". It requires: "Simulate memory experiments with noise. Use heralding information, such as loss-detection flags".
It suggests clifft (a Stim extension supporting leakage and loss). Our pipeline: the kit's Stim circuits for the Gross code
(288 qubits, 12 cycles, 84 CX layers, DEPOLARIZE2 after each CX), per-basis decoding (936 detectors x 8784 mechanisms),
BP-OSD (ldpc) and Relay-BP (relay_bp 0.2.2) baselines, and our agreement gate. The ML so far failed to beat simple rules under uniform Pauli noise.

## Facts Claude verified just now (stim 1.16)
- HERALDED_ERASE(p) q works: with probability p the herald bit is 1 and q gets a uniformly random Pauli (toy test: herald rate 0.502, flip rate 0.501 given a herald, 0.000 without).
- The DEM needs approximate_disjoint_errors=True with HERALDED_ERASE; the DEM is herald-blind (it averages over heralds).
- Putting HERALDED_ERASE after every DEPOLARIZE2 gives 20,736 erasure locations per circuit; sampling 2,000 shots takes 0.05 s and m2d conversion 0.1 s.
- Gotcha: heralds are measurement records, so inserting them shifts the relative rec[-k] targets of later DETECTORs (we got "non-deterministic detectors").
  Detector targets must be renumbered (track absolute measurement indices), or loss must be sampled another way.
- An erasure right after a CX produces single-qubit Paulis on that qubit. Those symptoms already appear as columns of the base DEM
  (DEPOLARIZE2 contains the P x I terms), so per-shot erasure-aware decoding may only need to raise the priors of existing columns.
  Mapping location -> columns is possible via stim's explain_detector_error_model_errors.
- Per-shot priors: ldpc BpOsdDecoder.update_channel_probs exists. relay_bp has no prior update, but building a new Relay-BP decoder takes 1.8 ms
  (decodes take 20-1300 ms per pair).
- Real neutral-atom loss is not the same as erasure: a lost atom stays lost, later gates with it fail, and loss is typically detected only at
  measurement or end of cycle (delayed, location within the cycle unknown); detection can have false positives/negatives. clifft can model true loss, but we have not installed or tested it.

## Questions
1. Which loss model should we use in hackathon time (~5-7 h total for loss): (i) immediate perfect-herald erasure (stim HERALDED_ERASE),
   (ii) erasure with delayed/coarse heralds (we know the qubit and cycle but not the exact gate), (iii) imperfect heralds (missed or false flags),
   (iv) true loss via clifft? Recommend a staged plan, saying what is credible and what is too risky.
2. Parameters: loss rate relative to p (e.g., erasure fraction of total error), and where loss happens (after CX, idle, measurement). How do we keep the required p in {0.003, 0.004, 0.005} sweep meaningful?
3. Decoder use of heralds: exactly how to turn heralds into per-shot priors for BP-OSD / Relay-BP / our gate. Any better erasure-specific decoding (e.g., Gaussian elimination / peeling on erased columns)?
4. Where can ML genuinely beat a physics rule here? (We need a real ML-assisted result.) Be specific: inputs, outputs, labels, model, and the simple baseline it must beat.
5. Baselines, metrics and sanity checks (e.g., herald-blind vs herald-aware; erasure-aware should beat blind by a large margin; the same shots for all).
6. The biggest risks and how to detect bugs early.
