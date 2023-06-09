class Alpha_Plateau:
    def __init__(self, states, player, alpha):
        self.states = states
        self.player = player
        self.alpha = alpha
        self.plateau_id = f'({alpha}, {self.player+1})'

    def __hash__(self):
        return hash(self.plateau_id)

    def __str__(self):
        return f'Player: {self.player+1}, Alpha: {self.alpha}'

    def __repr__(self):
        return self.plateau_id


class Plateau_U:
    def __init__(self, u_map: dict):
        self.u_map = u_map
        self.states = u_map.keys()
        self.u_map_id = '{'
        for state in self.states:
            self.u_map_id += f'{state}: {u_map[state]}, '
        self.u_map_id = self.u_map_id[:-2] + '}'

    def __eq__(self, other):
        if self.u_map_id == other.u_map_id:
            return True

    def __hash__(self):
        return hash(self.u_map_id)

    def __str__(self):
        return self.u_map_id

    def __repr__(self):
        return self.u_map_id


class Viacomp:
    def __init__(self, state, plan):
        self.state = state
        self.plan = plan

    def __str__(self):
        return str(self.plan)

    def __repr__(self):
        return repr(self.plan)


class Admissible:
    def __init__(self, viacomp):
        self.state = viacomp.state
        self.plan = viacomp.plan
        self.state_payoff = self.plan.get_payoff(self.state)

    def __str__(self):
        return str(self.plan)

    def __repr__(self):
        return repr(self.plan)
