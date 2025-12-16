import tkinter as tk
from tkinter import ttk, colorchooser
from typing import List

from shapes import Rectangle, Oval, Line, Shape, Star

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Рисование фигур (OOP Pattern)")
        self.root.geometry("800x600")

        self.current_color = "black"
        self.current_width = 2
        self.shape_classes = {
            "Прямоугольник": Rectangle,
            "Овал": Oval,
            "Линия": Line,
            "Звезда": Star
        }
        self.selected_shape_name = "Прямоугольник"
        self.current_shape_object = None

        self.drawn_shapes: List[Shape] = []

        self._setup_ui()

    def _setup_ui(self):
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(control_frame, text="Выберите фигуру:").pack(anchor=tk.W, pady=5)
        self.shape_var = tk.StringVar(value="Прямоугольник")
        
        for shape_name in self.shape_classes:
            rb = ttk.Radiobutton(
                control_frame, 
                text=shape_name, 
                variable=self.shape_var, 
                value=shape_name,
                command=self._set_shape_type
            )
            rb.pack(anchor=tk.W)

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        self.color_btn = tk.Button(
            control_frame, 
            text="Цвет: ■", 
            fg=self.current_color,
            command=self._choose_color
        )
        self.color_btn.pack(fill='x', pady=5)

        ttk.Label(control_frame, text="Толщина линии:").pack(anchor=tk.W, pady=(10, 0))
        self.width_scale = tk.Scale(
            control_frame, 
            from_=1, to=20, 
            orient=tk.HORIZONTAL,
            command=self._set_width
        )
        self.width_scale.set(self.current_width)
        self.width_scale.pack(fill='x')

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        ttk.Button(control_frame, text="Очистить холст", command=self._clear_canvas).pack(fill='x')

        self.canvas = tk.Canvas(self.root, bg="white", cursor="cross")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.root.bind("<Control-z>", self._undo)

    def _set_shape_type(self):
        self.selected_shape_name = self.shape_var.get()

    def _choose_color(self):
        color = colorchooser.askcolor(color=self.current_color)[1]
        if color:
            self.current_color = color
            self.color_btn.config(text="Цвет: ■", fg=color)

    def _set_width(self, val):
        self.current_width = int(val)

    def _clear_canvas(self):
        self.canvas.delete("all")

    def _on_mouse_down(self, event):
        shape_class = self.shape_classes[self.selected_shape_name]
        
        self.current_shape_object = shape_class(
            self.canvas, 
            event.x, 
            event.y, 
            self.current_color, 
            self.current_width
        )

    def _on_mouse_drag(self, event):
        if self.current_shape_object:
            self.current_shape_object.draw(event.x, event.y)

    def _on_mouse_up(self, event):
        self.drawn_shapes.append(self.current_shape_object)
        self.current_shape_object = None
    
    def _undo(self, event):
        self.drawn_shapes[-1].remove()
        self.drawn_shapes.pop()

if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()