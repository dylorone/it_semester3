import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QGroupBox, QGridLayout, QSpinBox,
                             QCheckBox, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from model import GameModel, GameOperation, WinCondition

class StoneHeapsSolver(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Солвер задач ЕГЭ 19-21: Каменные кучи")
        self.setGeometry(100, 100, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        
        title = QLabel("Солвер для задач ЕГЭ 19-21: Игра с каменными кучами")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        self.operation_widgets = [] # Список для хранения виджетов (чекбокс, поле ввода, кнопка)

        self.create_parameters_group(main_layout)
        self.create_operations_group(main_layout)
        self.create_solve_buttons_group(main_layout)
        self.create_results_group(main_layout)
        
    def create_parameters_group(self, parent_layout):
        """Создает группу для ввода основных параметров"""
        group = QGroupBox("Параметры игры")
        layout = QGridLayout(group)
        
        layout.addWidget(QLabel("Камней для выигрыша:"), 1, 0)
        self.win_condition = QSpinBox()
        self.win_condition.setRange(1, 10000)
        self.win_condition.setValue(444)
        layout.addWidget(self.win_condition, 1, 1)
        
        # Максимальное значение S для анализа
        layout.addWidget(QLabel("Максимальное S для анализа:"), 2, 0)
        self.max_s = QSpinBox()
        self.max_s.setRange(1, 1000)
        self.max_s.setValue(400)
        layout.addWidget(self.max_s, 2, 1)
        
        parent_layout.addWidget(group)
        
    def create_operations_group(self, parent_layout):
        """Создает группу для ввода операций"""
        group = QGroupBox("Операции над кучей")
        main_group_layout = QVBoxLayout(group)

        # Создаем область с прокруткой для списка операций
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        # Этот layout будет содержать все строки с операциями
        self.operations_layout = QVBoxLayout(scroll_widget)
        self.operations_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(scroll_widget)
        main_group_layout.addWidget(scroll_area)

        # Добавляем операции по умолчанию
        default_ops = ["+2", "+5", "*3"]
        for op_text in default_ops:
            self.add_operation(op_text=op_text)
        
        # Кнопка для добавления новой операции
        add_op_btn = QPushButton("Добавить операцию")
        add_op_btn.clicked.connect(self.add_operation)
        main_group_layout.addWidget(add_op_btn)
        
        parent_layout.addWidget(group)
    
    def create_solve_buttons_group(self, parent_layout):
        """Создает группу с кнопками для решения задач"""
        group = QGroupBox("Решение задач")
        layout = QHBoxLayout(group)
        
        self.solve_19_btn = QPushButton("Задача 19\n(Ваня выигрывает первым ходом)")
        self.solve_19_btn.clicked.connect(self.solve_task_19)
        self.solve_19_btn.setMinimumHeight(60)
        layout.addWidget(self.solve_19_btn)
        
        self.solve_20_btn = QPushButton("Задача 20\n(Петя выигрывает вторым ходом)")
        self.solve_20_btn.clicked.connect(self.solve_task_20)
        self.solve_20_btn.setMinimumHeight(60)
        layout.addWidget(self.solve_20_btn)
        
        self.solve_21_btn = QPushButton("Задача 21\n(Ваня выигрывает 1-2 ходом)")
        self.solve_21_btn.clicked.connect(self.solve_task_21)
        self.solve_21_btn.setMinimumHeight(60)
        layout.addWidget(self.solve_21_btn)
        
        
        self.solve_all_btn = QPushButton("Решить все задачи")
        self.solve_all_btn.clicked.connect(self.solve_all_tasks)
        self.solve_all_btn.setMinimumHeight(60)
        self.solve_all_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        layout.addWidget(self.solve_all_btn)
        
        parent_layout.addWidget(group)
        
    def create_results_group(self, parent_layout):
        """Создает группу для отображения результатов"""
        group = QGroupBox("Результаты")
        layout = QVBoxLayout(group)
        
        
        self.results_text = QTextEdit()
        self.results_text.setMinimumHeight(200)
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.results_text)
        
        
        clear_btn = QPushButton("Очистить результаты")
        clear_btn.clicked.connect(self.clear_results)
        layout.addWidget(clear_btn)
        
        parent_layout.addWidget(group)
        
    def add_operation(self, op_text=""):
        """Добавляет новую строку для ввода операции в интерфейс."""
        op_row_widget = QWidget() # Контейнер для одной строки
        op_layout = QHBoxLayout(op_row_widget)
        op_layout.setContentsMargins(0,0,0,0)

        checkbox = QCheckBox()
        checkbox.setChecked(True)
        
        op_input = QLineEdit(str(op_text)) # Преобразуем в строку на случай если придет не строка
        op_input.setPlaceholderText("Например: +1, *2")
        
        remove_btn = QPushButton("Удалить")

        op_layout.addWidget(checkbox)
        op_layout.addWidget(op_input)
        op_layout.addWidget(remove_btn)

        # Добавляем виджет строки в основной layout операций
        self.operations_layout.addWidget(op_row_widget)
        
        # Сохраняем виджеты для последующего доступа
        widget_tuple = (checkbox, op_input, op_row_widget)
        self.operation_widgets.append(widget_tuple)
        
        # Связываем кнопку удаления с функцией удаления этой конкретной строки
        # Мы используем lambda, чтобы передать нужные аргументы в слот
        remove_btn.clicked.connect(lambda: self.remove_operation(widget_tuple))

    def remove_operation(self, widget_tuple):
        """Удаляет строку операции из интерфейса и из списка."""
        if widget_tuple in self.operation_widgets:
            # Удаляем из нашего списка отслеживания
            self.operation_widgets.remove(widget_tuple)
            
            # Получаем главный виджет-контейнер строки и удаляем его
            # Qt автоматически удалит и все дочерние виджеты (чекбокс, поле, кнопку)
            row_widget = widget_tuple[2]
            row_widget.deleteLater()
            
    def solve_task_19(self):
        """Решает задачу 19"""
        self.results_text.append("=== ЗАДАЧА 19 ===")
        self.results_text.append("Поиск минимального S, при котором:")
        self.results_text.append("- Петя не может выиграть за один ход")
        self.results_text.append("- Ваня может выиграть первым ходом при любом ходе Пети")
        self.results_text.append("")
        self.results_text.append("Алгоритм решения будет реализован в следующей версии...")
        self.results_text.append("")
        
    def solve_task_20(self):
        """Решает задачу 20"""
        self.results_text.append("=== ЗАДАЧА 20 ===")
        self.results_text.append("Поиск двух наименьших S, при которых:")
        self.results_text.append("- У Пети есть выигрышная стратегия")
        self.results_text.append("- Петя не может выиграть за один ход")
        self.results_text.append("- Петя может выиграть вторым ходом")
        self.results_text.append("")
        self.results_text.append("Алгоритм решения будет реализован в следующей версии...")
        self.results_text.append("")
        
    def solve_task_21(self):
        """Решает задачу 21"""
        self.results_text.append("=== ЗАДАЧА 21 ===")
        self.results_text.append("Поиск максимального S, при котором:")
        self.results_text.append("- У Вани есть выигрышная стратегия (1-2 ход)")
        self.results_text.append("- У Вани нет стратегии для выигрыша первым ходом")
        self.results_text.append("")
        self.results_text.append("Алгоритм решения будет реализован в следующей версии...")
        self.results_text.append("")
    
    # Внутри класса StoneHeapsSolver
    def _create_game_from_ui(self) -> GameModel | None:
        """Собирает объект GameModel из текущих настроек в интерфейсе."""
        try:
            # Собираем активные операции
            active_ops = []
            for checkbox, op_input, _ in self.operation_widgets: 
                if checkbox.isChecked():
                    op_text = op_input.text().strip()
                    if op_text:  # Убедимся, что поле не пустое
                        active_ops.append(GameOperation(op_text))
            
            if not active_ops:
                self.results_text.append("Ошибка: Не выбрано ни одной операции!")
                return None

            # Создаем условие выигрыша
            win_con = WinCondition(self.win_condition.value())

            # Создаем и возвращаем модель игры
            return GameModel(operations=active_ops, win_condition=win_con)

        except ValueError as e:
            self.results_text.append(f"Ошибка в параметрах игры: {e}")
            return None
    
    def solve_all_tasks(self):
        """Решает все задачи, используя GameModel"""
        self.clear_results()
        self.results_text.append("=== РЕШЕНИЕ ВСЕХ ЗАДАЧ ===")
        
        game = self._create_game_from_ui()
        if game is None:
            return # Если была ошибка при создании игры, прекращаем работу

        max_s_val = self.max_s.value()
        # Запускаем полный анализ
        game.analyze_range(max_s_val)
        
        # Задача 19
        self.results_text.append("--- ЗАДАЧА 19 ---")
        self.results_text.append("S, при которых Ваня выигрывает первым ходом (состояния V1):")
        task_19_res = game.get_task_19_solution()
        self.results_text.append(f"Найденные S: {task_19_res}")
        if task_19_res:
            self.results_text.append(f"ОТВЕТ: Минимальное S = {min(task_19_res)}\n")
        else:
            self.results_text.append("ОТВЕТ: Подходящих S не найдено.\n")

        # Задача 20
        self.results_text.append("--- ЗАДАЧА 20 ---")
        self.results_text.append("S, при которых Петя выигрывает вторым ходом (состояния P2):")
        task_20_res = game.get_task_20_solution()
        self.results_text.append(f"Найденные S: {task_20_res}")
        if len(task_20_res) >= 2:
            task_20_res.sort()
            self.results_text.append(f"ОТВЕТ: Два наименьших S = {task_20_res[0]}, {task_20_res[1]}\n")
        else:
            self.results_text.append("ОТВЕТ: Не удалось найти два наименьших S.\n")

        # Задача 21
        self.results_text.append("--- ЗАДАЧА 21 ---")
        self.results_text.append("S, при которых Ваня выигрывает 1-м или 2-м ходом (состояния V2):")
        task_21_res = game.get_task_21_solution()
        self.results_text.append(f"Найденные S: {task_21_res}")
        if task_21_res:
            self.results_text.append(f"ОТВЕТ: Максимальное S = {max(task_21_res)}\n")
        else:
            self.results_text.append("ОТВЕТ: Подходящих S не найдено.\n")
        
    def clear_results(self):
        """Очищает результаты"""
        self.results_text.clear()

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    
    app.setStyleSheet("""
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555555;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QPushButton {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 5px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #505050;
        }
        QPushButton:pressed {
            background-color: #353535;
        }
        QLineEdit, QSpinBox {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 5px;
        }
        QTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #555555;
            border-radius: 3px;
        }
    """)
    
    window = StoneHeapsSolver()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
