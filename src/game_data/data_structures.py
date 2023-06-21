class AlphaPlateau:
    def __init__(self, states):
        self.states = states
        self.player = states[0].player
        self.alpha = states[0].alpha
        self.plateau_id = f'({self.alpha}, {self.player + 1})'

    def __hash__(self):
        return hash(self.plateau_id)

    def __str__(self):
        return f'Player: {self.player + 1}, Alpha: {self.alpha}'

    def __repr__(self):
        return self.plateau_id


class PlateauU:
    def __init__(self, u_map: dict):
        self.u_map = u_map
        self.states = list(u_map.keys())
        self.u_map_id = '{'
        for state in self.states:
            self.u_map_id += f'{state}: {u_map[state]}, '
        self.u_map_id = self.u_map_id[:-2] + '}'

    def __getitem__(self, key):
        return self.u_map[key]

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
    def __init__(self, viacomp, threat_pair=None):
        self.state = viacomp.state
        self.plan = viacomp.plan
        self.state_payoff = self.plan.get_payoff(self.state)
        if threat_pair is not None:
            self.threat_pair = threat_pair
        else:
            self.threat_pair = None

    def __str__(self):
        return str(self.plan)

    def __repr__(self):
        return repr(self.plan)


class Iteration_Data:
    def __init__(self, gamma, start_alpha, safe_steps, alpha_exits):
        self.start_alpha = start_alpha
        self.gamma = gamma
        self.safe_steps = safe_steps
        self.alpha_exits = alpha_exits

    def __str__(self):
        return f'{self.start_alpha}'

    def __repr__(self):
        return f'{self.start_alpha}'


class ThreatPair:
    def __init__(self, state_t, state_x, plan_v):
        self.state_t = state_t
        self.state_x = state_x
        self.plan_v = plan_v
