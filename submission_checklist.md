# Project 4 · Submission and Stretch Evidence

This checklist records observable artifacts, not an awarded grade. Course reviewers determine credit, including whether the local symbolic retrieval/planning implementation satisfies their interpretation of AI and RAG.

## Required submission artifacts

| Requirement | Current evidence | Status |
|---|---|---|
| Correct GitHub repository | [eziuche-E/my-applied-ai-system-project](https://github.com/eziuche-E/my-applied-ai-system-project) | Code, evidence, and presentation documents committed and pushed to `main`. |
| Public repository | GitHub repository-page metadata reports `repository_public=true` | Verified during development; keep visibility public. |
| Runnable code | `app.py`, `demo.py`, pinned requirements, documented startup steps | Automated CLI and browser runs verified. |
| Base project identified | README base-project section with original name, link, scope, and extension | Present. |
| Mermaid source in `diagrams/` | `diagrams/architecture.mmd` | Present; diagram and README overview parsed with Mermaid 11.12.1. |
| Comprehensive README | Setup, architecture, trade-offs, five sample interactions, guardrail examples, evaluation commands | Present. |
| Responsible-AI reflection | `model_card.md` covers limitations, bias, misuse, testing observations, and accepted/revised direction | Present; student must review and personalize the marked sections. |
| Reproducible evidence | `assets/evidence/*.txt`, `assets/evaluation.json`, browser check JSON | Committed actual outputs and tool results. |
| At least 2–3 example inputs/outputs | Five fenced examples in README; full CLI output linked | Present. |
| Multiple meaningful commits | Preparation, core system, evaluation harness, documentation/evidence | Preserved with original project history. |
| Presentation | `presentation.md` with timed 6½-minute outline and demo commands | Guide prepared; rehearsal and delivery remain. |
| Portfolio artifact | `portfolio.md` with code link, summary, evidence, and reflection draft | Prepared; student must review the personal paragraph. |
| Optional Loom video | No recording provided | Optional; add a real link only after recording. |
| Deadline and course submission | Not specified or performed in this repository | Student must confirm the deadline and submit through the course system. |

## Optional stretch features: evidence and limits

| Stretch feature | Evidence | Claim supported by the implementation |
|---|---|---|
| Custom or multi-source retrieval (+2 possible) | Three authored files in `knowledge/`; topic + companion retrieval in `retriever.py`; actual retrieved passages in coach answers; retrieval contribution in `model_card.md` | Custom local retrieval is implemented and integrated. It uses lexical retrieval and templated responses, with no language-model generation. |
| Agentic workflow (+2 possible) | `coach.py` orchestrates public-state reading, retrieval, exact math, conditional next-move planning, and verification; `ai_interactions.md` links committed `interactions[].trace` records | A multi-step local tool workflow and decision-dependent plan are implemented; intermediate observable tool events are retained. |
| Fine-tuning or model specialization (+2 possible) | A static baseline comparison documents context adaptation, but there is no trained model, few-shot model prompting, or fine-tuning run | **Not claimed.** A specialized rule/template system and a static baseline comparison do not establish specialized model behavior. |
| Evaluation harness (+2 possible) | `evaluate.py` runs predefined questions plus simulations and prints `15/15 passed; 0 failed`; actual output and JSON report are committed | The runnable evaluation script and its pass/fail summary are implemented. |

The project supplies evidence relevant to **three stretch categories, worth up to +6 if accepted by the grader**. It does not claim all +8 points. The static baseline in the system card is a comparison policy, not an experiment with two language models.

## Student's final actions

- [ ] Play the app and review the mathematics and limitations so you can explain them.
- [ ] Personalize the marked observations and collaboration reflection in `model_card.md` without inventing experiences.
- [ ] Review the portfolio paragraph in your own voice.
- [ ] Rehearse and deliver the 5–7 minute presentation.
- [ ] If recording a Loom, add its actual link to the README; no video is required for text-based grading.
- [ ] Confirm the repository remains public and final work is pushed before the actual course deadline.
- [ ] Submit the public repository URL through the course's required submission process.
