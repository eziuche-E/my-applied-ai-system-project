# Round rules and safe play

Every new game chooses an inclusive range with 20–200 integers and a random
limit of 3–9 tries. Both the range and the limit differ from the previous round.
They stay fixed until New random game is pressed. A new secret can happen to
match an earlier secret; the sampling is independent within each new range.

Only whole numbers inside the current feasible interval are accepted. Empty,
decimal, duplicate, out-of-range, and already-ruled-out guesses use no attempts.
A wrong accepted guess costs 5 points. A winning guess earns max(10, 100 minus
10 times the attempt number). New games reset the round score; session points
and completed-round wins/losses persist until the browser session resets.

The player chooses and submits every guess. Asking the coach or applying its
suggestion to the input box does not use a try. The coach cannot read the secret
and cannot make guesses for the player. Asking for the secret is refused.

Source: game.py and logic_utils.py in this repository.
