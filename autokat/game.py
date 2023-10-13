import dataclasses
import datetime
from typing import Literal, Protocol
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mppatch
import time

from autokat.animals import Flock, Dog, Sheep


class Game:
    state: Literal['intro', 'playing', 'victory']
    victory_time: datetime.timedelta | None
    def __init__(self, size=(1024, 768)):
        self.size = size
        self.flock = Flock(self.size)
        self.dog = Dog()
        self.sheep_house = {
            'xy': (10, 20),
            'width': 5,
            'height': 10
        }
        self.refresh_rate = 0.1 # seconds
        self.add_sheep_time = 10 # seconds
        self.current_tick = 0
        self.total_dt = datetime.timedelta(seconds=0)
        self.last_pointer_position = (0, 0)
        self.state = 'intro'
        self.intro_box = (
            (self.width - 200 - 50, self.height / 2 - 100),
            (self.width - 50, self.height / 2 + 100),
        )
        self.maelstrom_center = 200, 500
        self.maelstrom_radius = 100
        self.victory_time = None

    @property
    def width(self) -> float:
        return self.size[0]
    
    @property
    def height(self) -> float:
        return self.size[1]


    def tick(self, pointer_location: tuple[float, float], total_dt: datetime.timedelta, dt: datetime.timedelta):
        self.last_pointer_position = pointer_location
        self.total_dt = total_dt
        self.dog.update_dog_location(pointer_location)
        if self.state == 'intro':
            dog_x, dog_y = self.dog.current_location
            ((l, t), (r, b)) = self.intro_box
            if l <= dog_x <= r and t <= dog_y <= b:
                self.state = 'playing'
        if self.state == 'playing':
            for sheep in self.flock:
                sheep.calculate_new_coordinate(
                    self.dog.current_location,
                    self.size,
                    dt=dt,
                    total_dt=total_dt,
                    maelstrom_center=self.maelstrom_center,
                    maelstrom_radius=self.maelstrom_radius,
                )
                if all(s.state == 'caught' for s in self.flock):
                    self.victory_time = total_dt
                    self.state = 'victory'

        self.current_tick += 1


    def simulate(self):
        # create playfield
        plt.ion()
        fig, ax = plt.subplots()
        plt.xlim([-10, self.size[0] + 10])
        plt.ylim([-10, self.size[1] + 10])
        plt.connect('motion_notify_event', self.dog.mouse_move)
        sheep_house_patch = mppatch.Rectangle(self.sheep_house['xy'], self.sheep_house['width'], self.sheep_house['height'])
        ax.add_patch(sheep_house_patch)


        point_dog, = ax.plot(*self.dog.current_location, marker='x')
        sheep_plots = []
        for sheep in self.flock:
            sheep_data, = ax.plot(*sheep.current_location, marker='o')
            sheep_plots.append(sheep_data)
        
        
        tick = 0
        max_ticks = int(self.add_sheep_time / self.refresh_rate)

        while not self.has_won() and plt.fignum_exists(fig.number):
            # update dog location
            self.dog.update_dog_location()
            point_dog.set_data(*self.dog.current_location)

            # update sheep's position
            for i, sheep in enumerate(self.flock.sheeps):
                sheep.calculate_new_coordinate(self.dog.current_location, self.size)
                sheep_plots[i].set_data(*sheep.current_location)
                if sheep.in_house_bool(self.sheep_house):
                    self.flock.sheeps.remove(sheep)
                    sheep_plots.remove(sheep_plots[i])
            if tick == max_ticks:
                if len(self.flock.sheeps) < self.flock.max_flock_size:
                    self.flock.sheeps.append(Sheep((0,0)))
                    sheep_data, = ax.plot(*self.flock.sheeps[-1].current_location, marker='o')
                    sheep_plots.append(sheep_data)
                tick = 0
            tick += 1
            # print(tick, "/", max_ticks)
            fig.canvas.draw()
            fig.canvas.flush_events()
            time.sleep(self.refresh_rate)
            
    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "dog": self.dog.to_dict(),
            "sheep": [sheep.to_dict() for sheep in self.flock],
            "tick": self.current_tick,
            "total_dt": self.total_dt.total_seconds(),
            "pointer_position": self.last_pointer_position,
            "intro_box": self.intro_box,
            "maelstrom": {
                "center": self.maelstrom_center,
                "radius": self.maelstrom_radius,
            }
        }


if __name__ == '__main__':
    game = Game()
    game.simulate()