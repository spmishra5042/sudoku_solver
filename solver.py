"""
solver.py
---------
Core logic of the Sudoku Solver (Design and Analysis of Algorithms part).

Algorithm used: BACKTRACKING (a depth-first search with pruning).

Idea in one line:
    Find an empty cell, try digits 1-9 in it, keep the first digit that is
    "safe", move to the next empty cell, and if we ever get stuck, undo
    (backtrack) the last choice and try the next digit.

The board is a 9x9 list of lists. The value 0 means "empty cell".
"""

import time

N = 9          # size of the board (9 x 9)
BOX = 3        # size of one small box (3 x 3)


# ---------------------------------------------------------------------------
# 1. Helper functions
# ---------------------------------------------------------------------------
def find_empty(board):
    """Return (row, col) of the first empty cell, or None if the board is full."""
    for row in range(N):
        for col in range(N):
            if board[row][col] == 0:
                return row, col
    return None


def is_safe(board, row, col, num):
    """
    Check the three Sudoku rules for placing `num` at (row, col):
      1. `num` must not already be in the same ROW
      2. `num` must not already be in the same COLUMN
      3. `num` must not already be in the same 3x3 BOX
    """
    # Rule 1: row check
    for c in range(N):
        if board[row][c] == num:
            return False

    # Rule 2: column check
    for r in range(N):
        if board[r][col] == num:
            return False

    # Rule 3: 3x3 box check
    start_row = row - row % BOX
    start_col = col - col % BOX
    for r in range(start_row, start_row + BOX):
        for c in range(start_col, start_col + BOX):
            if board[r][c] == num:
                return False

    return True


def is_valid_puzzle(board):
    """
    Check that the puzzle entered by the user follows the rules BEFORE solving.
    Returns (True, "") when valid, otherwise (False, "error message").
    """
    if len(board) != N or any(len(row) != N for row in board):
        return False, "The board must have exactly 9 rows and 9 columns."

    for row in range(N):
        for col in range(N):
            num = board[row][col]
            if not isinstance(num, int) or num < 0 or num > 9:
                return False, f"Invalid value at row {row + 1}, column {col + 1}."
            if num != 0:
                board[row][col] = 0            # temporarily remove it
                safe = is_safe(board, row, col, num)
                board[row][col] = num          # put it back
                if not safe:
                    return False, (
                        f"Number {num} at row {row + 1}, column {col + 1} "
                        "breaks a Sudoku rule (duplicate in row, column or box)."
                    )
    return True, ""


# ---------------------------------------------------------------------------
# 2. The backtracking algorithm
# ---------------------------------------------------------------------------
def solve(board, stats, steps=None, max_steps=3000):
    """
    Recursive backtracking solver. Changes `board` in place.

    stats  : dict that counts recursive calls and backtracks (for analysis)
    steps  : optional list that records each move, used for the
             step-by-step view in the web app
    Returns True if the board was solved, otherwise False.
    """
    stats["recursive_calls"] += 1

    empty = find_empty(board)
    if empty is None:              # BASE CASE: no empty cell -> solved
        return True

    row, col = empty

    for num in range(1, 10):       # try digits 1 to 9
        if is_safe(board, row, col, num):
            board[row][col] = num  # CHOOSE
            if steps is not None and len(steps) < max_steps:
                steps.append(("place", row, col, num))

            if solve(board, stats, steps, max_steps):   # EXPLORE
                return True

            board[row][col] = 0    # UN-CHOOSE (backtrack)
            stats["backtracks"] += 1
            if steps is not None and len(steps) < max_steps:
                steps.append(("remove", row, col, num))

    return False                   # no digit fits -> go back


def solve_sudoku(puzzle, record_steps=False):
    """
    Friendly wrapper used by the web app.

    Returns a dictionary:
      solved        -> True / False
      board         -> solved board (a copy, the input is not changed)
      error         -> error message if the puzzle is invalid
      time_ms       -> time taken in milliseconds
      recursive_calls, backtracks, empty_cells, steps
    """
    board = [row[:] for row in puzzle]          # work on a copy
    result = {
        "solved": False,
        "board": board,
        "error": "",
        "time_ms": 0.0,
        "recursive_calls": 0,
        "backtracks": 0,
        "empty_cells": sum(row.count(0) for row in board),
        "steps": [],
    }

    valid, message = is_valid_puzzle(board)
    if not valid:
        result["error"] = message
        return result

    stats = {"recursive_calls": 0, "backtracks": 0}
    steps = [] if record_steps else None

    start = time.perf_counter()
    solved = solve(board, stats, steps)
    end = time.perf_counter()

    result.update(
        solved=solved,
        time_ms=(end - start) * 1000,
        recursive_calls=stats["recursive_calls"],
        backtracks=stats["backtracks"],
        steps=steps or [],
    )
    if not solved:
        result["error"] = "This puzzle has no solution."
    return result


# ---------------------------------------------------------------------------
# 3. Conversion helpers (text <-> board)
# ---------------------------------------------------------------------------
def board_from_string(text):
    """
    Convert an 81-character string into a board.
    Digits 1-9 are clues; '0' or '.' are empty cells. Spaces/new lines ignored.
    """
    chars = [ch for ch in text if ch.isdigit() or ch == "."]
    if len(chars) != 81:
        raise ValueError(f"Expected 81 cells, but found {len(chars)}.")
    values = [0 if ch == "." else int(ch) for ch in chars]
    return [values[i * 9:(i + 1) * 9] for i in range(9)]


def board_to_string(board):
    """Convert a board back into an 81-character string."""
    return "".join(str(num) for row in board for num in row)


# Run this file directly to test the solver in the terminal:
#     python solver.py
if __name__ == "__main__":
    from puzzles import PUZZLES

    for name, text in PUZZLES.items():
        if name == "Empty board":
            continue
        out = solve_sudoku(board_from_string(text))
        print(f"{name:8} solved={out['solved']}  "
              f"time={out['time_ms']:.2f} ms  "
              f"calls={out['recursive_calls']}  "
              f"backtracks={out['backtracks']}")
