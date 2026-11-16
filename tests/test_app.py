from dataclasses import asdict
from pathlib import Path

from streamlit.testing.v1 import AppTest

from game import Game, RoundConfig

APP_PATH = Path(__file__).parents[1] / "app.py"


def run_app():
    app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    assert not app.exception
    return app


def submit(app, raw):
    app.text_input(key="guess").set_value(raw)
    app.button(key="FormSubmitter:guess_form-Submit guess").click().run()
    assert not app.exception


def test_invalid_input_uses_no_attempt_in_ui():
    app = run_app()
    before = asdict(app.session_state["game"])
    submit(app, "abc")
    assert asdict(app.session_state["game"]) == before
    assert app.warning


def test_new_game_changes_range_and_limit_and_clears_chat():
    app = run_app()
    previous = app.session_state["game"].config
    app.button(key="ask_strategy").click().run()
    assert app.session_state["messages"]
    app.button(key="new_game").click().run()
    assert not app.exception
    game = app.session_state["game"]
    assert (game.config.low, game.config.high) != (previous.low, previous.high)
    assert game.config.attempt_limit != previous.attempt_limit
    assert game.history == [] and game.score == 0
    assert app.session_state["messages"] == []


def test_coach_uses_live_hints_without_changing_game():
    app = run_app()
    app.session_state["game"] = Game(RoundConfig(1, 100, 3), 80)
    app.run()
    submit(app, "50")
    before = asdict(app.session_state["game"])
    app.button(key="ask_odds").click().run()
    assert not app.exception
    assert asdict(app.session_state["game"]) == before
    answer = app.session_state["messages"][-1]
    assert "2 of 3 tries left" in answer["answer"]
    assert "50 possible numbers (51–100)" in answer["answer"]
    assert "6.00%" in answer["answer"]
    assert "secret" not in answer["context"]


def test_chat_question_renders_and_retrieves_sources():
    app = run_app()
    app.chat_input(key="coach_question").set_value("What is the best strategy?").run()
    assert not app.exception
    reply = app.session_state["messages"][-1]
    assert reply["status"] == "ok" and reply["sources"]
    assert "Recommended next guess" in reply["answer"]
    assert app.session_state["game"].history == []


def test_suggestion_requires_human_submission():
    app = run_app()
    app.button(key="ask_strategy").click().run()
    suggestion = app.session_state["messages"][-1]["recommendation"]
    before = asdict(app.session_state["game"])
    app.button(key="use_suggestion").click().run()
    assert not app.exception
    assert app.text_input(key="guess").value == str(suggestion)
    assert asdict(app.session_state["game"]) == before


def test_win_score_persists_across_rounds_without_double_counting():
    app = run_app()
    app.session_state["game"] = Game(RoundConfig(1, 100, 3), 50)
    app.run()
    submit(app, "50")
    assert app.session_state["wins"] == 1
    assert app.session_state["total_points"] == 90
    app.button(key="ask_odds").click().run()
    assert not app.exception
    assert app.session_state["wins"] == 1
    assert "already won" in app.session_state["messages"][-1]["answer"]
    app.button(key="new_game").click().run()
    assert app.session_state["total_points"] == 90 and app.session_state["wins"] == 1
    assert app.session_state["game"].score == 0


def test_secret_is_not_rendered_during_active_game():
    app = run_app()
    app.session_state["game"] = Game(RoundConfig(1, 100, 3), 87)
    app.run()
    visible = [item.value for item in app.markdown]
    app.session_state["game"] = Game(RoundConfig(1, 100, 3), 23)
    app.run()
    assert [item.value for item in app.markdown] == visible
    assert not any("Secret:" in item.value for item in app.markdown)
