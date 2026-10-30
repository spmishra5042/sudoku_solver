# Sudoku Solver Web Application using Backtracking

MCA Mini Project — Design and Analysis of Algorithms
Language: **Python 3** · Web framework: **Streamlit**

---

## 1. What this project does

The user enters a 9×9 Sudoku puzzle (by typing, pasting 81 digits, or loading a
sample). The app checks the puzzle, solves it with the **backtracking**
algorithm, and shows:

- the solved board (given clues in black, solved digits in blue)
- time taken, number of recursive calls, and number of backtracks
- a step-by-step view that shows every digit placed and every backtrack

## 2. Project structure

```
sudoku_solver/
├── app.py            # Streamlit web interface (what the user sees)
├── solver.py         # Backtracking algorithm (the DAA part)
├── puzzles.py        # Sample puzzles: Easy, Medium, Hard, Expert, Empty
├── test_solver.py    # Unit tests for the solver
├── requirements.txt  # Python packages needed
└── README.md         # This file
```

The project is split on purpose: **solver.py has no Streamlit code**, so you
can explain and test the algorithm on its own.

## 3. How to run

```bash
# 1. (optional) create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 2. install Streamlit
pip install -r requirements.txt

# 3. start the web app
streamlit run app.py
```

The browser opens at `http://localhost:8501`.

Other useful commands:

```bash
python solver.py                       # solve all samples in the terminal
python -m unittest test_solver.py -v   # run the tests
```

## 4. The algorithm (backtracking)

Backtracking builds the answer one step at a time. When a step leads to a dead
end, it **undoes that step** and tries the next option.

```
SOLVE(board):
    cell = FIND_EMPTY(board)
    if cell is None:  return True          # base case: board full -> solved
    (row, col) = cell
    for num in 1..9:
        if IS_SAFE(board, row, col, num):
            board[row][col] = num          # choose
            if SOLVE(board): return True   # explore
            board[row][col] = 0            # un-choose (backtrack)
    return False                           # no digit fits -> go back
```

`IS_SAFE` checks the three Sudoku rules:

1. the digit is not already in the same **row**
2. the digit is not already in the same **column**
3. the digit is not already in the same **3×3 box** (top-left corner =
   `row - row % 3`, `col - col % 3`)

### Functions in solver.py

| Function | Purpose |
|---|---|
| `find_empty(board)` | returns the first empty cell `(row, col)` or `None` |
| `is_safe(board, row, col, num)` | checks row, column and box rules |
| `is_valid_puzzle(board)` | checks the user's clues before solving |
| `solve(board, stats, steps)` | the recursive backtracking function |
| `solve_sudoku(puzzle)` | wrapper: validates, times, counts, returns result |
| `board_from_string(text)` | converts 81 characters into a 9×9 board |

## 5. Complexity analysis

| Measure | Value | Reason |
|---|---|---|
| Worst-case time | **O(9^m)** | m = empty cells; each may try 9 digits |
| `is_safe` check | O(9) | one row + one column + one box |
| Space | **O(m)** | recursion depth = number of empty cells |
| Best case | O(m · 9) | first safe digit is always right, no backtracking |

In practice it is far faster than 9^m because `is_safe` **prunes** invalid
branches early.

Measured on the sample puzzles:

| Puzzle | Recursive calls | Backtracks |
|---|---|---|
| Easy | 55 | 9 |
| Medium | 4,209 | 4,157 |
| Hard | 19,023 | 18,969 |
| Expert | 49,559 | 49,498 |

## 6. Possible viva questions

1. **What is backtracking?** A depth-first search that abandons a partial
   solution as soon as it breaks a rule, then tries the next choice.
2. **Why is it called backtracking?** Because on a dead end the algorithm goes
   *back* to the previous cell and changes its value.
3. **What is the base case?** When `find_empty` returns `None` — no empty cell
   means the board is solved.
4. **Why is the worst case O(9^m)?** Each of the m empty cells can take up to 9
   values, giving 9 × 9 × … (m times) combinations.
5. **How is the 3×3 box found?** `start_row = row - row % 3`,
   `start_col = col - col % 3`.
6. **Difference from brute force?** Brute force fills the whole board and then
   checks. Backtracking checks at every step and stops early.
7. **How can it be made faster?** Choose the empty cell with the fewest
   possible digits first (MRV heuristic), or use constraint propagation.
8. **What if the puzzle has no solution?** `solve` returns `False` after
   trying every option, and the app shows "This puzzle has no solution."

## 7. Future enhancements

- MRV (minimum remaining values) heuristic to reduce backtracks
- Puzzle generator with difficulty levels
- Upload a photo of a Sudoku and read it with OCR
- Compare backtracking with other algorithms in a chart
