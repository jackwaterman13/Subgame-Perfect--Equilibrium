from .Plan_Finder import *


class State:
    def __init__(self, player: int, suffix='', payoffs=None):
        """
        Parameters:
        player (int): player number [0,inf)
        
        """
        self.player = player
        self.suffix = suffix
        self.neighbours = []

        self.terminal = True
        self.terminal_state = None

        self.payoffs = payoffs
        self.alpha = float('-inf')

        self.sid = f'{self.player}{suffix}'
        self.id = f'{self.player + 1}{suffix}*'

        self.plans = None
        self.viable = None

        if payoffs is None:
            self.terminal = False
            self.id = f'{self.player + 1}{suffix}'

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, State):
            return self.id == other.id
        return False

    def __lt__(self, other):
        if self.player != other.player:
            return self.player < other.player

        if self.suffix == other.suffix:
            return False

        if self.suffix == '' and other.suffix != '':
            return True

        if self.suffix != '' and other.suffix == '':
            return False

        return self.suffix < other.suffix

    def get_actions(self):
        actions = self.neighbours.copy()
        actions.append(self.terminal_state)
        return actions

    def same_player(self, other):
        if isinstance(other, State):
            if self.player == other.player:
                return True
        return False

    def add_neighbours(self, neighbours: list):
        self.neighbours.extend(neighbours)

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)

    def is_terminal_of(self, state):
        if isinstance(state, State):
            return self.sid == state.sid and state.terminal
        return False

    def set_terminal(self, state):
        self.terminal_state = state
        self.payoffs = state.payoffs
        self.alpha = self.payoffs[self.player]

    def add_terminal(self, payoffs):
        self.terminal_state = State(self.player, self.suffix, payoffs)
        self.payoffs = payoffs
        self.alpha = self.payoffs[self.player]

    def payoffs(self):
        if self.terminal:
            return self.payoffs
        else:
            return self.terminal_state.payoffs

    def get_payoff(self, state=None):
        if self.terminal:
            if state is None:
                return self.payoffs[self.player]
            return self.payoffs[state.player]
        else:
            if state is None:
                return self.terminal_state.payoffs[self.player]
            return self.terminal_state.payoffs[state.player]

    def create_plans(self):
        self.plans = get_all_plans(self)

    def update_viable(self, viable):
        self.viable = viable

    def update_alpha(self, alpha):
        self.alpha = alpha

    def get_viable(self):
        if self.terminal:
            return Plan([self])
        return self.viable