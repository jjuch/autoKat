import numpy as np
import matplotlib.pyplot as plt
import time

from autoKat.animals import Flock, Dog


class Game():
    def __init__(self):
        self.size = (100, 100)
        self.currentField = None
        self.flock = Flock(self.size)
        self.dog = Dog()
        self.simulate()

    def hasWon(self):
        # Check if the game is over
        return False


    def simulate(self):
        plt.ion()
        fig, ax = plt.subplots()
        point_dog, = ax.plot(*self.dog.current_location, marker='x')
        sheep_plots = []
        for sheep in self.flock.sheeps:
            sheep_data, = ax.plot(*sheep.current_location, marker='o')
            sheep_plots.append(sheep_data)
        

        while not self.hasWon():
            self.dog.update_dog_location(self.size)
            point_dog.set_data(*self.dog.current_location)

            for i, sheep in enumerate(self.flock.sheeps):
                sheep.calculate_new_coordinate(self.dog.current_location)
                print(sheep.current_location)
                sheep_plots[i].set_data(*sheep.current_location)
            fig.canvas.draw()
            fig.canvas.flush_events()
            time.sleep(1)
            
            

            

            

            
            



if __name__ == '__main__':
    game = Game()