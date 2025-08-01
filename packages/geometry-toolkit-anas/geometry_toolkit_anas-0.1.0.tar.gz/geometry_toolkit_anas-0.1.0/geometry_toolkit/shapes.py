# geometry_toolkit/shapes.py
import math
def rectangle_area(length, width):
    return length * width
def rectangle_perimeter(length, width):
    return 2 * (length + width)
def square_area(side):
    return side * side
def square_perimeter(side):
    return 4 * side
def circle_area(radius):
    return math.pi * radius * radius
def circle_circumference(radius):
    return 2 * math.pi * radius