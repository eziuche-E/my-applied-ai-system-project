# Guesswise · System Card and Responsible-AI Reflection

## Purpose and intended use

Guesswise extends the Module 1 **Game Glitch Investigator: The Impossible Guesser** into an interactive probability-learning system. Its player-facing goal is to explain the chance of a correct next guess, the chance of winning within the remaining attempts, and a strategy appropriate to the current public game history. It is intended for education and portfolio demonstration, not betting, high-stakes decisions, or adversarial competition.

## System type and capabilities

The coach is a **local symbolic reasoning agent**: English intent routing → public-state retrieval → local document retrieval → exact probability tool → midpoint/what-if planner → output verification → source-grounded response template. It uses no trained model, hosted model endpoint, fine-tuning dataset, embeddings, or API key. The word “AI” here refers to constrained reasoning and tool orchestration, with deterministic behavior on the same inputs.

The three custom references cover probability, binary-search strategy, and game rules. Retrieval ranks the routed topic first, then related-topic boosts and lexical overlap. Actual retrieved passages form part of each supported answer. A verification failure or missing required reference yields a safe error instead of fabricated advice.

## Data, assumptions, and access boundaries

- The secret is sampled uniformly within each round's displayed inclusive range.
- Guess histories contain only accepted integer guesses and truthful comparison outcomes.
- The coach receives a `PublicGame` snapshot with range, attempt limit, history, and status. There is no secret field.
- An optimal-play probability assumes the player follows an optimal policy in future moves. It is not a personalized forecast.
- There is no automatic win for merely identifying a number after attempts run out; the correct number must be submitted while a try remains.
- Evidence consists of synthetic public snapshots, actual automated runs, and agent tool-event summaries. No personal dataset or human study was collected.

## What are the limitations or biases?

1. **Uniform-prior bias:** `1/N` assumes all remaining candidates are equally likely. It would be wrong for a biased secret generator or misleading hints. Those variants are outside this version's rules.
2. **Policy dependence:** best-play odds describe an optimal strategy, while the blind-policy comparison ignores future hints. Neither describes every human play style.
3. **Language coverage:** the router supports a bounded English vocabulary with a few common spelling variants, not general language understanding. Ambiguous or unrelated requests can be refused or routed poorly.
4. **Retrieval limits:** three authored local documents are inspectable but narrow. Lexical retrieval can miss paraphrases, and stale documents could contradict future code changes. Source citation does not itself establish truth.
5. **Templated explanations:** advice is detailed and repeatable but can be repetitive. No LLM or fine-tuning performance is implied.
6. **Random difficulty:** 3–9 attempts and 20–200 candidates sometimes produce rounds with very low success odds. The UI reports this rather than silently guaranteeing a win.
7. **Deployment limits:** state and scores are per Streamlit browser session. This is not an authenticated multiplayer service; the code owner can inspect the game state. The public-data boundary protects coach behavior, not a hostile server administrator.
8. **Accessibility and generalization:** automated desktop/mobile checks are recorded, but no assistive-technology audit, classroom user study, non-English study, or deployment load test has been performed. The dependency lock was verified on Python 3.12/Linux.

## Could the AI be misused, and how is that prevented?

A player could ask for the secret, try to bypass the coach's scope, or present its percentages as guarantees. The question guardrail refuses explicit secret requests; more fundamentally, none of the coach's tools receive the private secret. Answers state assumptions, distinguish immediate and multi-try odds, and avoid a success guarantee when coverage is incomplete. Invalid, duplicate, or ruled-out guesses consume no tries; output checks reject impossible probabilities and invalid recommendations.

The human remains in the loop: a recommendation can populate the input but cannot automatically submit. A snapshot identifier prevents an old recommendation from being applied after the history changes. This is educational probability guidance, not a prediction tool for financial or gambling decisions.

Raw questions are excluded from disk telemetry. The optional downloadable evidence includes questions and public tool results, so users should avoid personal data and review an export before sharing. There is no remote analytics or model-provider transmission in the implemented workflow; Streamlit usage telemetry is disabled in the repository configuration.

## Reliability testing and measured results

The recorded environment uses Python 3.12 with [requirements-lock.txt](requirements-lock.txt). A separate fresh virtual environment was installed from that lock and used to rerun the same checks.

| Check | Result | Evidence |
|---|---|---|
| Unit, guardrail, retrieval, and Streamlit interaction tests | 64 passed | [pytest output](assets/evidence/pytest-output.txt) |
| Predefined-input evaluator and mathematical crosschecks | 15/15 passed; 0 failed | [evaluation output](assets/evidence/evaluation-output.txt) |
| Midpoint success coverage | 1,800 size/try combinations; 180,900 secrets; 0 mismatches | [structured report](assets/evaluation.json) |
| Optimality crosscheck | All next moves considered for 144 small size/try combinations; 0 mismatches | [evaluate.py](evaluate.py) |
| Browser workflow | Odds, invalid input, human-approved suggestion, feedback, stale-action removal, reset, typed chat, narrow viewport | [browser checks](assets/evidence/browser-checks.json) |
| Hidden-secret isolation | Different secrets, identical public inputs → identical coach replies and active-game content | [coach tests](tests/test_coach.py), [UI tests](tests/test_app.py) |
| Retrieval integration | Replacing a retrieved passage changes the displayed answer | [coach tests](tests/test_coach.py) |
| Corrupted tool output | A fabricated 100% probability is rejected before advice is rendered | [coach tests](tests/test_coach.py) |

