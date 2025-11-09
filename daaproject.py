
import tkinter as tk
from tkinter import ttk, messagebox

# ---------- Solver (Backtracking as a generator) ----------
def nqueens_steps(n):
    cols = set()
    diag1 = set()  # r - c
    diag2 = set()  # r + c
    board = [-1] * n  # board[r] = c

    def backtrack(r):
        if r == n:
            # Found a full solution
            yield ("solution", board.copy())
            return
        for c in range(n):
            if c in cols or (r - c) in diag1 or (r + c) in diag2:
                continue
            # Place queen
            cols.add(c); diag1.add(r - c); diag2.add(r + c); board[r] = c
            yield ("place", r, c, board.copy())
            # Recurse
            yield from backtrack(r + 1)
            # Remove queen (backtrack)
            yield ("remove", r, c, board.copy())
            cols.remove(c); diag1.remove(r - c); diag2.remove(r + c); board[r] = -1

    yield from backtrack(0)

# ---------- UI ----------
class NQueensApp:
    def __init__(self, root):
        self.root = root
        self.root.title("N-Queens Visualization (Backtracking)")
        self.root.geometry("900x700")

        # State
        self.n = tk.IntVar(value=8)
        self.delay = tk.IntVar(value=60)  # ms
        self.stop_first = tk.BooleanVar(value=True)
        self.is_running = False
        self.after_id = None
        self.step_gen = None
        self.steps = 0
        self.solutions = 0

        # Layout
        self._build_controls()
        self._build_canvas()
        self._draw_empty_board()

    def _build_controls(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(frame, text="N:").pack(side=tk.LEFT)
        self.n_entry = ttk.Spinbox(frame, from_=4, to=20, width=5, textvariable=self.n)
        self.n_entry.pack(side=tk.LEFT, padx=(5, 15))

        ttk.Label(frame, text="Speed (ms):").pack(side=tk.LEFT)
        self.speed = ttk.Scale(frame, from_=0, to=500, orient=tk.HORIZONTAL,
                               command=lambda v: self.delay.set(int(float(v))))
        self.speed.set(self.delay.get())
        self.speed.pack(side=tk.LEFT, padx=(5, 15), fill=tk.X, expand=True)

        self.stop_chk = ttk.Checkbutton(frame, text="Stop at first solution",
                                        variable=self.stop_first)
        self.stop_chk.pack(side=tk.LEFT, padx=10)

        self.start_btn = ttk.Button(frame, text="Start", command=self.start)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = ttk.Button(frame, text="Pause", command=self.pause, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = ttk.Button(frame, text="Reset", command=self.reset)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        self.info_lbl = ttk.Label(frame, text="Steps: 0   Solutions: 0")
        self.info_lbl.pack(side=tk.RIGHT)

        # Style
        try:
            self.root.style = ttk.Style()
            self.root.style.theme_use("clam")
        except:
            pass

    def _build_canvas(self):
        self.canvas_frame = ttk.Frame(self.root, padding=10)
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#f9f9f9")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Configure>", lambda e: self._draw_board())

    # ---------- Drawing ----------
    def _draw_empty_board(self):
        self.board = [-1] * self.n.get()
        self.steps = 0
        self.solutions = 0
        self._draw_board()
        self._update_info()

    def _draw_board(self, highlight=None):
        """Draw board grid and queens. highlight=(r,c,'place'/'remove') optionally color the last action."""
        self.canvas.delete("all")
        n = self.n.get()

        # Determine square size and offsets to keep it centered
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        size = min(w, h) - 20
        self.cell = size / n
        left = (w - size) / 2
        top = (h - size) / 2

        self.left = left
        self.top = top

        # Draw squares
        for r in range(n):
            for c in range(n):
                x1 = left + c * self.cell
                y1 = top + r * self.cell
                x2 = x1 + self.cell
                y2 = y1 + self.cell
                color = "#eee" if (r + c) % 2 == 0 else "#999"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#666")

        # Highlight recent action cell
        if highlight is not None:
            r, c, action = highlight
            x1 = left + c * self.cell
            y1 = top + r * self.cell
            x2 = x1 + self.cell
            y2 = y1 + self.cell
            hl = "#d4f4be" if action == "place" else "#fddcdc"
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=hl, outline="#444")

        # Draw queens
        for r, c in enumerate(self.board):
            if c >= 0:
                x = left + c * self.cell + self.cell / 2
                y = top + r * self.cell + self.cell / 2
                # Draw a simple queen: circle + crown text
                radius = self.cell * 0.32
                self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                        fill="#3b82f6", outline="#1e40af", width=2)
                self.canvas.create_text(x, y, text="♛", font=("Segoe UI", int(self.cell * 0.5)),
                                        fill="white")

    def _update_info(self):
        self.info_lbl.config(text=f"Steps: {self.steps}   Solutions: {self.solutions}")

    # ---------- Controls ----------
    def start(self):
        if self.is_running:
            return
        # Validate N
        try:
            n = int(self.n.get())
        except:
            messagebox.showerror("Invalid N", "Please enter a valid integer for N (4–20).")
            return
        if n < 4 or n > 20:
            messagebox.showerror("Out of range", "Please choose N between 4 and 20.")
            return

        # Fresh run if N changed or board empty
        if len(self.board) != n or all(v == -1 for v in self.board):
            self._draw_empty_board()

        self.step_gen = nqueens_steps(n)
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.n_entry.config(state=tk.DISABLED)
        self.stop_chk.config(state=tk.DISABLED)
        self._tick()

    def _tick(self):
        if not self.is_running:
            return
        try:
            event = next(self.step_gen)
        except StopIteration:
            # Finished searching all solutions
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED)
            self.n_entry.config(state=tk.NORMAL)
            self.stop_chk.config(state=tk.NORMAL)
            return

        self.steps += 1
        if event[0] == "place":
            _, r, c, board = event
            self.board = board
            self._draw_board(highlight=(r, c, "place"))
        elif event[0] == "remove":
            _, r, c, board = event
            self.board = board
            self._draw_board(highlight=(r, c, "remove"))
        elif event[0] == "solution":
            _, board = event
            self.board = board
            self.solutions += 1
            self._draw_board()
            if self.stop_first.get():
                # Pause on first solution
                self.pause()
                self.start_btn.config(state=tk.NORMAL)
                self.n_entry.config(state=tk.NORMAL)
                self.stop_chk.config(state=tk.NORMAL)
                self.pause_btn.config(state=tk.DISABLED)
                self._update_info()
                return

        self._update_info()
        # Schedule next step
        delay = max(0, int(self.delay.get()))
        self.after_id = self.root.after(delay, self._tick)

    def pause(self):
        if not self.is_running:
            return
        self.is_running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.n_entry.config(state=tk.NORMAL)
        self.stop_chk.config(state=tk.NORMAL)

    def reset(self):
        # Stop timers
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except:
                pass
            self.after_id = None
        self.is_running = False
        self.step_gen = None
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.n_entry.config(state=tk.NORMAL)
        self.stop_chk.config(state=tk.NORMAL)
        self._draw_empty_board()

def main():
    root = tk.Tk()
    app = NQueensApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
