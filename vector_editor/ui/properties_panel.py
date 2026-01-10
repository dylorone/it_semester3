from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QSpinBox, QDoubleSpinBox, QPushButton,
                               QColorDialog, QFrame)
from PySide6.QtCore import Qt

from logic.commands import ChangeWidthCommand, ChangeColorCommand


class PropertiesPanel(QFrame):
    def __init__(self, scene, undo_stack: QUndoStack, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.undo_stack = undo_stack
        self.setFixedWidth(220)

        self._init_ui()

        self.scene.selectionChanged.connect(self.on_selection_changed)
        self.scene.changed.connect(self.on_scene_changed)

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.lbl_type = QLabel("Selection: None")
        layout.addWidget(self.lbl_type)
        layout.addSpacing(5)

        geo_layout = QHBoxLayout()

        self.spin_x = QDoubleSpinBox()
        self.spin_x.setRange(-10000, 10000)
        self.spin_x.setPrefix("X: ")
        self.spin_x.valueChanged.connect(self.on_geo_changed)

        self.spin_y = QDoubleSpinBox()
        self.spin_y.setRange(-10000, 10000)
        self.spin_y.setPrefix("Y: ")
        self.spin_y.valueChanged.connect(self.on_geo_changed)

        geo_layout.addWidget(self.spin_x)
        geo_layout.addWidget(self.spin_y)
        layout.addLayout(geo_layout)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Color:"))
        self.btn_color = QPushButton()
        self.btn_color.setFixedHeight(30)
        self.btn_color.clicked.connect(self.on_pick_color)
        layout.addWidget(self.btn_color)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Stroke Width:"))
        self.spin_width = QSpinBox()
        self.spin_width.setRange(1, 50)
        self.spin_width.valueChanged.connect(self.on_width_changed)
        layout.addWidget(self.spin_width)

        layout.addStretch()
        self.setEnabled(False)

    def on_selection_changed(self):
        selected = self.scene.selectedItems()

        if not selected:
            self.setEnabled(False)
            self.lbl_type.setText("Selection: None")
            return

        self.setEnabled(True)
        self._update_type_label(selected)
        self._update_geometry_ui(selected)
        self._update_properties_ui(selected)

    def on_scene_changed(self, region):
        if self.scene.selectedItems():
            self._update_geometry_ui(self.scene.selectedItems())

    def _update_type_label(self, selected):
        item = selected[0]
        type_text = getattr(item, "type_name", type(item).__name__).capitalize()

        if len(selected) > 1:
            type_text += f" (+{len(selected) - 1})"

        self.lbl_type.setText(type_text)

    def _update_geometry_ui(self, selected):
        self.spin_x.blockSignals(True)
        self.spin_y.blockSignals(True)

        item = selected[0]
        self.spin_x.setValue(item.x())
        self.spin_y.setValue(item.y())

        self.spin_x.blockSignals(False)
        self.spin_y.blockSignals(False)

    def _update_properties_ui(self, selected):
        first_width = -1
        is_mixed = False

        item0 = selected[0]
        if hasattr(item0, "pen"):
            first_width = item0.pen().width()
            first_color = item0.pen().color().name()
        elif hasattr(item0, "childItems") and item0.childItems():
            child = item0.childItems()[0]
            if hasattr(child, "pen"):
                first_width = child.pen().width()
                first_color = child.pen().color().name()
            else:
                first_width = 2
                first_color = "#000000"
        else:
            first_width = 2
            first_color = "#000000"

        if len(selected) > 1:
            pass

        self.spin_width.blockSignals(True)
        self.spin_width.setValue(first_width)
        self.spin_width.setStyleSheet("")
        self.spin_width.blockSignals(False)

    def on_geo_changed(self, value):
        if not self.scene.selectedItems():
            return

        new_x = self.spin_x.value()
        new_y = self.spin_y.value()

        for item in self.scene.selectedItems():
            item.setPos(new_x, new_y)

    def on_width_changed(self, value):
        if not self.scene.selectedItems():
            return

        self.undo_stack.beginMacro("Change width of selected")
        for item in self.scene.selectedItems():
            if hasattr(item, "set_pen_width"):
                self.undo_stack.push(ChangeWidthCommand(item, value))

        self.undo_stack.endMacro()
        self.scene.update()

    def on_pick_color(self):
        color = QColorDialog.getColor()
        if not color.isValid():
            return

        hex_color = color.name()
        self.btn_color.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #aaa;")

        self.undo_stack.beginMacro("Change color of selected")
        for item in self.scene.selectedItems():
            if hasattr(item, "set_active_color"):
                self.undo_stack.push(ChangeColorCommand(item, hex_color))

        self.undo_stack.endMacro()
        self.scene.update()
