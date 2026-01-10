from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItemGroup
from PySide6.QtGui import QPen, QColor, QPainterPath, QBrush
from PySide6.QtCore import Qt


class ShapeMixin:
    def to_dict(self) -> dict:
        raise NotImplementedError

    @property
    def type_name(self) -> str:
        raise NotImplementedError

    def set_active_color(self, color_name: str): raise NotImplementedError

    def set_pen_width(self, width: int): raise NotImplementedError


class Shape(QGraphicsPathItem, ShapeMixin):
    def __init__(self, color="black", stroke_width=2):
        super().__init__()
        pen = QPen(QColor(color))
        pen.setWidth(stroke_width)
        self.setPen(pen)

        self.setBrush(QBrush(QColor(255, 255, 255, 50)))
        self.setFlags(
            QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsPathItem.GraphicsItemFlag.ItemIsMovable
        )
        self.stroke_width = stroke_width

    def set_active_color(self, color_name: str):
        pen = QPen(QColor(color_name))
        pen.setWidth(self.stroke_width)
        self.setPen(pen)

    def set_pen_width(self, width: int):
        self.stroke_width = width
        pen = self.pen()
        pen.setWidth(width)
        self.setPen(pen)

    def to_dict(self) -> dict: raise NotImplementedError

    @property
    def type_name(self) -> str: raise NotImplementedError

    def set_geometry(self, s, e): raise NotImplementedError


class Group(QGraphicsItemGroup, ShapeMixin):
    def __init__(self):
        super().__init__()
        self.setFlags(
            QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable
        )
        self.setHandlesChildEvents(True)

    @property
    def type_name(self) -> str:
        return "group"

    def set_geometry(self, start, end):
        pass

    def set_active_color(self, color_name: str):
        for child in self.childItems():
            if isinstance(child, ShapeMixin):
                child.set_active_color(color_name)

    def to_dict(self) -> dict:
        children_data = []
        for child in self.childItems():
            if isinstance(child, ShapeMixin):
                children_data.append(child.to_dict())

        return {
            "type": self.type_name,
            "props": {
                "x": self.x(),
                "y": self.y(),
                "children": children_data
            }
        }

    def set_pen_width(self, width: int):
        for child in self.childItems():
            if isinstance(child, ShapeMixin):
                child.set_pen_width(width)


class Rectangle(Shape):
    def __init__(self, x=0, y=0, w=0, h=0, color="black"):
        super().__init__(color)
        self.update_data(x, y, w, h)

    @property
    def type_name(self) -> str:
        return "rect"

    def update_data(self, x, y, w, h):
        self.w, self.h = w, h

        path = QPainterPath()
        path.addRect(0, 0, self.w, self.h)
        self.setPath(path)

        self.setPos(x, y)

    def set_geometry(self, start_point, end_point):
        x1, y1 = start_point.x(), start_point.y()
        x2, y2 = end_point.x(), end_point.y()
        self.update_data(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))

    def to_dict(self):
        return {
            "type": "rect",
            "pos": [self.x(), self.y()],
            "props": {
                "x": self.x(),
                "y": self.y(),
                "w": self.w,
                "h": self.h,
                "color": self.pen().color().name(),
                "width": self.pen().width()
            }
        }


class Ellipse(Shape):
    def __init__(self, x=0, y=0, w=0, h=0, color="black"):
        super().__init__(color)
        self.update_data(x, y, w, h)

    def update_data(self, x, y, w, h):
        self.w, self.h = w, h

        path = QPainterPath()
        path.addEllipse(0, 0, self.w, self.h)
        self.setPath(path)

        self.setPos(x, y)

    def set_geometry(self, start_point, end_point):
        x1, y1 = start_point.x(), start_point.y()
        x2, y2 = end_point.x(), end_point.y()
        self.update_data(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))

    def to_dict(self):
        return {
            "type": "ellipse",
            "pos": [self.x(), self.y()],
            "props": {
                "x": self.x(), "y": self.y(),
                "w": self.w, "h": self.h,
                "color": self.pen().color().name(),
                "width": self.pen().width()
            }
        }

    @property
    def type_name(self) -> str: return "ellipse"


class Line(Shape):
    def __init__(self, x1=0, y1=0, x2=0, y2=0, color="black"):
        super().__init__(color)
        self.update_data(x1, y1, x2, y2)

    def update_data(self, x1, y1, x2, y2):
        local_x2 = x2 - x1
        local_y2 = y2 - y1

        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(local_x2, local_y2)
        self.setPath(path)

        self.setPos(x1, y1)

        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    def set_geometry(self, start_point, end_point):
        self.update_data(start_point.x(), start_point.y(), end_point.x(), end_point.y())

    def to_dict(self):
        return {
            "type": "line",
            "pos": [self.x(), self.y()],
            "props": {
                "x1": self.x1, "y1": self.y1,
                "x2": self.x2, "y2": self.y2,
                "color": self.pen().color().name(),
                "width": self.pen().width()
            }
        }

    @property
    def type_name(self) -> str: return "line"
