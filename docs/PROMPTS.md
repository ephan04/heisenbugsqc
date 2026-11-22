# Prompts used in this project

## 1. Prompts to Claude (Claude Code session, verbatim, times in UTC)

1. `2026-11-21 20:01`: look through this : https://github.com/Infleqtion/MidQWest-2026
2. `2026-11-21 20:08`: explain to me the options more simply
3. `2026-11-21 20:11`: check if you have access to gpt and agy
4. `2026-11-21 20:18`: explain in a very simple version what challange 1 is asking of us
5. `2026-11-21 20:24`: okay from this, build upon it and explain it a little more complex
6. `2026-11-21 20:31`: This is the repo: https://github.com/Infleqtion/MidQWest-2026, using this example, point out files that relate to topics
7. `2026-11-21 20:36`: when you say small fast ai model, do you mean like qwen 3.5B small or anthropic sonnet 4.0 small
8. `2026-11-21 20:43`: is the gross code that we are improving opun?
9. `2026-11-21 20:46`: what does it mean for 144 qubits to store 12
10. `2026-11-21 20:51`: so we have 144 bits where each one is a 111 or 000
11. `2026-11-21 20:51`: we have 144 digits that can be 111 or 000 that are in sequence
12. `2026-11-21 21:16`: looking at the repo, what does the test_kit.py do?
13. `2026-11-21 21:17`: it allows me to type, d oi need to type anything?
14. `2026-11-21 21:45`: explain to me again what the idea is for challenge 1
15. `2026-11-21 22:22`: Okay, so the appraoch my team is having is kinda like this paper (https://arxiv.org/html/2611.16271v1), having a 'light' decoder to go through the code and remove any quick and easy errors, and then haveing a ml route the more complicated errors into another decoder, if a heavyier error, go to something more accurate but not as fast, if the error is slightly more difficult then it goes to a faster decoder with slightyly lower accuracy
16. `2026-11-21 22:28`: Is there a better decoder than the ones they mentioned in the repo?
17. `2026-11-21 22:30`: Have a conversation with gpt and gemini and talk about the appraoch, what would be the best method, and how you all would go about it and try a exmple, you 3 have freedome in this flder
18. `2026-11-21 23:46`: Double check this and run with different shots and noise levels to make sure that this approach is effective. Discuss with gpt and gemini
19. `2026-11-22 00:21`: what are seeds here?
20. `2026-11-22 00:22`: where does the random number come from
21. `2026-11-22 00:24`: Create a sinlge page infographic explaining whats happening here
22. `2026-11-22 00:33`: what do you mean by 'skip' version?
23. `2026-11-22 00:34`: what is the reason that the router is slower on the slowest shots?
24. `2026-11-22 00:35`: What about the next slowest? How much slower compared to the baseline are those?
25. `2026-11-22 00:38`: Okat from here, what is the next step
26. `2026-11-22 00:41`: I like that but I want to think about addressing and solving the higher noise levels
27. `2026-11-22 00:43`: can you detect the noise level
28. `2026-11-22 00:47`: DO NOT START ANYTHING WITH THE ML. I want you to try this approach with different shots and noise levels that will provide valuable data. Talk with ChatGPT and Gemini and think about what data values are good to test. Run those tests. Ands just to reiterate, when there is a alarm, the ml model detects the noise level and applies its effect depending on that
29. `2026-11-22 03:10`: what is k
30. `2026-11-22 03:11`: and what data are you working off of here?
31. `2026-11-22 03:12`: have you seen the repo? In the file? Theres files in there taht you can run at different parameters and get data from, just look and tell me what you think
32. `2026-11-22 03:13`: how long will that take
33. `2026-11-22 03:21`: Why is it less accurate for lower noises?
34. `2026-11-22 03:27`: push to repo
35. `2026-11-22 03:29`: push everything(everythin), crete a file with all the prompts used in this chate as well
36. `2026-11-22 03:30`: So if you build the ML model, thats light, we're all good?
37. `2026-11-22 03:31`: is there any parallel computation that we could offsource to another computer?
38. `2026-11-22 03:33`: how much time would it take to make the ML
39. `2026-11-22 03:34`: can you build it and to some quick tests to see if its viable?
40. `2026-11-22 03:42`: so ML isn't needed. What is left? Just running on the BPOSD?
41. `2026-11-22 03:45`: if we did the preshot version, would it still be 6 hrs?
42. `2026-11-22 03:50`: run the alarm counting model on the BPOSD and run the ML-assited model on a subset of BPOSD
43. `2026-11-22 04:36`: how long will it take to do the lower values of relay bp
44. `2026-11-22 04:37`: just do 0.003
45. `2026-11-22 05:04`: push to repo
46. `2026-11-22 05:05`: create a thourough report and explenation of everything that we've done here, from the problem, the pre-reqs, what approaches we thought of, and where we are right now with figures. have gpt and agy help you write it. as a pdf
47. `2026-11-22 05:23`: whats the hardware cost?
48. `2026-11-22 05:27`: how light is this in comparision to what the repo mentioens
49. `2026-11-22 05:30`: What was the approach for ML that you recommanded?
50. `2026-11-22 05:31`: how long would this take
51. `2026-11-22 05:31`: apply a and work through it with gpt and gagy
52. `2026-11-22 05:39`: so is there any space where ML can help out?
53. `2026-11-22 05:44`: i want you 3 to look at the challaneg what we are solving (challenge 1) and check that this approach satisfies it
54. `2026-11-22 05:49`: i want you 3 to think about how to appraoch teh loss simulation appraoch and how you can fo it
55. `2026-11-22 09:06`: where does https://github.com/ephan04/heisenbugsqc/tree/ml-router ran in the work you've done?
56. `2026-11-22 09:09`: go for it
57. `2026-11-22 09:10`: can you just do 0.003
58. `2026-11-22 09:23`: so can what we have work out of the gate with no AI and ML?
59. `2026-11-22 09:24`: What about detecting the noise level? Does the program do that itself as well?
60. `2026-11-22 13:37`: okay start running
61. `2026-11-22 13:50`: stop this run
62. `2026-11-22 13:51`: look at emmas repo and run her model with p = 0.003,0.004, 0.005 at 10k shots
63. `2026-11-22 15:16`: can you push the data
64. `2026-11-22 15:32`: we want to do a live demo of what was made, not emmas ML. I want you 3 too come up a plan for a quick live demonstartion that once completed, shows the data on a graph comparing the data that they provided and our output, copmaring speed and accuracy, the figure can have 2 graphs for each run, if possible, try to see if you can create a live graph that is updated and geerated as ran. don't build come back with a plan
65. `2026-11-22 15:44`: u 3, pull al the data and metrics and present the hardware facts and then give me some figures
66. `2026-11-22 15:52`: for 2, how long would it take to create the data to fill in the solid orange bar>
67. `2026-11-22 15:55`: can you add scaling factors to image 2 to show the improvement that our gate approahc had
68. `2026-11-22 16:06`: Okay we are done here, I want you to look at the current repo, https://github.com/ephan04/heisenbugsqc, pull everything thats on it, and then prganize the whole thing and push the new repo, Work along with the other 2. it should be well orgnaized, titled, and the read me should be simple with figures and concepts, a good intro. Then before you push it, show it to me locally

## 2. Prompts Claude sent to GPT (codex) and Gemini (agy)

Each round's prompt is a file in `docs/discussion/`, and each reply sits next to it (`*_gpt.md`, `*_gemini.md`).
The `docs/discussion/.gemini_prompt*.txt` files hold the exact text sent to Gemini in rounds 1-4, with the files pasted in, because Gemini could not read files itself.

- `docs/discussion/02_round2_prompt.md`
- `docs/discussion/03_round3_prompt.md`
- `docs/discussion/04_verify_prompt.md`
- `docs/discussion/06_round5_prompt.md`
- `docs/discussion/08_noise_adaptive_prompt.md`
- `docs/discussion/10_discovery_review_prompt.md`
- `docs/discussion/11_confirm_review_prompt.md`
- `docs/discussion/00_brief.md`
- `docs/discussion/17_report_brief.md`
- `docs/discussion/19_hardshot_design_prompt.md`
- `docs/discussion/20_hardshot_result_prompt.md`
- `docs/discussion/22_challenge_check_prompt.md`
- `docs/discussion/23_loss_design_prompt.md`
- `docs/discussion/29_demo_plan_prompt.md`
- `docs/discussion/31_hardware_figures_prompt.md`
- `docs/discussion/33_reorg_prompt.md`
