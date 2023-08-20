class ThreatPair:
    def __init__(self, state_t, state_x, plan_v):
        self.state_t = state_t
        self.state_x = state_x
        self.state_y = plan_v[0]
        self.plan_v = plan_v
        self.edge = (state_x, plan_v[0])
        self.sequences = []
        self.exit_sets = []

    def __str__(self):
        return f'AD-iv: ({self.state_x}, {self.plan_v})'
