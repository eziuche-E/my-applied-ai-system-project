"""Small, independently testable rules inherited from Game Glitch Investigator."""

import re


def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Legacy helper retained for the original project's callers."""
    return {"Easy": (1, 20), "Normal": (1, 100), "Hard": (1, 200)}.get(
        difficulty, (1, 100)
    )


def parse_guess(raw: str | None) -> tuple[bool, int | None, str | None]:
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return False, None, "Enter a guess."
    if not isinstance(raw, str) or not re.fullmatch(r"[+-]?[0-9]+", raw.strip()):
        return False, None, "Enter a whole number, such as 42."
    if len(raw.strip()) > 20:
        return False, None, "That number is too large."
    return True, int(raw.strip()), None


def check_guess(guess: int, secret: int) -> tuple[str, str]:
    guess, secret = int(guess), int(secret)
    if guess == secret:
        return "Win", "Correct!"
    if guess > secret:
        return "Too High", "Go LOWER!"
    return "Too Low", "Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    if outcome == "Win":
        return current_score + max(10, 100 - 10 * attempt_number)
    if outcome in {"Too High", "Too Low"}:
        return current_score - 5
    return current_score
