import sys

from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QFrame, QPushButton, QVBoxLayout, QApplication, QWidget
import qdarktheme

class VectorEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vector Editor")
        self.resize(800, 600)

        self._setup_layout()

    def _setup_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        tools_panel = QFrame()
        tools_panel.setFixedWidth(120)  # Фиксируем ширину

        # Внутри панели кнопки идут вертикально
        tools_layout = QVBoxLayout(tools_panel)
        tools_layout.addWidget(QPushButton("Line"))
        tools_layout.addWidget(QPushButton("Rect"))
        tools_layout.addWidget(QPushButton("Ellipse"))
        tools_layout.addStretch()  # Пружина, которая прижмет кнопки наверх

        canvas_placeholder = QFrame()

        main_layout.addWidget(tools_panel)
        main_layout.addWidget(canvas_placeholder)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = VectorEditorWindow()
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))

    window.show()

    sys.exit(app.exec())
