from State import *


def find_safe_steps(state_t: State):
    safe = []

    if state_t.get_payoff(state_t) >= state_t.alpha:
        safe.append(state_t.terminal_state)

    for state_u in state_t.neighbours:
        viable_u = viable(state_u)

        if all(alpha_sat(plan, state_t) for plan in viable_u):
            safe.append(state_u)

    return safe


def alpha_sat(plan, state_t):
    if isinstance(state_t, list):
        states = state_t
    else:
        states = [state_t]

    for state_u in plan:
        for state in states:
            if state_u.get_payoff(state) >= state.alpha:
                continue
            return False
    return True


def viable(state_t: State):
    viable_plans = []

    plans_t = all_plans(state_t)

    for plan in plans_t:
        state_u = plan[-1]
        if state_u.get_payoff(state_t) >= state_t.alpha:
            viable_plans.append(plan)

    return viable_plans


def all_plans(state_t):
    deep_paths = dfs_path(state_t)

    plans = []

    for path in deep_paths:
        plan = []
        for state_t in path:
            plan.append(state_t)
            terminal_plan = plan.copy()
            terminal_plan.append(state_t.terminal_state)

            if terminal_plan not in plans:
                plans.append(terminal_plan)

    return plans


def dfs_path(state_t, halt_states=None, path=None):
    if halt_states is None:
        halt_states = [state_t]

    if path is None:
        path = [state_t]

    deep_paths = []

    for state_u in state_t.neighbours:

        if state_u in halt_states:
            # path.append(state_u)
            deep_paths.append(path)
            continue

        if state_u not in path:
            next_path = path.copy()
            next_path.append(state_u)
            new_paths = dfs_path(state_u, halt_states, next_path)

            for path_y in new_paths:
                if isinstance(path_y, list):
                    deep_paths.append(path_y)
                else:
                    deep_paths.append(new_paths)
                    break
        # else:
        #     # print('dfs_path(): Loop')

    return deep_paths


def alpha_safe_combinations(alpha_plateau):
    pass


def admissible(plan_g, state_t: State, U_comp):
    # AD-ii
    if plan_g is None:
        return True

    # AD-i: Assuming alpha_t refers to the plan payoff
    if plan_g[-1].get_payoff(state_t) > state_t.alpha:
        return True

    visited_dict = {state_u: False for state_u in set(U_comp)}
    appeared_once_U = True

    for state_u in plan_g:

        if visited_dict.get(state_u) is not None:
            if visited_dict[state_u]:
                appeared_once_U = False

            visited_dict[state_u] = True

        # AD-i
        if state_t.same_player(state_u) and state_u.get_payoff() > state_t.get_payoff() and appeared_once_U:
            return True

        # AD-iv: (a) and (b)
        if appeared_once_U and not state_t.same_player(state_u):
            if is_threat_pair(state_t, state_u, plan_g):
                return True

    # AD-iii
    if appeared_once_U:
        return True


def is_threat_pair(state_t, state_x: State, plan_g):
    # (c)
    for state_v in state_x.neighbours:

        # (d)
        if plan_g[first_occurrence_index(plan_g, state_x) + 1] == state_v:
            continue
        # (e)
        for plan_v in viable(state_v):
            if not alpha_sat(plan_v, [state_x, state_t]):
                return True

    return False


def first_occurrence_index(plan_g, state_t):
    return next((index for index, state in enumerate(plan_g) if state == state_t),
                Exception(f'{state_t} not in plan plan'))


def viable_compatible(plan_g, state_t, U_compatible):
    first_action_index = first_occurrence_index(plan_g, state_t) + 1

    if first_action_index == len(plan_g):
        return True

    if plan_g[first_action_index] in U_compatible[state_t]:
        return True


def alpha_safe_combination(alpha_plateau):
    U_compatible = {}

    for alpha in alpha_plateau:
        for state in alpha_plateau[alpha]:
            U_compatible[state] = find_safe_steps(state)

    return U_compatible


class Game:
    def __init__(self):
        self.playable_states = {}
        self.states = []
        self.alpha = {}
        self.test_game()

        self.equilibrium()

    def test_game(self):
        self.states = [State(0, suffix='a'),
                       State(0, suffix='a', payoffs=[-2, 0, 1]),
                       State(1),
                       State(1, payoffs=[-3, 1, 0]),
                       State(0, suffix='b'),
                       State(0, suffix='b', payoffs=[-1, 2, -2]),
                       State(2),
                       State(2, payoffs=[2, 2, -1])]

        for state_t in self.states:
            for state_u in self.states:
                if not state_u.terminal:
                    continue

                if state_t.is_terminal_of(state_u):
                    state_t.add_terminal(state_u)

        self.playable_states[self.states[0]] = [self.states[2]]
        self.playable_states[self.states[2]] = [self.states[4]]
        self.playable_states[self.states[4]] = [self.states[0], self.states[6]]
        self.playable_states[self.states[6]] = [self.states[0]]

        for state in self.playable_states.keys():
            state.add_neighbours(self.playable_states[state])

    def equilibrium(self):

        safe_steps = {state: find_safe_steps(state) for state in self.playable_states}
        alpha_plateau = self.find_alpha_plateaus()

    def find_alpha_plateaus(self):

        alpha_map = {state.alpha: [] for state in self.playable_states}

        for state in self.playable_states:
            alpha_map[state.alpha].append(state)

        return alpha_map


Game()
