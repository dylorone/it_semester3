import math
from typing import Dict, List, Optional, Tuple, Set

from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
                               QGraphicsLineItem, QGraphicsSimpleTextItem)


class GraphEdge(QGraphicsLineItem):
    def __init__(self, node1, node2):
        super().__init__()
        self.node1 = node1
        self.node2 = node2
        self.setPen(QPen(Qt.black, 2))
        self.setZValue(0)  # Линии под кругами
        self.update_position()

    def update_position(self):
        line = self.line()
        p1 = self.node1.scenePos()
        p2 = self.node2.scenePos()
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())


class GraphNode(QGraphicsEllipseItem):
    # Радиус вершины
    RADIUS = 20

    def __init__(self, index: int, label_text: str, editor_ref):
        super().__init__(-self.RADIUS, -self.RADIUS, self.RADIUS * 2, self.RADIUS * 2)
        self.index = index
        self.editor = editor_ref

        # Настройка внешнего вида
        self.setBrush(QBrush(QColor("lightblue")))
        self.setPen(QPen(Qt.black, 1))
        self.setZValue(1)  # Круги над линиями

        # Флаги взаимодействия
        self.setFlags(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsScenePositionChanges |
                      QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)

        # Текст (номер)
        self.text_item = QGraphicsSimpleTextItem(label_text, self)
        font = QFont("Arial", 10, QFont.Bold)
        self.text_item.setFont(font)
        # Центрирование текста
        r = self.text_item.boundingRect()
        self.text_item.setPos(-r.width() / 2, -r.height() / 2)

        self.edges: List[GraphEdge] = []

    def add_edge(self, edge: GraphEdge):
        self.edges.append(edge)

    def remove_edge(self, edge: GraphEdge):
        if edge in self.edges:
            self.edges.remove(edge)

    def itemChange(self, change, value):
        # Если позиция изменилась, обновляем привязанные ребра
        if change == QGraphicsEllipseItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        # Передаем событие клика в редактор для логики соединения
        self.editor.on_node_clicked(self)
        super().mousePressEvent(event)

    def set_highlight(self, active: bool):
        if active:
            self.setBrush(QBrush(QColor("yellow")))
            self.setPen(QPen(QColor("red"), 2))
        else:
            self.setBrush(QBrush(QColor("lightblue")))
            self.setPen(QPen(Qt.black, 1))


# --- РЕДАКТОР ГРАФА (GRAPH EDITOR WIDGET) ---

class GraphEditorWidget(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_obj = QGraphicsScene(self)
        self.setScene(self.scene_obj)
        self.setRenderHint(QPainter.Antialiasing)

        # Данные графа
        self.nodes: List[GraphNode] = []
        self.edges_set: Set[Tuple[int, int]] = set()  # (min_id, max_id)
        self.edges_map: Dict[Tuple[int, int], GraphEdge] = {}

        self.selected_node: Optional[GraphNode] = None

    def reset_graph(self, n: int):
        self.scene_obj.clear()
        self.nodes = []
        self.edges_set = set()
        self.edges_map = {}
        self.selected_node = None

        width = self.width() if self.width() > 100 else 400
        height = self.height() if self.height() > 100 else 400
        cx, cy = 0, 0  # Центр сцены (0,0 в QGraphicsScene обычно центр)

        radius = min(width, height) / 2 - 40

        for i in range(n):
            angle = 2 * math.pi * i / n - math.pi / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            node = GraphNode(i, str(i + 1), self)
            node.setPos(x, y)
            self.scene_obj.addItem(node)
            self.nodes.append(node)

    def on_node_clicked(self, node: GraphNode):
        if self.selected_node is None:
            # Выбираем первую вершину
            self.selected_node = node
            node.set_highlight(True)
        elif self.selected_node == node:
            # Снимаем выделение
            self.selected_node.set_highlight(False)
            self.selected_node = None
        else:
            # Вторая вершина -> тоглим ребро
            u, v = self.selected_node.index, node.index
            self.toggle_edge(u, v)

            # Сброс выделения
            self.selected_node.set_highlight(False)
            self.selected_node = None

    def toggle_edge(self, u_idx: int, v_idx: int):
        u, v = sorted((u_idx, v_idx))
        key = (u, v)

        if key in self.edges_set:
            # Удалить ребро
            edge = self.edges_map[key]
            self.scene_obj.removeItem(edge)
            self.nodes[u].remove_edge(edge)
            self.nodes[v].remove_edge(edge)
            del self.edges_map[key]
            self.edges_set.remove(key)
        else:
            # Создать ребро
            node1 = self.nodes[u]
            node2 = self.nodes[v]
            edge = GraphEdge(node1, node2)
            self.scene_obj.addItem(edge)

            node1.add_edge(edge)
            node2.add_edge(edge)

            self.edges_map[key] = edge
            self.edges_set.add(key)

    def get_adjacency_matrix(self) -> List[List[int]]:
        n = len(self.nodes)
        matrix = [[0] * n for _ in range(n)]
        for (u, v) in self.edges_set:
            matrix[u][v] = 1
            matrix[v][u] = 1
        return matrix

