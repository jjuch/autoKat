from __future__ import annotations
import datetime
import math
import random
from typing import Any, Iterator, Literal
import numpy as np

from autokat.track import SCREEN_HEIGHT, SCREEN_WIDTH


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


def calculate_heading(
    a: tuple[float, float], b: tuple[float, float], current_heading: float = 0
) -> float:
    xa, ya = a
    xb, yb = b
    new_heading = (
        math.atan2(yb - ya, xb - xa) if (yb - ya) or (xb - xa) else current_heading
    )
    # make sure that switching from e.g 0.9*pi to -0.9*pi animates smoothly in CSS.
    # if the current heading is .9pi and the new heading is -.9pi, make the new heading 1.1pi instead
    if abs(heading_diff := (new_heading - current_heading)) > math.pi:
        heading_diff -= np.sign(heading_diff) * math.pi * 2
    return current_heading + heading_diff

def d(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

class Sheep:
    state: Literal["idle", "fleeing", "flushing", "caught"]
    scale: float
    random_target: tuple[float, float]

    def __init__(
        self, id: int, init_location: tuple[float, float], init_heading: float
    ):
        self.id = id
        self.current_location = init_location
        self.max_velocity = 120
        self.current_heading = init_heading
        self.state = "idle"
        self.random_target = init_location
        self.scale = 1

    def in_house_bool(self, sheep_house):
        x_range = (sheep_house["xy"][0], sheep_house["xy"][0] + sheep_house["width"])
        y_range = (sheep_house["xy"][1], sheep_house["xy"][1] + sheep_house["height"])

        if (x_range[0] < self.current_location[0] < x_range[1]) and (
            y_range[0] < self.current_location[1] < y_range[1]
        ):
            return True
        else:
            return False

    def calculate_new_coordinate(
        self,
        dog_location: tuple[float, float],
        field_size: tuple[float, float],
        dt: datetime.timedelta,
        total_dt: datetime.timedelta,
        maelstrom_center: tuple[float, float],
        maelstrom_radius: float,
    ) -> tuple[float, float]:
        if self.state == "caught":
            return
        new_x, new_y = x, y = self.current_location
        dog_x, dog_y = dog_location
        diff = diff_x, diff_y = x - dog_x, y - dog_y
        distance_to_dog = math.sqrt(diff_x**2 + diff_y**2)
        old_state = self.state

        def move_to(target: tuple[float, float]) -> tuple[float, float]:
            tx, ty = target
            d = math.sqrt((tx - x) ** 2 + (ty - y) ** 2)
            _x = np.clip(
                x + (tx - x) / d * self.max_velocity * dt.total_seconds(),
                0,
                field_size[0] - 1,
            )
            _y = np.clip(
                y + (ty - y) / d * self.max_velocity * dt.total_seconds(),
                0,
                field_size[1] - 1,
            )
            return _x, _y

        if self.state == "fleeing" and distance_to_dog > 200:
            self.state = "idle"

        if self.state == "fleeing" or distance_to_dog <= 180:
            self.state = "fleeing"
            new_x = np.clip(
                new_x
                + diff_x / distance_to_dog * self.max_velocity * dt.total_seconds(),
                0,
                field_size[0] - 1,
            )
            new_y = np.clip(
                new_y
                + diff_y / distance_to_dog * self.max_velocity * dt.total_seconds(),
                0,
                field_size[1] - 1,
            )

        if self.state == "idle":
            random_x, random_y = self.random_target
            if old_state != "idle" or (math.sqrt((random_x - new_x) ** 2 + (random_y - new_y) ** 2)) < 10:
                for _ in range(100):
                    random_distance = 180
                    random_angle = math.pi * random.uniform(0, 2)
                    self.random_target = (
                        np.clip(new_x + math.cos(random_angle) * random_distance, 0, field_size[0] - 1),
                        np.clip(new_y + math.sin(random_angle) * random_distance, 0, field_size[1] - 1),
                    )
                    # check if this takes us into the maelstrom
                    maelstrom = False
                    for step in range(1001):
                        t = step / 1000
                        x_step = new_x  * (1 - t) + self.random_target[0] * t
                        y_step = new_y  * (1 - t) + self.random_target[1] * t
                        step = x_step, y_step
                        if d(maelstrom_center, step) <= maelstrom_radius:
                            maelstrom = True
                            break
                    if not maelstrom:
                        break
                        
            else:
                new_x, new_y = move_to(self.random_target)

        if self.state == "caught":
            return
        
        if self.state == "flushing":
            suck_duration = datetime.timedelta(seconds=5)
            suck_velocity = maelstrom_radius / suck_duration.total_seconds()
            current_distance = d(maelstrom_center, self.current_location)
            current_angle = math.atan2(y - maelstrom_center[1], x - maelstrom_center[0])
            new_angle = current_angle - 2 * math.pi * 1 * dt.total_seconds()
            while new_angle < 0:
                new_angle += math.pi * 2
            new_distance = max(1, current_distance - suck_velocity * dt.total_seconds())
            self.scale = new_distance / maelstrom_radius;
            new_x = maelstrom_center[0] + math.cos(new_angle) * new_distance
            new_y = maelstrom_center[1] + math.sin(new_angle) * new_distance
        
        if d((new_x, new_y), maelstrom_center) <= 2:
            self.state = 'caught'
            return

        new_location = (new_x, new_y)
        new_heading = calculate_heading((x, y), (new_x, new_y), self.current_heading)
        self.current_location = new_location
        self.current_heading = new_heading

        if d(self.current_location, maelstrom_center) <= maelstrom_radius:
            self.state = 'flushing'


    def to_dict(self) -> dict[str, Any]:
        x, y = self.current_location
        return {
            "id": self.id,
            "type": "sheep",
            "x": x,
            "y": y,
            "heading": self.current_heading,
            "state": self.state,
            "scale": self.scale,
        }


class Dog:
    def __init__(self, initial_location: tuple[float, float]):
        self.current_location = initial_location
        self.approach_rate = 2
        self.current_heading = 0
        self.max_speed = 30

    def update_dog_location(self, pointer_location: tuple[float, float]):
        x, y = self.current_location
        px, py = pointer_location
        dx = px - x
        dy = py - y
        distance = math.sqrt(dx**2 + dy**2)
        if distance < 0.01:
            return
        new_x = x + dx * min(self.max_speed, distance) / distance
        new_y = y + dy * min(self.max_speed, distance) / distance
        self.current_location = new_x, new_y
        self.current_heading = calculate_heading(
            (x, y), (new_x, new_y), self.current_heading
        )

    def to_dict(self) -> dict[str, Any]:
        x, y = self.current_location
        return {
            "id": 1_000_000,
            "type": "dog",
            "x": x,
            "y": y,
            "heading": self.current_heading,
        }
