
class Admissible:
    def __init__(self, state, plan, u_map, condition):
        self.state = state
        self.plan = plan
        self.u_map = dict(u_map)
        self.state_payoff = self.plan.get_payoff(self.state)
        self.condition = condition

    def __str__(self):
        return f'g = {self.plan}, \u03C6t = {self.state_payoff}'

    def __repr__(self):
        return repr(self.plan)
