> Historical Module 1 reflection retained from the base project. Current Project 4 reflection: [model_card.md](model_card.md).

# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
it was nice till I ran my first try the go higer and go lower was not helpful and the 1 out of 100 tries was also a lie
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").
  1. the hints was not working was only looking at the first two number so 3000000 was 
  gonnea say go hiher but 50 is going to say go lower.
  2. The restart button was also not working as I ran out of time. When it says i
  3. The tries I have where incorrect it said 100 tries to go but ran out afte 3.
**Bug Reproduction Log**
enter at least 3 bug

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Guessed a very large number (e.g., 3000000) when the secret number was around 50 | Hint says "Go Lower" because the guess is higher than the secret | Hint says "Go Higher". The comparison seems to treat the guess like text (looking at the first digit), so 3000000 is treated as smaller than 50 | No error shown. The game runs, but the hint is wrong |

| Guessed 50 when the secret number was lower than 50 | Hint says "Go Lower" | Hint was inconsistent with the number size. Sometimes it said "Go Lower" and sometimes "Go Higher" for guesses that did not match the real order | No error shown |

| Used up my attempts, then clicked the New Game / restart button 
| A fresh game starts: new secret number, attempts reset, and I can guess again 
| Restart button did not work properly. The game stayed stuck at the end and I could not start a new round | No error shown (Streamlit page just did not reset) |

| Started a new game and watched the attempts counter while guessing 
| Counter matches the real limit (e.g., 100 tries means 100 guesses) 
| Game said I had about 100 tries left, but the game ended after only 3 guesses | No error shown |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
I used cloud, Agent and copilot
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the r 
  The ai suggested what i needed to fix and where to go find it as my difficult level was not right, as normal was harder than the hard so i changed it from 1 - 50 to 1 to 200 to balance it out.













sult).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

 The ai made the normal more difficut than the hard and I figured it out by running the ai out put in another ai and it told my that that was still the bug that excited so I went and manually changed it. form 1 to 50 to 1 to 200.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
   by running the app again and seeing and on the logics I understood changing the number myself is enough.
- Describe at least one test you ran (manual or using pytest)   I put in a letter and it did not take away the number of tries that I had.
  and what it showed you about your code. it says that its not a number. My code is working like It should.
- Did AI help you design or understand any tests? How?
yes it helped me in understanding how the the difficut and 
hint is working and why its not working right. so i went and 
fixed it.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
It allows you to use pyton to run a web app insted of css and others.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you fixing the problem.
my promting habbits has incresed
  - This could be a testing habit, a prompting strategy, or a way you used Git.
  want to reuse in future labs or projects?
being able to dubble check what ai says with another ai so I can keep each ai focused on a task. then going back and fixing it. so I would say promting habbit has become better.

- What is one thing you would do differently next time you work with AI on a coding task?
I would use an other ai to help me be more specific on what I want then i will take that and put it in the copilot in the viscode then tell it to the the proble or find the bug then 
- In one or two sentences, describe how this project changed the way you think about AI generated code.
It needs more reviscing or human overlooking it.
