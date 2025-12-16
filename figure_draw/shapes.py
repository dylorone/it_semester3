import tkinter as tk
import math

class Shape:
    def __init__(self, canvas: tk.Canvas, start_x, start_y, color, width):
        self.canvas = canvas
        self.start_x = start_x
        self.start_y = start_y
        self.color = color
        self.width = width
        self.item_id = None

    def update(self, current_x, current_y):
        if self.item_id is not None:
            self.canvas.coords(self.item_id, self.start_x, self.start_y, current_x, current_y)

    def remove(self):
        if self.item_id is not None:
            self.canvas.delete(self.item_id)

class Rectangle(Shape):
    def draw(self, current_x, current_y):
        if not self.item_id:
            self.item_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, current_x, current_y,
                outline=self.color, width=self.width
            )

        self.update(current_x, current_y)

class Oval(Shape):
    def draw(self, current_x, current_y):
        if not self.item_id:
            self.item_id = self.canvas.create_oval(
                self.start_x, self.start_y, current_x, current_y,
                outline=self.color, width=self.width
            )
        self.update(current_x, current_y)

class Line(Shape):
    def draw(self, current_x, current_y):
        if not self.item_id:
            self.item_id = self.canvas.create_line(
                self.start_x, self.start_y, current_x, current_y,
                fill=self.color, width=self.width
            )
        self.update(current_x, current_y)

class Star(Shape):
    def draw(self, current_x, current_y):
        center_x = (self.start_x + current_x) / 2
        center_y = (self.start_y + current_y) / 2
        
        rx = abs(current_x - self.start_x) / 2
        ry = abs(current_y - self.start_y) / 2
        
        points = []
        rays = 5
        inner_ratio = 0.4
        
        angle = -math.pi / 2
        step = math.pi / rays

        for i in range(rays * 2):
            current_rx = rx if i % 2 == 0 else rx * inner_ratio
            current_ry = ry if i % 2 == 0 else ry * inner_ratio
            
            x = center_x + math.cos(angle) * current_rx
            y = center_y + math.sin(angle) * current_ry
            
            points.append(x)
            points.append(y)
            angle += step

        if not self.item_id:
            self.item_id = self.canvas.create_polygon(
                points,
                outline=self.color, 
                width=self.width,
                fill="" 
            )
        else:
            self.canvas.coords(self.item_id, *points)
