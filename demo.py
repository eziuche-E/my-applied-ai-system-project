"""Reproducible command-line entry point to the same coach used by the UI."""

import argparse
import json

from coach import Coach
from runtime_logging import configure_logging
from scenarios import SCENARIOS


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=[*SCENARIOS, "all"], default="opening")
    parser.add_argument("--question", help="Override the scenario's question (1–500 characters)")
    parser.add_argument("--json", action="store_true", help="Include structured tool-call evidence")
    args = parser.parse_args()
    configure_logging()
    names = SCENARIOS if args.scenario == "all" else [args.scenario]
    records = []
    for name in names:
        scenario = SCENARIOS[name]
        question = args.question if args.question is not None else scenario.question
        result = Coach().answer(question, scenario.public)
        records.append({"scenario": name, "question": question, **result.to_dict()})
        if not args.json:
            print(f"=== {name}: {scenario.title} ===")
            print(f"Input: {question}\n")
            print(result.answer)
            print(f"\nStatus: {result.status}\n")
    if args.json:
        print(json.dumps(records, indent=2, ensure_ascii=False))
    return int(any(record["status"] == "error" for record in records))


if __name__ == "__main__":
    raise SystemExit(main())
