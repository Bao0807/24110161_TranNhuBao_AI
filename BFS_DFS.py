import customtkinter as ctk
from tkinter import Canvas
from collections import deque
import heapq
import time
import random

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# UI Colors
BG_COLOR = "#0a0e17"
PANEL_COLOR = "#111827"
ACCENT_PRIMARY = "#00d9ff"
ACCENT_SECONDARY = "#ff006e"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#a0aec0"
BORDER_COLOR = "#2d3748"
SUCCESS_COLOR = "#06ffa5"
ERROR_COLOR = "#ff4757"
EMPTY_COLOR = "#0f1419"

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

PUZZLE_SIZE = 3
CELL_SIZE = 60


class Puzzle8App:

    def __init__(self, root):
        self.root = root
        self.root.title("🎮 8-Puzzle Solver")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(fg_color=BG_COLOR)

        self.goal_state = tuple(range(1, 9)) + (0,)
        self.current_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        self.solving = False
        self.selected_algo = ctk.StringVar(value="BFS")  # mặc định BFS

        self.main_frame = ctk.CTkFrame(root, fg_color=BG_COLOR, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # TITLE
        title = ctk.CTkLabel(
            self.main_frame,
            text="8-PUZZLE SOLVER",
            font=("Arial", 28, "bold"),
            text_color=ACCENT_PRIMARY
        )
        title.pack(pady=15)

        # CONTENT FRAME
        content_frame = ctk.CTkFrame(self.main_frame, fg_color=BG_COLOR)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # ── LEFT PANEL ──────────────────────────────────────────────
        left_panel = ctk.CTkFrame(content_frame, fg_color=PANEL_COLOR, corner_radius=15)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            left_panel,
            text="Current State",
            font=("Arial", 18, "bold"),
            text_color=ACCENT_PRIMARY
        ).pack(pady=10)

        self.current_canvas = Canvas(
            left_panel,
            width=PUZZLE_SIZE * CELL_SIZE,
            height=PUZZLE_SIZE * CELL_SIZE,
            bg=EMPTY_COLOR,
            highlightthickness=2,
            highlightbackground=BORDER_COLOR
        )
        self.current_canvas.pack(pady=10)
        self.current_rects = self.create_puzzle_grid(self.current_canvas)

        # Shuffle button
        button_frame = ctk.CTkFrame(left_panel, fg_color=PANEL_COLOR)
        button_frame.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkButton(
            button_frame,
            text="🔀 Shuffle",
            command=self.shuffle_puzzle,
            height=40,
            font=("Arial", 12, "bold"),
            fg_color=ACCENT_PRIMARY
        ).pack(fill="x", pady=5)

        # Algorithm selection label
        ctk.CTkLabel(
            left_panel,
            text="Chọn thuật toán:",
            font=("Arial", 13, "bold"),
            text_color=TEXT_SECONDARY
        ).pack(pady=(10, 2))

        # Radio buttons for algorithm
        algo_frame = ctk.CTkFrame(left_panel, fg_color=PANEL_COLOR)
        algo_frame.pack(fill="x", padx=15, pady=5)

        algo_colors = {
            "BFS": "#4a9eff",
            "UCS": ACCENT_SECONDARY,
            "DFS": SUCCESS_COLOR,
        }

        for algo in ["BFS", "UCS", "DFS"]:
            ctk.CTkRadioButton(
                algo_frame,
                text=algo,
                variable=self.selected_algo,
                value=algo,
                font=("Arial", 13, "bold"),
                text_color=algo_colors[algo],
                fg_color=algo_colors[algo],
                hover_color=algo_colors[algo],
            ).pack(anchor="w", padx=10, pady=4)

        # Solve button
        ctk.CTkButton(
            left_panel,
            text="✨ Solve",
            command=self.solve_puzzle,
            height=44,
            font=("Arial", 13, "bold"),
            fg_color=SUCCESS_COLOR,
            text_color="#000000"
        ).pack(fill="x", padx=15, pady=15)

        # ── MIDDLE PANEL ─────────────────────────────────────────────
        middle_panel = ctk.CTkFrame(content_frame, fg_color=PANEL_COLOR, corner_radius=15)
        middle_panel.pack(side="left", fill="both", expand=True, padx=5)

        ctk.CTkLabel(
            middle_panel,
            text="Goal State",
            font=("Arial", 18, "bold"),
            text_color=ACCENT_SECONDARY
        ).pack(pady=10)

        self.goal_canvas = Canvas(
            middle_panel,
            width=PUZZLE_SIZE * CELL_SIZE,
            height=PUZZLE_SIZE * CELL_SIZE,
            bg=EMPTY_COLOR,
            highlightthickness=2,
            highlightbackground=BORDER_COLOR
        )
        self.goal_canvas.pack(pady=10)
        self.goal_rects = self.create_puzzle_grid(self.goal_canvas)

        ctk.CTkLabel(
            middle_panel,
            text="Goal: [1,2,3,4,5,6,7,8,0]",
            font=("Arial", 11),
            text_color=TEXT_SECONDARY
        ).pack(pady=20)

        self.redraw_puzzles()

        # ── RIGHT PANEL ───────────────────────────────────────────────
        right_panel = ctk.CTkFrame(content_frame, fg_color=PANEL_COLOR, corner_radius=15)
        right_panel.pack(side="left", fill="both", expand=True, padx=(10, 0))

        ctk.CTkLabel(
            right_panel,
            text="📋 Kết quả",
            font=("Arial", 16, "bold"),
            text_color=ACCENT_PRIMARY
        ).pack(pady=10, padx=15)

        self.algo_label = ctk.CTkLabel(
            right_panel,
            text="Chọn thuật toán và nhấn Solve...",
            font=("Arial", 10),
            text_color=TEXT_SECONDARY,
            justify="left"
        )
        self.algo_label.pack(pady=10, padx=15, anchor="nw")

        ctk.CTkFrame(right_panel, height=1, fg_color=BORDER_COLOR).pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            right_panel,
            text="🚀 Solution Steps",
            font=("Arial", 12, "bold"),
            text_color=SUCCESS_COLOR
        ).pack(pady=(10, 5), padx=15, anchor="nw")

        self.steps_text = ctk.CTkTextbox(
            right_panel,
            height=200,
            font=("Courier", 9),
            fg_color=EMPTY_COLOR,
            text_color=TEXT_PRIMARY,
            border_color=BORDER_COLOR,
            border_width=1
        )
        self.steps_text.pack(fill="both", padx=15, pady=(0, 15), expand=True)

    # ── PUZZLE GRID ───────────────────────────────────────────────────

    def create_puzzle_grid(self, canvas):
        rects = []
        for i in range(PUZZLE_SIZE * PUZZLE_SIZE):
            r = i // PUZZLE_SIZE
            c = i % PUZZLE_SIZE
            x1, y1 = c * CELL_SIZE, r * CELL_SIZE
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
            rect = canvas.create_rectangle(x1, y1, x2, y2, fill="#1a2332", outline=BORDER_COLOR, width=2)
            rects.append(rect)
        return rects

    def draw_puzzle(self, canvas, rects, state):
        for i, val in enumerate(state):
            r = i // PUZZLE_SIZE
            c = i % PUZZLE_SIZE
            x1, y1 = c * CELL_SIZE, r * CELL_SIZE
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE

            color = EMPTY_COLOR if val == 0 else ACCENT_PRIMARY
            text = "" if val == 0 else str(val)

            canvas.itemconfig(rects[i], fill=color, outline=BORDER_COLOR)
            canvas.delete(f"text_{i}")
            canvas.create_text(
                x1 + CELL_SIZE // 2,
                y1 + CELL_SIZE // 2,
                text=text,
                font=("Arial", 24, "bold"),
                fill=TEXT_PRIMARY,
                tags=f"text_{i}"
            )

    def redraw_puzzles(self):
        self.draw_puzzle(self.current_canvas, self.current_rects, self.current_state)
        self.draw_puzzle(self.goal_canvas, self.goal_rects, self.goal_state)

    # ── SHUFFLE ───────────────────────────────────────────────────────

    def shuffle_puzzle(self):
        if self.solving:
            return
        state = list(self.goal_state)
        last_idx = -1
        for _ in range(200):
            zero_idx = state.index(0)
            moves = self.get_neighbors_idx(zero_idx)
            moves = [m for m in moves if m != last_idx]
            if moves:
                neighbor_idx = random.choice(moves)
                state[zero_idx], state[neighbor_idx] = state[neighbor_idx], state[zero_idx]
                last_idx = zero_idx
        self.current_state = tuple(state)
        self.redraw_puzzles()
        self.steps_text.delete("1.0", "end")
        self.algo_label.configure(text="Chọn thuật toán và nhấn Solve...")

    # ── NEIGHBORS ────────────────────────────────────────────────────

    def get_neighbors_idx(self, zero_idx):
        r, c = zero_idx // PUZZLE_SIZE, zero_idx % PUZZLE_SIZE
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < PUZZLE_SIZE and 0 <= nc < PUZZLE_SIZE:
                neighbors.append(nr * PUZZLE_SIZE + nc)
        return neighbors

    def get_neighbors(self, state):
        state = list(state)
        zero_idx = state.index(0)
        neighbors = []
        r, c = zero_idx // PUZZLE_SIZE, zero_idx % PUZZLE_SIZE
        for dr, dc, move_char in [(-1, 0, "↑"), (1, 0, "↓"), (0, -1, "←"), (0, 1, "→")]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < PUZZLE_SIZE and 0 <= nc < PUZZLE_SIZE:
                new_idx = nr * PUZZLE_SIZE + nc
                new_state = state.copy()
                new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
                neighbors.append((tuple(new_state), move_char))
        return neighbors

    # ── SEARCH ALGORITHMS ────────────────────────────────────────────

    def bfs_search(self):
        start_time = time.time()
        queue = deque([(self.current_state, [])])
        visited = {self.current_state}
        nodes_explored = 0
        while queue:
            state, path = queue.popleft()
            nodes_explored += 1
            if state == self.goal_state:
                return path, nodes_explored, time.time() - start_time
            for next_state, move in self.get_neighbors(state):
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append((next_state, path + [move]))
        return [], nodes_explored, time.time() - start_time

    def ucs_search(self):
        """Uniform Cost Search — ưu tiên trạng thái có chi phí tích lũy thấp nhất."""
        start_time = time.time()
        # (cost, counter, state, path)
        counter = 0
        pq = [(0, counter, self.current_state, [])]
        visited = {}   # state -> cost thấp nhất đã thấy
        nodes_explored = 0

        while pq:
            cost, _, state, path = heapq.heappop(pq)
            nodes_explored += 1

            if state == self.goal_state:
                return path, nodes_explored, time.time() - start_time

            # Bỏ qua nếu đã tìm được đường rẻ hơn đến state này
            if state in visited and visited[state] <= cost:
                continue
            visited[state] = cost

            for next_state, move in self.get_neighbors(state):
                new_cost = cost + 1  # mỗi bước có chi phí = 1
                if next_state not in visited or visited[next_state] > new_cost:
                    counter += 1
                    heapq.heappush(pq, (new_cost, counter, next_state, path + [move]))

        return [], nodes_explored, time.time() - start_time

    def dfs_search(self):
        """Iterative Deepening DFS — tránh crash do đệ quy quá sâu."""
        start_time = time.time()
        nodes_explored = 0

        def dls(state, path, visited, depth_limit):
            nonlocal nodes_explored
            nodes_explored += 1
            if state == self.goal_state:
                return path
            if len(path) >= depth_limit:
                return None
            for next_state, move in self.get_neighbors(state):
                if next_state not in visited:
                    visited.add(next_state)
                    result = dls(next_state, path + [move], visited, depth_limit)
                    if result is not None:
                        return result
                    visited.discard(next_state)
            return None

        for limit in range(1, 51):
            visited = {self.current_state}
            result = dls(self.current_state, [], visited, limit)
            if result is not None:
                return result, nodes_explored, time.time() - start_time

        return [], nodes_explored, time.time() - start_time

    # ── SOLVE ────────────────────────────────────────────────────────

    def solve_puzzle(self):
        if self.solving:
            return
        if self.current_state == self.goal_state:
            self.steps_text.delete("1.0", "end")
            self.steps_text.insert("1.0", "✅ Puzzle đã ở trạng thái đích!")
            return

        algo = self.selected_algo.get()
        self.algo_label.configure(text=f"⏳ Đang giải bằng {algo}...")
        self.root.update()

        # Chạy đúng thuật toán được chọn
        if algo == "BFS":
            path, nodes, elapsed = self.bfs_search()
        elif algo == "UCS":
            path, nodes, elapsed = self.ucs_search()
        else:
            path, nodes, elapsed = self.dfs_search()

        if not path:
            self.algo_label.configure(text=f"✗ {algo}: Không tìm được lời giải!")
            return

        # Hiển thị thông tin
        self.algo_label.configure(
            text=f"✅ {algo} hoàn thành!\n\n"
                 f"  ⏱ Thời gian : {elapsed:.4f}s\n"
                 f"  🔍 Nodes    : {nodes}\n"
                 f"  📏 Bước     : {len(path)}"
        )

        # Animate solution
        self.solving = True
        self.steps_text.delete("1.0", "end")
        self.steps_text.insert("1.0", f"🚀 {algo} — {len(path)} bước:\n\n")

        state = list(self.current_state)
        moves_map = {"↑": (-1, 0), "↓": (1, 0), "←": (0, -1), "→": (0, 1)}
        step_display = ""

        for i, move in enumerate(path, 1):
            zero_idx = state.index(0)
            r, c = zero_idx // PUZZLE_SIZE, zero_idx % PUZZLE_SIZE
            dr, dc = moves_map[move]
            new_idx = (r + dr) * PUZZLE_SIZE + (c + dc)
            state[zero_idx], state[new_idx] = state[new_idx], state[zero_idx]
            self.current_state = tuple(state)

            step_display += f"Step {i}: {move} "
            if i % 10 == 0:
                step_display += "\n"

            self.redraw_puzzles()
            self.root.update()
            time.sleep(0.3)

        self.steps_text.delete("1.0", "end")
        self.steps_text.insert(
            "1.0",
            f"✨ Giải xong bằng {algo}!\n"
            f"Bước: {len(path)}  |  Nodes: {nodes}  |  Time: {elapsed:.4f}s\n\n"
            f"{step_display}"
        )
        self.solving = False


def main():
    root = ctk.CTk()
    Puzzle8App(root)
    root.mainloop()


if __name__ == "__main__":
    main()