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