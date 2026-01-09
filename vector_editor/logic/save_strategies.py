from abc import ABC, abstractmethod
import json

from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtCore import QRectF

from logic.shapes import ShapeMixin


class SaveStrategy(ABC):
    @abstractmethod
    def save(self, filename: str, scene):
        """
        :param filename: Путь к файлу
        :param scene: QGraphicsScene
        """
        pass


class JsonSaveStrategy(SaveStrategy):
    def save(self, filename, scene):
        shapes_data = []

        items_in_order = scene.items()[::-1]

        for item in items_in_order:
            if isinstance(item, ShapeMixin) and item.parentItem() is None:
                shapes_data.append(item.to_dict())

        project_data = {
            "version": "1.0",
            "scene": {
                "width": scene.sceneRect().width(),
                "height": scene.sceneRect().height()
            },
            "shapes": shapes_data
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=4, ensure_ascii=False)


class ImageSaveStrategy(SaveStrategy):
    def __init__(self, fmt="PNG", bg_color="transparent"):
        self.fmt = fmt
        self.bg_color = bg_color

    def save(self, filename, scene):
        rect = scene.sceneRect()

        image = QImage(int(rect.width()), int(rect.height()), QImage.Format.Format_ARGB32)

        if self.bg_color == "transparent":
            image.fill(QColor(0, 0, 0, 0))
        else:
            image.fill(QColor(self.bg_color))

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        scene.render(painter, QRectF(image.rect()), rect)

        painter.end()

        if not image.save(filename, self.fmt):
            raise IOError(f"Не удалось сохранить изображение {filename}")