# -*- coding: utf-8 -*-

import json
import random
from typing import Any, Dict, List, Optional

class BattleshipView:
    def __init__(self, state="undetermined"):
        self.coordinates = []  # List of (row, col) tuples
        self.state = state

    def add_coordinates(self, coords):
        for coord in coords:
            self.coordinates.append(coord)


class BattleshipDataset:
    """
    A standard Reasoning Gym dataset class following the required output schema:
    { "question": str, "answer": str, "metadata": dict }
    """
    def __init__(self, board_size: int = 5, ship_sizes: Optional[List[int]] = None, seed: int = 42):
        self.board_size = board_size
        self.ship_sizes = ship_sizes if ship_sizes else [2, 3]
        self.rng = random.Random(seed)

    def _generate_deterministic_puzzle(self) -> Dict[str, Any]:
        """Procedurally places ships and defines clues to form a logical deduction puzzle."""
        ship_cells = set()
        water_cells = set()
        
        # Place ships cleanly without overlap
        for ship_len in sorted(self.ship_sizes, reverse=True):
            placed = False
            while not placed:
                orientation = self.rng.choice(["H", "V"])
                if orientation == "H":
                    row = self.rng.randint(0, self.board_size - 1)
                    col = self.rng.randint(0, self.board_size - ship_len)
                    coords = [(row, col + i) for i in range(ship_len)]
                else:
                    row = self.rng.randint(0, self.board_size - ship_len)
                    col = self.rng.randint(0, self.board_size - 1)
                    coords = [(row + i, col) for i in range(ship_len)]
                
                if not any(c in ship_cells for c in coords):
                    for c in coords:
                        ship_cells.add(c)
                    placed = True
                    
        for r in range(self.board_size):
            for c in range(self.board_size):
                if (r, c) not in ship_cells:
                    water_cells.add((r, c))

        # Core context items matching original design logic
        known_hit = list(ship_cells)[0]
        known_miss = list(water_cells)[0]
        
        remaining_water = list(water_cells.difference({known_miss}))
        extra_misses = self.rng.sample(remaining_water, k=min(2, len(remaining_water)))
        all_misses = [known_miss] + extra_misses

        remaining_ships = list(ship_cells.difference({known_hit}))
        target_indirect_hit = remaining_ships[0]
        
        # Mix the target indirect hit with a known miss coordinate to force an elimination step
        mixed_clue_coords = [target_indirect_hit, known_miss]

        # Select a target for the test question (either direct or indirect logical deduction)
        q_type = self.rng.choice(["direct_hit", "indirect_hit", "direct_miss"])
        
        if q_type == "direct_hit":
            target_coord = known_hit
            expected_answer = "hit"
        elif q_type == "indirect_hit":
            target_coord = target_indirect_hit
            expected_answer = "hit"
        else:
            target_coord = known_miss
            expected_answer = "miss"

        # Construct the clear text context for the reasoning engine
        clues_text = [
            f"Shot at {known_hit} resulted in a: hit",
            f"Shot at {known_miss} resulted in a: miss",
            f"Group strike at coordinates {extra_misses} resulted in a: miss",
            f"Group strike at coordinates {mixed_clue_coords} confirmed a: hit"
        ]
        self.rng.shuffle(clues_text)
        
        context_string = "\n".join([f"- {clue}" for clue in clues_text])
        question_string = (
            f"Based on the following past history logs from a Battleship game:\n"
            f"{context_string}\n\n"
            f"Deduce the state of the cell at coordinate {target_coord}. "
            f"Answer with exactly 'hit' or 'miss' without formatting."
        )

        return {
            "question": question_string,
            "answer": expected_answer,
            "metadata": {
                "board_size": self.board_size,
                "question_type": q_type,
                "target_coordinate": target_coord,
                "hidden_ships": list(ship_cells)
            }
        }

    def generate_records(self, size: int) -> List[Dict[str, Any]]:
        return [self._generate_deterministic_puzzle() for _ in range(size)]

def export_reasoning_gym_dataset(size=1000, seed=42, file_name="battleship_gym.jsonl"):
    print(f"Generating {size} true 'Reasoning Gym' schema records...")
    
    dataset_generator = BattleshipDataset(board_size=5, ship_sizes=[2, 3], seed=seed)
    records = dataset_generator.generate_records(size)

    with open(file_name, "w", encoding="utf-8") as f:
        for entry in records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Successfully wrote data records to {file_name}!")

if __name__ == "__main__":
    export_reasoning_gym_dataset(size=1000)
