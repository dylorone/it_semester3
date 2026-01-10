import sys
from PySide6.QtWidgets import QApplication
from app import VectorEditorWindow
import qdarktheme


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())

    window = VectorEditorWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
