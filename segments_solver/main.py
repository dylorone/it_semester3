import sys
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QTextEdit, QMessageBox)
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtCore import Qt, QRectF

# --- ЯДРО SOLVER ---
class ShrinkSolver:
    def __init__(self):
        self.segments = {}

    def clean_text(self, text):
        """Очистка от спецсимволов и унификация"""
        if not text: return ""
        unicode_map = {
            '𝑥': 'x', '𝑦': 'y', '𝑧': 'z',
            '𝑃': 'P', '𝑄': 'Q', '𝐴': 'A', '𝐵': 'B', '𝐶': 'C', '𝐷': 'D',
            '−': '-', '–': '-', '—': '-',
            '[': '[', ']': ']', '(': '(', ')': ')',
            ' ': ' ', # Неразрывный пробел
            '\t': ' '
        }
        for u, a in unicode_map.items():
            text = text.replace(u, a)
        return text

    def parse_input(self, segments_text):
        self.segments = {}
        clean_seg_text = self.clean_text(segments_text)
        
        # Улучшенная регулярка: допускает пробелы везде (напр. [ 10 ; 20 ])
        pattern = re.compile(r'([A-Za-z]+)\s*=\s*\[\s*(\d+)\s*[;,]\s*(\d+)\s*\]')
        
        all_coords = []
        for line in clean_seg_text.split('\n'):
            match = pattern.search(line)
            if match:
                name, start, end = match.groups()
                start, end = int(start), int(end)
                self.segments[name] = (start, end)
                all_coords.extend([start, end])
        
        if not all_coords:
            return 0, 100
        return min(all_coords) - 10, max(all_coords) + 10

    def prepare_expression(self, expr_raw):
        expr = self.clean_text(expr_raw)
        
        ops_map = {
            '¬': 'n',
            'not ': 'n',
            '≡': ' == ',
            '→': ' <= ',
            '∧': ' and ',
            '∨': ' or ',
            '&&': ' and ',
            '||': ' or ',
            '∈': ' in '
        }
        
        # Сначала меняем длинные операторы, потом короткие
        for op in sorted(ops_map.keys(), key=len, reverse=True):
            expr = expr.replace(op, ops_map[op])
            
        # 2. Подстановка отрезков (P, Q...)
        for name, (start, end) in self.segments.items():
            pattern = fr"\bx\s+in\s+{name}\b"
            replacement = f"({start} <= x <= {end})"
            expr = re.sub(pattern, replacement, expr)
            
        # 3. Замена A
        expr = re.sub(r"\bx\s+in\s+A\b", "(a0 <= x <= a1)", expr)
        
        return expr

    def solve(self, expr_raw, segments_text):
        try:
            univ_min, univ_max = self.parse_input(segments_text)
            py_expr = self.prepare_expression(expr_raw)
            
            # Проверка на грубые ошибки замены
            if '∈' in py_expr or '→' in py_expr:
                return "Ошибка: не все спецсимволы заменены. Проверьте ввод.", 0, None

            # Компиляция выражения
            try:
                code_obj = compile(py_expr, '<string>', 'eval')
            except SyntaxError as e:
                # Часто ошибка здесь из-за баланса скобок
                return f"Ошибка синтаксиса (проверьте скобки):\n{py_expr}\n\n{e}", 0, None
            
            # Контекст для eval (включая функцию n для отрицания)
            # n(x) безопасно инвертирует булево значение
            eval_globals = {'n': lambda b: not b}
            
            check_range = range(univ_min, univ_max + 1)
            A = [univ_min, univ_max]

            # Функция проверки
            def check_all_x(current_a0, current_a1):
                if current_a0 > current_a1: return False
                for x in check_range:
                    ctx = {'x': x, 'a0': current_a0, 'a1': current_a1}
                    # Объединяем глобальный контекст (функция n) и локальный (x, a0, a1)
                    try:
                        if not eval(code_obj, eval_globals, ctx):
                            return False
                    except NameError as ne:
                        # Если вылезло "name 'Q' is not defined", значит регулярка не поймала Q
                        raise Exception(f"Не найден отрезок или переменная: {ne}")
                return True

            # --- Алгоритм сужения ---
            
            # Слева
            while A[0] <= A[1]:
                if check_all_x(A[0], A[1]):
                    A[0] += 1
                else:
                    break
            A[0] -= 1

            # Справа
            while A[1] >= A[0]:
                if check_all_x(A[0], A[1]):
                    A[1] -= 1
                else:
                    break
            A[1] += 1
            
            length = A[1] - A[0]
            if length < 0:
                return "Пустое множество", 0, None
                
            return f"Отрезок A: [{A[0]}; {A[1]}]\nДлина: {length}", length, (A[0], A[1])

        except Exception as e:
            return f"Ошибка выполнения: {e}", 0, None

