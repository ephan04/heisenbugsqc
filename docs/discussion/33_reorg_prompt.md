# 33 — Reorganise the repo and write a simple README (do not run tools)

Hackathon repo (MidQWest 2026, Infleqtion Challenge 1: decoding the [[144,12,12]] Gross code). Team members:
Fernando (+ Claude/GPT/Gemini, our main work: the "agreement gate" decoder), Emma Phan (an ML router, branch ml-router,
copied into ml_router/), a teammate "rarepineapples" (kit upload, a tail-latency benchmark in results/tail_latency/).
The user wants it "well organized, titled, and the README should be simple with figures and concepts, a good intro".
Judges will read it. Constraints: scripts are run from the repo root and read/write data/ and results/ by relative path;
scripts import each other via sys.path (gate.py imported by 5 scripts; adaptive_report, adaptive_select, noise_ml,
bposd_compare_report, report_figures also imported); the organisers' kit must stay unmodified. We must not lose any data.

## Current tree (top level and key folders)
```
challenge-1-ml-decoder-kit
data
discussion
experiments
figures
kit
ml_router
PROMPTS.md
README.md
report
results

experiments/: __pycache__ adaptive_collect.py adaptive_confirm.py adaptive_report.py adaptive_select.py agree_plot.py agree_report.py agree.py analyze.py bposd_compare_report.py bposd_compare.py collect.py escalate.py estimated_priors_report.py estimated_priors.py gate.py hardshot.py hardware_figures.py hardware_probe.py high_noise.py lean_gate.py metrics_summary.py noise_estimate.py noise_ml.py probe_bp.py report_figures.py router_compare_report.py router_compare.py router_eval_report.py 
results/: ablation_k5.json ablation_k5.txt ablation_k50.json ablation_k50.txt adaptive_confirm.json adaptive_confirm.txt adaptive_discovery.json adaptive_discovery.txt adaptive_selected.json agree_ler_vs_latency.png agree_report.json agree_report.txt agree_verdicts.png all_metrics.json all_metrics.md bposd_compare.json bposd_compare.txt escalate_p0.004_slack2.json escalate_p0.004.json estimated_priors.json estimated_priors.txt hardshot_check.txt hardshot_headroom.txt hardshot_separability.txt hardware_probe.json infographic.html large_p0.003.json large_p0.003.txt lean_gate.txt noise_ml.json noise_ml.txt results_p0.004.txt revised_p0.003.json router_compare_p0.003.json router_compare_p0.003.txt router_eval.json router_eval.txt router_train_p0.003.txt router_train_p0.005.txt tail_latency 
data/: ablation adapt_p0.003.npz adapt_p0.004.npz adapt_p0.0045.npz adapt_p0.005.npz adapt_p0.0055.npz adapt_p0.006.npz agree_p0.003_s201.npz agree_p0.004_s101.npz agree_p0.004_s401.npz agree_p0.004.npz agree_p0.005_s301.npz agree_smoke.npz agree_timing_p0.004_s501.npz compare_p0.003.npz compare_p0.004.npz compare_p0.005.npz confirm_p0.003.npz confirm_p0.004.npz confirm_p0.0045.npz confirm_p0.005.npz confirm_p0.0055.npz confirm_p0.006.npz estprior_p0.003.npz estprior_p0.004.npz hardshot_models.pkl large_p0.003.npz noise_detector.pkl p0.004_s11.npz router_compare_p0.003.npz router_eval_p0.004.npz router_eval_p0.005.npz smoke.npz v2_p0.003.npz v2_p0.004.npz 
discussion/: 00_brief.md 01_claude.md 01_gemini.md 01_gpt.md 02_gemini.md 02_gpt.md 02_round2_prompt.md 03_gemini.md 03_gpt.md 03_round3_prompt.md 04_gemini.md 04_gpt.md 04_verify_prompt.md 05_preregistration.md 06_gemini.md 06_gpt.md 06_round5_prompt.md 07_conclusion.md 08_gemini.md 08_gpt.md 08_noise_adaptive_prompt.md 09_noise_adaptive_prereg.md 10_discovery_review_prompt.md 10_gemini.md 10_gpt.md 11_confirm_review_prompt.md 11_gemini.md 11_gpt.md 12_addendum_prereg.md 13_noise_adaptive_conclusion.md 14_bposd_compare_prereg.md 15_p0003_large_prereg.md 16_ml_bposd_conclusion.md 17_gemini_sections.tex 17_gpt_sections.tex 17_report_brief.md 18_gemini_factcheck.md 18_gpt_factcheck.md 19_gemini.md 19_gpt.md 19_hardshot_design_prompt.md 20_gemini.md 20_gpt.md 20_hardshot_result_prompt.md 21_hardshot_conclusion.md 22_challenge_check_prompt.md 22_gemini.md 22_gpt.md 23_gemini.md 23_gpt.md 23_loss_design_prompt.md 24_loss_plan.md 25_router_compare_prereg.md 26_router_compare_result.md 27_estimated_priors_prereg.md 28_router_eval_10k.md 29_demo_plan_prompt.md 29_gemini.md 29_gpt.md 30_demo_plan.md 31_gemini.md 31_gpt.md 31_hardware_figures_prompt.md 32_hardware_figures.md 33_reorg_prompt.md SUMMARY.md 
report/: build.log figures report.log report.pdf report.tex sections_gemini_approaches.tex sections_gemini_lessons.tex sections_gpt.tex 
ml_router/: __pycache__ evaluate_router.py fast_bp.py make_routing_data.py README.md requirements.txt result train_router.py 
figures/: 1_accuracy_vs_p.pdf 1_accuracy_vs_p.png 2_speed.pdf 2_speed.png 3_latency_distribution.pdf 3_latency_distribution.png 4_speed_vs_accuracy.pdf 4_speed_vs_accuracy.png 5_hardware.pdf 5_hardware.png 
```

## Key results to feature (all on the same shots, our laptop, MacBook Air M5)
- Gate vs Relay-BP mean time: 2.60x / 1.37x / 1.15x faster at p = 0.003 / 0.004 / 0.005; accuracy statistically
  indistinguishable at 0.004 and 0.005 (PASS at 0.005), 100k-pair run at 0.003 inconclusive (86 vs 74 failures);
  3-8x fewer failures than BP-OSD; p99 latency about equal to Relay-BP (not improved).
- No training, CPU only, +5.5 MB per process. ML attempts (noise detector, hard-shot spotter, Emma's router) did not
  beat simple rules under uniform noise; qubit-loss plan is the next step where ML has a real job.
- Headline figures in figures/: 1_accuracy_vs_p, 2_speed (with speed-up labels), 3_latency_distribution,
  4_speed_vs_accuracy, 5_hardware. Full PDF report in report/report.pdf.

## Questions (concise, under 450 words)
1. Proposed folder layout (tree), including where the decoder, experiments (grouped by study), teammates' work, the AI
   discussion logs, the report, plans (loss, demo) and PROMPTS.md go. What to delete (junk: .DS_Store, .new shell
   history, __pycache__, LaTeX logs).
2. How to keep imports and relative paths working with the least risk.
3. README outline: section titles and what goes in each (intro for non-experts, key concepts, results with which
   figures, how to run, repo map, team/credits). Keep it simple.