These counts refer to automated tests and simulations, not human-rated accuracy. They establish behavior for the tested cases and mathematical model, not general intelligence or universal safety.

### Baseline versus specialized local behavior

The baseline is explicitly a simple static rule: **always suggest 50 and report 1% next-guess odds**. It is not another model. This comparison measures whether the implemented game-specific reasoning adapts to current data; it is not a fine-tuning study.

| Public input | Static baseline | Context-aware coach |
|---|---|---|
| 1–100, 3 tries, no hints | Guess 50; 1% next chance | Guess 50; 1% next chance; 7% best-play win chance |
| 1–100, 5-try round; 50 Too Low, 75 Too High | Guess 50 (ruled out); 1% | Guess 62; 24 candidates, 3 tries; 4.17% next; 29.17% best-play |
| 10–29, 3-try round; 15 Too Low, 23 Too High | Guess 50 (outside range); 1% | Guess 19; 7 candidates, 1 try; 14.29% next and best-play |

Measured summary: baseline feasible recommendations **1/3**, correct next-guess odds **1/3**; context-aware coach **3/3** for both. Full current-run data is in `baseline_comparison` in [assets/evaluation.json](assets/evaluation.json).

### Retrieval's contribution

Before retrieval, a bare arithmetic answer can say “7%” without explaining what that means. The integrated answer combines live calculations with an actual retrieved decision-tree explanation and a cited strategy reference. The probability and strategy sources clarify that a midpoint improves future information rather than the immediate `1/N` chance. This qualitative benefit is documented; no human-measured quality improvement is claimed. Retrieval-content changes and missing-reference errors are tested directly.

## What surprised you while testing reliability?

An important counterintuitive result from the automated runs is that a game with 100 candidates and three tries has **1% next-guess odds but 7% optimal-play success odds**, not 3%. Higher/lower hints create two adaptive search branches. A second edge case leaves only one candidate after the last incorrect submission: knowing the answer still does not win when no tries remain.

Testing also exposed a problem in the first secrecy test itself: searching for the digits of the secret matched a CSS color. The revised test compares rendered active-game content across two different hidden secrets, holding the public input constant. That tests the intended information boundary without confusing static styles with a secret leak.

These are observations from AI-assisted automated testing. **The student should review this section and add their own personal reaction after playing; no personal reaction or manual validation is being invented here.**

## Collaboration with AI: accepted and revised suggestions

### Recorded collaboration

The student supplied the assignment, chose the previous game, created the dedicated repository, and asked for a side-by-side coach that retrieves the number of remaining guesses, explains probability, and provides a strategy. They explicitly authorized implementation and useful supporting improvements. The AI assistant implemented the game engine, public-state boundary, retrieval notes, probability/planning tools, UI, guardrails, evaluation harness, and documentation, and ran the recorded automated checks.

### Accepted direction

The assistant initially suggested extending the number-guessing project with an **integrated AI Guessing Coach** that explains recommendations without reading the hidden number. The student continued with that direction and explicitly requested implementing the coach beside the game. Input guardrails, inspectable sources, and an evaluator support that goal.

### A suggestion or assumption revised

The initial coaching proposal built on the original game's difficulty-based settings. The student revised that scope by requesting **random attempt limits and a randomly changing range for every game**, plus a live probability explanation. The implementation therefore removes the fixed-difficulty UI and computes advice from each actual randomized snapshot. This revision makes a static “1 out of 100” answer inappropriate and is checked by the randomized-round and live-history tests.

A further implementation revision during AI-assisted work replaced the brittle secret-digit assertion with the differential secrecy check described above. It was a test-quality correction, not evidence that the student personally ran or authored that test.

### Student review before submission

This section records what can be established from the conversation and executed tools. The student should verify that the accepted/revised direction accurately reflects their choices, add their own observations from playing and reviewing the code, and be prepared to explain the probability formula. Do not submit AI-authored statements as a claim of personal testing that did not happen.

## Future improvements

- Expand question paraphrases and evaluate routing on a held-out set of real player questions.
- Offer an optional language-model presentation layer while allowing only verified structured numeric facts into its response.
- Add accessible nonvisual feedback and review with keyboard/screen-reader users.
- Explore non-uniform priors as a separate game mode with different probability calculations.
- Run classroom human evaluation and record criteria/results in structured tables.
- Add automated checks for consistency between knowledge documents and rule changes.
