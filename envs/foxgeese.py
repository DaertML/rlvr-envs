# -*- coding: utf-8 -*-

import json
import random
from typing import Any, Dict, List

class FoxAndGeeseDataset:
    """
    A standard Reasoning Gym dataset class for Fox and Geese deductive reasoning.
    Outputs the strict schema: { "question": str, "answer": str, "metadata": dict }
    """
    def __init__(self, board_size: int = 5, seed: int = 42):
        # Using a 5x5 grid cross layout for simplicity
        self.board_size = board_size
        self.rng = random.Random(seed)

    def _get_valid_directions(self) -> List[tuple]:
        """Returns standard orthogonal move vectors (Up, Down, Left, Right)."""
        return [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def _is_in_bounds(self, r: int, c: int) -> bool:
        """Verifies if a coordinate falls within the valid cross-shaped board boundaries."""
        # Simple cross-shape rule: corners of a 5x5 grid are invalid.
        # Valid if not in the (0,0)-(1,1), (0,3)-(1,4), (3,0)-(4,1), or (3,3)-(4,4) corners.
        if (r < 2 or r > 2) and (c < 2 or c > 2):
            return False
        return 0 <= r < self.board_size and 0 <= c < self.board_size

    def _generate_puzzle_instance(self) -> Dict[str, Any]:
        # Generate all valid coordinates on the cross board
        valid_coords = [(r, c) for r in range(self.board_size) for c in range(self.board_size) if self._is_in_bounds(r, c)]
        
        # Decide procedurally whether this specific instance will have a valid capture available
        has_valid_capture = self.rng.choice([True, False])
        
        while True:
            # Pick a random spot for the Fox
            fox_coord = self.rng.choice(valid_coords)
            
            geese_coords = set()
            directions = self._get_valid_directions()
            capture_found = False
            
            if has_valid_capture:
                # Force-inject a valid capture path configuration
                self.rng.shuffle(directions)
                for dr, dc in directions:
                    goose_r, goose_c = fox_coord[0] + dr, fox_coord[1] + dc
                    land_r, land_c = fox_coord[0] + (dr * 2), fox_coord[1] + (dc * 2)
                    
                    if self._is_in_bounds(goose_r, goose_c) and self._is_in_bounds(land_r, land_c):
                        geese_coords.add((goose_r, goose_c))
                        capture_found = True
                        break
                
                if not capture_found:
                    continue  # Retry if the chosen fox location couldn't support a jump bounds-wise
            
            # Fill out the rest of the board with a random number of background distraction geese
            num_extra_geese = self.rng.randint(2, 6)
            potential_extra_spots = [c for c in valid_coords if c != fox_coord and c not in geese_coords]
            
            # Ensure if we wanted a NO capture board, we don't accidentally create a jump path
            extra_samples = self.rng.sample(potential_extra_spots, k=min(num_extra_geese, len(potential_extra_spots)))
            for spot in extra_samples:
                # If we're strictly aiming for no capture, reject spots that form a jump sequence
                if not has_valid_capture:
                    is_accidental_jump = False
                    for dr, dc in directions:
                        neighbor = (fox_coord[0] + dr, fox_coord[1] + dc)
                        landing = (fox_coord[0] + (dr * 2), fox_coord[1] + (dc * 2))
                        if spot == neighbor and self._is_in_bounds(landing[0], landing[1]):
                            # This spot could create a jump if the landing area stays clear. We look broadly:
                            is_accidental_jump = True
                    if is_accidental_jump:
                        continue
                geese_coords.add(spot)

            # Final validation check: verify the actual final state matches our target binary expectation
            actual_capture_available = False
            for dr, dc in directions:
                goose_pos = (fox_coord[0] + dr, fox_coord[1] + dc)
                land_pos = (fox_coord[0] + (dr * 2), fox_coord[1] + (dc * 2))
                if goose_pos in geese_coords and self._is_in_bounds(land_pos[0], land_pos[1]) and land_pos not in geese_coords and land_pos != fox_coord:
                    actual_capture_available = True
                    break
            
            if actual_capture_available == has_valid_capture:
                expected_answer = "yes" if actual_capture_available else "no"
                break

        # 4. Render the spatial grid into an easy-to-read textual layout map
        board_lines = []
        for r in range(self.board_size):
            row_chars = []
            for c in range(self.board_size):
                coord = (r, c)
                if not self._is_in_bounds(r, c):
                    row_chars.append(" ")  # Out of bounds corners space
                elif coord == fox_coord:
                    row_chars.append("F")  # Fox
                elif coord in geese_coords:
                    row_chars.append("G")  # Goose
                else:
                    row_chars.append(".")  # Empty functional cross space
            board_lines.append(" ".join(row_chars))

        grid_display = "\n".join(board_lines)

        question_string = (
            f"You are evaluating a spatial tracking snapshot of a Fox and Geese match layout:\n\n"
            f"{grid_display}\n\n"
            f"Legend:\n"
            f"- 'F' represents the Fox.\n"
            f"- 'G' represents a Goose.\n"
            f"- '.' represents an empty playable cell.\n"
            f"- Empty space indicates out-of-bounds corners.\n\n"
            f"Rules: The Fox can capture a adjacent Goose orthogonally (Up, Down, Left, Right) if there is an empty space ('.') directly behind that Goose to land on.\n\n"
            f"Based on the text layout map above, can the Fox execute a legal capture jump on its turn?\n"
            f"Answer with exactly 'yes' or 'no' without punctuation."
        )

        return {
            "question": question_string,
            "answer": expected_answer,
            "metadata": {
                "board_size": self.board_size,
                "fox_location": fox_coord,
                "geese_locations": list(geese_coords),
                "capture_possible": actual_capture_available
            }
        }

    def generate_records(self, size: int) -> List[Dict[str, Any]]:
        return [self._generate_puzzle_instance() for _ in range(size)]

def export_foxandgeese_dataset(size=1000, seed=42, file_name="foxandgeese_gym.jsonl"):
    print(f"Generating {size} text-based Fox and Geese spatial reasoning tasks...")
    
    generator = FoxAndGeeseDataset(board_size=5, seed=seed)
    records = generator.generate_records(size)

    with open(file_name, "w", encoding="utf-8") as f:
        for entry in records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Successfully exported dataset directly to {file_name}!")

if __name__ == "__main__":
    export_foxandgeese_dataset(size=1000)
