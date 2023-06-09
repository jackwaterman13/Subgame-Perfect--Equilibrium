import Equilibrium
from gui.Test_GUI import *
import timeit


class Game_Solver:
    def __init__(self):
        self.name = 'new_test'
        self.game = Equilibrium.Game(self.name)

        self.iteration()

        # execution_time = timeit.timeit(self.iteration, number=11500)
        # print("Execution time:", execution_time, "seconds")

    def iteration(self):
        converged = False
        itr = 0
        while not converged:
            print(f'Iteration{itr}')
            self.game.get_alpha_dict()
            self.game.get_viable_plans()
            self.game.get_alpha_plateaus()
            self.game.get_U_compatible()
            self.game.get_viable_compatible()
            self.game.get_admissible()
            self.game.get_beta()
            self.game.get_gamma()
            converged = self.game.update_delta()
            itr += 1

    def gui(self):
        GUI(self.game)


solver = Game_Solver()
