1. **R2 is the leading explanation, but causation is not established.** The excess failures concentrate on `no_solution`, where the referee determines the outcome. Discovery’s 10 versus 12 failures provides little evidence that R2 is better. However, “6/7” mixes basis-decode counts with pair-level counts; map those events to pairs before attributing that fraction. RNG carryover also prevents treating R5 as an identical fallback to standalone Relay-BP.

2. **Honest headline:** “A non-ML adaptive decoder reduced average runtime, but no confirmatory operating point met both our accuracy and latency requirements.”

   At 0.003, latency passed but accuracy failed; at 0.004, accuracy remained inconclusive; at 0.0045–0.005, accuracy passed but latency failed. The exploratory points motivate further work, not a validated extension of the operating range. Accuracy PASS means meeting the registered margin, not outperforming Relay-BP.

   **Resolve one reporting inconsistency before presenting:** every displayed latency ratio satisfies its displayed inequality, yet most latency verdicts say FAIL. State the additional registered criterion or uncertainty calculation responsible—or correct the labels if erroneous. Do not silently reinterpret them.

3. **Single best next experiment: a paired referee ablation at p = 0.003.** Freeze K=5 and all gate decisions; compare R2 versus R5 fallback against Relay-BP on the same fresh shots. Use explicit, isolated RNG streams per shot, basis, and component, with matched R5 streams for fallback and comparator. Randomize timing order.

   Pre-register the accuracy margin, latency rule, and sample size sufficient for these rare failures. Record both pair-level discordances and their paths. This directly tests whether replacing R2 removes the accuracy deficit while preserving the only confirmed latency win.
