import math

class Shape:
    def get_perimeter(self):
        raise NotImplementedError

    def get_area(self):
        raise NotImplementedError

    @property
    def perimeter(self):
        return self.get_perimeter()

    @property
    def area(self):
        return self.get_area()

class Parallelogram(Shape):
    def __init__(self, a, b, alpha):
        self.a = a
        self.b = b
        self.alpha = alpha

        if not (0 < self.alpha < math.pi):
            raise ValueError("Invalid angle")

    def get_perimeter(self):
        return 2 * (self.a + self.b)

    def get_area(self):
        return self.a * self.b * math.sin(self.alpha)

class Rectangle(Parallelogram):
    def __init__(self, a, b):
        super().__init__(a, b, math.pi/2)

class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def get_perimeter(self):
        return 2*math.pi*self.radius

    def get_area(self):
        return math.pi * self.radius**2

class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

        if not (self.a < self.b + self.c or self.b < self.a + self.c or self.c < self.a + self.c):
            raise ValueError("Invalid triangle")

    def get_perimeter(self):
        return self.a + self.b + self.c

    def get_area(self):
        p = self.get_perimeter() / 2
        return math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))


shapes = [Triangle(2, 2, 2), Circle(4), Parallelogram(2, 1, math.pi/4)]
for shape in shapes:
    print(f"{type(shape).__name__}: area={shape.area:.1f}; perimeter={shape.perimeter:.1f}")
