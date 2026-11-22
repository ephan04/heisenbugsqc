1. **Run one condition: p = 0.004, 1,000 shot pairs.** Run the agreement gate, Relay-BP and BP-OSD on identical X/Z pairs, using eight workers. Your measured times predict **92 seconds of decoding**: `1,000 × (191 + 262 + 282) ms / 8`. Budget **110–150 seconds after warm-up**. This gives meaningful speed comparisons and roughly nine failures per decoder—enough to illustrate accuracy, not establish equivalence. Skip p = 0.003 because failures are too rare, and p = 0.005 because it consumes the stage budget.

2. **Final figure: two panels, both with decoder on the horizontal axis.**
   - **Accuracy:** vertical axis is logical error rate per cycle, logarithmic. Compute pair failure as “X or Z failed,” then transform with `1 − (1 − P_pair_fail)^(1/12)`. Show organisers’ p = 0.004 values as grey diamonds with their quoted uncertainties; live results as coloured circles with **95% Wilson intervals calculated on pair failure probability, then transformed**. Label counts and sample sizes. Add smaller hollow markers for your previous 6,000-pair gate/Relay results, clearly labelled “previous laptop run.” If zero failures occur, show an upper-limit marker.
   - **Speed:** vertical axis is **mean decode time per pair / Relay-BP mean**, lower is better. Live Relay = 1; expected gate ≈ 0.73 and BP-OSD ≈ 1.08. Include grey organiser ratios: Relay = 1, BP-OSD ≈ 0.87. Each dataset uses its **own machine’s baseline**; these are not cross-machine speedups. Annotate live milliseconds per pair. Final timing intervals can use paired bootstrap resampling.

3. **Use a Matplotlib interactive window.** Worker processes decode batches of **eight pairs** and return per-shot outcomes, timings and gate-path counts through `imap_unordered`. Only the main process plots, refreshing **once per second**. Time each decoder separately, summing X/Z decode time; rotate decoder order across pairs. Show completed pairs, elapsed time, provisional points/error bars, and gate-path percentages. Organiser references remain visible throughout. Keep submission bounded so stopping is practical.

4. **Prepare before the stage timer starts.** Build all decoders in every worker, warm each with a pair, and pre-sample using fixed recorded seeds; exclude preparation from decode timings. Use mains power and close competing workloads. Rehearse the exact configuration. At **140 seconds**, stop submitting batches and finish outstanding work; display the actual completed sample count. Keep a labelled recording and saved figure from the same configuration ready.

5. **Presenter script:**
   > “This is our agreement gate—no ML router.”  
   > “All three decoders receive the same noisy shots on this laptop.”  
   > “The left panel shows accuracy uncertainty; the right measures speed against our live Relay baseline.”  
   > “This short run demonstrates operation and timing. Our larger runs provide stronger accuracy evidence.”
