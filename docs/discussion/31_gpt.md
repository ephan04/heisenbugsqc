Based only on the supplied data, the timing arithmetic checks out; several hardware claims lack supporting probe output.

1. **Machine/CPU:** The model, core split, RAM, CPU-only execution and eight processes are not independently established here. Eight workers do **not** prove efficiency-core execution; scheduling or residency evidence is needed.
2. **Memory/matrices:** No probe output supports these figures here. Specify RSS versus another memory measure, baseline versus incremental allocation, and whether “per basis” includes all construction steps. Don’t imply these are peak decode-memory measurements.
3. **Construction:** The 5–20 ms claim needs measurements identifying which decoders and whether initialization is included.
4. **Throughput:** Correct approximately. Label it **estimated aggregate throughput**, assuming eight concurrent workers sustain the measured mean. Rounded means give gate ≈364/42/7 pairs/s; 365 is compatible with unrounded data. This is not measured wall-clock throughput.
5. **Machine comparison:** The reported Relay-BP times imply 1.75/1.45/1.27× speedups. Say “our measured runs were faster,” rather than attributing the difference entirely to hardware: workloads and execution conditions may differ. Same-shot, same-machine ratios are the stronger comparison.
6. **Requirements/state:** The described gate requires no training or additional training data. CPU-only execution needs implementation evidence. “Only extra state is a second seed” is misleading: additional decoder instances, working buffers and fallback state may be retained, consistent with your stated 5.5 MB increment.
7. **Latency ratios:** Correct rounded point estimates: mean 0.38/0.73/0.87; p99 0.76/1.03/0.97. Don’t claim universal tail improvement or preserved accuracy: the supplied accuracy verdicts are FAIL/INCONCLUSIVE/PASS, with 100k low-noise validation INCONCLUSIVE.

Proposed figures:

| Title | Axes and rows | Message and honest caveat |
|---|---|---|
| **Accuracy: organisers and our runs** | x: physical error probability; log y: LER/cycle. Organiser BP-OSD/Relay-BP plus our same-shot BP-OSD/Relay-BP/gate. | Direct accuracy context. Use supplied organiser rates, not their summed failure counts; sample sizes differ. |
| **Reported decoding time** | x: p; y: mean ms/pair. Same rows, separate source panels. | Shows provided and reproduced timings. Cross-machine bars are descriptive, not controlled speedups. |
| **Gate latency relative to Relay-BP** | x: p; y: gate/Relay ratio; mean, p90, p99 series from same shots; reference at 1. | Mean gains shrink with noise; tails are mixed. Label point estimates separately from supplied bounds. |
| **Speed–accuracy tradeoff** | x: mean ms/pair; log y: LER/cycle; facets by p. Our same-shot three-decoder rows. | Gate’s tradeoff versus both baselines. BP-OSD is faster at high noise; omit unmatched router runs. |
| **Low-noise validation at scale** | x: 10k/100k cohort; y: LER/cycle; gate/Relay bars. | Shows sensitivity to sample size. Cohorts may overlap; 100k accuracy remains inconclusive. |

Exclude the old K=50 tail run from current-setting comparisons.
