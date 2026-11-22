# 30 — Live demo plan (synthesis of Claude, GPT 29_gpt.md, Gemini 29_gemini.md)

> Copied from `docs/discussion/` (the original discussion file), kept here as an easy entry point.

**What runs live:** our agreement gate (K10 R5) and kit Relay-BP on the same fixed-seed shots, 8 workers.
- p = 0.003: 2,000 pairs (~20 s; expected time = pairs x (gate + Relay ms) / 8).
- p = 0.004: 1,000 pairs (~60 s).
- p = 0.005: not live (7 pairs/s); shown from our recorded 3,000-pair run.
BP-OSD is not run live: its accuracy comes from the organisers' table and its speed from the recorded runs.
Total ~1.5 min after a ~10 s warm-up.

**Figure (one row per live run, 2 panels each), updating 2-4 times per second:**
- *Accuracy (left):* LER per cycle, log scale. Grey = organisers' BP-OSD and Relay-BP with their error bars.
  Colour = live gate and live Relay-BP with 95% intervals (zero failures -> upper-limit arrow). Hollow = our earlier
  large runs (10k / 6k pairs), labelled as such. The title shows the failure counts and pairs done.
- *Speed (right):* the distribution of time per pair (cumulative curve, log time axis) for live gate vs live Relay-BP,
  with the running mean and p99 marked and the ratio printed ("gate mean = 0.38x Relay-BP"). The organisers' raw
  seconds are not plotted against ours (different machine); only their BP-OSD / Relay-BP ratio is shown as a grey note.
- A strip under the figure: progress, elapsed time, gate path shares (first 80 iterations / seeds agreed / referee).

**Technology:** one script, `demo/live_demo.py`. Matplotlib interactive window (no web stack).
`Pool.imap_unordered` over batches of ~8 pairs; workers return per-pair outcomes, times and paths; only the main
process plots. Decoder order is shuffled per shot.

**Stage safety:**
- Workers build and warm up their decoders before the timer starts; shots are pre-sampled.
- Seeds fixed and declared in advance: the same seeds as our recorded runs, not picked for a good result.
- `--max-seconds` stops submitting work and plots what is done.
- `--replay` animates the same figure from recorded data (data/compare_p*.npz) if anything fails; a saved PNG is the last resort.

**Honesty rules for the narration** (fixing overclaims from the drafts): small runs illustrate, they don't prove.
At p = 0.003 the live run expects about 1 failure per decoder, so the message there is speed. At 0.004 the error bars
overlap. Point to the large runs for accuracy evidence. Never say "zero accuracy loss".

**Presenter script:**
1. "Same noisy shots of the Gross code, decoded live on this laptop by Relay-BP and by our agreement gate. No ML."
2. "Bottom strip: most shots are solved in the first 80 iterations, or two quick runs agree, so the heavy fallback is rare."
3. "Left: our error rate sits on Relay-BP's, and on the organisers' numbers. Error bars are wide for a one-minute run;
   our 10,000-pair runs are the hollow markers."
4. "Right: same accuracy in about 0.4x the time at p = 0.003 and 0.7x at 0.004 on average. The slowest shots still
   cost about the same as Relay-BP."

**Build estimate:** ~1.5-2 h including rehearsal (script ~1 h, replay mode ~20 min, rehearsal and timing ~30 min).
