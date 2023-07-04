from game_data.game_utils.game_generator import *
from game_data.game_utils.plans import *


class GameGraph:
    def __init__(self, name='game', load_game=None):
        self.name = name

        self.states = None
        self.players = None
        self.action_map = dict()
        self.neighbours_map = dict()
        self.payoffs = dict()
        self.alpha = dict()
        self.plans = dict()

        if load_game is not None:
            self.load_game(load_game)
        else:
            self.generate_game()

    def load_game(self, filepath):
        # Implement the logic to load a game from a given filepath here
        pass

    def generate_game(self, num_players=3, num_states=4, cycle_length=3):
        self.states, self.players = create_states(num_players, num_states)
        self.action_map = create_edges(self.states, cycle_length)

        for state in self.states:
            self.neighbours_map[state] = self.action_map[state][1:]
            self.alpha[state] = state.payoffs[state.player]

        self.plans = create_plans(self.states, self.neighbours_map)

    def game1(self):
        self.states, self.action_map = example_game_1()

        for state in self.states:
            self.neighbours_map[state] = self.action_map[state][1:]
            self.alpha[state] = state.payoffs[state.player]

        self.plans = create_plans(self.states, self.neighbours_map)
