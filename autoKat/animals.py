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
        self.velocity_scaling = 50
        self.max_velocity = 5

    def in_house_bool(self, sheep_house):
        x_range = (sheep_house['xy'][0], sheep_house['xy'][0] + sheep_house['width'])
        y_range = (sheep_house['xy'][1] , sheep_house['xy'][1] +  sheep_house['height'])
    
        if (x_range[0] < self.current_location[0] < x_range[1]) and (y_range[0] < self.current_location[1] < y_range[1]):
            return True
        else:
            return False

    def calculate_new_coordinate(self, dog_location, field_size):
        def check_boundaries(val, idx):
            if val > field_size[idx]:
                val = field_size[idx]
            elif val < 0:
                val = 0
            return val
        
        distance_to_dog = self.current_location[0] - dog_location[0], self.current_location[1] - dog_location[1]

        new_x = self.current_location[0] + np.sign(self.velocity_scaling/distance_to_dog[0]) * min(self.max_velocity, abs(self.velocity_scaling/distance_to_dog[0]))
        new_x += (2*random.random() - 1) * self.velocity_scaling/50
        new_x = check_boundaries(new_x, 0)

        new_y = self.current_location[1] + np.sign(self.velocity_scaling/distance_to_dog[1]) * min(self.max_velocity, abs(self.velocity_scaling/distance_to_dog[1]))
        new_y += (2*random.random() - 1) * self.velocity_scaling/50
        new_y = check_boundaries(new_y, 1)

        new_location = (new_x, new_y)
    
        print("sheep: ", new_location)
        
        self.current_location = new_location


class Dog():
    def __init__(self):
        self.current_location = (0.0, 0.0)
        self.last_pointer_location = (0.0, 0.0)
        self.approach_rate = 2

    def update_dog_location(self):
        error = (
            self.last_pointer_location[0] - self.current_location[0],
            self.last_pointer_location[1] - self.current_location[1]
        )
        gain_error = self.approach_rate * error
        self.current_location = (
            gain_error[0] + self.current_location[0],
            gain_error[1] + self.current_location[1]
        )

    def mouse_move(self, *args):
        event = args[0]
        x, y = event.xdata, event.ydata
        print("Mouse: ", x, ", ", y)
        if x is not None and y is not None:
            self.last_pointer_location = (x, y)


    
