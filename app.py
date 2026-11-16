"""Guesswise: a randomized game with a side-by-side, public-data-only coach."""

from dataclasses import asdict
import json

import streamlit as st

from coach import Coach, calculate_odds, percent, state_id
from game import new_game
from runtime_logging import configure_logging

st.set_page_config(page_title="Guesswise · Game Glitch Investigator", page_icon="🎯", layout="wide")
configure_logging()

st.markdown("""
<style>
.block-container {max-width: 1320px; padding-top: 2.2rem; padding-bottom: 2rem;}
h1, h2, h3 {letter-spacing: -0.035em;}
.eyebrow {font-size: .74rem; letter-spacing: .16em; font-weight: 700; color: #087f5b; margin-bottom: .7rem;}
.hero {font-size: clamp(2.2rem, 4vw, 3.5rem); line-height: 1.07; font-weight: 750; letter-spacing: -.055em; color: #183c32; margin-bottom: .8rem;}
.hero span {color: #087f5b;}
.hero-note {color: #60716b; max-width: 780px; font-size: 1.05rem; line-height: 1.65;}
div[data-testid="stMetric"] {background: #fff; border: 1px solid #dce7e0; border-radius: 12px; padding: 14px 16px;}
div[data-testid="stMetricLabel"] {color: #60716b;}
div[data-testid="stMetricValue"] {font-size: 1.65rem; color: #183c32;}
.stButton button, .stFormSubmitButton button {border-radius: 9px;}
</style>
<div class="eyebrow">GAME GLITCH INVESTIGATOR / APPLIED AI</div>
<div class="hero">A little luck.<br><span>A better strategy.</span></div>
<div class="hero-note">A new range. A new limit. A coach that helps you understand your odds — without peeking at the answer.</div>
""", unsafe_allow_html=True)
st.write("")


def reset_round() -> None:
    previous = st.session_state.game.config if "game" in st.session_state else None
    st.session_state.game = new_game(previous)
    st.session_state.round_number = st.session_state.get("round_number", 0) + 1
    st.session_state.messages = []
    st.session_state.feedback = None
    st.session_state.guess = ""


if "game" not in st.session_state:
    reset_round()
    st.session_state.wins = 0
    st.session_state.losses = 0
    st.session_state.total_points = 0
    st.session_state.audit = []


def submit_guess() -> None:
    game = st.session_state.game
    old_score = game.score
    accepted, message = game.submit(st.session_state.guess)
    st.session_state.feedback = (accepted, message)
    if accepted:
        st.session_state.total_points += game.score - old_score
        if game.status == "won":
            st.session_state.wins += 1
        elif game.status == "lost":
            st.session_state.losses += 1


def ask_coach(question: str) -> None:
    # The secret never crosses this boundary. Questions cannot mutate the game.
    public = st.session_state.game.public()
    result = Coach().answer(question, public)
    record = {"question": question[:500], "round": st.session_state.round_number,
              "context": asdict(public), **result.to_dict()}
    st.session_state.messages = (st.session_state.messages + [record])[-12:]
    st.session_state.audit = (st.session_state.audit + [record])[-50:]


def use_suggestion() -> None:
    st.session_state.guess = str(calculate_odds(st.session_state.game.public()).recommendation)


game = st.session_state.game
public = game.public()
odds = calculate_odds(public)
left, right = st.columns([1, 1.12], gap="large")

