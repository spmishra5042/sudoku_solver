"""
app.py
------
Streamlit web interface for the Sudoku Solver.

Run with:
    streamlit run app.py
"""

import streamlit as st

from puzzles import PUZZLES
from solver import board_from_string, board_to_string, solve_sudoku

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Sudoku Solver | Backtracking", page_icon="🧩", layout="wide")

st.markdown(
    """
    <style>
      /* Make the 81 input boxes small, square and centred */
      div[data-testid="stTextInput"] input {
          text-align: center; font-size: 20px; font-weight: 600;
          padding: 6px 0; height: 44px;
      }
      .sudoku-table { border-collapse: collapse; margin: 0 auto; }
      .sudoku-table td {
          width: 44px; height: 44px; text-align: center; font-size: 22px;
          border: 1px solid #b9b9b9; font-family: monospace;
      }
      .sudoku-table tr:nth-child(3n) td { border-bottom: 3px solid #222; }
      .sudoku-table tr:first-child td   { border-top: 3px solid #222; }
      .sudoku-table td:nth-child(3n)    { border-right: 3px solid #222; }
      .sudoku-table td:first-child      { border-left: 3px solid #222; }
      .given  { color: #111; font-weight: 700; background: #f2f2f2; }
      .filled { color: #1565c0; font-weight: 600; }
      .active { background: #fff3c4; }
      .removed{ background: #ffd6d6; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session state helpers (the 81 input boxes are stored in st.session_state)
# ---------------------------------------------------------------------------
def cell_key(r, c):
    return f"cell_{r}_{c}"


def load_board(board):
    """Put a board into the 81 input boxes."""
    for r in range(9):
        for c in range(9):
            st.session_state[cell_key(r, c)] = str(board[r][c]) if board[r][c] else ""
    st.session_state.pop("result", None)


def read_board():
    """Read the 81 input boxes. Returns (board, error_message)."""
    board = []
    for r in range(9):
        row = []
        for c in range(9):
            text = st.session_state.get(cell_key(r, c), "").strip()
            if text == "":
                row.append(0)
            elif text.isdigit() and 1 <= int(text) <= 9:
                row.append(int(text))
            else:
                return None, f"Row {r + 1}, column {c + 1}: '{text}' is not a digit from 1 to 9."
        board.append(row)
    return board, ""


def on_load_sample():
    load_board(board_from_string(PUZZLES[st.session_state["sample_choice"]]))


def on_clear():
    load_board([[0] * 9 for _ in range(9)])


def on_load_text():
    try:
        load_board(board_from_string(st.session_state["puzzle_text"]))
    except ValueError as err:
        st.session_state["text_error"] = str(err)


# First run: start with the Easy puzzle
if cell_key(0, 0) not in st.session_state:
    load_board(board_from_string(PUZZLES["Easy"]))


def render_board(board, givens, highlight=None, highlight_class="active"):
    """Return an HTML table for a board. Given clues are bold, solved digits blue."""
    html = '<table class="sudoku-table">'
    for r in range(9):
        html += "<tr>"
        for c in range(9):
            value = board[r][c]
            classes = "given" if givens[r][c] else ("filled" if value else "")
            if highlight == (r, c):
                classes += " " + highlight_class
            html += f'<td class="{classes}">{value if value else ""}</td>'
        html += "</tr>"
    return html + "</table>"


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("🧩 Puzzle controls")
    st.selectbox("Sample puzzle", list(PUZZLES.keys()), key="sample_choice")
    st.button("Load sample", on_click=on_load_sample, use_container_width=True)
    st.button("Clear board", on_click=on_clear, use_container_width=True)

    st.divider()
    st.subheader("Paste a puzzle")
    st.text_area(
        "81 digits, row by row (0 or . = empty)",
        key="puzzle_text",
        height=100,
        placeholder="530070000600195000098000060...",
    )
    st.button("Load from text", on_click=on_load_text, use_container_width=True)
    if st.session_state.get("text_error"):
        st.error(st.session_state.pop("text_error"))

    st.divider()
    record = st.checkbox("Record steps for visualisation", value=True)
    st.caption("MCA Mini Project · Design and Analysis of Algorithms")


# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
st.title("Sudoku Solver using Backtracking")
st.write(
    "Enter a puzzle in the grid (leave empty cells blank) or load a sample from the "
    "sidebar, then press **Solve**."
)

tab_solver, tab_theory, tab_about = st.tabs(["Solver", "How backtracking works", "About the project"])

# ----------------------------- Tab 1: Solver -------------------------------
with tab_solver:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("Input puzzle")
        # 9 columns + 2 thin spacer columns to show the 3x3 boxes
        spec = [1, 1, 1, 0.2, 1, 1, 1, 0.2, 1, 1, 1]
        for r in range(9):
            if r in (3, 6):
                st.write("")  # small gap between box rows
            cols = st.columns(spec)
            col_positions = [0, 1, 2, 4, 5, 6, 8, 9, 10]
            for c in range(9):
                with cols[col_positions[c]]:
                    st.text_input(
                        f"r{r}c{c}", key=cell_key(r, c), max_chars=1,
                        label_visibility="collapsed",
                    )

        solve_clicked = st.button("🔍 Solve", type="primary", use_container_width=True)

    if solve_clicked:
        puzzle, error = read_board()
        if error:
            st.session_state["result"] = {"error": error}
        else:
            outcome = solve_sudoku(puzzle, record_steps=record)
            outcome["puzzle"] = puzzle
            st.session_state["result"] = outcome

    with right:
        st.subheader("Result")
        result = st.session_state.get("result")

        if result is None:
            st.info("Press **Solve** to see the solution here.")
        elif result.get("error"):
            st.error(result["error"])
        else:
            puzzle = result["puzzle"]
            givens = [[puzzle[r][c] != 0 for c in range(9)] for r in range(9)]
            st.success("Puzzle solved!")
            st.markdown(render_board(result["board"], givens), unsafe_allow_html=True)

            st.write("")
            m1, m2 = st.columns(2)
            m3, m4 = st.columns(2)
            m1.metric("Time", f"{result['time_ms']:.2f} ms")
            m2.metric("Recursive calls", f"{result['recursive_calls']:,}")
            m3.metric("Backtracks", f"{result['backtracks']:,}")
            m4.metric("Cells filled", result["empty_cells"])

            st.code(board_to_string(result["board"]), language=None)

    # ---------------- Step-by-step visualisation ----------------
    result = st.session_state.get("result")
    if result and result.get("steps"):
        st.divider()
        st.subheader("Step-by-step visualisation")
        steps = result["steps"]
        st.caption(
            f"{len(steps):,} steps recorded"
            + (" (only the first 3,000 are kept)" if len(steps) >= 3000 else "")
            + ". Yellow = digit placed, red = digit removed (backtrack)."
        )
        step_no = st.slider("Step", 1, len(steps), 1)

        # Rebuild the board up to the chosen step
        puzzle = result["puzzle"]
        board = [row[:] for row in puzzle]
        for action, r, c, num in steps[:step_no]:
            board[r][c] = num if action == "place" else 0
        action, r, c, num = steps[step_no - 1]
        givens = [[puzzle[i][j] != 0 for j in range(9)] for i in range(9)]

        a, b = st.columns([1, 1])
        with a:
            st.markdown(
                render_board(board, givens, (r, c), "active" if action == "place" else "removed"),
                unsafe_allow_html=True,
            )
        with b:
            if action == "place":
                st.markdown(f"**Step {step_no}:** placed **{num}** at row {r + 1}, column {c + 1} because it is safe.")
            else:
                st.markdown(
                    f"**Step {step_no}:** removed **{num}** from row {r + 1}, column {c + 1}. "
                    "The next cells had no valid digit, so the algorithm **backtracks**."
                )

# ------------------------ Tab 2: Theory ------------------------------------
with tab_theory:
    st.subheader("What is backtracking?")
    st.write(
        "Backtracking is a problem-solving technique that builds a solution step by step. "
        "When a partial solution cannot be completed, it **undoes the last step** and tries "
        "another option. It is a depth-first search over all possible choices, but it "
        "**prunes** (skips) choices that already break a rule."
    )

    st.subheader("Sudoku rules checked by is_safe()")
    st.markdown(
        "1. The digit must not repeat in the same **row**.\n"
        "2. The digit must not repeat in the same **column**.\n"
        "3. The digit must not repeat in the same **3×3 box**."
    )

    st.subheader("Algorithm")
    st.code(
        """SOLVE(board):
    cell = FIND_EMPTY(board)
    if cell is None:             # base case
        return True              # board is full -> solved
    (row, col) = cell
    for num in 1..9:
        if IS_SAFE(board, row, col, num):
            board[row][col] = num            # choose
            if SOLVE(board):                 # explore
                return True
            board[row][col] = 0              # un-choose (backtrack)
    return False                             # trigger backtracking""",
        language="text",
    )

    st.subheader("Complexity analysis")
    st.markdown(
        "| Measure | Value | Reason |\n"
        "|---|---|---|\n"
        "| Worst-case time | O(9^m) | m = number of empty cells, each can take 9 values |\n"
        "| is_safe() check | O(n) = O(9) | scans one row, one column and one box |\n"
        "| Space | O(m) | depth of the recursion stack |\n"
        "| Best case | O(m) | every first safe digit is correct, no backtracking |"
    )
    st.info(
        "In practice the solver is much faster than 9^m because is_safe() prunes most "
        "branches early. Compare the 'Recursive calls' count for Easy and Expert puzzles."
    )

# ------------------------ Tab 3: About -------------------------------------
with tab_about:
    st.subheader("Project summary")
    st.markdown(
        "- **Title:** Sudoku Solver Web Application using Backtracking\n"
        "- **Language:** Python 3\n"
        "- **Framework:** Streamlit (web interface)\n"
        "- **Subject area:** Design and Analysis of Algorithms\n"
        "- **Files:** `solver.py` (algorithm), `puzzles.py` (samples), `app.py` (web UI)"
    )
    st.subheader("Features")
    st.markdown(
        "- Enter any puzzle by typing, pasting 81 digits, or loading a sample\n"
        "- Input validation (invalid characters and rule-breaking clues)\n"
        "- Solves using recursive backtracking\n"
        "- Shows time taken, recursive calls and number of backtracks\n"
        "- Step-by-step visualisation of placements and backtracks"
    )
