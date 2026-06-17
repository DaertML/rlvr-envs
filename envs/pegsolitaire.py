# -*- coding: utf-8 -*-

import json
import random
from typing import Any, Dict, List

class PegSolitaireDataset:
    """
    A standard Reasoning Gym dataset class for Peg Solitaire.
    Outputs the strict schema: { "question": str, "answer": str, "metadata": dict }
    """
    def __init__(self, array_length: int = 6, seed: int = 42):
        self.array_length = array_length
        self.rng = random.Random(seed)

    def _generate_puzzle_instance(self) -> Dict[str, Any]:
        while True:
            # Build a random 1D peg array layout
            # P = Peg, . = Empty Hole
            board = [self.rng.choice(["P", "."]) for _ in range(self.array_length)]
            
            # Look for legal moves: either index jumps right (P P .) or left (. P P)
            legal_jumps = []
            for i in range(self.array_length):
                # Right jump check
                if i <= self.array_length - 3:
                    if board[i] == "P" and board[i+1] == "P" and board[i+2] == ".":
                        legal_jumps.append((i, i+1, i+2, "Right"))
                # Left jump check
                if i >= 2:
                    if board[i] == "P" and board[i-1] == "P" and board[i-2] == ".":
                        legal_jumps.append((i, i-1, i-2, "Left"))

            # Loop until we find an initial arrangement that contains a valid operational jump step
            if legal_jumps:
                selected_jump = self.rng.choice(legal_jumps)
                start, over, land, direction = selected_jump
                
                # Compute the transformed final board state configuration
                final_board = board[:]
                final_board[start] = "."
                final_board[over] = "."
                final_board[land] = "P"
                
                break

        board_display = " ".join(board)
        indices_display = " ".join([str(x) for x in range(self.array_length)])
        expected_answer = " ".join(final_board)

        question_string = (
            f"You are simulating a linear tracking step in Peg Solitaire.\n\n"
            f"Initial Layout:\n"
            f"Board Cells:   {board_display}\n"
            f"Index Labels:  {indices_display}\n\n"
            f"Legend:\n"
            f"- 'P' represents a slot holding a peg.\n"
            f"- '.' represents an empty open hole.\n\n"
            f"Rules:\n"
            f"- A move is made by a peg jumping over an adjacent peg orthogonally into an empty hole.\n"
            f"- The peg that was jumped over is removed from the board entirely.\n\n"
            f"Action: Execute a move where the peg at index {start} jumps over index {over} and lands in the empty hole at index {land}.\n\n"
            f"What will the layout array look like after completing this operation? "
            f"Provide your answer exactly as a space-separated string of characters (e.g., 'P . . P . P') without formatting or brackets."
        )

        return {
            "question": question_string,
            "answer": expected_answer,
            "metadata": {
                "initial_board": board,
                "executed_jump": {
                    "from_index": start,
                    "over_index": over,
                    "landing_index": land,
                    "direction": direction
                },
                "final_board": final_board
            }
        }

    def generate_records(self, size: int) -> List[Dict[str, Any]]:
        return [self._generate_puzzle_instance() for _ in range(size)]


# Standalone Export Hook
if __name__ == "__main__":
    generator = PegSolitaireDataset(seed=42)
    records = generator.generate_records(1000)
    with open("peg_solitaire_gym.jsonl", "w", encoding="utf-8") as f:
        for entry in records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("Exported peg_solitaire_gym.jsonl successfully.")
