print_get_X = False

class Alpha_Exit:
    def __init__(self, state_x, state_y, subset_X):
        self.state_x = state_x
        self.state_y = state_y
        self.subset_X = subset_X
        self.exit_id = f'e = ({state_x}, {state_y})\n' \
                       f'X = {subset_X}'

    def __str__(self):
        return self.exit_id


def find_alpha_exit(game, safe_steps):
    X = get_X(game, safe_steps)
    alpha_exits = []

    for subset in X:
        alpha_exits.extend(subset_alpha_exits(subset, safe_steps))

    for alpha_exit in alpha_exits:
        print('Alpha Exit')
        print(alpha_exit)


def subset_alpha_exits(subset_x, safe_steps):
    esc, step_map = find_ESC(subset_x, safe_steps)
    alpha_exits = []

    for state_x in step_map:
        for state_y in step_map[state_x]:
            is_alpha_exit = True
            for viable_y in state_y.get_viable():
                if not alpha_sat(viable_y, subset_x):
                    is_alpha_exit = False

            if is_alpha_exit:
                alpha_exits.append(Alpha_Exit(state_x, state_y, subset_x))

    return alpha_exits


def get_X(game, safe_steps):
    states = list(game.keys())
    feasible_X = find_subsets(states)

    c = find_C(feasible_X.copy())
    p = find_P(feasible_X.copy())
    e = find_E(feasible_X.copy(), safe_steps)

    x = find_all_X(c, p, e)

    if print_get_X:
        print(f'C = {c}')
        print(f'P = {p}')
        print(f'E = {e}')
        print(f'X = {x}')

    return x


def find_subsets(states):
    subsets = [[]]  # Start with an empty set

    # Generate subsets for each element in the original set
    for state in states:
        subsets += [subset + [state] for subset in subsets]

    subsets = [set(subset) for subset in subsets[1:]]
    return subsets


def find_POS(subset):
    pos = set(state for state in subset if state.alpha > 0)
    return pos

    # pos = []
    #
    # for subset in feasible_X:
    #     pos_viable = True
    #
    #     for state in subset:
    #         if state.alpha <= 0:
    #             pos_viable = False
    #             break
    #
    #     if pos_viable:
    #         pos.append(set(subset))
    #
    # return pos


def find_ESC(subset, safe_steps):
    esc = set()
    step_map = {}

    for state in subset:
        for step in safe_steps[state]:
            if step not in subset:
                y = step_map.get(state, [])
                y.append(step)
                step_map[state] = y
                esc.add(state)

    return esc, step_map


def find_C(feasible_X):
    c = []

    for subset in feasible_X:
        c_viable_set = True

        for state_x in subset:
            c_viable_x = False

            for action_x in state_x.get_actions():
                if action_x in subset:
                    c_viable_x = True
                    break

            if not c_viable_x:
                c_viable_set = False
                break

        if c_viable_set:
            c.append(set(subset))

    return c


def find_P(feasible_x):
    p = []

    for subset in feasible_x:
        if find_POS(subset) != set():
            p.append(subset)

    return p


def find_E(feasible_x, safe_steps):
    e = []

    for subset in feasible_x:
        esc, _ = find_ESC(subset, safe_steps)
        pos = find_POS(subset)
        if esc.intersection(pos) == set():
            e.append(subset)

    return e


def find_all_X(c, p, e):
    x = []

    for subset_c in c:
        if subset_c in p and subset_c in e:
            x.append(subset_c)

    return x


def alpha_sat(plan, check_states=None):
    if check_states is None:
        check_states = plan.get_state_set()

    sat = True

    for state in check_states:
        if plan.get_payoff(state) < state.alpha:
            sat = False

    return sat
