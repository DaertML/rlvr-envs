# -*- coding: utf-8 -*-

import json
import random
from typing import Any, Dict, List

class WaterJugDataset:
    """
    A standard Reasoning Gym dataset class for the Water Jug arithmetic riddle.
    Outputs the strict schema: { "question": str, "answer": str, "metadata": dict }
    """
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def _generate_puzzle_instance(self) -> Dict[str, Any]:
        # 1. Randomly assign distinct coprime-leaning max capacities to the jugs to make it interesting
        cap_a = self.rng.choice([3, 4, 5])
        cap_b = self.rng.choice([5, 6, 7, 8])
        while cap_a == cap_b:
            cap_b = self.rng.choice([5, 6, 7, 8])

        # Initial state: both jugs start empty
        vol_a = 0
        vol_b = 0

        # Define the set of valid physical operations
        # "FILL_A", "FILL_B", "EMPTY_A", "EMPTY_B", "POUR_A_TO_B", "POUR_B_TO_A"
        operations_pool = ["FILL_A", "FILL_B", "POUR_A_TO_B", "POUR_B_TO_A"]
        
        num_steps = self.rng.randint(3, 5)
        history_logs = []
        
        # 2. Simulate the tracking steps sequentially
        for _ in range(num_steps):
            op = self.rng.choice(operations_pool)
            
            if op == "FILL_A":
                vol_a = cap_a
                history_logs.append(f"Fill Jug A to its maximum capacity.")
            elif op == "FILL_B":
                vol_b = cap_b
                history_logs.append(f"Fill Jug B to its maximum capacity.")
            elif op == "POUR_A_TO_B":
                # Pour from A to B until B is full or A is empty
                space_in_b = cap_b - vol_b
                amount_poured = min(vol_a, space_in_b)
                vol_a -= amount_poured
                vol_b += amount_poured
                history_logs.append("Pour water from Jug A into Jug B until either Jug B is full or Jug A is empty.")
            elif op == "POUR_B_TO_A":
                # Pour from B to A until A is full or B is empty
                space_in_a = cap_a - vol_a
                amount_poured = min(vol_b, space_in_a)
                vol_b -= amount_poured
                vol_a += amount_poured
                history_logs.append("Pour water from Jug B into Jug A until either Jug A is full or Jug B is empty.")

        # 3. Choose which jug will be the target of our test question
        target_jug = self.rng.choice(["A", "B"])
        expected_answer = str(vol_a) if target_jug == "A" else str(vol_b)

        # 4. Construct the question string layout
        steps_display = "\n".join([f"{i+1}. {step}" for i, step in enumerate(history_logs)])

        question_string = (
            f"You are presented with a fluid measurement logic puzzle.\n\n"
            f"Initial Setup:\n"
            f"- Jug A has a maximum capacity of {cap_a} liters and is initially empty (0L).\n"
            f"- Jug B has a maximum capacity of {cap_b} liters and is initially empty (0L).\n\n"
            f"A sequence of actions is performed in order:\n"
            f"{steps_display}\n\n"
            f"After completing all the steps listed above, exactly how many liters of water are remaining in Jug {target_jug}?\n"
            f"Answer with exactly the digit representing the volume number without units or extra text."
        )

        return {
            "question": question_string,
            "answer": expected_answer,
            "metadata": {
                "jug_a_max": cap_a,
                "jug_b_max": cap_b,
                "final_vol_a": vol_a,
                "final_vol_b": vol_b,
                "question_target": target_jug,
                "executed_steps_count": num_steps
            }
        }

    def generate_records(self, size: int) -> List[Dict[str, Any]]:
        return [self._generate_puzzle_instance() for _ in range(size)]

def export_waterjug_dataset(size=1000, seed=42, file_name="waterjug_gym.jsonl"):
    print(f"Generating {size} text-based Water Jug volume simulation tasks...")
    
    generator = WaterJugDataset(seed=seed)
    records = generator.generate_records(size)

    with open(file_name, "w", encoding="utf-8") as f:
        for entry in records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Successfully exported dataset directly to {file_name}!")

if __name__ == "__main__":
    export_waterjug_dataset(size=1000)
