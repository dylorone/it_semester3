import sys
import math
from itertools import permutations
from typing import Dict, List, Optional, Tuple, Set

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QGridLayout, QLabel, QSpinBox,
                               QPushButton, QCheckBox, QFrame, QMessageBox,
                               QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
                               QGraphicsLineItem, QGraphicsSimpleTextItem, QGroupBox)
from PySide6.QtCore import Qt, QPointF, Signal, QObject
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainter

from graph_editor import GraphEditorWidget
from solver import GraphSolver


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЕГЭ Информатика №1: Solver (PySide6)")
        self.resize(1000, 700)

        self.vertex_count = 5
        self.use_latin = True
        self.matrix_buttons: List[List[QPushButton]] = []

        # --- ЦЕНТРАЛЬНЫЙ ВИДЖЕТ ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- ПАНЕЛЬ УПРАВЛЕНИЯ ---
        controls_group = QGroupBox("Настройки")
        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Кол-во вершин:"))
        self.spin_n = QSpinBox()
        self.spin_n.setRange(2, 12)
        self.spin_n.setValue(5)
        controls_layout.addWidget(self.spin_n)

        btn_gen = QPushButton("Сгенерировать / Сброс")
        btn_gen.clicked.connect(self.build_ui)
        controls_layout.addWidget(btn_gen)

        self.check_latin = QCheckBox("Латиница")
        self.check_latin.setChecked(True)
        self.check_latin.toggled.connect(self.update_labels)
        controls_layout.addWidget(self.check_latin)

        controls_layout.addStretch()

        btn_solve = QPushButton("Найти решение")
        btn_solve.clicked.connect(self.solve)
        btn_solve.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        controls_layout.addWidget(btn_solve)

        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)

        # --- РАБОЧАЯ ОБЛАСТЬ (Splitter аналог) ---
        work_layout = QHBoxLayout()

        # ЛЕВАЯ ЧАСТЬ: МАТРИЦА
        left_box = QGroupBox("Матрица смежности (Буквы)")
        self.matrix_layout = QGridLayout()
        # Чтобы матрица не разъезжалась, добавляем её во wrapper widget или выравниваем
        matrix_wrapper = QWidget()
        matrix_wrapper.setLayout(self.matrix_layout)

        # Scroll area если матрица большая (опционально), но здесь просто положим в Layout
        # Добавим spacer, чтобы матрица прижималась к верху
        left_vbox = QVBoxLayout()
        left_vbox.addWidget(matrix_wrapper)
        left_vbox.addStretch()
        left_box.setLayout(left_vbox)

        work_layout.addWidget(left_box, stretch=1)

        # ПРАВАЯ ЧАСТЬ: ГРАФ
        right_box = QGroupBox("Граф (Числа)")
        right_layout = QVBoxLayout()
        self.graph_editor = GraphEditorWidget()
        right_layout.addWidget(self.graph_editor)
        right_layout.addWidget(QLabel("ЛКМ: выделить вершину. ЛКМ по другой: соединить.\nDrag'n'Drop: переместить."))
        right_box.setLayout(right_layout)

        work_layout.addWidget(right_box, stretch=2)

        main_layout.addLayout(work_layout)

        # --- РЕЗУЛЬТАТ ---
        self.lbl_result = QLabel("Ожидание ввода...")
        self.lbl_result.setStyleSheet("font-size: 14px; color: blue; border: 1px solid gray; padding: 5px;")
        self.lbl_result.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_result)

        # Initial Build
        self.build_ui()

    def get_label(self, idx: int) -> str:
        if self.check_latin.isChecked():
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        else:
            letters = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ"

        if idx < len(letters):
            return letters[idx]
        return f"{letters[idx % len(letters)]}{idx // len(letters)}"

    def build_ui(self):
        n = self.spin_n.value()
        self.vertex_count = n

        # 1. Очистка матрицы
        # Удаляем старые виджеты из layout
        while self.matrix_layout.count():
            item = self.matrix_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.matrix_buttons = []
        self.row_labels = []
        self.col_labels = []

        # Заголовки столбцов
        for j in range(n):
            lbl = QLabel(self.get_label(j))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedSize(30, 30)
            self.matrix_layout.addWidget(lbl, 0, j + 1)
            self.col_labels.append(lbl)

        # Строки
        for i in range(n):
            lbl = QLabel(self.get_label(i))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedSize(30, 30)
            self.matrix_layout.addWidget(lbl, i + 1, 0)
            self.row_labels.append(lbl)

            row_btns = []
            for j in range(n):
                if i == j:
                    btn = QPushButton("-")
                    btn.setFixedSize(30, 30)
                    btn.setEnabled(False)
                    btn.setStyleSheet("background-color: #eee; border: none;")
                else:
                    btn = QPushButton("")
                    btn.setFixedSize(30, 30)
                    btn.setCheckable(True)
                    # Стили для состояний
                    btn.setStyleSheet("""
                        QPushButton { background-color: white; border: 1px solid #ccc; }
                        QPushButton:checked { background-color: #90EE90; }
                    """)
                    # Лямбда с замыканием
                    btn.clicked.connect(lambda checked, r=i, c=j: self.on_matrix_click(r, c, checked))

                self.matrix_layout.addWidget(btn, i + 1, j + 1)
                row_btns.append(btn)
            self.matrix_buttons.append(row_btns)

        # 2. Сброс графа
        self.graph_editor.reset_graph(n)
        self.lbl_result.setText("Графы сброшены. Введите данные.")

    def on_matrix_click(self, r, c, checked):
        # Симметричное обновление
        btn_sym = self.matrix_buttons[c][r]
        if r != c:
            # Блокируем сигналы, чтобы не вызвать рекурсию (хотя здесь checked передается явно, но для надежности)
            btn_sym.blockSignals(True)
            btn_sym.setChecked(checked)
            btn_sym.blockSignals(False)

    def update_labels(self):
        # Обновляем текст заголовков матрицы
        n = len(self.row_labels)
        for i in range(n):
            txt = self.get_label(i)
            self.row_labels[i].setText(txt)
            self.col_labels[i].setText(txt)

    def get_matrix_data(self) -> List[List[int]]:
        n = self.vertex_count
        mat = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j: continue
                # Проверяем, является ли виджет кнопкой и нажат ли он
                btn = self.matrix_buttons[i][j]
                if isinstance(btn, QPushButton) and btn.isChecked():
                    mat[i][j] = 1
        return mat

    def solve(self):
        mat_letters = self.get_matrix_data()
        mat_numbers = self.graph_editor.get_adjacency_matrix()

        solver = GraphSolver()
        mapping = solver.solve(mat_letters, mat_numbers)

        if mapping:
            res_str = []
            # Сортируем по ключам (индексам букв)
            for k in sorted(mapping.keys()):
                letter = self.get_label(k)
                number = mapping[k] + 1
                res_str.append(f"{letter} → {number}")

            self.lbl_result.setText("Ответ:  " + "  |  ".join(res_str))
            self.lbl_result.setStyleSheet(
                "font-size: 14px; color: green; font-weight: bold; border: 1px solid gray; padding: 5px;")
        else:
            self.lbl_result.setText("Решение не найдено (графы не изоморфны)")
            self.lbl_result.setStyleSheet("font-size: 14px; color: red; border: 1px solid gray; padding: 5px;")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()