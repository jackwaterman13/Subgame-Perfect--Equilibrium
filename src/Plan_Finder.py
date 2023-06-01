from State import *


def get_all_plans(state_t):

    all_plans = []

    for path in dfs_path(state_t):
        find_plans_on_path(path, all_plans)

    return all_plans


def find_plans_on_path(path, all_plans):
    current_plan = []

    for state_t in path:

        if state_t in current_plan:
            current_plan.append(state_t)
            loop_plan = Plan(current_plan, False)

            if loop_plan not in all_plans:
                all_plans.append(loop_plan)
            continue

        current_plan.append(state_t)
        terminal_plan = Plan(current_plan + [state_t.terminal_state])

        if terminal_plan not in all_plans:
            all_plans.append(terminal_plan)

    return all_plans


def dfs_path(state_t, halt_states=None, path=None):
    if halt_states is None:
        halt_states = [state_t]

    if path is None:
        path = [state_t]

    deep_paths = []

    for state_u in state_t.neighbours:

        if state_u in path:
            loop = path.copy()
            loop.append(state_u)
            deep_paths.append(loop)
            continue

        next_path = path.copy()
        next_path.append(state_u)
        new_paths = dfs_path(state_u, halt_states, next_path)

        for path_y in new_paths:
            if isinstance(path_y, list):
                deep_paths.append(path_y)
            else:
                deep_paths.append(new_paths)
                break

    return deep_paths


class Plan:
    def __init__(self, plan=None, absorbing=True):
        if plan is None:
            plan = []
        self.plan = plan
        self.absorbing = absorbing

    def __len__(self):
        return len(self.plan)

    def __str__(self):
        return str(self.plan)

    def __repr__(self):
        return repr(self.plan)

    def __eq__(self, other):
        if isinstance(other, Plan):
            return self.plan == other.plan and self.absorbing == other.absorbing
        return False

    def __getitem__(self, item):
        return self.plan[item]

    def get_payoff(self, state):
        if not self.absorbing:
            return 0

        return self.plan[-1].get_payoff(state)


    def get_state_set(self):
        return set(self.plan)

    def is_absorbing(self):
        return self.absorbing
