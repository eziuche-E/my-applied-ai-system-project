# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [] Describe the game's purpose.
let you guess and then gives you hint on where to guess and then restarts when i say new game also keeps the score.

- [ ] Detail which bugs you found.
I found hint bug, guessing erro, imput erro out put erro, and restart button erro.
- [ ] Explain what fixes you applied.
I appled all of them and fixed all the bugs.

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step --> type in a numer in rage of the difficulty 
2. <!-- Describe this step -->
then the hint tells you which direction to go if you get it your scored and if you run out of tries you loose points.
3. <!-- Describe this step -->
restart game after win or loose and keep plaiying and it keeps the score of your total game time.
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results
========================== 12 passed in 2.34s ===========================
```
# Paste your pytest output here, e.g.:
# pytest tests/
# ========================= X passed in 0.XXs =========================
 python -m pytest tests\test_game_logic.py
========================== test session starts ==========================
platform win32 -- Python 3.9.13, pytest-8.4.2, pluggy-1.6.0
rootdir: C:\Users\ejima\Downloads\codepath\gameglitch\ai110-module1show-gameglitchinvestigator-starter
collected 12 items                                                       

tests\test_game_logic.py ............                              [100%]

========================== 12 passed in 2.34s ===========================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
