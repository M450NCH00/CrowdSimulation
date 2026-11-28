# RF-43: whose left and right? Frames of reference in LLMs and in people, and what fixes the confusion

Issue #132, track #55. Literature only: no model call, no template, no code, USD 0. Written on 2026-11-25.

This answers the supervisor's point 2 of November 2026 (SV8 in `llm_negotiation/docs/architecture.md`, section 8.8). DeepSeek mistakes the other person's left and right for its own, even when told that the two face each other. It comes before the fixes are built: RF-47 (a menu in words), RF-48 (an absolute frame), RF-50 and RF-51 (a grid).

| File | What it holds |
| --- | --- |
| this README | the sources (section 1), answers to the issue's questions 1 to 4 (sections 2 to 5), the recommendation for AS5 (section 6), limits (section 7) |
| [`probes.md`](probes.md) | task 4 (optional, **not run**): 20 static prompts that test the conversion alone |
| `refs/rf43_excerpts.txt` | every passage cited here, with its line number in the full text extract |
| `WORK_LOG-132.md` | the search terms, what could not be reached, and the process |

**How to read the citations.** `[file:line]` points to a line of the text extract. Excerpts are in `refs/rf43_excerpts.txt` under that file name and line. Van der Ham et al. is tracked in full as `refs/rf43_vanderham2021.txt`. Other claims are marked:
- `[secondary]`: taken from another paper's account of a source I could not open;
- `[inference]`: my reasoning, not a source's finding;
- `[unverified]`: not checked against a source.

