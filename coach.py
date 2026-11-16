"""A local retrieval-and-planning agent, not a hosted language model.

The orchestration selects tools, retrieves curated explanations, computes exact
odds, proposes a feedback-dependent plan, and checks structured results before
rendering a response. No tool receives a Game or its private secret.
"""

from dataclasses import asdict, dataclass
from fractions import Fraction
import hashlib
import json
import logging
import re

from game import PublicGame
from retriever import Document, Retriever

LOGGER = logging.getLogger("guesswise.coach")


@dataclass(frozen=True)
class Odds:
    low: int
    high: int
    candidates: int
    attempts_left: int
    next_guess: Fraction
    best_play: Fraction
    blind_play: Fraction
    guarantee_tries: int
    recommendation: int | None


@dataclass(frozen=True)
class CoachReply:
    status: str
    intent: str
    answer: str
    recommendation: int | None
    sources: tuple[str, ...]
    trace: tuple[dict, ...]
    state_id: str

    def to_dict(self) -> dict:
        return asdict(self)


def state_id(game: PublicGame) -> str:
    return hashlib.sha256(json.dumps(asdict(game), sort_keys=True).encode()).hexdigest()[:12]


def calculate_odds(game: PublicGame) -> Odds:
    lo, hi = game.candidate_bounds()
    count, tries = hi - lo + 1, game.attempts_left
    active = game.status == "playing"
    if active:
        next_chance = Fraction(1, count)
        best = Fraction(min(count, (1 << tries) - 1), count)
        blind = Fraction(min(tries, count), count)
    else:
        next_chance = Fraction(0)
        best = blind = Fraction(int(game.status == "won"))
    return Odds(
        lo, hi, count, tries, next_chance, best, blind, count.bit_length(),
        (lo + hi) // 2 if active else None,
    )


def verify_odds(game: PublicGame, odds: Odds) -> None:
    """Independent checks on tool output; fail closed on invalid recommendations."""
    lo, hi = game.candidate_bounds()
    if (odds.low, odds.high, odds.candidates, odds.attempts_left) != (
        lo, hi, hi - lo + 1, game.attempts_left
    ):
        raise ValueError("Computed context does not match the public game.")
    if not all(0 <= p <= 1 for p in (odds.next_guess, odds.best_play, odds.blind_play)):
        raise ValueError("A probability is outside zero to one.")
    if game.status == "playing":
        n, t = hi - lo + 1, game.attempts_left
        if odds.recommendation != (lo + hi) // 2:
            raise ValueError("The recommendation is not the feasible midpoint.")
        if odds.next_guess != Fraction(1, n):
            raise ValueError("Single-guess probability is inconsistent.")
        # Branch coverage verifies the decision-tree formula via the proposed move.
        capacity = (2 ** (t - 1)) - 1
        covered = 1 + min(odds.recommendation - lo, capacity) + min(hi - odds.recommendation, capacity)
        if odds.best_play != Fraction(covered, n):
            raise ValueError("The strategy cannot achieve its stated probability.")
        if odds.blind_play != Fraction(min(t, n), n) or odds.guarantee_tries != n.bit_length():
            raise ValueError("The comparison or guarantee is inconsistent.")
    elif odds.recommendation is not None or odds.next_guess != 0:
        raise ValueError("A finished round cannot have another move.")
    elif odds.best_play != int(game.status == "won") or odds.blind_play != odds.best_play:
        raise ValueError("A finished round has a known outcome.")


def classify(question: str) -> str:
    text = question.lower()
    if (re.search(r"\b(reveal|show|tell|give|print|leak|ignore|bypass)\b", text)
            and re.search(r"\b(secret|hidden|answer|instructions|prompt)\b", text)) or re.search(
                r"\bwhat(?:'s| is) (?:the )?(?:secret|winning number)\b", text):
        return "refused"
    if any(word in text for word in ("strateg", "stratag", "stratagy", "plan", "binary", "best", "optimal")):
        return "strategy"
    if any(word in text for word in ("probab", "probap", "chance", "odds", "percent", "likel", "why", "win")):
        return "probability"
    if any(word in text for word in ("hint", "suggest", "next", "recommend", "should i guess")):
        return "hint"
    if any(word in text for word in ("rule", "tries", "attempt", "score", "random", "range", "help", "how many guesses", "how to play", "higher", "lower")):
        return "rules"
    return "unsupported"


