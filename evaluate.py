"""Evaluate real coach responses, guardrails, and exact strategy coverage."""

import argparse
from dataclasses import asdict
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path

from coach import Coach, calculate_odds, chance_with_first_guess, verify_odds
from game import Observation, PublicGame
from runtime_logging import configure_logging
from scenarios import SCENARIOS


def midpoint_wins(secret: int, lo: int, hi: int, tries: int) -> bool:
    """Independent simulated player; no formula from the coach is used."""
    for _ in range(tries):
        move = (lo + hi) // 2
        if move == secret:
            return True
        if move < secret:
            lo = move + 1
        else:
            hi = move - 1
    return False


@lru_cache(maxsize=None)
def optimal_coverage(count: int, tries: int) -> int:
    """Exhaustively consider every possible next move for small intervals."""
    if not count or not tries:
        return 0
    return max(1 + optimal_coverage(left, tries - 1)
               + optimal_coverage(count - left - 1, tries - 1) for left in range(count))


def run_evaluation() -> dict:
    results: list[dict] = []
    transcripts: list[dict] = []

    def record(name: str, passed: bool, detail: str) -> None:
        results.append({"name": name, "passed": bool(passed), "detail": detail})

    expected = {
        "opening": (100, 3, Fraction(1, 100), Fraction(7, 100), 50),
        "after-hints": (24, 3, Fraction(1, 24), Fraction(7, 24), 62),
        "last-try": (7, 1, Fraction(1, 7), Fraction(1, 7), 19),
    }
    for name, scenario in SCENARIOS.items():
        reply = Coach().answer(scenario.question, scenario.public)
        transcripts.append({"scenario": name, "question": scenario.question,
                            "public_game": asdict(scenario.public), **reply.to_dict()})
        if name in expected:
            odds = calculate_odds(scenario.public)
            actual = (odds.candidates, odds.attempts_left, odds.next_guess, odds.best_play, odds.recommendation)
            verified = reply.status == "ok" and reply.trace[-1].get("result") == "passed"
            record(name, verified and actual == expected[name],
                   f"{odds.candidates} candidates; {odds.attempts_left} tries; next={odds.next_guess}; best={odds.best_play}; recommendation={odds.recommendation}")
        elif name == "guardrail":
            record(name, reply.status == "blocked" and reply.recommendation is None, "Secret request refused")
        elif name == "what-if":
            record(name, reply.status == "ok" and "4.00%" in reply.answer and "7.00%" in reply.answer,
                   "Guess 1 then best play = 4%; optimal first move = 7%")

    for name, question, public, status in [
        ("empty_question", "", PublicGame(1, 100, 3), "blocked"),
        ("long_question", "x" * 501, PublicGame(1, 100, 3), "blocked"),
        ("unsupported", "Write an essay about France", PublicGame(1, 100, 3), "unsupported"),
        ("contradictory_hints", "What are my odds?", PublicGame(1, 100, 3, (Observation(50, "Too Low"), Observation(20, "Too High"))), "error"),
        ("won", "Best strategy?", PublicGame(1, 20, 3, (Observation(7, "Win"),), "won"), "ok"),
        ("lost", "What are my odds?", PublicGame(1, 20, 3, (Observation(5, "Too Low"), Observation(10, "Too Low"), Observation(15, "Too Low")), "lost"), "ok"),
    ]:
        reply = Coach().answer(question, public)
        record(name, reply.status == status and reply.recommendation is None, f"Expected {status}; got {reply.status}")
        transcripts.append({"scenario": name, "question": question, "public_game": asdict(public), **reply.to_dict()})

    # Test every secret for each supported interval size and attempt count.
    grids = outcomes = mismatches = 0
    for count in range(1, 201):
        for tries in range(1, 10):
            public = PublicGame(1, count, tries)
            odds = calculate_odds(public)
            verify_odds(public, odds)
            wins = sum(midpoint_wins(secret, 1, count, tries) for secret in range(1, count + 1))
            mismatches += Fraction(wins, count) != odds.best_play
            grids += 1
            outcomes += count
    record("coverage_simulation", mismatches == 0,
           f"{grids} interval/try combinations; {outcomes} secret outcomes; {mismatches} mismatches")

    optimal_mismatches = sum(
        optimal_coverage(n, t) != min(n, (1 << t) - 1)
        for n in range(1, 25) for t in range(1, 7)
    )
    record("optimality_crosscheck", optimal_mismatches == 0,
           f"144 small-interval exhaustive move comparisons; {optimal_mismatches} mismatches")

    hypothetical = chance_with_first_guess(PublicGame(1, 100, 3), 1)
    wins_with_edge = 1 + sum(midpoint_wins(secret, 2, 100, 2) for secret in range(2, 101))
    record("what_if_simulation", hypothetical == Fraction(wins_with_edge, 100),
           f"Edge-first policy: {wins_with_edge}/100 wins")

    baseline_valid = baseline_odds = adapted_valid = adapted_odds = 0
    for name in expected:
        public = SCENARIOS[name].public
        lo, hi = public.candidate_bounds()
        actual = calculate_odds(public)
        # Explicit static baseline, not another model: always guess 50, report 1%.
        baseline_valid += lo <= 50 <= hi
        baseline_odds += Fraction(1, 100) == expected[name][2]
        reply = Coach().answer("What is the best strategy?", public)
        adapted_valid += reply.status == "ok" and lo <= reply.recommendation <= hi
        adapted_odds += actual.next_guess == expected[name][2]
    comparison = {
        "cases": 3,
        "static_baseline": {"valid_suggestions": baseline_valid, "correct_next_odds": baseline_odds},
        "context_aware_coach": {"valid_suggestions": adapted_valid, "correct_next_odds": adapted_odds},
    }
    record("context_adaptation", adapted_valid == 3 and adapted_odds == 3,
           f"Static baseline: {baseline_valid}/3 feasible, {baseline_odds}/3 correct odds; coach: {adapted_valid}/3 feasible, {adapted_odds}/3 correct odds")

    return {"summary": {"passed": sum(item["passed"] for item in results),
                        "failed": sum(not item["passed"] for item in results),
                        "total": len(results), "secret_outcomes": outcomes},
            "results": results, "baseline_comparison": comparison, "interactions": transcripts}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write this run's structured report and tool-call transcripts")
    args = parser.parse_args()
    configure_logging()
    report = run_evaluation()
    for result in report["results"]:
        print(f"{'PASS' if result['passed'] else 'FAIL'} {result['name']}: {result['detail']}")
    summary = report["summary"]
    print(f"\nEvaluation: {summary['passed']}/{summary['total']} passed; {summary['failed']} failed.")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Report written to {args.output}")
    return int(summary["failed"] != 0)


if __name__ == "__main__":
    raise SystemExit(main())
