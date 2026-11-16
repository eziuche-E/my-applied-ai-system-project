"""Optional real-browser smoke checks; run after starting Streamlit on port 8502.

Requires Playwright 1.62.0 and either system Chromium or playwright install chromium.
"""

import argparse
import json
from pathlib import Path
import re
import shutil

from playwright.sync_api import expect, sync_playwright


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8502")
    parser.add_argument("--output", type=Path, default=Path("assets/evidence/browser-checks.json"))
    args = parser.parse_args()
    report = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=shutil.which("chromium"), headless=True,
                                    args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
        page.goto(args.base_url, wait_until="networkidle")
        page.get_by_role("button", name="My odds", exact=True).click()
        page.get_by_text("Next-guess chance:", exact=False).wait_for()
        assert page.locator('[data-testid="stException"]').count() == 0
        report.append({"check": "odds_answer", "result": "PASS"})
        page.get_by_label("Your guess", exact=True).fill("abc")
        page.get_by_role("button", name="Submit guess", exact=True).click()
        page.get_by_text("Enter a whole number, such as 42.", exact=True).wait_for()
        report.append({"check": "invalid_guess_guardrail", "result": "PASS"})
        page.get_by_role("button", name="Best strategy", exact=True).click()
        page.get_by_text("Recommended next guess:", exact=False).wait_for()
        suggestion_button = page.get_by_role("button", name="Put suggested", exact=False)
        suggestion_button.wait_for()
        suggestion_button.click()
        expect(page.get_by_label("Your guess", exact=True)).to_have_value(re.compile(r"[0-9]+"))
        assert page.get_by_text("No guesses yet.", exact=False).count() == 1
        report.append({"check": "human_approval_suggestion_does_not_submit", "result": "PASS"})
        page.get_by_role("button", name="Submit guess", exact=True).click()
        page.locator('[data-testid="stDataFrame"]').wait_for()
        expect(page.get_by_role("button", name="Put suggested", exact=False)).to_have_count(0)
        report.append({"check": "guess_feedback_and_stale_suggestion", "result": "PASS"})
        page.get_by_role("button", name="New random game", exact=True).click()
        page.get_by_role("heading", name="Round 02", exact=True).wait_for()
        page.get_by_text("No guesses yet.", exact=False).wait_for()
        report.append({"check": "new_round_resets_history", "result": "PASS"})
        chat = page.get_by_placeholder("Ask about probability, strategy, hints, or rules", exact=True)
        chat.fill("What are my chances if I guess 1?")
        chat.press("Enter")
        page.get_by_text("If you guess 1:", exact=False).wait_for()
        report.append({"check": "typed_chat_what_if", "result": "PASS"})
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        report.append({"check": "mobile_no_horizontal_overflow", "result": "PASS"})
        assert page.locator('[data-testid="stException"]').count() == 0
        browser.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
