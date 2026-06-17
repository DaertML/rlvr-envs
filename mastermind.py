import json
import random

def generate_mastermind_puzzle(game_id, code_length=4, num_colors=6):
    """
    Generates a single Mastermind puzzle entry with examples, 
    a test question, and metadata.
    """
    colors = [str(i) for i in range(1, num_colors + 1)] # Colors represented as '1', '2', '3'...
    
    # 1. Generate a secret code
    secret_code = [random.choice(colors) for _ in range(code_length)]
    
    def get_feedback(guess, secret):
        """Returns (black_pegs, white_pegs)"""
        blacks = sum(1 for g, s in zip(guess, secret) if g == s)
        
        # Count remaining colors for white pegs
        guess_remaining = [g for g, s in zip(guess, secret) if g != s]
        secret_remaining = [s for g, s in zip(guess, secret) if g != s]
        
        whites = 0
        for g in guess_remaining:
            if g in secret_remaining:
                whites += 1
                secret_remaining.remove(g)
        return blacks, whites

    # 2. Generate a pool of unique random guesses
    all_possible_guesses = []
    while len(all_possible_guesses) < 5:
        random_guess = [random.choice(colors) for _ in range(code_length)]
        if random_guess not in all_possible_guesses and random_guess != secret_code:
            all_possible_guesses.append(random_guess)
            
    # 3. Create historical rounds (Train Examples)
    train_examples = []
    example_text_list = []
    
    for i, guess in enumerate(all_possible_guesses[:3]): # Use 3 guesses for examples
        blacks, whites = get_feedback(guess, secret_code)
        guess_str = " ".join(guess)
        
        train_examples.append({
            "input": guess,
            "output": {"black_pegs": blacks, "white_pegs": whites}
        })
        
        example_text_list.append(
            f"Example {i+1}:\nGuess: {guess_str}\nFeedback: {blacks} Black (correct position), {whites} White (wrong position)"
        )

    examples_string = "\n\n".join(example_text_list)
    
    # 4. Create the final test scenario
    # We will give them one final guess that reveals the exact code if combined with previous clues
    test_guess = all_possible_guesses[3]
    t_blacks, t_whites = get_feedback(test_guess, secret_code)
    test_guess_str = " ".join(test_guess)
    
    # Constructing the prompt question string
    question_text = (
        f"You are playing Mastermind. The code length is {code_length} and uses colors from {colors[0]} to {colors[-1]} (duplicates allowed).\n"
        f"Based on the historic feedback below, deduce the hidden logic and rules to find the secret code.\n\n"
        f"{examples_string}\n\n"
        f"Below is your final test input guess and feedback. Combine this with the examples above to deduce the true underlying secret code.\n\n"
        f"Test Input Guess: {test_guess_str}\n"
        f"Feedback: {t_blacks} Black, {t_whites} White\n\n"
        f"Describe your step-by-step elimination process and reasoning in detail before submitting your answer. "
        f"Your final answer must be just the secret code separated by spaces (e.g., {' '.join(secret_code)})."
    )
    
    # 5. Format exactly like the requested schema
    json_entry = {
        "question": question_text,
        "answer": " ".join(secret_code),
        "metadata": {
            "source_dataset": "mastermind_gym",
            "source_index": game_id,
            "task_name": "deduce_secret_code",
            "size": code_length,
            "train_examples": train_examples,
            "test_example": {
                "input": test_guess,
                "output": {"black_pegs": t_blacks, "white_pegs": t_whites}
            },
            "difficulty": {
                "code_length": code_length,
                "num_colors": num_colors
            }
        }
    }
    
    return json_entry

# --- Execution block mimicking your reasoning_gym script loop ---
file_name = "mastermind_reasoning.jsonl"
num_puzzles_to_generate = 1000  # Adjust as needed

with open(file_name, "w", encoding="utf-8") as f:
    for i in range(num_puzzles_to_generate):
        # Generate data entry
        entry = generate_mastermind_puzzle(game_id=i, code_length=4, num_colors=6)
        
        # Map fields precisely to your structure
        json_line = {
            "question": entry.get("question"),
            "answer": str(entry.get("answer")), 
            "metadata": entry.get("metadata", {})
        }

        # Write out to JSONL line
        f.write(json.dumps(json_line, ensure_ascii=False) + "\n")

print(f"Dataset successfully exported to {file_name}")
