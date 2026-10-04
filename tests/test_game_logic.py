from pathlib import Path

from streamlit.testing.v1 import AppTest

from logic_utils import check_guess, parse_guess, update_score

APP_PATH = Path(__file__).parents[1] / "app.py"

def run_app():
    return AppTest.from_file(str(APP_PATH), default_timeout=10).run()

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result[0] == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == ("Too High", "📉 Go LOWER!")

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == ("Too Low", "📈 Go HIGHER!")

def test_large_guess_is_compared_numerically():
    result = check_guess(3000000, "50")
    assert result == ("Too High", "📉 Go LOWER!")

def test_invalid_guess_returns_error():
    assert parse_guess("abc") == (False, None, "That is not a number.")

def test_invalid_guess_does_not_change_score():
    assert update_score(20, "Invalid", 1) == 20

def test_too_high_guess_loses_points():
    assert update_score(20, "Too High", 2) == 15

def test_first_attempt_win_score_has_no_extra_attempt_penalty():
    assert update_score(0, "Win", 1) == 90

def test_invalid_guess_does_not_consume_attempt():
    app = run_app()
    app.text_input[0].set_value("abc")
    app.button[0].click().run()

    assert app.session_state["attempts"] == 0

def test_invalid_guess_does_not_add_to_history():
    app = run_app()
    app.text_input[0].set_value("abc")
    app.button[0].click().run()

    assert app.session_state["history"] == []

def test_new_game_resets_state_and_uses_difficulty_range():
    app = run_app()
    app.selectbox[0].select("Hard").run()
    app.session_state["status"] = "lost"
    app.session_state["score"] = 25
    app.session_state["attempts"] = 3
    app.session_state["history"] = [10, 20, 30]
    app.button[1].click().run()

    assert app.session_state["status"] == "playing"
    assert app.session_state["score"] == 0
    assert app.session_state["attempts"] == 0
    assert app.session_state["history"] == []
    assert 1 <= app.session_state["secret"] <= 200

def test_changing_difficulty_starts_a_fresh_in_range_game():
    app = run_app()
    app.session_state["score"] = 25
    app.session_state["attempts"] = 3
    app.session_state["history"] = [10, 20, 30]
    app.session_state["status"] = "lost"
    app.selectbox[0].select("Easy").run()

    assert app.session_state["status"] == "playing"
    assert app.session_state["score"] == 0
    assert app.session_state["attempts"] == 0
    assert app.session_state["history"] == []
    assert 1 <= app.session_state["secret"] <= 20
    assert "Guess a number between 1 and 20." in app.info[0].value
