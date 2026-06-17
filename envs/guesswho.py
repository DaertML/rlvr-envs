# -*- coding: utf-8 -*-

import json
import random
from typing import Any, Dict, List

class GuessWhoDataset:
    """
    A standard Reasoning Gym dataset class for Guess Who deductive reasoning.
    Outputs the strict schema: { "question": str, "answer": str, "metadata": dict }
    """
    def __init__(self, pool_size: int = 5, seed: int = 42):
        self.pool_size = pool_size
        self.rng = random.Random(seed)
        
        # Universal attribute definitions
        self.attributes = ["Hat", "Glasses", "Beard", "Earrings"]
        
        # A static dictionary of characters and their traits for consistent generation
        self.character_pool = [
            {"name": "Alex", "Hat": True, "Glasses": False, "Beard": True, "Earrings": False},
            {"name": "Anita", "Hat": False, "Glasses": True, "Beard": False, "Earrings": True},
            {"name": "Bernard", "Hat": True, "Glasses": False, "Beard": True, "Earrings": True},
            {"name": "Claire", "Hat": True, "Glasses": True, "Beard": False, "Earrings": True},
            {"name": "Dennis", "Hat": False, "Glasses": False, "Beard": True, "Earrings": False},
            {"name": "Eva", "Hat": False, "Glasses": True, "Beard": False, "Earrings": False},
            {"name": "Franz", "Hat": True, "Glasses": True, "Beard": True, "Earrings": False},
            {"name": "Grace", "Hat": False, "Glasses": False, "Beard": False, "Earrings": True},
        ]

    def _generate_puzzle_instance(self) -> Dict[str, Any]:
        # 1. Sample a dynamic subset of active characters for this puzzle instance
        active_characters = self.rng.sample(self.character_pool, k=self.pool_size)
        
        # 2. Pick one to be the hidden secret target
        target_char = self.rng.choice(active_characters)
        
        # 3. Procedurally generate historical question-and-answer logs
        # We sample 2 distinct attributes to query
        sampled_attrs = self.rng.sample(self.attributes, k=2)
        clues_text = []
        
        # Track characters who survive the clues logically
        candidates = active_characters[:]
        
        for attr in sampled_attrs:
            # Determine the correct true/false answer for the secret target
            has_attr = target_char[attr]
            answer_str = "Yes" if has_attr else "No"
            
            clues_text.append(f"Question: Is the target wearing/having a {attr}? -> Answer: {answer_str}")
            
            # Filter the candidates list based on this feedback log
            candidates = [c for c in candidates if c[attr] == has_attr]

        # 4. Pick a subject character for the final test question
        # We pick either an eliminated character, a surviving candidate, or a random pool member
        test_subject = self.rng.choice(active_characters)
        
        # Determine the ground truth evaluation answer
        # Is the subject definitively the target, completely eliminated, or undetermined?
        if test_subject not in candidates:
            expected_answer = "eliminated"
        elif len(candidates) == 1 and test_subject == target_char:
            expected_answer = "target"
        else:
            expected_answer = "undetermined"

        # 5. Format character profiles as an easy-to-read layout reference string
        profiles_list = []
        for c in active_characters:
            traits = [f"{attr}: {'Yes' if c[attr] else 'No'}" for attr in self.attributes]
            profiles_list.append(f"- {c['name']} -> ({', '.join(traits)})")
        
        profiles_display = "\n".join(profiles_list)
        context_clues = "\n".join(clues_text)

        question_string = (
            f"You are evaluating a deductive sorting log from a game of Guess Who.\n\n"
            f"Active Character Roster:\n"
            f"{profiles_display}\n\n"
            f"Historical Match Clues:\n"
            f"{context_clues}\n\n"
            f"Based strictly on boolean set elimination from the clues above, what is the logical status of character '{test_subject['name']}'?\n"
            f"Answer with exactly 'target' (if they are the only remaining candidate), 'eliminated' (if they violate the clues), or 'undetermined' (if they match the clues but aren't uniquely isolated yet)."
        )

        return {
            "question": question_string,
            "answer": expected_answer,
            "metadata": {
                "active_roster": [c["name"] for c in active_characters],
                "secret_target": target_char["name"],
                "remaining_candidates": [c["name"] for c in candidates],
                "test_subject": test_subject["name"]
            }
        }

    def generate_records(self, size: int) -> List[Dict[str, Any]]:
        return [self._generate_puzzle_instance() for _ in range(size)]

def export_guesswho_dataset(size=1000, seed=42, file_name="guesswho_gym.jsonl"):
    print(f"Generating {size} text-based Guess Who elimination tasks...")
    
    generator = GuessWhoDataset(pool_size=5, seed=seed)
    records = generator.generate_records(size)

    with open(file_name, "w", encoding="utf-8") as f:
        for entry in records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Successfully exported dataset directly to {file_name}!")

if __name__ == "__main__":
    export_guesswho_dataset(size=1000)
