# -*- coding: utf-8 -*-

import json
import random
from typing import Any, Dict, List

class NimDataset:
    """
    A standard Reasoning Gym dataset class for the game of Nim.
    Outputs the strict schema: { "question": str, "answer": str, "metadata": dict }
    """
    def __init__(self, min_piles: int = 3, max_piles: int = 4, max_pile_size: int = 7, seed: int = 42):
        self.min_piles = min_piles
        self.max_piles = max_piles
        self.max_pile_size = max_pile_size
        self.rng = random.Random(seed)

    def _generate_puzzle_instance(self) -> Dict[str, Any]:
        num_piles = self.rng.randint(self.min_piles, self.max_piles)
        
        # Generate random sizes for the piles, avoiding all-empty boards
        while True:
            piles = [self.rng.randint(1, self.max_pile_size) for _ in range(num_piles)]
            if sum(piles) > 0:
                break
        
        # Calculate the nim-sum (bitwise XOR sum of all pile sizes)
        nim_sum = 0
        for pile in piles:
            nim_sum ^= pile
            
        # Standard Normal Play Nim Rule: If nim-sum != 0, it's a winning position.
        # If nim-sum == 0, it's a losing position.
        expected_answer = "winning" if nim_sum != 0 else "losing"
        
        piles_display = ", ".join([f"Pile {i+1}: {count} objects" for i, count in enumerate(piles)])
        
        question_string = (
            f"You are evaluating a strategic board state in the game of Nim.\n\n"
            f"Current Board State:\n"
            f"[{piles_display}]\n\n"
            f"Rules:\n"
            f"- On their turn, a player must remove any number of objects (at least one) from a single pile.\n"
            f"- The game follows normal play convention: the player who takes the very last object wins.\n"
            f"- A 'winning' position means the current player can force a win under optimal play.\n"
            f"- A 'losing' position means no matter what move the current player makes, the opponent can force a win.\n\n"
            f"Is the current board state a winning or losing position for the player whose turn it is?\n"
            f"Answer with exactly 'winning' or 'losing' without extra text or punctuation."
        )
        
        return {
            "question": question_string,
            "answer": expected_answer,
            "metadata": {
                "piles": piles,
                "nim_sum": nim_sum,
                "is_winning": nim_sum != 0
            }
        }

    def generate_records(self, size: int) -> List[Dict[str, Any]]:
        return [self._generate_puzzle_instance() for _ in range(size)]


def export_all_datasets(size=1000, seed=42):
    # 1. Export Nim
    print(f"Generating {size} Nim dataset records...")
    nim_gen = NimDataset(seed=seed)
    nim_records = nim_gen.generate_records(size)
    with open("nim_gym.jsonl", "w", encoding="utf-8") as f:
        for entry in nim_records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    export_all_datasets(size=1000)
