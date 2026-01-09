from abc import ABC, abstractmethod
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt

from logic.commands import AddShapeCommand, MoveCommand
from logic.factory import ShapeFactory


class Tool(ABC):
    def __init__(self, canvas_view):
        self.view = canvas_view
        self.scene = canvas_view.scene

    @abstractmethod
    def mouse_press(self, event): pass

    @abstractmethod
    def mouse_move(self, event): pass

    @abstractmethod
    def mouse_release(self, event): pass


class CreationTool(Tool):
    def __init__(self, canvas_view, shape_type, undo_stack):
        super().__init__(canvas_view)
        self.shape_type = shape_type
        self.undo_stack = undo_stack
        self.start_point = None
        self.active_shape = None


    def mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = self.view.mapToScene(event.pos())

            self.active_shape = ShapeFactory.create_shape(
                self.shape_type,
                self.start_point,
                self.start_point,
                self.view.current_color
            )

            if self.active_shape:
                self.scene.addItem(self.active_shape)
                self.active_shape.setOpacity(0.6)

    def mouse_move(self, event):
        if self.active_shape and self.start_point:
            current_point = self.view.mapToScene(event.pos())

            self.active_shape.set_geometry(self.start_point, current_point)

    def mouse_release(self, event):
        if self.active_shape and event.button() == Qt.MouseButton.LeftButton:


            self.scene.removeItem(self.active_shape)

            end_point = self.view.mapToScene(event.pos())

            final_shape = ShapeFactory.create_shape(
                self.shape_type,
                self.start_point,
                end_point,
                self.view.current_color
            )

            if final_shape:
                final_shape.setOpacity(1.0)

                command = AddShapeCommand(self.scene, final_shape)
                self.undo_stack.push(command)

                print(f"Command '{command.text()}' pushed")

            self.active_shape = None
            self.start_point = None

class SelectionTool(Tool):
    def __init__(self, view, undo_stack):
        super().__init__(view)

        self.undo_stack = undo_stack
        self.start_positions = {}

    def mouse_press(self, event):

        QGraphicsView.mousePressEvent(self.view, event)

        item = self.view.itemAt(event.pos())
        if item:
            self.view.setCursor(Qt.CursorShape.ClosedHandCursor)

        self.start_positions.clear()
        for item in self.scene.selectedItems():
            self.start_positions[item] = item.pos()

    def mouse_move(self, event):
        QGraphicsView.mouseMoveEvent(self.view, event)

        if not (event.buttons() & Qt.MouseButton.LeftButton):
            item = self.view.itemAt(event.pos())
            if item:
                self.view.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.view.setCursor(Qt.CursorShape.ArrowCursor)

    def mouse_release(self, event):
        QGraphicsView.mouseReleaseEvent(self.view, event)

        item = self.view.itemAt(event.pos())
        if item:
            self.view.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.view.setCursor(Qt.CursorShape.ArrowCursor)


        moved_items = []
        for item, old_pos in self.start_positions.items():
            if item.scene() != self.scene:
                continue

            new_pos = item.pos()
            if new_pos != old_pos:
                moved_items.append((item, old_pos, new_pos))

        if moved_items:
            self.undo_stack.beginMacro("Move Items")
            for item, old_pos, new_pos in moved_items:
                cmd = MoveCommand(item, old_pos, new_pos)
                self.undo_stack.push(cmd)
            self.undo_stack.endMacro()

            print(f"Recorded move of {len(moved_items)} items")

        self.start_positions.clear()