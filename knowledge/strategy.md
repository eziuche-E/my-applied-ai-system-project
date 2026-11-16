# Binary-search strategy

Guess the midpoint of the remaining inclusive interval. On a Too Low hint,
discard the guess and everything below it. On a Too High hint, discard the guess
and everything above it. Repeat. This balances the two feedback branches and
maximizes coverage for a fixed number of tries under the uniform secret model.

To guarantee a win on N candidates, including submitting the final answer, you
need ceil(log2(N+1)) tries. In integer arithmetic that is N.bit_length().
If fewer tries remain, the midpoint strategy is still optimal for the probability
of winning, but success is not guaranteed. A useful next-step plan shows the
lower and higher intervals and the attempts left after the proposed guess.

Source: https://en.wikipedia.org/wiki/Binary_search_algorithm
The limited-tries coverage claim is the project's decision-tree derivation.
