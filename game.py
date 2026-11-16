"""Random rounds and a strict public-data boundary for the coach."""

from dataclasses import dataclass, field
import random

from logic_utils import check_guess, parse_guess, update_score


@dataclass(frozen=True)
class RoundConfig:
    low: int
    high: int
    attempt_limit: int


@dataclass(frozen=True)
class Observation:
    guess: int
    outcome: str


@dataclass(frozen=True)
class PublicGame:
    """Only player-visible facts. Deliberately has no secret field."""

    low: int
    high: int
    attempt_limit: int
    history: tuple[Observation, ...] = ()
    status: str = "playing"

    @property
    def attempts_left(self) -> int:
        return self.attempt_limit - len(self.history)

    def candidate_bounds(self) -> tuple[int, int]:
        """Validate a snapshot while reconstructing its feasible interval."""
        if any(type(n) is not int for n in (self.low, self.high, self.attempt_limit)):
            raise ValueError("Round limits must be whole numbers.")
        if not 1 <= self.low <= self.high <= 1000 or not 1 <= self.attempt_limit <= 20:
            raise ValueError("Round limits are outside supported bounds.")
        if self.status not in {"playing", "won", "lost"}:
            raise ValueError("Unknown round status.")
        if len(self.history) > self.attempt_limit:
            raise ValueError("More guesses than allowed attempts.")
        lo, hi = self.low, self.high
        seen: set[int] = set()
        won = False
        for observation in self.history:
            guess = observation.guess
            if won or type(guess) is not int or guess in seen or not lo <= guess <= hi:
                raise ValueError("Guess history is inconsistent with earlier hints.")
            seen.add(guess)
            if observation.outcome == "Too Low":
                lo = guess + 1
            elif observation.outcome == "Too High":
                hi = guess - 1
            elif observation.outcome == "Win":
                lo = hi = guess
                won = True
            else:
                raise ValueError("Unknown hint in guess history.")
            if lo > hi:
                raise ValueError("The hints leave no possible number.")
        expected = "won" if won else "lost" if self.attempts_left == 0 else "playing"
        if self.status != expected:
            raise ValueError("Round status does not match the guess history.")
        return lo, hi


@dataclass
class Game:
    config: RoundConfig
    secret: int = field(repr=False)
    history: list[Observation] = field(default_factory=list)
    score: int = 0
    status: str = "playing"

    def public(self) -> PublicGame:
        return PublicGame(
            self.config.low, self.config.high, self.config.attempt_limit,
            tuple(self.history), self.status,
        )

    def submit(self, raw: str) -> tuple[bool, str]:
        if self.status != "playing":
            return False, "This round is over. Start a new random game."
        ok, guess, error = parse_guess(raw)
        if not ok:
            return False, error or "Invalid guess."
        if not self.config.low <= guess <= self.config.high:
            return False, f"Stay inside this round's range: {self.config.low}–{self.config.high}."
        if any(item.guess == guess for item in self.history):
            return False, "You already tried that number. No attempt used."
        lo, hi = self.public().candidate_bounds()
        if not lo <= guess <= hi:
            return False, f"Earlier hints ruled that out. Choose {lo}–{hi}. No attempt used."
        outcome, message = check_guess(guess, self.secret)
        self.history.append(Observation(guess, outcome))
        self.score = update_score(self.score, outcome, len(self.history))
        if outcome == "Win":
            self.status = "won"
        elif len(self.history) == self.config.attempt_limit:
            self.status = "lost"
        return True, message


def new_game(previous: RoundConfig | None = None, rng: random.Random | None = None) -> Game:
    """Choose new limits once per round; avoid repeating either setting."""
    rng = rng or random.SystemRandom()
    widths = (20, 30, 40, 50, 75, 100, 150, 200)
    ranges = [(lo, lo + width - 1) for lo in range(1, 81) for width in widths]
    if previous is not None:
        ranges = [bounds for bounds in ranges if bounds != (previous.low, previous.high)]
    low, high = rng.choice(ranges)
    limits = [n for n in range(3, 10) if previous is None or n != previous.attempt_limit]
    config = RoundConfig(low, high, rng.choice(limits))
    return Game(config, rng.randint(low, high))
