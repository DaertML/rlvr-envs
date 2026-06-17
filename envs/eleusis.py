# -*- coding: utf-8 -*-

import json
import random
from typing import Any, Dict, List

class EleusisZendoDataset:
    """
    A standard Reasoning Gym dataset class for Eleusis/Zendo inductive logic.
    Outputs the strict schema: { "question": str, "answer": str, "metadata": dict }
    """
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.suits = ["Hearts", "Diamonds", "Clubs", "Spades"]

    def _eval_rule(self, rule_type: str, seq: List[Dict[str, Any]]) -> bool:
        """Evaluates whether a sequence matches a secret rule."""
        if len(seq) < 3:
            return False
            
        if rule_type == "alternating_color":
            # Rule: Card colors must strictly alternate (Hearts/Diamonds vs Clubs/Spades)
            is_red = [c["suit"] in ["Hearts", "Diamonds"] for c in seq]
            return all(is_red[i] != is_red[i-1] for i in range(1, len(is_red)))
            
        elif rule_type == "strictly_increasing":
            # Rule: Each card's numerical value must be strictly greater than the previous
            return all(seq[i]["value"] > seq[i-1]["value"] for i in range(1, len(seq)))
            
        elif rule_type == "even_sum":
            # Rule: The sum of all cards in the sequence must be an even number
            return sum(c["value"] for c in seq) % 2 == 0
            
        return False

    def _generate_card(self) -> Dict[str, Any]:
        return {
            "value": self.rng.randint(1, 10),
            "suit": self.rng.choice(self.suits)
        }

    def _generate_sequence(self, length: int = 3) -> List[Dict[str, Any]]:
        return [self._generate_card() for _ in range(length)]

    def _format_seq(self, seq: List[Dict[str, Any]]) -> str:
        return " -> ".join([f"[{c['value']} of {c['suit']}]" for c in seq])

    def _generate_puzzle_instance(self) -> Dict[str, Any]:
        # Choose a rule type
        rule_type = self.rng.choice(["alternating_color", "strictly_increasing", "even_sum"])
        rule_descriptions = {
            "alternating_color": "Card colors must strictly alternate between Red (Hearts/Diamonds) and Black (Clubs/Spades).",
            "strictly_increasing": "The numerical values of the cards must be strictly increasing.",
            "even_sum": "The sum of all card values in the sequence must be an even number."
        }

        valid_examples = []
        invalid_examples = []
        
        # Gather distinct historical traces demonstrating the pattern
        while len(valid_examples) < 2 or len(invalid_examples) < 2:
            test_seq = self._generate_sequence(length=3)
            is_valid = self._eval_rule(rule_type, test_seq)
            formatted = self._format_seq(test_seq)
            
            if is_valid and len(valid_examples) < 2 and formatted not in valid_examples:
                valid_examples.append(formatted)
            elif not is_valid and len(invalid_examples) < 2 and formatted not in invalid_examples:
                invalid_examples.append(formatted)

        # Generate the ultimate test sequence for the question
        target_seq = self._generate_sequence(length=3)
        expected_answer = "valid" if self._eval_rule(rule_type, target_seq) else "invalid"
        target_display = self._format_seq(target_seq)

        # Mix the trace lines to provide a balanced historical data stream
        history_lines = (
            [f"- Sequence: {ex} -> Status: VALID" for ex in valid_examples] +
            [f"- Sequence: {ex} -> Status: INVALID" for ex in invalid_examples]
        )
        self.rng.shuffle(history_lines)
        history_display = "\n".join(history_lines)

        question_string = (
            f"You are analyzing a research log from a game of Eleusis/Zendo.\n"
            f"A secret dealer rule governs whether a card sequence sequence is accepted.\n\n"
            f"Historical Observation Data:\n"
            f"{history_display}\n\n"
            f"Task:\n"
            f"Identify the underlying pattern linking the valid rows, and evaluate this specific new target sequence:\n"
            f"New Sequence: {target_display}\n\n"
            f"Based on the hidden rule, is this new sequence 'valid' or 'invalid'?\n"
            f"Answer with exactly 'valid' or 'invalid' without extra punctuation."
        )

        return {
            "question": question_string,
            "answer": expected_answer,
            "metadata": {
                "hidden_rule_category": rule_type,
                "ground_truth_rule": rule_descriptions[rule_type],
                "target_sequence_data": target_seq
            }
        }

    def generate_records(self, size: int) -> List[Dict[str, Any]]:
        return [self._generate_puzzle_instance() for _ in range(size)]

def export_all_datasets(size=1000, seed=42):
# 2. Export Eleusis/Zendo
    print(f"Generating {size} Eleusis/Zendo dataset records...")
    eleusis_gen = EleusisZendoDataset(seed=seed)
    eleusis_records = eleusis_gen.generate_records(size)
    with open("eleusiszendo_gym.jsonl", "w", encoding="utf-8") as f:
        for entry in eleusis_records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    export_all_datasets(size=1000)
