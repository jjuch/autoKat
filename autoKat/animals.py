import random
import numpy as np

class Flock():
    def __init__(self, size_field):
        self.max_flock_size = 5
        self.sheeps = []
        self.init_flock(size_field)

    def init_flock(self, size_field):
        for _ in np.arange(self.max_flock_size):
            x_coord = random.uniform(0, size_field[0])
            y_coord = random.uniform(0, size_field[1])
            coords = (x_coord, y_coord)
            sheep = Sheep(coords)
            self.sheeps.append(sheep)


class Sheep():
    def __init__(self, init_location):
        self.current_location = init_location
        self.distance_from_dog = (0.0, 0.0)
        self.velocity_scaling = 10

    def calculate_new_coordinate(self, dog_location):
        distance_to_dog = self.current_location[0] - dog_location[0], self.current_location[1] - dog_location[1]

        new_location = (
            self.current_location[0] + self.velocity_scaling/distance_to_dog[0],
            self.current_location[1] + self.velocity_scaling/distance_to_dog[1]
        )
        self.current_location = new_location


class Dog():
    def __init__(self):
        self.current_location = (0.0, 0.0)

    def update_dog_location(self, field_size: tuple):
        x_coord = random.uniform(0, field_size[0])
        y_coord = random.uniform(0, field_size[1])
        self.current_location = (x_coord, y_coord)
