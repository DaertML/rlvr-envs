# -*- coding: utf-8 -*-

import json
import random
from typing import Any, Dict, List

class ChompDataset:
    """
    A standard Reasoning Gym dataset class for the game of Chomp.
    Outputs the strict schema: { "question": str, "answer": str, "metadata": dict }
    """
    def __init__(self, max_rows: int = 4, max_cols: int = 5, seed: int = 42):
        self.max_rows = max_rows
        self.max_cols = max_cols
        self.rng = random.Random(seed)

    def _generate_puzzle_instance(self) -> Dict[str, Any]:
        # Generate a random initial board shape (descending row lengths)
        rows = self.rng.randint(2, self.max_rows)
        cols = self.rng.randint(2, self.max_cols)
        
        # Start with a complete grid profile
        initial_profile = [cols] * rows
        
        # Select a random valid block to bite (avoiding the poisoned top-left 0,0 square)
        # To make it an interesting question, we pick from available squares
        bite_r = self.rng.randint(0, rows - 1)
        # Column bite must land within the current row length
        bite_c = self.rng.randint(0, initial_profile[bite_r] - 1)
        
        # If they pick (0,0), re-roll to avoid immediate poison game-over scenario
        if bite_r == 0 and bite_c == 0:
            bite_c = min(1, initial_profile[0] - 1)
            if bite_c == 0:
                bite_r = 1
                bite_c = 0

        # Calculate the post-bite cookie state
        # Rule: any cell with r >= bite_r AND c >= bite_c is eliminated
        final_profile = []
        final_count = 0
        
        for r in range(rows):
            current_len = initial_profile[r]
            if r >= bite_r:
                # Truncate the row at the bite column
                new_len = min(current_len, bite_c)
            else:
                new_len = current_len
            final_profile.append(new_len)
            final_count += new_len

        # Construct visual ASCII representation of the initial board
        grid_lines = []
        for r in range(rows):
            row_chars = ["O"] * initial_profile[r] + ["."] * (cols - initial_profile[r])
            grid_lines.append(f"Row {r}: " + " ".join(row_chars))
        grid_display = "\n".join(grid_lines)

        question_string = (
            f"You are analyzing a state in the grid-biting game of Chomp.\n\n"
            f"Current Grid Layout:\n"
            f"{grid_display}\n\n"
            f"Legend:\n"
            f"- 'O' represents a remaining chocolate block.\n"
            f"- '.' represents an empty space that was already eaten.\n"
            f"- Coordinate (0,0) at Row 0, Column 0 contains the poison block.\n\n"
            f"Rules:\n"
            f"- Choosing a block at row index R and column index C eats that block and ALL blocks below and to the right of it (any block where row >= R and column >= C).\n\n"
            f"If a player takes a bite at row index {bite_r}, column index {bite_c}, exactly how many blocks of chocolate ('O') will be left remaining on the entire board?\n"
            f"Answer with exactly the integer count without text or formatting."
        )

        return {
            "question": question_string,
            "answer": str(final_count),
            "metadata": {
                "initial_shape": initial_profile,
                "bite_coordinate": [bite_r, bite_c],
                "final_shape": final_profile,
                "remaining_count": final_count
            }
        }

    def generate_records(self, size: int) -> List[Dict[str, Any]]:
        return [self._generate_puzzle_instance() for _ in range(size)]


# Standalone Export Hook
if __name__ == "__main__":
    generator = ChompDataset(seed=42)
    records = generator.generate_records(1000)
    with open("chomp_gym.jsonl", "w", encoding="utf-8") as f:
        for entry in records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("Exported chomp_gym.jsonl successfully.")
