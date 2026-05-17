import random
import customtkinter as ctk
from tkinter import Canvas
from collections import deque


GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)
MOVE_DIRS = [(-1, 0, "U"), (1, 0, "D"), (0, -1, "L"), (0, 1, "R")]



def get_neighbors(state):
	"""Tra ve cac trang thai ke va nuoc di tu trang thai hien tai."""
	zero_index = state.index(0)
	zx, zy = divmod(zero_index, 3)
	neighbors = []
	for dx, dy, move in MOVE_DIRS:
		nx, ny = zx + dx, zy + dy
		if 0 <= nx < 3 and 0 <= ny < 3:
			swap_index = nx * 3 + ny
			new_state = list(state)
			new_state[zero_index], new_state[swap_index] = new_state[swap_index], new_state[zero_index]
			neighbors.append((tuple(new_state), move))
	return neighbors


def is_solvable(state):
	"""Kiem tra trang thai 8-puzzle co the giai duoc hay khong."""
	flat = [n for n in state if n != 0]
	inversions = 0
	for i in range(len(flat)):
		for j in range(i + 1, len(flat)):
			if flat[i] > flat[j]:
				inversions += 1
	return inversions % 2 == 0


def bfs(start_state):
	"""Chay BFS tu trang thai bat dau va tra ve (duong di, nuoc di)."""
	if start_state == GOAL_STATE:
		return [start_state], []
	if not is_solvable(start_state):
		return None

	frontier = deque([start_state])
	explored = {start_state}
	parent = {start_state: None}
	parent_move = {start_state: None}

	while frontier:
		node = frontier.popleft()
		for child, move in get_neighbors(node):
			if child not in explored:
				parent[child] = node
				parent_move[child] = move
				if child == GOAL_STATE:
					return build_path(parent, parent_move, child)
				explored.add(child)
				frontier.append(child)
	return None


def build_path(parent, parent_move, goal_state):
	"""Truy vet lai duong di va chuoi nuoc di tu cac bang parent."""
	path = []
	moves = []
	current = goal_state
	while current is not None:
		path.append(current)
		move = parent_move[current]
		if move is not None:
			moves.append(move)
		current = parent[current]
	path.reverse()
	moves.reverse()
	return path, moves


def random_state():
	"""Sinh trang thai ngau nhien hop le khac goal."""
	state = list(GOAL_STATE)
	while True:
		random.shuffle(state)
		candidate = tuple(state)
		if is_solvable(candidate) and candidate != GOAL_STATE:
			return candidate

