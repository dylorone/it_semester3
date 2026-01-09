from PySide6.QtGui import QUndoCommand


class AddShapeCommand(QUndoCommand):
    def __init__(self, scene, item):
        """
        :param scene: Сцена, куда добавляем
        :param item: Сама фигура (наследник QGraphicsItem)
        """
        super().__init__()
        self.scene = scene
        self.item = item

        name = getattr(item, "type_name", "Shape")
        self.setText(f"Add {name}")

    def redo(self):
        if self.item.scene() != self.scene:
            self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)

class MoveCommand(QUndoCommand):
    def __init__(self, item, old_pos, new_pos):
        super().__init__()
        self.item = item
        self.old_pos = old_pos
        self.new_pos = new_pos
        self.setText(f"Move {getattr(item, 'type_name', 'Item')}")

    def undo(self):
        self.item.setPos(self.old_pos)

    def redo(self):
        self.item.setPos(self.new_pos)


class DeleteCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item
        self.setText(f"Delete {getattr(item, 'type_name', 'Item')}")

    def redo(self):
        self.scene.removeItem(self.item)

    def undo(self):
        self.scene.addItem(self.item)