**The problem in RF-40's numbers** (`llm_negotiation/runs/rf40_round1_head_on_turn_taking/comparison_report.md`, "In short" and section 5):
- **E1, the speaker converts.** "I'll keep to my left" (the speaker's own frame) matched the speaker's own move in 44 of 46. "Coming through on your right" (the listener's frame) matched in only 11 of 27.
- **E2, the listener converts.** Of 100 heard side messages where both people moved aside, the listener's move made room in 35 (p = 0.004 against a coin). For own-frame messages it made room in 14 of 42, and for listener-frame messages in 12 of 44.
- **E3, the listener restates the side and still goes wrong.** 44 listener replies restated the side in the other's frame; 18 of them fitted. In some, the facing note of `resolve_v9` was applied to words that were already in the listener's own frame. The note reads: "Person N is facing you: their left is your right, and their right is your left" (`llm_negotiation/negsim/negotiation/templates/resolve_v9.yaml:216`).

## 1. Sources

One row per source. "Text" means the model read a text description; "image" means a picture.

| Source | What was tested | Models | Result (numbers as printed) | Where |
| --- | --- | --- | --- | --- |
| **Jiang, Qin & Li 2026**, *SpatialText* (arXiv 2603.03002v1, preprint) | Text only, 485 questions on 100 to 105 real indoor scenes, in egocentric, allocentric and hybrid descriptions. Type III is "perspective transformation" (observer moves; switching reference systems). Temperature 0, with a "think step by step" system prompt | 7B to 14B open models; DeepSeek-V3.2 as the large reference | Type III accuracy: **DeepSeek-V3.2 86.32** (allocentric 92.59, hybrid 80.95). Others: Qwen3-8B 62.39, OpenPangu-7B 65.81, Gemma-2-9B 59.83, Gemma-3-12B 54.70, DeepSeek-R1-Distill-Llama-8B 39.32, Qwen2.5-7B 34.19, Mistral-7B 30.77. Every model scores lower on hybrid than on allocentric descriptions (DeepSeek-V3.2: 76.44 against 88.74). Errors pair "Left" with "West" instead of rotating | Table 3 `[rf43_spatialtext2026.txt:408-414]`; text `[:487-493]`, `[:567-578]` |
| **Premsri & Kordjamshidi 2025**, *FoREST* (arXiv 2502.17775v3) | Text only. Which frame a sentence uses, and converting between frames. The C-split states both the frame of the context and the frame of the question. Prompts: 0-shot, 4-shot, CoT, and SG+CoT (Spatial-Guided: first extract the frame, then reason). Temperature 0 | Llama3-70B, Qwen2-72B, Qwen2VL-72B, GPT-4o | Context from the camera, question from the object's own view (a conversion): at most **55.5%** (Llama3-70B, CoT); **GPT-4o, CoT: 53.0%**. The reverse conversion reaches 82.4% (GPT-4o). Llama3-70B "systematically reverses left and right". SG helps identify the frame (+2.9 to +30 points where context and question share it) but "does not enhance reasoning across perspectives" | Table 3 `[rf43_forest2025.txt:531-549]`; text `[:654-692]`, `[:708-726]` |
| **Sidhu & Hockenmaier 2026**, *Grid Spatial Understanding* (GSU, arXiv 2603.17333v1, preprint) | Text-only grids. "Instructor" turns coordinates into moves, either in a fixed **Cardinal** frame or in an **Egocentric** frame that turns with the walker. "Card2Ego" translates north, south, east and west into left, right, forward and back. 1-shot prompting with a worked reasoning example | 14 prompted LLMs and VLMs (7B to 72B, GPT-4o, Gemini-3-Pro) and 2 fine-tuned small models | Instructor, Cardinal against Egocentric: GPT-4o **0.89 against 0.67**, Qwen-72b **1.0 against 0.47**, Llama-70b 0.26 against 0.09, Mistral-7b 0.59 against 0.15. The fixed frame is easier in 12 of the 14 prompted models; Gemini-3-Pro ties at 1.0, QwenVL-32b is the exception (0.12 against 0.17). Card2Ego: GPT-4o 0.93, Qwen-72b 0.53, Llama-70b 0.1. Gemini-3-Pro scores 1.0 throughout. Models "forget" an updated heading and fall back to the default one | Table 1 `[rf43_gridspatial2026.txt:384-404]`; text `[:488-533]`, `[:555-580]` |
| **Cohn & Blackwell 2025**, cardinal directions revisited (arXiv 2507.12059v2) | Text only, 5,760 questions: which compass direction, for an agent moving along or around a lake, island, park or road. Varies the person ("I", "you", "he", …) and the means of moving. 0-shot, temperature 0 where it can be set; 8 answers, so a guess scores 0.125 | 28 models, including deepseek-chat and deepseek-reasoner (2025 versions, not stated more exactly) | **deepseek-reasoner 0.84, deepseek-chat 0.48**; o1 0.92 (best). "Striking how much better Deepseek-reasoner is compared to the base model". The person form makes little difference for the top models. DeepSeek R1's median reply took 34 s | Figure 1 (values read from the rendered page; the extract separates labels from values) `[rf43_cohn2025_cardinal.txt:221-235]`, `[:446-452]`, `[:627-632]` |
| **Wu et al. 2024**, Visualization-of-Thought (VoT; arXiv 2404.03622, NeurIPS 2024) | Text grids: navigation in words, visual navigation, tiling. VoT ("Visualize the state after each reasoning step") against CoT | GPT-4 | VoT against CoT: route success 14.72 against 9.48; next step 55.28 against 48.61; tiling 63.94 against 54.15; navigation in words 59.00 against 54.00 (p < 0.16, not significant) | Table 1 `[rf43_vot2024.txt:310-323]` |
| **Leonard, Woodard & Murray 2024** (arXiv 2409.13929v1, workshop preprint) | **Images**: is a cube to the avatar's left or right, at 8 angles. 10 runs per image. One CoT prompt states the rule: "if the person is facing the camera … the cube is to the inverse of the camera's left or right" | GPT-4o | Fails once the rotation reaches about 90°. Stating the rule fixes **180° only**, not 90° to 135°. Numbers only in Figures 3 and 4 (not read off) | `[rf43_leonard2024_vpt.txt:122-130]`, `[:150-160]` |
| **Zhang et al. 2025**, *COMFORT* (ICLR 2025; arXiv 2410.17385v2) | Images, in 109 languages: frame ambiguity. Its background section summarises Levinson 2003 | 9 VLMs | VLMs follow English conventions, "lack the flexibility to accommodate multiple FoRs", and ignore other languages' conventions. Background: three frames (absolute, intrinsic, relative). English prefers the speaker's relative frame when none is stated. English reflects only front and back | Abstract `[rf43_comfort2024.txt:12-26]`; background `[:125-160]` |
| **Tversky & Hard 2009**, *Cognition* 110, 124–129 | **People** (students; Study 1 n = 190; Study 2 about 154, from its F(1,150)). A photo shows a bottle and a book, with or without a person behind the table facing the viewer. Question: "where is the book?" | — | With a person in the photo, **about 25%** described from that person's view (3% with no person). With an action question, **about 50%** took the other's view and about 20% their own. **Only 13% (Study 1) and 21% (Study 2) said whose left they meant** | `[rf43_tversky_hard2009.txt:180-215]`, `[:362-372]`, `[:392-400]` |
| **van der Ham, Dijkerman & van Stralen 2021**, *QJEP* 74(3), 497–509 (CC BY 4.0) | **People.** Exp. 1: self-rating out of 10 (n = 404). Exp. 2: naming the hand of a drawn figure seen from the front (mirrored) or from the back (n = 229) | — | Rated their own left and right 5 or less: **14.6%**. Rated it 5 or less "from the perspective of a person sitting in front of them, facing them": **28.7%**. Accuracy for the figure from the front: 87.3 to 92.1%; from the back: 88.8 to 96.0% (main effect of side, p < .001). Wolf 1973 `[secondary]`: 17.5% of women and 8.8% of men report frequent problems | `refs/rf43_vanderham2021.txt:36-44`, `:196-237`, Table 4 `:593-603` |
| **Gormley, Dempster & Best 2008**, *BMJ* 337:a2826 | **People** (290 medical students), Bergen right-left test: 48 figures a section, 90 s a section | — | Mean correct out of 48: **back view 41.55, front view 37.36**, mixed 33.69. Each difference p < 0.001 | `[rf43_bmj2008_lrd.txt:196-230]` |
| **Siebinga 2024**, "A Model of the Sidewalk Salsa" (arXiv 2412.04023) | **A model, not observation:** two pedestrians head-on, each believing which side the other will take. 100 runs a scenario | — | Pavement dances in 100 runs: symmetric 6; **same side bias 3; opposite side biases 26** (25 collisions). The author notes that people break a dance with gestures or speech ("After you!"); this is not modelled | Table II `[rf43_siebinga2024_salsa.txt:519-525]`; text `[:488-517]` |
| Martorell 2025, via #52 (`literature/environment-description/findings.md:90-93`) | Text, a 5×5 grid in six encodings | 1B to 90B | 66% success with JSON coordinates against 30% with the best drawn grid | already reviewed in #52 |

**Not reached** (all tried, and blocked by a bot check, a 403 error or a cookie wall; see the work log):
- **Levinson 2003** (book) and **Majid et al. 2004** (*TiCS* 8(3), 108–114): cited only through COMFORT `[secondary]`.
- **Schober 1993** (*Cognition* 47, 1–24): cited only through Tversky & Hard `[secondary]`.
- **Hill 1982**: cited only through FoREST `[secondary]`.

A reader with library access can fetch them in a browser in minutes.

## 2. Question 1: is converting another person's left and right a known weakness of LLMs?

**Yes.** Every study found fails at the same step: turning a side seen in one frame into another frame.

- **The size of the failure.** FoREST's text-only conversion from the viewer's frame to the object's own frame peaks at 55.5%, and GPT-4o with CoT reaches 53.0% (Table 3). That is about one answer in two, close to RF-40's E1 (11 of 27) and E2 (35 of 100). The reverse conversion, into the viewer's frame, is easier (up to 82.4%).
- **The error is specifically left and right.** Llama3-70B "systematically reverses left and right" (FoREST, Figure 3 and text). People, by contrast, in English tend to reverse front and back and keep the sides (Hill 1982 `[secondary]`).
- **Fixed frames are easier than frames that turn with a person.** In GSU, producing moves in a fixed (cardinal) frame beats producing them in the walker's own frame in 12 of 14 prompted models (one tie, one exception). Even a pure word translation from compass to left and right (Card2Ego) is weak for most of them (Llama-70b 0.1, Qwen-72b 0.53).
- **Failures look like a default frame showing through.** Models state the correct heading, then conclude as if they faced the default way. They "forget" an updated heading. GSU's example: "-X is to my right, so x values smaller than me are to my left". SpatialText's version is the "Left = West" association. RF-40's agents fit this: their own frame is right 44 of 46 times, and the other frame shows through when they convert `[inference]`.
- **The listener's error E3 is a frame-identification failure.** FoREST finds that Qwen2 often ignores the perspective a question states and answers from the context's frame (attention analysis, Appendix D; `[rf43_forest2025.txt:615-623]`). In E3 the note "their left is your right" was applied to words already in the listener's frame. That is a failure to identify the frame the words were in, before any conversion `[inference]`.

**What it depends on:**
- **Model size and generation.** SpatialText's Type III rises from 31 to 34% (Mistral-7B, Qwen2.5-7B) to 86% (DeepSeek-V3.2). In GSU, only Gemini-3-Pro solves everything.
- **Reasoning ("thinking") mode.** For DeepSeek in particular, Cohn & Blackwell measured **deepseek-reasoner 0.84 against deepseek-chat 0.48** on the same 5,760 questions. That is cardinal directions, not left and right between two people. A small model distilled from reasoning traces is weak (SpatialText: R1-Distill-Llama-8B 39% on Type III). CoT can shift a model's frame preference: GPT-4o turned towards the object's own frame under CoT, and its camera-frame accuracy fell (FoREST, A-split; `[rf43_forest2025.txt:624-628]`).
- **Wording.** For the strongest models, the grammatical person ("I", "you", "she") matters little (Cohn & Blackwell, `[rf43_cohn2025_cardinal.txt:456-460]`). How the frame is stated matters more: hybrid descriptions, mixing compass words with relative ones, are below allocentric ones for every SpatialText model.

## 3. Question 2: which fixes were measured for LLMs, and by how much?

| Fix | Measured? | Effect | Source |
| --- | --- | --- | --- |
| **Absolute or allocentric description** (compass, fixed axes) | Yes, as a frame comparison, not as an added fix | A fixed frame beats a body frame when producing moves: GPT-4o 0.89 against 0.67, Qwen-72b 1.0 against 0.47 (GSU). Allocentric descriptions score above hybrid ones (SpatialText; different questions, so not a paired test). **But** compass reasoning that needs inference is itself weak for non-reasoning models: deepseek-chat 0.48 (Cohn & Blackwell) | GSU Table 1; SpatialText Table 3; Cohn Figure 1 |
| **Grid** | Yes | VoT on grids: +5 to +10 points over CoT for GPT-4 (route success 9.48 to 14.72). JSON coordinates beat a drawn grid, 66% against 30% (Martorell, via #52). A fixed-frame grid is easy for large models (GSU). A grid where the walker turns is not (GSU Egocentric) | VoT Table 1; #52; GSU |
| **Stating the transformation** (a rule such as "facing you, their left is your right") | Partly | Fixes the 180° case for GPT-4o on images, and nothing in between (Leonard et al., Figure 4; no number in the text). FoREST's SG (state the frame first) improves frame identification, not conversion. RF-40 had the note on every heard message, so it cannot say whether the note helped | Leonard `[:150-160]`; FoREST `[:708-726]`; RF-40 report section 5 |
| **Worked examples** | Yes | Mixed: 4-shot lowered GPT-4o from 95.6 to 81.5 on FoREST's A-split; 1-shot with a full worked trace was GSU's best setting (its Tables 9 and 15, not cached here `[unverified]`) | FoREST Table 2; GSU `[:296-303]` |
| **Asking the model to restate the side in its own frame** | **Could not find** a study | RF-40's agents did this unprompted: 18 of 44 restatements fitted, about the same as all heard messages (35 of 100) | RF-40 report section 5 |
| **Leaving the conversion to code** | **Could not find** a direct test | Indirect support only. The step that fails is the conversion: Card2Ego in GSU, and FoREST's 53 to 55%. Code that does it removes the step `[inference]` | — |
| **Reasoning mode** | Yes, for compass directions | deepseek-reasoner 0.84 against deepseek-chat 0.48 | Cohn Figure 1 |

## 4. Question 3: people

- **Frames of reference.** Levinson 2003 names three: **absolute** (fixed bearings such as north and south), **intrinsic** (from an object's or a person's own front), and **relative** (from a viewer). English prefers the speaker's relative frame when none is stated `[secondary: COMFORT, rf43_comfort2024.txt:128-158]`. Languages differ in how a viewer's frame is projected onto another object: English reflects only front and back, Hausa translates it, Tamil rotates it `[secondary]`. The issue's `[to check]` on Levinson 2003 stays open: the book itself was not read.
- **How often people confuse left and right.**
  - Self-report: 14.6% rate themselves 5 or less out of 10 (van der Ham et al., n = 404). For a person sitting in front of them and facing them, it is **28.7%**, about double.
  - Measured: a figure seen from the front (mirrored, like someone walking towards you) is harder than one seen from the back. Van der Ham et al. found about 87 to 92% accuracy against 89 to 96%. Gormley et al. found 37.36 against 41.55 correct out of 48 in a timed test.
  - So people also find a facing person's left and right harder, but they get it right roughly 9 times in 10. RF-40's listeners got it right about 1 time in 3.
- **Which frame people use when speaking about another person's space.** Tversky & Hard found that with a person present, a quarter of describers used that person's left and right. With an action question, half did. Most did not say whose left they meant: 13% did in Study 1 and 21% in Study 2. Speakers also often take an addressee's perspective in conversation (Schober 1993) `[secondary: via Tversky & Hard, rf43_tversky_hard2009.txt:232-237]`. So "on your right", in the listener's frame, is a natural human choice, and an unmarked "on the left" is ambiguous for people too.
- **Pedestrians and cyclists speaking to someone coming the other way: could not find a study.**
  - Searches found only forum posts and opinion pieces about cyclists calling "on your left". That call is made when **overtaking**, where the two people face the same way and the frames coincide `[unverified: forums only]`.
  - No study was found of what pedestrians say in a head-on meeting.
  - Siebinga's model notes that people break a pavement dance "by hand gestures or speech ('After you!')". That is the author's remark, not data.
- **Cultures that describe space with absolute directions.** Majid et al. 2004 compare speakers of Dutch, who mostly use the relative frame, with speakers of Tzeltal, who mostly use the absolute frame, in non-verbal tasks. They argue that language shapes spatial cognition. Some Australian languages are reported to have only the absolute frame (Guugu Yimithirr is the usual example). All of this is `[secondary or unverified]`: the paper was not reached, and the details come from search snippets and COMFORT's citation of it.

## 5. Question 4: for this project

### 5.1 Each RF-40 error, and the fix the literature supports

| RF-40 error | What it is | Supported fix | Strength |
| --- | --- | --- | --- |
| **E1**: the speaker says "on your right" and moves the wrong way (11 of 27 right) | Converting the speaker's own side into the listener's frame | **Do not ask for it.** Have the speaker name its own side ("I'll go to my left"), which was right 44 of 46 times, or a wall. Ask it to mark whose side ("my left"), since even people rarely mark it (Tversky & Hard) | Strong: conversion is the step that fails (FoREST, GSU) |
| **E2**: the listener hears a side and makes room in 35 of 100 | Converting the speaker's frame into its own | **Remove the conversion:** use an absolute frame (walls), so there is nothing to convert (RF-48). Or **let code convert:** the description adds the side in the listener's own frame, e.g. "(Person 1 means their own left: the wall on your right)" | Strong for removing it (GSU fixed frame). Code conversion was not tested in any study; it is an `[inference]` |
| **E3**: the facing note is applied to words already in the listener's frame (18 of 44 restatements fitted) | Identifying which frame the words are in | **Code identifies the frame**, not the agent. A generic note ("their left is your right") makes the agent guess whose frame the words are in. A note written for the message ("they said *your* right: that is your right") does not. FoREST: stating the frame helps identification | Medium: FoREST's SG on identification; RF-40 itself |

### 5.2 Which representations RF-47, RF-48 and RF-50/51 should test

- **RF-47 (a menu in words, own left and right; variant B).** The literature supports own-frame words for an agent's **own** move: RF-40's 44 of 46, and GSU, where a model's own frame is easy until it has to turn. The risk is **talk**. Recommended `[inference]`:
  - the instructions ask a speaker to say "my left" or "my right", never "your";
  - the analysis counts how often it does not;
  - if the user wants the strongest test of the menu alone, run B in silent first (AS2 already runs silent and talk).
- **RF-48 (an absolute frame; variant C).** It has the best support: a fixed frame beats a turning frame (GSU, 12 of 14 models), and it removes E1 to E3 by construction. Two cautions from the sources:
  - models have default headings and "Left = West" associations (GSU, SpatialText). Compass words could be turned back into a body frame by an agent that assumes it faces north;
  - compass inference is weak without reasoning mode (deepseek-chat 0.48).
  
  So the absolute frame should be **simple naming**, not compass reasoning: positions and moves named by the walls, and no heading (as AS5 says). See section 6.
- **RF-50/51 (a grid; variants D and E).** Grids help most when the frame is fixed: GSU's cardinal grids, Martorell's coordinates. A grid with own left and right (D) keeps the body frame, which is GSU's hard case. **E should beat D** if the literature carries over `[inference]`. VoT-style state drawing gave only +5 to +10 points to GPT-4 and is not needed for one-step moves.
- **The expected trap remains.** With absolute walls and no heading, both agents can choose the same wall (AS5's "expected trap"). Siebinga's model suggests that a **shared** side bias cuts pavement dances (3 in 100) and opposite biases multiply them (26 in 100). Removing keep right may remove a shared bias. RF-11 found that 62% of round 1's resolved pairs passed on their right. This is a model result, not data, so RF-49 and RF-52 must measure it.

### 5.3 Is DeepSeek's thinking mode worth a try?

**A small try, yes, but first as a static probe, not a full run.** This is a recommendation.
- **For:** the one DeepSeek-specific comparison found, deepseek-reasoner 0.84 against deepseek-chat 0.48, is large (Cohn & Blackwell). DeepSeek-V3.2 was the strongest model on SpatialText's perspective transformation (86%), with CoT prompted.
- **Against:**
  - the gain was measured on compass questions, not on two people facing each other;
  - CoT can shift a model's frame preference the wrong way (FoREST);
  - RF-28 found that a larger model (v4-pro) did not help round 1;
  - replies are slower (R1: a median of 34 s in 2025, Cohn & Blackwell) and longer, so cost and the 300-token reply cap need checking `[unverified for the current deepseek-flash]`;
  - this repo's configs note that "temperature has no effect in DeepSeek's thinking mode" (`llm_negotiation/configs/experiments/c1_gamechat_replication.yaml:39`, a repo note, not rechecked here). That changes how the noise floor is measured.
- **How:** [`probes.md`](probes.md) gives 20 prompts that isolate the conversion. Run them with thinking off and on (task 4; **not run**).

## 6. Recommendation for RF-42's decisions (AS5): **a recommendation, not a decision**

AS5 is the user's provisional decision of 2026-11-25 (`llm_negotiation/docs/action-space.md`, section 7), to be rechecked after this issue.

1. **Do not tell the agent its heading.** Keep AS5. The literature puts the failure in the conversion between frames (FoREST 53 to 55%; GSU's Card2Ego and its forgotten headings). Telling the heading invites the agent to convert again.
2. **Keep the rest of AS5's structure:**
   - positions measured from one wall;
   - moves named by the walls;
   - the parser converts to left and right for the executor;
   - talk names walls;
   - no facing note.
   
   This is "leave the conversion to code" (section 3), the one fix that removes E1, E2 and E3 together.
3. **The words for the walls: prefer neutral landmark names to compass names**, for example "the window side" and "the shop side", or "wall A" and "wall B".
   - Compass words carry habits that models fall back on: north as straight ahead, the default +Y heading and the "Left = West" association (GSU `[:555-580]`, SpatialText `[:567-578]`). An agent that assumes it faces north turns "the north wall" back into a body side.
   - A landmark name has no such pairing `[inference]`.
   - **Gap:** no study compares compass and landmark names for LLMs. If the user prefers compass names, which are Levinson's absolute frame proper, probes 13 to 16 in `probes.md` test exactly this risk.
4. **Talk in the left-and-right variants (B and D):** speakers name their own side and say so ("my left"). If a facing note is kept, code writes it for the message, giving the side in the listener's frame. It should not be a generic flip rule (E3).

## 7. Limits and open questions

- **Almost no source tests RF-40's situation itself**: two people facing each other, in text, with one telling the other a side. FoREST (objects and a camera) and Leonard et al. (images, an avatar) are the closest. Every carry-over to the corridor is an `[inference]`.
- **Most LLM sources are preprints**: SpatialText, GSU, Leonard et al. and Siebinga. SpatialText's text names a "Qwen-Flash" (0.75, 0.70) that is not in its Table 3, and its Type III has no egocentric questions (Table 2). Its numbers come from one deterministic run each.
- **Model versions drift.** Cohn & Blackwell's deepseek-chat and deepseek-reasoner are 2025 versions. SpatialText's DeepSeek-V3.2 is not the `deepseek-flash` this project runs, and the fingerprint of `deepseek-flash` itself changed between runs (RF-39).
- **People are not like the agents in one respect.** People who face each other get left and right right about 9 times in 10 (van der Ham et al., Gormley et al.). RF-40's agents got it right about 1 time in 3. So "behave like a person" cannot copy a human error rate here: the agents are far worse.
- **The human sources on speaking are about tables and photos** (Tversky & Hard), not walking. No study was found of what pedestrians say in a head-on meeting.
- **Not reached:** Levinson 2003, Majid et al. 2004, Schober 1993, Hill 1982 (`[secondary]` throughout).
- **For the user:**
  - whether to switch AS5 to landmark names (section 6, item 3);
  - whether to run the probe in `probes.md` (paid, small: section 3 there), and with thinking mode on;
  - whether code-written notes for heard messages (section 5.1, E2 and E3) belong in RF-47, which would be a new template version.