# giao dien
class PuzzleApp(ctk.CTk):
	def __init__(self):
		"""Khoi tao giao dien va trang thai ban dau."""
		super().__init__()
		self.title("8-Puzzle BFS")
		self.geometry("520x620")
		self.resizable(False, False)

		self.current_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
		self.solution_path = []
		self.solution_moves = []
		self.anim_index = 0

		self.canvas = Canvas(self, width=360, height=360, bg="#f6f4ef", highlightthickness=0)
		self.canvas.pack(pady=20)

		controls = ctk.CTkFrame(self)
		controls.pack(pady=10)

		self.input_entry = ctk.CTkEntry(controls, width=300, placeholder_text="1 2 3 4 5 6 7 8 0")
		self.input_entry.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

		self.apply_button = ctk.CTkButton(controls, text="Apply State", command=self.apply_state)
		self.apply_button.grid(row=1, column=0, padx=10, pady=5)

		self.random_button = ctk.CTkButton(controls, text="Random", command=self.set_random_state)
		self.random_button.grid(row=1, column=1, padx=10, pady=5)

		self.solve_button = ctk.CTkButton(controls, text="Solve BFS", command=self.solve)
		self.solve_button.grid(row=2, column=0, padx=10, pady=5)

		self.reset_button = ctk.CTkButton(controls, text="Reset", command=self.reset)
		self.reset_button.grid(row=2, column=1, padx=10, pady=5)

		self.status_label = ctk.CTkLabel(self, text="Ready")
		self.status_label.pack(pady=10)

		self.moves_label = ctk.CTkLabel(self, text="Moves: ", wraplength=480, justify="left")
		self.moves_label.pack(pady=4)

		self.draw_board(self.current_state)
		self.update_entry_from_state()

	def reset(self):
		"""Dat lai trang thai mac dinh va xoa ket qua."""
		self.current_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
		self.solution_path = []
		self.solution_moves = []
		self.anim_index = 0
		self.status_label.configure(text="Ready")
		self.moves_label.configure(text="Moves: ")
		self.draw_board(self.current_state)
		self.update_entry_from_state()

	def update_entry_from_state(self):
		"""Dong bo o nhap voi trang thai hien tai."""
		self.input_entry.delete(0, "end")
		self.input_entry.insert(0, " ".join(str(n) for n in self.current_state))

	def apply_state(self):
		"""Doc o nhap va cap nhat trang thai neu hop le."""
		text = self.input_entry.get().strip()
		parts = [p for p in text.replace(",", " ").split() if p]
		try:
			numbers = [int(p) for p in parts]
		except ValueError:
			self.status_label.configure(text="Invalid input")
			return

		if len(numbers) != 9 or set(numbers) != set(range(9)):
			self.status_label.configure(text="Need 9 numbers: 0-8")
			return

		self.current_state = tuple(numbers)
		self.solution_path = []
		self.solution_moves = []
		self.anim_index = 0
		self.status_label.configure(text="State updated")
		self.moves_label.configure(text="Moves: ")
		self.draw_board(self.current_state)

	def set_random_state(self):
		"""Chon trang thai ngau nhien va cap nhat giao dien."""
		self.current_state = random_state()
		self.solution_path = []
		self.solution_moves = []
		self.anim_index = 0
		self.status_label.configure(text="Random state")
		self.moves_label.configure(text="Moves: ")
		self.draw_board(self.current_state)
		self.update_entry_from_state()

	def solve(self):
		"""Giai bang BFS va hien thi ket qua."""
		self.apply_state()
		if self.status_label.cget("text") in {"Invalid input", "Need 9 numbers: 0-8"}:
			return
		self.status_label.configure(text="Solving...")
		self.update_idletasks()
		result = bfs(self.current_state)
		if not result:
			self.status_label.configure(text="No solution")
			return
		path, moves = result
		self.solution_path = path
		self.solution_moves = moves
		self.anim_index = 0
		self.status_label.configure(text=f"Steps: {len(path) - 1}")
		self.moves_label.configure(text=f"Moves: {''.join(moves)}")
		self.animate()

	def animate(self):
		"""Chay hoat canh tung buoc cua loi giai."""
		if self.anim_index >= len(self.solution_path):
			return
		state = self.solution_path[self.anim_index]
		self.draw_board(state)
		self.anim_index += 1
		self.after(250, self.animate)

	def draw_board(self, state):
		"""Ve ban co 3x3 len canvas."""
		self.canvas.delete("all")
		tile_size = 110
		padding = 10
		for i, value in enumerate(state):
			row, col = divmod(i, 3)
			x0 = col * tile_size + padding
			y0 = row * tile_size + padding
			x1 = x0 + tile_size - padding
			y1 = y0 + tile_size - padding
			if value != 0:
				self.canvas.create_rectangle(x0, y0, x1, y1, fill="#d8b384", outline="#8d6e52", width=2)
				self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=str(value), font=("Arial", 32, "bold"))
			else:
				self.canvas.create_rectangle(x0, y0, x1, y1, fill="#f6f4ef", outline="#e0d8cf", width=2)


if __name__ == "__main__":
	ctk.set_appearance_mode("light")
	ctk.set_default_color_theme("blue")
	app = PuzzleApp()
	app.mainloop()
