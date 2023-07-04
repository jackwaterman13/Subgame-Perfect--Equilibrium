
def create_plans(states, neighbour_map):

    plans = {state: [] for state in states}
    for state in states:
        reachable = find_reachable(state, neighbour_map)

        for path in reachable:
            plans[state] = find_plans(path, plans[state])

    return plans


def find_plans(path, all_plans):
    current_plan = []

    for state_t in path:

        if state_t in current_plan:
            loop_plan = Plan(current_plan + [state_t], False)

            if loop_plan not in all_plans:
                all_plans.append(loop_plan)
            continue

        current_plan.append(state_t)
        terminal_plan = Plan(current_plan + [state_t.terminal_state])

        if terminal_plan not in all_plans:
            all_plans.append(terminal_plan)

    return all_plans


def find_reachable(state_t, neighbour_map, path=None):

    if path is None:
        path = []

    path = path + [state_t]
    deep_paths = [path]

    for state_u in neighbour_map[state_t]:
        if state_u not in path:
            new_paths = find_reachable(state_u, neighbour_map, path)
            deep_paths.extend(new_paths)
            continue

        loop_path = path.copy()
        loop_path.append(state_u)
        deep_paths.append(loop_path)

    return deep_paths


class Plan:
    def __init__(self, plan=None, is_absorbing=True):
        if plan is None:
            plan = []
        self.plan = plan
        self.is_absorbing = is_absorbing

    def __len__(self):
        return len(self.plan)

    def __str__(self):
        if not self.is_absorbing:
            return str(self.plan) + ' Non-absorbing'
        return str(self.plan)

    def __repr__(self):
        if not self.is_absorbing:
            return repr(self.plan) + ' Non-absorbing'
        return repr(self.plan)

    def __eq__(self, other):
        if isinstance(other, Plan):
            return self.plan == other.plan and self.is_absorbing == other.is_absorbing
        return False

    def __getitem__(self, item):
        return self.plan[item]

    def get_payoff(self, state_t):
        if not self.is_absorbing:
            return 0

        return self.plan[-1].payoffs[state_t.player]

    def plan_set(self):
        return set(self.plan)
