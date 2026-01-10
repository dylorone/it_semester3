from logic.shapes import Rectangle, Ellipse, Line, Group


class ShapeFactory:
    @staticmethod
    def create_shape(shape_type: str, start_point, end_point, color="white"):
        """
        shape_type: строка ('rect', 'line', 'ellipse')
        start_point, end_point: объекты QPointF (координаты сцены)
        """
        x1 = start_point.x()
        y1 = start_point.y()
        x2 = end_point.x()
        y2 = end_point.y()

        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)

        if shape_type == "rect":
            return Rectangle(x, y, w, h, color)

        elif shape_type == "ellipse":
            return Ellipse(x, y, w, h, color)

        elif shape_type == "line":
            return Line(x1, y1, x2, y2, color)

        else:
            raise ValueError("Unknown shape type")

    @staticmethod
    def from_dict(data: dict):
        """
        Восстанавливает объект (или дерево объектов) из словаря.
        """
        shape_type = data.get("type")

        if shape_type == "group":
            return ShapeFactory._create_group(data)
        elif shape_type in ["rect", "line", "ellipse"]:
            return ShapeFactory._create_primitive(data)
        else:
            print(f"Unknown type: {shape_type}")
            return None

    @staticmethod
    def _create_primitive(data: dict):
        props = data.get("props", {})
        shape_type = data.get("type")

        color = props.get("color", "#000000")
        stroke_width = props.get("width", 2)

        obj = None

        if shape_type == "rect":
            obj = Rectangle(props['x'], props['y'], props['w'], props['h'], color)

        elif shape_type == "line":
            obj = Line(props['x1'], props['y1'], props['x2'], props['y2'], color)

        elif shape_type == "ellipse":
            obj = Ellipse(props['x'], props['y'], props['w'], props['h'], color)

        if obj:
            if hasattr(obj, 'set_pen_width'):
                obj.set_pen_width(stroke_width)

            pos = data.get("pos", [0, 0])
            obj.setPos(pos[0], pos[1])

        return obj

    @staticmethod
    def _create_group(data: dict):
        group = Group()

        pos = data.get("pos", [0, 0])
        group.setPos(pos[0], pos[1])

        children_data = data.get("children", [])
        for child_dict in children_data:
            child_item = ShapeFactory.from_dict(child_dict)

            if child_item:
                saved_pos = child_item.pos()
                child_item.setPos(0, 0)

                group.addToGroup(child_item)

                child_item.setPos(saved_pos)

        return group
