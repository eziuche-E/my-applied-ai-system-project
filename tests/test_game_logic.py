"""Regression coverage for the base project plus the randomized round rules."""

from dataclasses import asdict
import random

import pytest

from game import Game, RoundConfig, new_game
from logic_utils import check_guess, parse_guess, update_score


def test_winning_guess():
    assert check_guess(50, 50)[0] == "Win"


def test_guess_too_high():
    assert check_guess(60, 50) == ("Too High", "Go LOWER!")


def test_guess_too_low():
    assert check_guess(40, 50) == ("Too Low", "Go HIGHER!")


def test_large_guess_is_compared_numerically():
    assert check_guess(3000000, "50") == ("Too High", "Go LOWER!")


@pytest.mark.parametrize("raw", [None, "", " ", "abc", "4.7", "4.0", "nan", "1e2", "9" * 501, 5, True])
def test_invalid_guesses_are_not_silently_coerced(raw):
    assert parse_guess(raw)[0] is False


@pytest.mark.parametrize("raw,expected", [("42", 42), (" 7 ", 7), ("+5", 5), ("-4", -4)])
def test_integer_parsing(raw, expected):
    assert parse_guess(raw) == (True, expected, None)


def test_invalid_guess_does_not_change_score():
    assert update_score(20, "Invalid", 1) == 20


def test_too_high_guess_loses_points():
    assert update_score(20, "Too High", 2) == 15


def test_first_attempt_win_score_has_no_extra_attempt_penalty():
    assert update_score(0, "Win", 1) == 90


def test_invalid_guesses_do_not_change_game():
    game = Game(RoundConfig(1, 100, 3), 80)
    for raw in ["abc", "4.7", "0", "101", ""]:
        before = asdict(game)
        assert not game.submit(raw)[0]
        assert asdict(game) == before


def test_duplicate_and_ruled_out_guesses_use_no_attempt():
    game = Game(RoundConfig(1, 100, 3), 80)
    assert game.submit("50")[0]
    before = asdict(game)
    assert not game.submit("50")[0]
    assert not game.submit("40")[0]
    assert asdict(game) == before


def test_secret_stays_fixed_and_round_ends_exactly_at_limit():
    game = Game(RoundConfig(1, 100, 3), 99)
    for raw in ["50", "75", "90"]:
        assert game.submit(raw)[0]
        assert game.secret == 99
    assert game.status == "lost" and game.public().attempts_left == 0
    before = asdict(game)
    assert not game.submit("99")[0]
    assert asdict(game) == before


def test_win_ends_round_and_keeps_score():
    game = Game(RoundConfig(1, 100, 3), 50)
    assert game.submit("50")[0]
    assert game.status == "won" and game.score == 90
    assert not game.submit("50")[0]
    assert game.score == 90


def test_new_game_randomizes_both_limits_and_resets_state():
    rng = random.Random(314159)
    previous = None
    for _ in range(200):
        game = new_game(previous, rng)
        assert 20 <= game.config.high - game.config.low + 1 <= 200
        assert 3 <= game.config.attempt_limit <= 9
        assert game.config.low <= game.secret <= game.config.high
        if previous:
            assert (game.config.low, game.config.high) != (previous.low, previous.high)
            assert game.config.attempt_limit != previous.attempt_limit
        assert game.history == [] and game.score == 0 and game.status == "playing"
        previous = game.config
