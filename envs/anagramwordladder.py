# -*- coding: utf-8 -*-

import json
import random
from typing import Any, Dict, List

class AnagramLadderDataset:
    """
    A standard Reasoning Gym dataset class for Anagram Word Ladders.
    Outputs the strict schema: { "question": str, "answer": str, "metadata": dict }
    """
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        # Small controlled dictionary of valid 4-letter words to guarantee perfect checking
        self.valid_words = {"TEAM", "MEAT", "MEET", "MELT", "MOUT", "MOST", "POST", "STOP", "SPOT", "POTS", "SOLD", "GOLD", "COLD", "CORD", "CARD"}

    def _is_single_letter_change(self, w1: str, w2: str) -> bool:
        if len(w1) != len(w2):
            return False
        diffs = sum(1 for c1, c2 in zip(w1, w2) if c1 != c2)
        return diffs == 1

    def _is_anagram_change(self, w1: str, w2: str) -> bool:
        return sorted(w1) == sorted(w2) and w1 != w2

    def _generate_puzzle_instance(self) -> Dict[str, Any]:
        # Procedurally build or pull a sequence path trace
        # We define a few structured ground truth sequences
        paths_pool = [
            ["TEAM", "MEAT", "MEET", "MELT"],
            ["STOP", "SPOT", "POTS", "POST"],
            ["GOLD", "SOLD", "COLD", "CORD", "CARD"]
        ]
        
        selected_path = self.rng.choice(paths_pool)
        is_valid_puzzle = self.rng.choice([True, False])
        
        display_path = selected_path[:]
        
        if not is_valid_puzzle:
            # Inject an illegal modification step into the path
            break_idx = self.rng.randint(1, len(display_path) - 1)
            # Replace it with a broken non-connected node token string
            display_path[break_idx] = "GOLD" if display_path[break_idx] != "GOLD" else "TEAM"

        # Check path state integrity step by step
        path_validity = True
        for i in range(len(display_path) - 1):
            w1 = display_path[i]
            w2 = display_path[i+1]
            
            is_mutation = self._is_single_letter_change(w1, w2)
            is_anagram = self._is_anagram_change(w1, w2)
            
            if not (is_mutation or is_anagram):
                path_validity = False
                break

        expected_answer = "yes" if path_validity else "no"
        path_string = " -> ".join(display_path)

        question_string = (
            f"You are evaluating a word mutation link path in an Anagram Word Ladder puzzle.\n\n"
            f"Proposed Transition Chain:\n"
            f"{path_string}\n\n"
            f"Rules:\n"
            f"- A step is valid if you change exactly ONE letter while keeping the order the same (e.g., COLD -> CORD).\n"
            f"- A step is also valid if you rearrange the exact same letters to form a direct anagram of the word (e.g., TEAM -> MEAT).\n\n"
            f"Is the proposed transition chain listed above entirely legal and valid from start to finish according to these rules?\n"
            f"Answer with exactly 'yes' or 'no' without punctuation."
        )

        return {
            "question": question_string,
            "answer": expected_answer,
            "metadata": {
                "chain_rendered": display_path,
                "is_structurally_valid": path_validity
            }
        }

    def generate_records(self, size: int) -> List[Dict[str, Any]]:
        return [self._generate_puzzle_instance() for _ in range(size)]


# Standalone Export Hook
if __name__ == "__main__":
    generator = AnagramLadderDataset(seed=42)
    records = generator.generate_records(1000)
    with open("anagram_ladder_gym.jsonl", "w", encoding="utf-8") as f:
        for entry in records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("Exported anagram_ladder_gym.jsonl successfully.")
