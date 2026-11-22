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

## 2. Prompts Claude sent to GPT (codex) and Gemini (agy)

Each round's prompt is a file in `discussion/`, and each reply sits next to it (`*_gpt.md`, `*_gemini.md`).
The `discussion/.gemini_prompt*.txt` files hold the exact text sent to Gemini in rounds 1-4, with the files pasted in, because Gemini could not read files itself.

- `discussion/02_round2_prompt.md`
- `discussion/03_round3_prompt.md`
- `discussion/04_verify_prompt.md`
- `discussion/06_round5_prompt.md`
- `discussion/08_noise_adaptive_prompt.md`
- `discussion/10_discovery_review_prompt.md`
- `discussion/11_confirm_review_prompt.md`
- `discussion/00_brief.md`
