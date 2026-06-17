# -*- coding: utf-8 -*-

import json
import random
from typing import Any, Dict, List

class MinesweeperDataset:
    """
    A standard Reasoning Gym dataset class for Minesweeper deductive reasoning.
    Outputs the strict schema: { "question": str, "answer": str, "metadata": dict }
    """
    def __init__(self, grid_size: int = 5, num_mines: int = 5, seed: int = 42):
        self.grid_size = grid_size
        self.num_mines = num_mines
        self.rng = random.Random(seed)

    def _get_neighbors(self, r: int, c: int) -> List[tuple]:
        """Returns valid 8-directional neighboring coordinates."""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                    neighbors.append((nr, nc))
        return neighbors

    def _generate_puzzle_instance(self) -> Dict[str, Any]:
        """Procedurally creates a solvable local Minesweeper logical deduction step."""
        while True:
            # 1. Place mines randomly
            all_cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]
            mine_cells = set(self.rng.sample(all_cells, k=self.num_mines))
            
            # 2. Compute full game board numbers
            full_board = [[0] * self.grid_size for _ in range(self.grid_size)]
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    if (r, c) in mine_cells:
                        full_board[r][c] = -1  # -1 represents a mine
                    else:
                        # Count neighboring mines
                        neighbors = self._get_neighbors(r, c)
                        full_board[r][c] = sum(1 for nr, nc in neighbors if (nr, nc) in mine_cells)

            # 3. Look for a solvable target cell using basic Minesweeper logic rules
            # Rule A: If a revealed 'N' touches exactly N unrevealed squares, all those squares are MINES.
            # Rule B: If a revealed 'N' already touches N flagged/known mines, all other unrevealed neighbors are SAFE.
            
            solvable_targets = []
            
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    if (r, c) in mine_cells:
                        continue
                        
                    val = full_board[r][c]
                    if val <= 0:
                        continue  # Skip 0s for this puzzle variant to keep it challenging
                        
                    neighbors = self._get_neighbors(r, c)
                    unrevealed_neighbors = neighbors[:] # At start, treat neighbors as unrevealed
                    
                    # Scenario 1: Force all unrevealed neighbors to be mines (Rule A)
                    # We flag all neighbors except one as known mines to test the rule
                    if len(neighbors) > val:
                        target_cell = neighbors[0]
                        assumed_mines = neighbors[1:val+1]
                        
                        # Verify this specific setup aligns with actual ground truth
                        if target_cell in mine_cells and all(m in mine_cells for m in assumed_mines):
                            solvable_targets.append({
                                "target": target_cell,
                                "answer": "mine",
                                "revealed_number_cell": (r, c),
                                "revealed_number": val,
                                "known_mines": assumed_mines,
                                "known_safe": neighbors[val+1:]
                            })
                            
                    # Scenario 2: Force remaining unrevealed neighbors to be safe (Rule B)
                    if val > 0 and len(neighbors) > val:
                        target_cell = neighbors[-1]
                        assumed_mines = neighbors[:val]
                        
                        if target_cell not in mine_cells and all(m in mine_cells for m in assumed_mines):
                            solvable_targets.append({
                                "target": target_cell,
                                "answer": "safe",
                                "revealed_number_cell": (r, c),
                                "revealed_number": val,
                                "known_mines": assumed_mines,
                                "known_safe": neighbors[val:-1]
                            })

            # If we found a valid deterministic deduction scenario, build the prompt
            if solvable_targets:
                puzzle = self.rng.choice(solvable_targets)
                target = puzzle["target"]
                
                # Build a visual text board layout representing the historical state
                board_lines = []
                for r in range(self.grid_size):
                    row_chars = []
                    for c in range(self.grid_size):
                        coord = (r, c)
                        if coord == target:
                            row_chars.append("?")  # The specific question mark target
                        elif coord == puzzle["revealed_number_cell"]:
                            row_chars.append(str(puzzle["revealed_number"]))
                        elif coord in puzzle["known_mines"]:
                            row_chars.append("M")  # Flagged/Known Mine
                        elif coord in puzzle["known_safe"]:
                            row_chars.append(".")  # Confirmed Open Safe Space
                        else:
                            row_chars.append("X")  # Covered / Unrelated cell
                    board_lines.append(" ".join(row_chars))
                
                grid_display = "\n".join(board_lines)
                
                question_string = (
                    f"You are analyzing a local snapshot of a Minesweeper board:\n\n"
                    f"{grid_display}\n\n"
                    f"Legend:\n"
                    f"- Numbers (1-8) represent adjacent mine counts.\n"
                    f"- 'M' marks confirmed positions containing a mine.\n"
                    f"- '.' marks confirmed safe opened spaces.\n"
                    f"- 'X' marks hidden squares.\n"
                    f"- '?' is the unknown target square.\n\n"
                    f"Using mathematical deduction based on the numbers visible, determine the exact status of the '?' square located at row index {target[0]}, column index {target[1]}.\n"
                    f"Answer with exactly 'mine' or 'safe' without further formatting."
                )
                
                return {
                    "question": question_string,
                    "answer": puzzle["answer"],
                    "metadata": {
                        "grid_size": self.grid_size,
                        "target_coordinate": target,
                        "trigger_cell": puzzle["revealed_number_cell"],
                        "all_mines_on_board": list(mine_cells)
                    }
                }

    def generate_records(self, size: int) -> List[Dict[str, Any]]:
        return [self._generate_puzzle_instance() for _ in range(size)]

def export_minesweeper_dataset(size=1000, seed=42, file_name="minesweeper_gym.jsonl"):
    print(f"Generating {size} text-based Minesweeper reasoning tasks...")
    
    generator = MinesweeperDataset(grid_size=5, num_mines=5, seed=seed)
    records = generator.generate_records(size)

    with open(file_name, "w", encoding="utf-8") as f:
        for entry in records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Successfully exported dataset directly to {file_name}!")

if __name__ == "__main__":
    export_minesweeper_dataset(size=1000)
