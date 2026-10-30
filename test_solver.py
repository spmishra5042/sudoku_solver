"""
test_solver.py
--------------
Simple tests for the solver. Run with:
    python -m unittest test_solver.py
"""

import unittest

from puzzles import PUZZLES
from solver import board_from_string, is_safe, is_valid_puzzle, solve_sudoku


def is_complete_and_correct(board):
    """A solved board has every digit 1-9 exactly once in each row, column and box."""
    full = set(range(1, 10))
    for i in range(9):
        if set(board[i]) != full:
            return False
        if {board[r][i] for r in range(9)} != full:
            return False
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            box = {board[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)}
            if box != full:
                return False
    return True


class TestSolver(unittest.TestCase):
    def test_all_sample_puzzles_are_solved_correctly(self):
        for name, text in PUZZLES.items():
            puzzle = board_from_string(text)
            result = solve_sudoku(puzzle)
            self.assertTrue(result["solved"], name)
            self.assertTrue(is_complete_and_correct(result["board"]), name)
            # the given clues must not be changed
            for r in range(9):
                for c in range(9):
                    if puzzle[r][c]:
                        self.assertEqual(result["board"][r][c], puzzle[r][c])

    def test_is_safe_rules(self):
        board = board_from_string(PUZZLES["Medium"])
        self.assertFalse(is_safe(board, 0, 2, 5))   # 5 already in row 1
        self.assertFalse(is_safe(board, 2, 0, 6))   # 6 already in column 1
        self.assertFalse(is_safe(board, 1, 1, 9))   # 9 already in top-left box
        self.assertTrue(is_safe(board, 0, 2, 4))

    def test_duplicate_clue_is_rejected(self):
        board = board_from_string("55" + "0" * 79)
        valid, _ = is_valid_puzzle(board)
        self.assertFalse(valid)
        self.assertFalse(solve_sudoku(board)["solved"])

    def test_unsolvable_puzzle_is_reported(self):
        # Row 1 needs a 9 in its last cell, but column 9 already has a 9.
        text = "123456780" + "000000009" + "0" * 63
        result = solve_sudoku(board_from_string(text))
        self.assertFalse(result["solved"])
        self.assertEqual(result["error"], "This puzzle has no solution.")

    def test_wrong_length_text_is_rejected(self):
        with self.assertRaises(ValueError):
            board_from_string("123")


if __name__ == "__main__":
    unittest.main()
