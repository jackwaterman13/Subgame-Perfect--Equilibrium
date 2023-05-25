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
