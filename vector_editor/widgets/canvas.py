from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtGui import QBrush, QColor, QPainter, QUndoStack
from PySide6.QtCore import Qt

from logic.commands import DeleteCommand
from logic.shapes import Group
from logic.tools import CreationTool, SelectionTool


class EditorCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(50)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setSceneRect(0, 0, 800, 600)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setBackgroundBrush(QBrush(QColor("#404040")))
        self.scene.addRect(0, 0, 800, 600, brush=QBrush(QColor("white")))

        self.setMouseTracking(True)

        self.current_color = "#000000"

        self.tools = {
            "select": SelectionTool(self, self.undo_stack),
            "line": CreationTool(self, "line", self.undo_stack),
            "rect": CreationTool(self, "rect", self.undo_stack),
            "ellipse": CreationTool(self, "ellipse", self.undo_stack)
        }

        self.active_tool = self.tools["select"]

    def set_tool(self, tool_name):
        if tool_name in self.tools:
            self.active_tool = self.tools[tool_name]

            if tool_name == "select":
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
                self.setCursor(Qt.CursorShape.ArrowCursor)
            else:
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
                self.setCursor(Qt.CursorShape.CrossCursor)

            print(f"Canvas: Switched to {tool_name}")

    def set_color(self, color_hex):
        self.current_color = color_hex

    def mousePressEvent(self, event):
        self.active_tool.mouse_press(event)

    def mouseMoveEvent(self, event):
        self.active_tool.mouse_move(event)

    def mouseReleaseEvent(self, event):
        self.active_tool.mouse_release(event)

    def group_selection(self):
        """Создает группу (Composite) из выделенных элементов"""
        selected_items = self.scene.selectedItems()

        if not selected_items:
            print("Ничего не выделено для группировки")
            return

        group = Group()

        self.scene.addItem(group)

        for item in selected_items:
            item.setSelected(False)

            group.addToGroup(item)

        group.setSelected(True)
        print(f"Группа создана из {len(selected_items)} элементов")

    def ungroup_selection(self):
        """Разбивает группу обратно на элементы"""
        selected_items = self.scene.selectedItems()

        if not selected_items:
            return

        items_to_ungroup = []
        for item in selected_items:
            if isinstance(item, Group):
                items_to_ungroup.append(item)

        if not items_to_ungroup:
            return

        for group in items_to_ungroup:
            self.scene.destroyItemGroup(group)

        print(f"Разгруппировано {len(items_to_ungroup)} групп")

    def delete_selection(self):
        """Удаляет выделенные объекты с поддержкой Undo"""
        selected = self.scene.selectedItems()
        if not selected:
            return

        self.undo_stack.beginMacro("Delete Selection")

        for item in selected:
            cmd = DeleteCommand(self.scene, item)
            self.undo_stack.push(cmd)

        self.undo_stack.endMacro()
        print("Deleted items")
