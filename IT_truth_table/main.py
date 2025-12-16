import tkinter as tk
from tkinter import ttk, messagebox

from table_generator import TruthTableGenerator
from solver import solve_variable_assignment

class TruthTableUI:
    def __init__(self):
        self.root = tk.Tk()
        self.generator = TruthTableGenerator()
        self.current_table = []
        self.filter_mode = tk.StringVar(value="all")
        
        self.setup_ui()
    
    def setup_ui(self):
        # self.root.tk.call("source", "azure.tcl")
        # self.root.tk.call("set_theme", "dark")

        # sv_ttk.set_theme("dark")

        self.root.title("Генератор таблиц истинности")
        self.root.geometry("1200x700")
                
        left_panel = ttk.Frame(self.root, padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_panel = ttk.Frame(self.root, padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        separator = ttk.Separator(self.root, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)
    
    def setup_left_panel(self, main_frame):
        
        title_label = ttk.Label(main_frame, text="Генератор таблиц истинности", 
                               font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        input_frame = ttk.LabelFrame(main_frame, text="Выражение", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Введите булево выражение (переменные: x, y, z, w):").pack(anchor=tk.W)
        
        self.expression_var = tk.StringVar(value="(x ∨ y) → (x ≡ z)")
        expression_entry = ttk.Entry(input_frame, textvariable=self.expression_var, width=50)
        expression_entry.pack(fill=tk.X, pady=(5, 5))
        
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Сгенерировать таблицу истинности", 
                  command=self.generate_table).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(buttons_frame, text="Очистить", 
                  command=self.clear_table).pack(side=tk.LEFT)
        
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтр результатов", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        filter_buttons_frame = ttk.Frame(filter_frame)
        filter_buttons_frame.pack()
        
        ttk.Radiobutton(filter_buttons_frame, text="Показать все", variable=self.filter_mode, 
                       value="all", command=self.apply_filter).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(filter_buttons_frame, text="Только true", variable=self.filter_mode, 
                       value="true", command=self.apply_filter).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(filter_buttons_frame, text="Только false", variable=self.filter_mode, 
                       value="false", command=self.apply_filter).pack(side=tk.LEFT)
        
        results_frame = ttk.LabelFrame(main_frame, text="Таблица истинности", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('x', 'y', 'z', 'w', 'result')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col if col != 'result' else 'Результат')
            self.tree.column(col, width=80, anchor=tk.CENTER)
        
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_right_panel(self, right_panel):
        self.solver_results = []
        self.solver_columns = ('x', 'y', 'z', 'w', 'result')
        self.solver_table_data = []
        self.solver_item_to_index = {}
        self.partial_rows = []
        
        title_label = ttk.Label(right_panel, text="Решатель таблиц истинности", 
                               font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        instructions_frame = ttk.Frame(right_panel)
        instructions_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(instructions_frame, text="Кликните на ячейки для установки частичных значений:").pack(anchor=tk.W)
        ttk.Label(instructions_frame, text="? = не задано, 0 = False, 1 = True").pack(anchor=tk.W)
        
        buttons_frame = ttk.Frame(right_panel)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="Обновить таблицу", 
                  command=self.update_solver_table).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Найти соответствия переменных", 
                  command=self.solve_variable_assignment).pack(side=tk.LEFT, padx=(0, 5))
        
        solver_table_frame = ttk.LabelFrame(right_panel, text="Интерактивная таблица", padding=10)
        solver_table_frame.pack(fill=tk.BOTH, expand=True)
        
        self.solver_tree = ttk.Treeview(solver_table_frame, columns=self.solver_columns, show='headings', height=15)
        for col in self.solver_columns:
            heading = '?' if col != 'result' else 'Результат'
            self.solver_tree.heading(col, text=heading)
            self.solver_tree.column(col, width=80, anchor=tk.CENTER)
        
        solver_v_scrollbar = ttk.Scrollbar(solver_table_frame, orient=tk.VERTICAL, command=self.solver_tree.yview)
        self.solver_tree.configure(yscrollcommand=solver_v_scrollbar.set)
        
        self.solver_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        solver_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.solver_tree.bind('<Button-1>', self.on_solver_click)
        
        result_frame = ttk.LabelFrame(right_panel, text="Результат", padding=10)
        result_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.result_label = tk.Text(result_frame, height=3, wrap=tk.WORD, font=("Consolas", 12))
        self.result_label.pack(fill=tk.X)
        
        self.result_label.config(state=tk.DISABLED)
        
        clear_button_frame = ttk.Frame(right_panel)
        clear_button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(clear_button_frame, text="Очистить частичные значения", 
                  command=self.clear_partial_values).pack()

    
    def generate_table(self):
        expression = self.expression_var.get().strip()
        if not expression:
            messagebox.showerror("Error", "Пожалуйста, введите булево выражение.")
            return
        
        self.root.update()
        
        self.current_table = self.generator.generate_truth_table(expression)
        self.display_table()
            
    
    def display_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtered_table = self.get_filtered_table()
        
        for row in filtered_table:
            values = [str(int(row['x'])), str(int(row['y'])), str(int(row['z'])), str(int(row['w'])), str(int(row['result']))]
            self.tree.insert('', tk.END, values=values)
    
    def get_filtered_table(self):
        if self.filter_mode.get() == "all":
            return self.current_table
        elif self.filter_mode.get() == "true":
            return [row for row in self.current_table if row['result']]
        else:
            return [row for row in self.current_table if not row['result']]
    
    def apply_filter(self):
        if self.current_table:
            self.display_table()
            filtered_count = len(self.get_filtered_table())
    
    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.current_table = []
    
    def update_solver_table(self):
        if not self.current_table:
            return
        
        self.solver_table_data = []
        self.solver_item_to_index = {}
        for item in self.solver_tree.get_children():
            self.solver_tree.delete(item)
        
        filtered_table = self.get_filtered_table()
        
        for row_idx, row in enumerate(filtered_table):
            row_data = {
                'x': row['x'],
                'y': row['y'],
                'z': row['z'],
                'w': row['w'],
                'result': row['result'],
                'partial': {'x': None, 'y': None, 'z': None, 'w': None, 'result': None},
            }
            self.solver_table_data.append(row_data)
            values = ['?', '?', '?', '?', '?']
            item_id = self.solver_tree.insert('', tk.END, values=values)
            self.solver_item_to_index[item_id] = row_idx
        
    
    def on_solver_click(self, event):
        item_id = self.solver_tree.identify_row(event.y)
        col_id = self.solver_tree.identify_column(event.x)
        
        if not item_id or not col_id or item_id == '':
            return
        
        try:
            col_index = int(col_id.replace('#', '')) - 1
        except (ValueError, AttributeError):
            return
        
        if col_index < 0 or col_index >= len(self.solver_columns):
            return
        
        variable = self.solver_columns[col_index]
        row_idx = self.solver_item_to_index.get(item_id)
        if row_idx is None:
            return
        
        current_partial = self.solver_table_data[row_idx]['partial'][variable]
        if current_partial is None:
            new_partial = 0
            new_text = '0'
        elif current_partial == 0:
            new_partial = 1
            new_text = '1'
        else:
            new_partial = None
            new_text = '?'
        self.solver_table_data[row_idx]['partial'][variable] = new_partial
        
        current_values = list(self.solver_tree.item(item_id, 'values'))
        current_values[col_index] = new_text
        self.solver_tree.item(item_id, values=current_values)
        
        return "break"
    
    def clear_partial_values(self):
        for idx, row_data in enumerate(self.solver_table_data):
            for var in ['x', 'y', 'z', 'w', 'result']:
                row_data['partial'][var] = None
        for item_id, row_idx in self.solver_item_to_index.items():
            values = ['?', '?', '?', '?', '?']
            self.solver_tree.item(item_id, values=values)
    
    
    def solve_variable_assignment(self):
        if not self.current_table:
            return
        
        partial_rows = []
        result_column = []
        for row_data in self.solver_table_data:
            partial_row = []
            has_partial = False
            for var in ['x', 'y', 'z', 'w']:
                if row_data['partial'][var] is not None:
                    partial_row.append(row_data['partial'][var])
                    has_partial = True
                else:
                    partial_row.append(None)
            
            if has_partial:
                partial_rows.append(partial_row)
                if row_data['partial']['result'] is not None:
                    result_column.append(row_data['partial']['result'])
                else:
                    result_column.append(None)
        
        if not partial_rows:
            return
        
        expression = self.expression_var.get().strip()
        if not expression:
            return
        
        try:
            solutions = solve_variable_assignment(partial_rows, expression, result_column)
            self.solver_results = solutions
            self.display_solutions()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при решении: {str(e)}")
    
    
    def display_solutions(self):
        if not self.solver_results:
            self.result_label.config(state=tk.NORMAL)
            self.result_label.delete(1.0, tk.END)
            self.result_label.insert(1.0, "Нет решений")
            self.result_label.config(state=tk.DISABLED)
            return
        
        self.result_label.config(state=tk.NORMAL)
        self.result_label.delete(1.0, tk.END)
        self.result_label.insert(1.0, "".join(self.solver_results[0]))
        self.result_label.config(state=tk.DISABLED)
    
    def run(self):
        self.root.mainloop()


def main():
    app = TruthTableUI()
    app.run()


if __name__ == "__main__":
    main()


