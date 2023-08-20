from game_data.game_utils.game_generator import *
from game_data.game_utils.plans import *


class GameGraph:
    def __init__(self, name='game', load_game=None):
        self.name = name

        self.states = None
        self.action_map = dict()
        self.neighbours_map = dict()
        self.alpha = dict()
        self.plans = dict()

        if load_game is not None:
            self.load_game(load_game)
        else:
            self.figure_4_game()

    def load_game(self, filepath):
        # Implement the logic to load a game from a given filepath here
        pass

    def generate_game(self, num_players=2, num_states=3, cycle_length=2):
        self.states = create_states(num_players, num_states)
        self.action_map = create_edges(self.states, cycle_length)

        self.init_game_graph()

    def game1(self):
        self.states, self.action_map = example_game_1()
        self.init_game_graph()

    def figure_4_game(self):
        self.states, self.action_map = fig_4_game()
        self.init_game_graph()

    def init_game_graph(self):
        for state in self.states:
            self.neighbours_map[state] = self.action_map[state][1:]
            self.alpha[state] = state.payoffs[state.player]

        self.plans = create_plans(self.states, self.neighbours_map)

    def update_payoffs(self, payoffs):
        payoffs = [list(payoffs[i:i+3]) for i in range(0, len(payoffs), 3)]

        for state_payoff, state in zip(payoffs, self.states):
            state.update_state_payoffs(state_payoff)
            self.alpha[state] = state.payoffs[state.player]
