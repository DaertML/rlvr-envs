# -*- coding: utf-8 -*-

import json
import random
from typing import Any, Dict, List

class BattleshipRadarDataset:
    """
    A standard Reasoning Gym dataset class for Battleship Radar triangulation.
    Outputs the strict schema: { "question": str, "answer": str, "metadata": dict }
    """
    def __init__(self, grid_size: int = 5, seed: int = 42):
        self.grid_size = grid_size
        self.rng = random.Random(seed)

    def _manhattan_distance(self, p1: tuple, p2: tuple) -> int:
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def _generate_puzzle_instance(self) -> Dict[str, Any]:
        # Place the hidden submarine
        sub_r = self.rng.randint(0, self.grid_size - 1)
        sub_c = self.rng.randint(0, self.grid_size - 1)
        sub_pos = (sub_r, sub_c)

        # Generate a pair of distinct sonar query positions
        all_cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]
        pings = self.rng.sample(all_cells, k=2)

        # Compute distances
        dist1 = self._manhattan_distance(pings[0], sub_pos)
        dist2 = self._manhattan_distance(pings[1], sub_pos)

        expected_answer = f"({sub_r}, {sub_c})"

        question_string = (
            f"You are triangulating an enemy submarine using a grid radar system.\n\n"
            f"Sonar Radar Log:\n"
            f"- Ping at coordinate ({pings[0][0]}, {pings[0][1]}) reports a Manhattan distance of {dist1} units.\n"
            f"- Ping at coordinate ({pings[1][0]}, {pings[1][1]}) reports a Manhattan distance of {dist2} units.\n\n"
            f"Note: Manhattan distance is calculated as abs(row1 - row2) + abs(col1 - col2) on a {self.grid_size}x{self.grid_size} grid (0 to {self.grid_size-1}).\n\n"
            f"Based on these intersection vectors, what is the exact coordinate where the submarine is hiding?\n"
            f"Answer exactly in the format '(row, col)' without extra text or spaces."
        )

        return {
            "question": question_string,
            "answer": expected_answer,
            "metadata": {
                "grid_size": self.grid_size,
                "submarine_position": sub_pos,
                "pings": pings,
                "distances": [dist1, dist2]
            }
        }

    def generate_records(self, size: int) -> List[Dict[str, Any]]:
        return [self._generate_puzzle_instance() for _ in range(size)]


if __name__ == "__main__":
    generator = BattleshipRadarDataset(seed=42)
    records = generator.generate_records(1000)
    with open("battleship_radar_gym.jsonl", "w", encoding="utf-8") as f:
        for entry in records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("Exported battleship_radar_gym.jsonl successfully.")
