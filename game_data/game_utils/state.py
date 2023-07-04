from game_data.game_utils.plans import *


class State:
    def __init__(self, player: int, payoffs, suffix='', is_terminal=False):

        self.player = player
        self.suffix = suffix
        self.is_terminal = is_terminal
        self.payoffs = payoffs
        self.state_id = f'{self.player + 1}{suffix}'

        if self.is_terminal:
            self.state_id = f'{self.player + 1}{suffix}*'
            self.terminal_state = self
        else:
            self.terminal_state = State(player, payoffs, suffix=suffix, is_terminal=True)

    def __str__(self):
        return self.state_id

    def __repr__(self):
        return self.state_id

    def __hash__(self):
        return hash(self.state_id)

    def __eq__(self, other):
        if isinstance(other, State):
            return self.state_id == other.state_id
        return False
