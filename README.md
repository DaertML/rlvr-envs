# rlvr-envs
Environments to generate RLVR data easily

# Introduction
Run the scripts in the envs folder to generate synthetic RLVR (Reinforcement Learning from Verifiable Rewards) datasets.

These are the environments:
🚢 Battleship Deductive Puzzle
- What it does: Generates a hidden grid containing ship structures and tracks past firing logs (hit or miss).
- The Logic Challenge: Instead of random guessing, the model uses grouped coordinate feedback and process-of-elimination steps to determine the exact state of a targeted, unrevealed cell.

👥 Guess Who?
- What it does: Generates an active roster of characters with boolean property profiles (e.g., Glasses: Yes, Beard: No), paired with diagnostic yes/no tracking logs.
- The Logic Challenge: Tests binary tree sorting and set intersection logic. The model determines if a specific character is the unique target, has been completely eliminated, or remains undetermined.

🦊 Fox and Geese
- What it does: Tracks a spatial layout of a traditional cross-shaped board containing a single Fox (F) and scattered Geese (G).
- The Logic Challenge: Evaluates spatial mapping and movement capabilities via text. The model must determine if the Fox can execute an orthogonal jump capture into an empty cell (.) directly behind a goose.

🧪 Water Jug Riddle
- What it does: Simulates two fluid containers with fixed maximum capacities undergoing sequential filling, emptying, and pouring operations.
- The Logic Challenge: Evaluates state-space tracking and simple arithmetic limits. The model tracks the fluid shifts across all steps to report the final volume in a target jug.

🎴 Eleusis / Zendo
- What it does: Simulates an inductive card-playing sequence where card groupings are systematically categorized as VALID or INVALID based on an unrevealed rule.
- The Logic Challenge: Tests inductive reasoning. The model must analyze the pattern across sample sequences (e.g., alternating colors or even sums) to predict the classification of a new target sequence.

🍫 Chomp
- What it does: Models a strategic grid-biting game played on a chocolate bar where taking a bite at a coordinate eats that block and everything below/to the right of it.
- The Logic Challenge: Tests coordinate grid subset operations. The model must calculate exactly how many chocolate squares remain after a specific structural bite is executed.

🔠 Anagram Word Ladder
- What it does: Evaluates a multi-step string transition path where each link must either change exactly one character or rearrange existing characters into a valid anagram.
- The Logic Challenge: Tests state-transition graph verification and lexical manipulation constraints to see if an entire word chain is entirely legal.

📡 Battleship Radar
- What it does: Replicates a geometric triangulation mechanic where an active sonar log reports the exact Manhattan distances from multiple ping points to a single hidden target.
- The Logic Challenge: Tests system linear constraint overlap solving. The model must cross-reference distance spheres to find the exact target coordinate intersection.

📦 Bloxorz Mini
- What it does: Tracks a $1 \times 1 \times 2$ rectangular block rolling directionally across a coordinate matrix plane.
- The Logic Challenge: Tests complex 3D spatial transformation mapping using pure text. The model computes successive rolls to predict whether the block finishes standing vertical or lying horizontal.

🎛️ Black Box
- What it does: Simulates straight-line ray tracing inside a hidden matrix container where lasers fired into the sides are either absorbed or exit safely.
- The Logic Challenge: Tests physics-based deflection modeling. The model evaluates whether a targeted position contains a hidden particle based on side-entry laser results.

🚪 Monty Hall Game Tree
- What it does: Sets up a classic conditional probability scenario involving three doors, an initial player choice, and a host reveal.
- The Logic Challenge: Tests branching tree validation and decision logic. The model verifies whether executing a switching move results in a definitive success.
