from __future__ import annotations
import math
import random
from typing import Any, Iterator, Literal
import numpy as np

class Flock:
    def __init__(self, size_field):
        self.max_flock_size = 5
        self.sheeps = []
        self.init_flock(size_field)

    def init_flock(self, size_field):
        for i in range(self.max_flock_size):
            x_coord = random.uniform(0, size_field[0])
            y_coord = random.uniform(0, size_field[1])
            coords = (x_coord, y_coord)
            heading = random.uniform(0, 2 * math.pi)
            sheep = Sheep(id=i, init_location=coords, init_heading=heading)
            self.sheeps.append(sheep)

    def __iter__(self) -> Iterator[Sheep]:
        return iter(self.sheeps)


def calculate_heading(a: tuple[float, float], b: tuple[float, float], current_heading: float = 0) -> float:
    xa, ya = a
    xb, yb = b
    new_heading = math.atan2(yb - ya, xb - xa) if (yb - ya) or (xb - xa) else current_heading
    # make sure that switching from e.g 0.9*pi to -0.9*pi animates smoothly in CSS.
    # if the current heading is .9pi and the new heading is -.9pi, make the new heading 1.1pi instead
    if abs(heading_diff := (new_heading - current_heading)) > math.pi:
        heading_diff -= np.sign(heading_diff) * math.pi * 2
    return current_heading + heading_diff



class Sheep:
    state: Literal['in_play', 'in_house']

    def __init__(self, id: int, init_location: tuple[float, float], init_heading: float):
        self.id = id
        self.current_location = init_location
        self.velocity_scaling = 2000
        self.max_velocity = 200
        self.current_heading = init_heading
        self.state = 'in_play'

    def in_house_bool(self, sheep_house):
        x_range = (sheep_house['xy'][0], sheep_house['xy'][0] + sheep_house['width'])
        y_range = (sheep_house['xy'][1] , sheep_house['xy'][1] +  sheep_house['height'])
    
        if (x_range[0] < self.current_location[0] < x_range[1]) and (y_range[0] < self.current_location[1] < y_range[1]):
            return True
        else:
            return False

    def calculate_new_coordinate(self, dog_location, field_size):
        if self.state == 'in_house':
            return
        def check_boundaries(val, idx):
            if val > field_size[idx]:
                val = field_size[idx]
            elif val < 0:
                val = 0
            return val
        x, y = self.current_location
        distance_to_dog = self.current_location[0] - dog_location[0], self.current_location[1] - dog_location[1]

        new_x = self.current_location[0] + np.sign(self.velocity_scaling/distance_to_dog[0]) * min(self.max_velocity, abs(self.velocity_scaling/distance_to_dog[0]))
        new_x += (2*random.random() - 1) * self.velocity_scaling/50
        new_x = check_boundaries(new_x, 0)

        new_y = self.current_location[1] + np.sign(self.velocity_scaling/distance_to_dog[1]) * min(self.max_velocity, abs(self.velocity_scaling/distance_to_dog[1]))
        new_y += (2*random.random() - 1) * self.velocity_scaling/50
        new_y = check_boundaries(new_y, 1)

        new_location = (new_x, new_y)
        distance = math.sqrt((new_x - x) ** 2 + (new_y - y) ** 2)
        new_heading = calculate_heading((x, y), (new_x, new_y), self.current_heading)
        # print("sheep: ", new_location)
        if distance > 10:
            self.current_location = new_location
            self.current_heading = new_heading

    def to_dict(self) -> dict[str, Any]:
        x, y = self.current_location
        return {
            "id": self.id,
            "type": "sheep",
            "x": x,
            "y": y,
            "heading": self.current_heading,
            "state": self.state,
        }


class Dog:
    def __init__(self):
        self.current_location = (0.0, 0.0)
        self.last_pointer_location = (0.0, 0.0)
        self.approach_rate = 2
        self.current_heading = 0
        self.max_speed = 10

    def update_dog_location(self, pointer_location: tuple[float, float]):
        x, y = self.current_location
        px, py = pointer_location
        dx = px - x
        dy = py - y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance < .01:
            return
        new_x = x + dx * min(self.max_speed, distance) / distance
        new_y = y + dy * min(self.max_speed, distance) / distance
        self.current_location = new_x, new_y
        self.current_heading = calculate_heading((x, y), (new_x, new_y), self.current_heading)

    def mouse_move(self, *args):
        event = args[0]
        x, y = event.xdata, event.ydata
        print("Mouse: ", x, ", ", y)
        if x is not None and y is not None:
            self.last_pointer_location = (x, y)

    def to_dict(self) -> dict[str, Any]:
        x, y = self.current_location
        return {
            "id": 1_000_000,
            "type": "dog",
            "x": x,
            "y": y,
            "heading": self.current_heading
        }
    
