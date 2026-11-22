# Round 6: design the data collection for a noise-adaptive agreement gate (NO ML yet)

User's intended final design (ML is NOT to be built now): when alarms arrive, an ML model estimates the noise level and
the decoder applies the settings best for that level. Our job now: run tests that tell us WHICH settings are best at
WHICH noise level, with valuable, trustworthy data. Noise level is given (not estimated) in these tests.

## What we know
- Skip gate (lean): fast Relay-BP seed 0 (stop_nconv=1, num_sets=50); accept if solved in deterministic first 80
  iterations; escalate if no solution; else run seed 1, accept on logical agreement, else referee (full Relay-BP).
  Accuracy matches Relay-BP at p=0.003-0.005; mean 0.36x / 0.63x / 0.88x Relay-BP time; tail worse at p>=0.004.
- p=0.005 breakdown: 52% of time = Relay-BP on the 7.3% seed-0 no-solution shots (4.5 s each, wrong 44%).
  90% of fast-run successes need <=10 restarts.
- Offline estimates (post-hoc, capped-run times scaled from iterations): cap fast runs at K=10-20 restarts + cheaper
  referee (Relay-BP stop_nconv=2) gives at p=0.005: fails 1.00x, mean 0.64-0.67x, p90 0.74-0.78x, p99 0.87-0.90x.
  At p=0.004 the cheaper referee cost accuracy on one seed (38-40 vs 30 fails) but not the other (28 vs 28).
- Noise can be read from alarms: mean X-basis alarms 95/122/147 at p=0.003/4/5; 100-shot window -> ~1% error in p.
- Compute (8 workers, decoding fast0+fast1+nconv2+relay on every shot): ~0.15 / 0.5 / 3 worker-seconds per pair at
  p=0.003/0.004/0.005, roughly x3 per +0.001 in p (so ~9 at p=0.006). Budget: ~2 hours wall clock on 8 workers
  (~57,600 worker-seconds). Relay-BP fails ~1/1000 pairs at 0.003, 1/100 at 0.004, 1/12 at 0.005.
- Candidate knobs: fast restart cap K; referee in {Relay-BP kit (nconv5, 300 sets), nconv2, nconv1/300 sets};
  maybe BP-OSD as the challenge's other baseline; maybe XYZ Relay-BP referee (1728 detectors, ~68k columns, slower).
- Pre-registration style used before: fresh seeds, fixed criteria, paired comparisons on identical shots.

## Questions (concise, under ~400 words, concrete numbers)
1. Which noise levels and how many pairs at each, within the budget? Consider what is needed to estimate failure
   ratios vs Relay-BP usefully at low p, and to cover the regime boundary where the best settings switch.
2. Which decoders/knobs must be measured directly on every shot (vs derived offline)? Is the "capped run = prefix of
   the 50-restart run" derivation trustworthy, or must caps be run for real?
3. Include BP-OSD? Include XYZ referee? Worth the compute?
4. What should the output be: what table/plot answers "best settings per noise level", and what pass criteria?
