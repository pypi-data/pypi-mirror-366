# =============== MAB Solver ===============

The MAB solver or the Multi Agent Bandit problem solver consists of four main functions.
Naturally it is meant to solve the MAB problem but it uses Pure Exploration, Pure exploitation, Fixed Exploration + Greedy Exploitation and finally Epsilon Greedy approach.
There are a handful of parameters which can be tweaked like time steps (t), number of arms (n), fixed time steps (tf) (used in Fixed Exploration + Greedy Exploitation) and epsilon (eps) (used in epsilon greedy).
The library handles the outputs randomly and for this version, there is no way of manipulating the input probabilities. But it can be expected in the future versions of the library.