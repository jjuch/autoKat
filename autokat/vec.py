from __future__ import annotations
import math
import random
from typing import NamedTuple


class Vec(NamedTuple):
    x: float
    y: float

    def __add__(self, other):
        match other:
            case Vec(x, y):
                return Vec(self.x + x, self.y + y)
            case float(s) | int(s):
                return Vec(self.x + s, self.y + s)
            case _:
                raise ValueError(f"Can't add {other} to Vec")
    
    def __sub__(self, other):
        return Vec(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other):
        match other:
            case float(f) | int(f):
                return Vec(self.x * f, self.y * f)
            case Vec(x, y):
                return Vec(self.x * x, self.y * y)
            case _:
                raise ValueError(f"Can't multiply Vec by {other}")
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def __truediv__(self, other):
        return Vec(self.x / other, self.y / other)
    
    def __div__(self, other):
        return Vec(self.x / other, self.y / other)
    
    @property
    def magnitude(self):
        return self.dot(self) ** .5
    
    def norm(self) -> Vec:
        return self / self.magnitude

    def truncate(self, max_magnitude) -> Vec:
        if self.magnitude > max_magnitude:
            return self.norm() * max_magnitude
        return self
    
    def reflect(self, normal: Vec) -> Vec:
        return self - normal * 2 * self.dot(normal)

    def rotate(self, rads: float) -> Vec:
        return Vec(
            self.x * math.cos(rads) - self.y * math.sin(rads),
            self.x * math.sin(rads) + self.y * math.cos(rads),
        )
    
    def distance_to(self, other: Vec) -> float:
        return (other - self).magnitude
    
    @classmethod
    def normalized_random(cls) -> Vec:
        return cls(1 - 2 * random.random(), 1 - 2 * random.random()).norm()