with left:
    heading, restart = st.columns([1, 1])
    with heading:
        st.subheader(f"Round {st.session_state.round_number:02d}")
    with restart:
        st.button("New random game", key="new_game", on_click=reset_round, use_container_width=True)
    st.caption("Your range and try limit are drawn once, then stay fixed for the round.")
    range_col, tries_col, score_col = st.columns(3)
    range_col.metric("Number range", f"{public.low}–{public.high}")
    tries_col.metric("Tries left", f"{public.attempts_left} / {public.attempt_limit}")
    score_col.metric("Round points", game.score)
    st.write("")

    with st.container(border=True):
        st.markdown("### Make your move")
        st.caption(f"Still possible: **{odds.low}–{odds.high}** · **{odds.candidates}** candidate numbers")
        with st.form("guess_form"):
            st.text_input("Your guess", key="guess", placeholder="Enter a whole number",
                          disabled=game.status != "playing")
            st.form_submit_button("Submit guess", type="primary", use_container_width=True,
                                  on_click=submit_guess, disabled=game.status != "playing")
        if st.session_state.feedback:
            accepted, message = st.session_state.feedback
            if not accepted:
                st.warning(message)
            elif game.status == "playing":
                st.info(message)
        if game.status == "won":
            st.success(f"You got it! The number was {game.secret}. Round score: {game.score}.")
        elif game.status == "lost":
            st.error(f"No tries left. The number was {game.secret}. Start a new round to try again.")
        else:
            st.caption("Letters, decimals, repeats, and ruled-out numbers never cost a try.")

    st.markdown("#### Your guess trail")
    if game.history:
        st.dataframe([
            {"Try": i, "Guess": item.guess, "Feedback": item.outcome}
            for i, item in enumerate(game.history, 1)
        ], hide_index=True, use_container_width=True)
    else:
        st.info("No guesses yet. Ask the coach for a plan, or make your first move.")
    st.caption(f"THIS SESSION · {st.session_state.wins} wins · {st.session_state.losses} losses · {st.session_state.total_points} total points")
    with st.expander("How the game stays fair"):
        st.markdown("""
- Each secret is sampled uniformly from the displayed inclusive range.
- Each new game changes both the range and the try limit (3–9).
- Some rounds cannot be guaranteed with the tries available. The coach will say so.
- Your hint history narrows the candidate interval; the secret stays fixed.
- Wrong accepted guesses cost 5 points. A win earns `max(10, 100 − 10 × try number)`.
- New games reset round points; session totals remain. Restarting an unfinished round does not count as a completed loss.
- There is no debug panel revealing the live secret. This is an educational game, not a secure competition server.
""")

with right:
    st.subheader("Your AI coach")
    st.caption("Local retrieval + exact math + a checked plan. No API key. No hidden-number access.")
    if game.status == "playing":
        immediate, planned = st.columns(2)
        immediate.metric("Next guess", percent(odds.next_guess), help="Any single number still possible; assumes a uniformly sampled secret.")
        planned.metric("Win with best play", percent(odds.best_play), help="Chance before tries expire if you follow an optimal higher/lower strategy. Not a guarantee unless 100%.")
        st.write("")
    quick_odds, quick_strategy, quick_hint = st.columns(3)
    quick_odds.button("My odds", key="ask_odds", on_click=ask_coach,
                      args=("What is the probability of winning before I run out of tries?",), use_container_width=True)
    quick_strategy.button("Best strategy", key="ask_strategy", on_click=ask_coach,
                          args=("What is the best strategy?",), use_container_width=True)
    quick_hint.button("Next hint", key="ask_hint", on_click=ask_coach,
                      args=("Give me a hint for my next guess",), use_container_width=True)
    with st.container(height=610, border=True):
        if not st.session_state.messages:
            with st.chat_message("assistant", avatar="🧭"):
                st.markdown("**Let's make the odds make sense.**\n\nAsk me how likely you are to win, why the probability changes, or what to try next. I'll read your public game history, retrieve my source notes, calculate, and check my advice.")
                st.caption("Try: ‘What are my chances if I guess 50?’ or ‘What is the best strategy?’ This is a specialized local agent, not a general-purpose language model.")
        for message in st.session_state.messages:
            with st.chat_message("user"):
                st.text(message["question"])
            with st.chat_message("assistant", avatar="🧭"):
                st.markdown(message["answer"])
                st.caption(f"Round {message['round']} · Answered with {message['context']['attempt_limit'] - len(message['context']['history'])} tries left. Ask again after a guess to refresh.")
                with st.expander("Sources & tool activity"):
                    st.caption("Observable tool calls and checks, not a model's private chain of thought.")
                    st.json({"sources": message["sources"], "status": message["status"], "trace": message["trace"]})
    question = st.chat_input("Ask about probability, strategy, hints, or rules", key="coach_question", max_chars=500)
    if question:
        ask_coach(question)
        st.rerun()
    current_suggestion = any(
        message["recommendation"] is not None and message["intent"] in {"strategy", "hint"}
        and message["state_id"] == state_id(public)
        for message in st.session_state.messages
    )
    if current_suggestion and game.status == "playing":
        st.button(f"Put suggested {odds.recommendation} in my guess box", key="use_suggestion",
                  on_click=use_suggestion, use_container_width=True)
        st.caption("You still decide when to submit. Asking the coach never uses a try.")
    if st.session_state.audit:
        st.download_button("Download session evidence (.json)",
                           json.dumps(st.session_state.audit, indent=2, ensure_ascii=False),
                           file_name="guesswise-session.json", mime="application/json")
        st.caption("Export includes your questions, public game snapshots, and tool results. It excludes the hidden secret. Only the latest 50 answers are retained in this session.")

st.divider()
st.caption("GUESSWISE · Built from Game Glitch Investigator · Human chooses. Agent advises. Math verifies.")
