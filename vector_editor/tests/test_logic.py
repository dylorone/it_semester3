import pytest
from PySide6.QtCore import QPointF
from logic.factory import ShapeFactory
from logic.shapes import Rectangle, Line

def test_rectangle_creation_normalization():
    start = QPointF(100, 100)
    end = QPointF(10, 10)

    shape = ShapeFactory.create_shape("rect", start, end, "#FF0000")

    assert isinstance(shape, Rectangle)

    assert shape.x() == 10
    assert shape.y() == 10
    assert shape.w == 90
    assert shape.h == 90

    # Проверка цвета
    assert shape.pen().color().name().upper() == "#FF0000"

def test_factory_unknown_shape():
    start = QPointF(0, 0)
    end = QPointF(10, 10)

    with pytest.raises(ValueError):
        ShapeFactory.create_shape("unknown_type", start, end, "black")

def test_serialization_cycle():
    line = Line(0, 0, 100, 200, "#00FF00")

    data = line.to_dict()

    assert data["type"] == "line"
    assert data["props"]["x2"] == 100

    new_line = ShapeFactory.from_dict(data)

    assert isinstance(new_line, Line)
    assert new_line.x1 == line.x1
    assert new_line.y2 == line.y2
    assert new_line.pen().color().name() == line.pen().color().name()
