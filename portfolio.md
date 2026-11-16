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

**Draft for the student's review and personalization:**

> This project represents the approach I want to bring to AI engineering: start with a clear user problem, make the system's assumptions visible, and verify its advice with reproducible evidence. By extending a familiar game into a probability coach, I can show how retrieval, modular reasoning tools, guardrails, and human control fit into one usable application. I want to build systems whose behavior people can inspect and question, and to be clear about the limits of both the technology and my own testing.

Review this paragraph in your own voice and add a genuine observation from using the app before publishing it as a personal reflection. The implementation record and graded responsible-AI discussion are in [model_card.md](model_card.md).

## Explore the artifact

- [Loom video walkthrough](https://www.loom.com/share/6277838cef04472d8da2146e19f6f8a7)
- [Project README and sample input/output](README.md)
- [Mermaid architecture source](diagrams/architecture.mmd)
- [Full demonstration output](assets/evidence/demo-output.txt)
- [Evaluation summary](assets/evidence/evaluation-output.txt)
- [Agent tool-call records](assets/evaluation.json)
- [Responsible-AI system card](model_card.md)
- [6½-minute presentation guide](presentation.md)
