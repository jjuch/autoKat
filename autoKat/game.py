import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mppatch
import time

from autoKat.animals import Flock, Dog, Sheep


class Game():
    def __init__(self):
        self.size = (100, 100)
        self.currentField = None
        self.flock = Flock(self.size)
        self.dog = Dog()
        self.sheep_house = {
            'xy': (10, 20),
            'width': 5,
            'height': 10
        }
        self.refresh_rate = 0.1 # seconds
        self.add_sheep_time = 10 # seconds
        self.simulate()

    def hasWon(self):
        # Check if the game is over
        return len(self.flock.sheeps) == 0


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
        for sheep in self.flock.sheeps:
            sheep_data, = ax.plot(*sheep.current_location, marker='o')
            sheep_plots.append(sheep_data)
        
        
        tick = 0
        max_ticks = int(self.add_sheep_time / self.refresh_rate)

        while not self.hasWon() and plt.fignum_exists(fig.number):
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
            
            

            

            

            
            



if __name__ == '__main__':
    game = Game()