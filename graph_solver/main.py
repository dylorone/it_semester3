import tkinter as tk
from tkinter import ttk, messagebox
from typing import List

from graph_editor import GraphEditor
from solver import GraphSolver


class GraphApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ЕГЭ Информатика: Задача №1 (Матрица + Граф)")

        # Настройки
        self.vertex_count_var = tk.StringVar(value="5")
        self.use_latin_var = tk.BooleanVar(value=True)

        # Хранилище виджетов матрицы
        self.matrix_entries: list[list[tk.Widget]] = []
        self.matrix_frame: tk.Frame | None = None
        self.labels_row: list[tk.Label] = []
        self.labels_col: list[tk.Label] = []

        # --- Панель управления (сверху) ---
        controls = ttk.Frame(self.root)
        controls.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(controls, text="Число вершин (N):").pack(side=tk.LEFT)
        ttk.Spinbox(controls, from_=2, to=15, textvariable=self.vertex_count_var, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Создать / Сбросить", command=self.build_ui).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(controls, text="Буквы (Latin)", variable=self.use_latin_var, command=self.update_labels).pack(
            side=tk.LEFT, padx=10)

        ttk.Button(controls, text="Найти решение", command=self.on_solve_mapping).pack(side=tk.RIGHT, padx=5)

        # --- Основной контейнер (разделен на две части) ---
        main_container = ttk.Frame(self.root)
        main_container.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Левая часть: Матрица (Буквы)
        self.left_frame = ttk.LabelFrame(main_container, text="Матрица (Буквы)")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.matrix_container = ttk.Frame(self.left_frame)
        self.matrix_container.pack(padx=10, pady=10)

        # Правая часть: Граф (Числа)
        self.right_frame = ttk.LabelFrame(main_container, text="Граф (Числа)")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.editor = GraphEditor(self.right_frame, width=350, height=350)
        self.editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Результат ---
        self.result_frame = ttk.Frame(self.root)
        self.result_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        self.mapping_label = ttk.Label(self.result_frame, text="Нажмите 'Найти решение'", font=("Arial", 12))
        self.mapping_label.pack()

        # Инициализация
        self.build_ui()

    @staticmethod
    def get_label_text(index: int, use_latin: bool) -> str:
        if use_latin:
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        else:
            letters = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭюЯ"

        if index < len(letters):
            return letters[index]
        return f"{letters[index % len(letters)]}{index // len(letters)}"

    def current_label(self, index: int) -> str:
        return self.get_label_text(index, self.use_latin_var.get())

    def build_ui(self) -> None:
        try:
            n = int(self.vertex_count_var.get())
            if n < 2: raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целое число вершин >= 2")
            return

        # 1. Перестройка матрицы
        for w in self.matrix_container.winfo_children():
            w.destroy()

        self.matrix_entries = []
        self.labels_row = []
        self.labels_col = []

        # Заголовки столбцов
        ttk.Label(self.matrix_container, text="").grid(row=0, column=0)
        for j in range(n):
            lbl = ttk.Label(self.matrix_container, text=self.current_label(j), width=3, anchor="center")
            lbl.grid(row=0, column=j + 1, padx=1, pady=1)
            self.labels_col.append(lbl)

        # Строки
        for i in range(n):
            lbl = ttk.Label(self.matrix_container, text=self.current_label(i), width=3, anchor="center")
            lbl.grid(row=i + 1, column=0, padx=1, pady=1)
            self.labels_row.append(lbl)

            row_widgets = []
            for j in range(n):
                if i == j:
                    w = ttk.Label(self.matrix_container, text="-", width=3, anchor="center", state="disabled")
                    w.grid(row=i + 1, column=j + 1)
                else:
                    w = tk.Button(
                        self.matrix_container,
                        text="",
                        width=3,
                        relief="groove",
                        bg="white",
                        command=lambda ii=i, jj=j: self.toggle_matrix_cell(ii, jj)
                    )
                    w.grid(row=i + 1, column=j + 1, padx=1, pady=1)
                row_widgets.append(w)
            self.matrix_entries.append(row_widgets)

        # 2. Сброс графического редактора
        self.editor.reset_graph(n)
        self.mapping_label.config(text="Граф сброшен. Введите данные.")

    def toggle_matrix_cell(self, i: int, j: int) -> None:
        current_text = self.matrix_entries[i][j].cget("text")
        new_text = "1" if current_text == "" else ""
        new_bg = "lightgreen" if new_text == "1" else "white"

        # Симметричное обновление
        self.matrix_entries[i][j].config(text=new_text, bg=new_bg)
        self.matrix_entries[j][i].config(text=new_text, bg=new_bg)

    def update_labels(self) -> None:
        n = len(self.labels_col)
        for k in range(n):
            txt = self.current_label(k)
            self.labels_col[k].config(text=txt)
            self.labels_row[k].config(text=txt)

    def get_matrix_from_table(self) -> List[List[int]]:
        n = len(self.matrix_entries)
        matrix = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j: continue
                val = self.matrix_entries[i][j].cget("text")
                matrix[i][j] = 1 if val == "1" else 0
        return matrix

    def on_solve_mapping(self) -> None:
        # Читаем матрицу из левой панели
        m_letters = self.get_matrix_from_table()
        # Читаем граф из правой панели
        m_numbers = self.editor.get_matrix()

        if len(m_letters) != len(m_numbers):
            # Теоретически невозможно в этом UI, но для надежности
            messagebox.showerror("Ошибка", "Размеры графов не совпадают")
            return

        solver = GraphSolver()
        mapping = solver.solve(m_letters, m_numbers)

        if mapping is None:
            self.mapping_label.config(text="Решение: Графы не изоморфны (соответствие не найдено)", foreground="red")
        else:
            parts = []
            # Сортируем по буквам для красивого вывода
            for i in range(len(mapping)):
                letter = self.current_label(i)
                num = mapping[i] + 1
                parts.append(f"{letter}→{num}")

            result_text = "  |  ".join(parts)
            self.mapping_label.config(text=f"Ответ: {result_text}", foreground="blue")


def main() -> None:
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