# --- ВИЗУАЛИЗАЦИЯ ---

class Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.segments = {}
        self.result_segment = None
        self.setMinimumHeight(200)
        self.setStyleSheet("background-color: white; border: 1px solid #ccc;")

    def update_data(self, input_segs, res_seg):
        self.segments = input_segs
        self.result_segment = res_seg
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        
        coords = []
        for s, e in self.segments.values():
            coords.extend([s, e])
        if self.result_segment:
            coords.extend([self.result_segment[0], self.result_segment[1]])
        
        if not coords:
            painter.drawText(self.rect(), Qt.AlignCenter, "Нет данных")
            return
            
        mn, mx = min(coords), max(coords)
        pad = (mx - mn) * 0.15 if mx != mn else 10
        min_v, max_v = mn - pad, mx + pad
        scale = w / (max_v - min_v) if max_v != min_v else 1
        
        def to_px(val): return (val - min_v) * scale

        ay = h - 40
        painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(0, ay, w, ay)
        
        font = QFont("Arial", 9)
        painter.setFont(font)
        drawn_labels = set()
        
        for p in sorted(list(set(coords))):
            px = to_px(p)
            painter.drawLine(px, ay - 6, px, ay + 6)
            if not any(abs(px - d) < 25 for d in drawn_labels):
                painter.drawText(px - 10, ay + 25, str(int(p)))
                drawn_labels.add(px)

        y = 20
        colors = [QColor("#1E90FF"), QColor("#32CD32"), QColor("#FF8C00")]
        i = 0
        for name, (s, e) in self.segments.items():
            px1, px2 = to_px(s), to_px(e)
            rect = QRectF(px1, y, max(1, px2-px1), 25)
            painter.setBrush(QBrush(colors[i % 3]))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, 4, 4)
            painter.setPen(Qt.black)
            painter.drawText(rect, Qt.AlignCenter, name)
            y += 35
            i += 1
            
        if self.result_segment:
            s, e = self.result_segment
            px1, px2 = to_px(s), to_px(e)
            rect = QRectF(px1, ay - 35, max(1, px2-px1), 30)
            painter.setBrush(QBrush(QColor("#DC143C")))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, 4, 4)
            painter.setPen(Qt.white)
            painter.drawText(rect, Qt.AlignCenter, f"A [{s}; {e}]")


# --- ГЛАВНОЕ ОКНО ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Солвер ЕГЭ №15 (Fix Unicode)")
        self.resize(750, 550)
        
        self.solver = ShrinkSolver()
        
        cw = QWidget()
        self.setCentralWidget(cw)
        layout = QVBoxLayout(cw)
        
        input_row = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel("Логическое выражение:"))
        self.expr_edit = QLineEdit("(𝑥∈𝑃)→(((𝑥∈𝑄)∧¬(𝑥∈𝐴))→¬(𝑥∈𝑃))") # Тестовый пример по умолчанию
        self.expr_edit.setPlaceholderText("Вставьте формулу из PDF")
        left.addWidget(self.expr_edit)
        
        right = QVBoxLayout()
        right.addWidget(QLabel("Отрезки:"))
        self.segs_edit = QTextEdit()
        self.segs_edit.insertPlainText("P=[10; 20]\nQ=[15; 25]")
        self.segs_edit.setMaximumHeight(80)
        right.addWidget(self.segs_edit)
        
        input_row.addLayout(left, 2)
        input_row.addLayout(right, 1)
        
        self.btn_solve = QPushButton("Решить")
        self.btn_solve.setFixedHeight(45)
        self.btn_solve.clicked.connect(self.run_calc)
        
        self.res_label = QLabel("Нажмите Решить")
        self.res_label.setStyleSheet("font-size: 15px; font-weight: bold; margin: 10px;")
        
        self.vis = Visualizer()
        
        layout.addLayout(input_row)
        layout.addWidget(self.btn_solve)
        layout.addWidget(self.res_label)
        layout.addWidget(self.vis, 1)
        
    def run_calc(self):
        expr = self.expr_edit.text()
        segs = self.segs_edit.toPlainText()
        text, length, res_seg = self.solver.solve(expr, segs)
        self.res_label.setText(text)
        self.vis.update_data(self.solver.segments, res_seg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())