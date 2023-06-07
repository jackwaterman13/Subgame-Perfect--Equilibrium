import Equilibrium


class Game_Solver:
    def __init__(self):
        self.name = 'new_test'
        self.game = Equilibrium.Game(self.name)
        self.iteration()

    def iteration(self):
        self.game.get_viable_plans()
        self.game.get_alpha_plateaus()
        self.game.get_U_compatible()
        self.game.get_viable_compatible()
        self.game.get_admissible()




solver = Game_Solver()
