# Guesswise · Applied AI Portfolio Artifact

**Code:** [github.com/eziuche-E/my-applied-ai-system-project](https://github.com/eziuche-E/my-applied-ai-system-project)  
**Base project:** Game Glitch Investigator: The Impossible Guesser (Module 1)  
**Stack:** Python 3.12, Streamlit, pytest; local lexical retrieval and symbolic reasoning tools

## Project summary

Guesswise turns an earlier number-guessing game into an interactive probability-learning system. Every round randomizes the range and number of attempts. A side-by-side coach retrieves custom notes, reconstructs what is still possible from the player's hints, calculates exact odds, and explains a feedback-dependent strategy without accessing the secret number.

The player can compare a proposed guess with an optimal move, inspect citations and tool activity, and decide whether to submit the recommendation. Guardrails reject invalid or redundant input without consuming attempts and block advice that fails verification.

## Evidence and engineering contributions

- **Modular design:** separate game engine, public-state boundary, retriever, probability/planning tools, response verification, and UI.
- **Retrieval integration:** custom probability, strategy, and rule documents contribute actual passages to explanations.
- **Agent workflow:** question routing, retrieval, calculations, conditional planning, and result checks; observable tool events are committed in a structured log.
- **Reliability:** 64 passing tests, 15/15 evaluator checks, and 180,900 independently simulated secret outcomes with zero probability mismatches in the tested model.
- **Responsible scope:** explicit assumptions, no hidden-secret access by the coach, human-approved submissions, bounded logs, and documented limitations.

This is a local symbolic agent with templated explanations. It does not call a language model or claim fine-tuning results.

## What this project says about me as an AI engineer

This project shows my ability to improve an existing program with AI assistance while keeping reliability and user understanding in mind. I extended my earlier guessing game into Guesswise, adding randomized rounds and a coach that retrieves information, explains probabilities, and recommends a strategy. The project demonstrates how retrieval, reasoning tools, guardrails, and automated tests can work together in one application. It reflects the kind of AI engineer I want to become: someone who builds useful systems, keeps people in control, and clearly explains what the technology can and cannot do.

The implementation record and graded responsible-AI discussion are in [model_card.md](model_card.md).

## Explore the artifact

- [Loom video walkthrough](https://www.loom.com/share/6277838cef04472d8da2146e19f6f8a7)
- [Project README and sample input/output](README.md)
- [Mermaid architecture source](diagrams/architecture.mmd)
- [Full demonstration output](assets/evidence/demo-output.txt)
- [Evaluation summary](assets/evidence/evaluation-output.txt)
- [Agent tool-call records](assets/evaluation.json)
- [Responsible-AI system card](model_card.md)
- [6½-minute presentation guide](presentation.md)
