import math
import tkinter as tk
from typing import List, Optional, Dict, Tuple, Set


class GraphEditor(tk.Canvas):
    def __init__(self, master, width=400, height=400, **kwargs):
        super().__init__(master, width=width, height=height, bg="white", **kwargs)
        self.nodes: List[Dict] = []  # [{'id': int, 'x': float, 'y': float, 'label': str}, ...]
        self.edges: Set[Tuple[int, int]] = set()  # Set of tuples (u, v) where u < v
        self.node_radius = 15
        self.selected_node_idx: Optional[int] = None

        # Переменная для drag-n-drop
        self.drag_data = {"x": 0, "y": 0, "item": None, "idx": None}

        # Привязка событий
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)

    def reset_graph(self, n_vertices: int):
        """Создает n вершин, расположенных по кругу."""
        self.nodes = []
        self.edges = set()
        self.selected_node_idx = None
        self.delete("all")

        cx, cy = int(self["width"]) // 2, int(self["height"]) // 2
        radius = min(cx, cy) - 40

        for i in range(n_vertices):
            angle = 2 * math.pi * i / n_vertices - math.pi / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            self.nodes.append({
                "id": i,
                "x": x,
                "y": y,
                "label": str(i + 1)
            })

        self.redraw()

    def get_matrix(self) -> List[List[int]]:
        """Возвращает матрицу смежности текущего графа."""
        n = len(self.nodes)
        matrix = [[0] * n for _ in range(n)]
        for u, v in self.edges:
            matrix[u][v] = 1
            matrix[v][u] = 1
        return matrix

    def redraw(self):
        self.delete("all")

        # Инструкция
        self.create_text(10, 10, anchor="nw", text="ЛКМ: выделить/соединить\nДраг: двигать", fill="gray")

        # Рисуем ребра
        for u, v in self.edges:
            x1, y1 = self.nodes[u]["x"], self.nodes[u]["y"]
            x2, y2 = self.nodes[v]["x"], self.nodes[v]["y"]
            self.create_line(x1, y1, x2, y2, width=2, fill="black")

        # Рисуем вершины
        for i, node in enumerate(self.nodes):
            color = "lightblue"
            outline = "black"
            width = 1

            if i == self.selected_node_idx:
                color = "yellow"
                width = 2
                outline = "red"

            x, y = node["x"], node["y"]
            r = self.node_radius

            # Круг
            self.create_oval(x - r, y - r, x + r, y + r, fill=color, outline=outline, width=width, tags=f"node_{i}")
            # Текст
            self.create_text(x, y, text=node["label"], font=("Arial", 10, "bold"), tags=f"node_{i}")

    def get_node_at_pos(self, x, y):
        for i, node in enumerate(self.nodes):
            dist = math.hypot(node["x"] - x, node["y"] - y)
            if dist <= self.node_radius:
                return i
        return None

    def on_click(self, event):
        idx = self.get_node_at_pos(event.x, event.y)

        if idx is not None:
            # Нажали на вершину
            if self.selected_node_idx is None:
                # Ничего не выбрано -> выбираем текущую
                self.selected_node_idx = idx
                # Готовимся к перетаскиванию
                self.drag_data["idx"] = idx
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
            else:
                # Уже была выбрана вершина
                if self.selected_node_idx == idx:
                    # Нажали на ту же самую -> снимаем выделение (но оставляем drag)
                    self.selected_node_idx = None
                    self.drag_data["idx"] = idx
                    self.drag_data["x"] = event.x
                    self.drag_data["y"] = event.y
                else:
                    # Нажали на другую -> тоглим ребро
                    u, v = sorted((self.selected_node_idx, idx))
                    if (u, v) in self.edges:
                        self.edges.remove((u, v))
                    else:
                        self.edges.add((u, v))
                    self.selected_node_idx = None  # Сброс выделения после соединения
        else:
            # Клик в пустоту -> сброс
            self.selected_node_idx = None

        self.redraw()

    def on_drag(self, event):
        idx = self.drag_data["idx"]
        if idx is not None:
            # Обновляем координаты
            self.nodes[idx]["x"] = event.x
            self.nodes[idx]["y"] = event.y
            self.redraw()

    def on_release(self, event):
        self.drag_data["idx"] = None


# --- MAIN APP ---