def percent(value: Fraction) -> str:
    return f"{float(value):.2%}"


def fraction(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def chance_with_first_guess(game: PublicGame, guess: int) -> Fraction:
    """Chance of winning if this move is followed by optimal feedback use."""
    lo, hi = game.candidate_bounds()
    if game.status != "playing" or not lo <= guess <= hi:
        return Fraction(0)
    capacity = (1 << (game.attempts_left - 1)) - 1
    return Fraction(1 + min(guess - lo, capacity) + min(hi - guess, capacity), hi - lo + 1)


def retrieved_passage(doc: Document) -> str:
    """Use actual retrieved text as part of the answer, not just a source label."""
    paragraphs = doc.text.split("\n\n")
    passage = paragraphs[1].replace("\n", " ") if len(paragraphs) > 1 else doc.text
    return f"> {passage}\n\nSource: `knowledge/{doc.id}.md` — {doc.title}"


class Coach:
    def __init__(self, retriever: Retriever | None = None):
        self.retriever = retriever

    def answer(self, question: str, game: PublicGame) -> CoachReply:
        trace: list[dict] = []
        sid = state_id(game)

        def reply(status: str, intent: str, answer: str, odds: Odds | None = None,
                  sources: tuple[str, ...] = ()) -> CoachReply:
            LOGGER.info(json.dumps({"status": status, "intent": intent, "state_id": sid,
                                    "tools": [event["tool"] for event in trace]}))
            return CoachReply(status, intent, answer, odds.recommendation if odds else None,
                              sources, tuple(trace), sid)

        if not isinstance(question, str) or not question.strip() or len(question) > 500:
            trace.append({"tool": "input_guardrail", "result": "rejected"})
            return reply("blocked", "invalid", "Ask a question using 1–500 characters. No attempt was used.")
        intent = classify(question)
        if intent == "refused":
            trace.append({"tool": "scope_guardrail", "result": "secret request refused"})
            return reply("blocked", intent, "I cannot reveal or look up the secret. I only receive the visible range, tries, and hints. Ask about odds or strategy instead.")
        if intent == "unsupported":
            trace.append({"tool": "scope_guardrail", "result": "unsupported topic"})
            return reply("unsupported", intent, "I specialize in this game, rather than general chat. Ask ‘What are my odds?’, ‘What is the best strategy?’, ‘Give me a hint’, or ‘How do the rules work?’")

        trace.append({"tool": "plan", "intent": intent,
                      "steps": ["read_public_game", "retrieve", "calculate_odds", "plan_guess", "verify"]})
        try:
            lo, hi = game.candidate_bounds()
            trace.append({"tool": "read_public_game", "range": [game.low, game.high],
                          "attempt_limit": game.attempt_limit, "attempts_left": game.attempts_left,
                          "observations": len(game.history), "candidate_interval": [lo, hi]})
            retriever = self.retriever or Retriever()
            docs = retriever.retrieve(question, intent)
            if not docs:
                raise ValueError("No relevant knowledge was retrieved.")
            trace.append({"tool": "retrieve", "documents": [doc.id for doc in docs],
                          "method": "intent routing plus companion-topic boost and lexical overlap"})
            odds = calculate_odds(game)
            trace.append({"tool": "calculate_odds", "candidates": odds.candidates,
                          "attempts_left": odds.attempts_left, "next_guess": fraction(odds.next_guess),
                          "best_play": fraction(odds.best_play), "blind_play": fraction(odds.blind_play)})
            trace.append({"tool": "plan_guess", "recommendation": odds.recommendation,
                          "if_too_high": [lo, odds.recommendation - 1] if odds.recommendation is not None and odds.recommendation > lo else [],
                          "if_too_low": [odds.recommendation + 1, hi] if odds.recommendation is not None and odds.recommendation < hi else [],
                          "remaining_after_guess": max(0, odds.attempts_left - 1)})
            verify_odds(game, odds)
            trace.append({"tool": "verify", "result": "passed",
                          "checks": ["public context", "probability bounds", "branch coverage", "feasible midpoint", "round status"]})
            answer = self._render(question, intent, game, odds, docs)
            return reply("ok", intent, answer, odds, tuple(f"knowledge/{doc.id}.md" for doc in docs))
        except (ValueError, OSError, UnicodeError) as exc:
            trace.append({"tool": "verify", "result": "blocked", "reason": type(exc).__name__})
            LOGGER.warning("coach stopped safely: %s", type(exc).__name__)
            return reply("error", intent, "I could not verify the game context or load my source notes. I will not invent odds. Start a new round; if this continues, check the knowledge/ folder and run the tests. No attempt was used.")

    def _render(self, question: str, intent: str, game: PublicGame, odds: Odds,
                docs: tuple[Document, ...]) -> str:
        source = retrieved_passage(docs[0])
        if game.status != "playing":
            result = "You already won this round." if game.status == "won" else "This round is over; there are no tries left."
            return f"{result} There is no next guess to recommend. Start a new random game for fresh odds.\n\n**Retrieved reference**\n\n{source}"

        n, t = odds.candidates, odds.attempts_left
        sections = [
            f"**Your live game:** {t} of {game.attempt_limit} tries left; {n} possible numbers ({odds.low}–{odds.high}), after {len(game.history)} accepted guesses.",
            f"**Next-guess chance:** 1/{n} = {percent(odds.next_guess)} for any one remaining number. The secret was sampled uniformly, and your hints leave these {n} equally likely candidates.",
            f"**Win before tries run out, with best play:** min({n}, 2^{t} − 1)/{n} = {percent(odds.best_play)}. Each guess can win immediately or split into a lower and a higher branch. With {t} tries, a balanced decision tree can cover up to {(1 << t) - 1} numbers.",
            f"**Comparison:** guessing distinct candidates without using future hints would cover at most {min(t, n)}/{n} = {percent(odds.blind_play)}. That is a comparison policy, not a prediction of your personal skill.",
        ]
        proposed = re.search(r"\b(?:guess|choose|pick|try)(?:ing)?\s+([+-]?[0-9]+)\b", question, re.I)
        if proposed and len(proposed.group(1)) < 21:
            chosen = int(proposed.group(1))
            chance = odds.next_guess if odds.low <= chosen <= odds.high else Fraction(0)
            sections.append(f"**If you guess {chosen}:** {percent(chance)} on that next guess. " + (
                "It is still a feasible candidate." if chance else "It is outside the remaining interval, so the input guardrail would reject it without using a try."))
            if chance:
                sections.append(f"**Your proposed move, then best play:** {percent(chance_with_first_guess(game, chosen))} chance to win within the {t} remaining tries, compared with {percent(odds.best_play)} for an optimal first move. This accounts for how unevenly your choice splits the remaining numbers.")

        if intent in {"strategy", "hint"}:
            midpoint = odds.recommendation
            branches = []
            if midpoint > odds.low:
                branches.append(f"Too High → search {odds.low}–{midpoint - 1}")
            if midpoint < odds.high:
                branches.append(f"Too Low → search {midpoint + 1}–{odds.high}")
            branch_text = "; ".join(branches) or "Only one candidate remains; submitting it wins."
            sections.append(
                f"**Recommended next guess: {midpoint}.** It is the midpoint of the remaining interval. "
                f"A midpoint does not improve the immediate 1/{n} chance; it balances what you can learn if wrong.\n\n"
                f"**Next-step plan:** Correct → stop; {branch_text}. "
                f"After this guess you have {t - 1} tries. Re-read the hint, rebuild the interval, and choose its midpoint again."
            )
        else:
            sections.append("Ask **‘What is the best strategy?’** for a recommended guess and a feedback-dependent plan.")

        if t >= odds.guarantee_tries:
            sections.append(f"**Guarantee check:** {odds.guarantee_tries} tries suffice for {n} candidates. With {t} left, following the midpoint plan can guarantee a win under these rules.")
        else:
            sections.append(f"**Guarantee check:** {odds.guarantee_tries} tries are needed to guarantee a win for {n} candidates; only {t} remain. The plan improves your odds but cannot promise a win.")
        if intent == "rules":
            paragraphs = docs[0].text.split("\n\n")
            if len(paragraphs) > 2:
                sections.append("**Scoring and input rules**\n\n" + paragraphs[2].replace("\n", " "))
        sections.append("**Retrieved reference**\n\n" + source)
        if len(docs) > 1:
            sections.append("**Related reference**\n\n" + retrieved_passage(docs[1]))
        sections.append("*Assumptions: uniform secret, truthful hints, and the stated strategy. I use public game data only; these are mathematical odds, not model confidence.*")
        return "\n\n".join(sections)
