# Probability without peeking

Each round samples one secret integer uniformly from its displayed inclusive range.
Higher/lower feedback removes inconsistent numbers. If N integers remain, each
remaining integer has probability 1/N of being the secret. Every feasible next
guess has the same immediate chance; a midpoint helps future guesses, not that
single-guess chance. A ruled-out guess has zero chance.

With t tries left, an optimal higher/lower decision tree can cover at most
2^t - 1 integers. Its maximum chance of winning before attempts expire is
min(N, 2^t - 1) / N. This assumes truthful hints and following an optimal plan.
The recurrence is C(0)=0 and C(t)=1+2*C(t-1): one current guess, then a lower
branch and a higher branch. Identifying the only remaining number still requires
submitting it; there is no automatic win after the final wrong guess.

Source: project mathematical derivation; exhaustively checked by evaluate.py.
