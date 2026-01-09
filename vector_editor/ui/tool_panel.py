from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton


class ToolPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(120)
        self._setup_layout()

    def _setup_layout(self):
        layout = QVBoxLayout(self)

        self.btn_select = QPushButton("Select")
        self.btn_line = QPushButton("Line")
        self.btn_rect = QPushButton("Rectangle")
        self.btn_ellipse = QPushButton("Ellipse")

        self.btn_color = QPushButton("Color")
        self.btn_color.setStyleSheet("border: 2px solid #555;")

        layout.addWidget(self.btn_select)
        layout.addWidget(self.btn_line)
        layout.addWidget(self.btn_rect)
        layout.addWidget(self.btn_ellipse)

        layout.addSpacing(20)
        layout.addWidget(self.btn_color)

        layout.addStretch()

        layout.addSpacing(20)

        self.btn_group = QPushButton("Group")
        self.btn_ungroup = QPushButton("Ungroup")

        layout.addWidget(self.btn_group)
        layout.addWidget(self.btn_ungroup)

        layout.addStretch()