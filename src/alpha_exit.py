from itertools import permutations

print_get_X = False


class Alpha_Exit:
    def __init__(self, edge, subset_X, esc):
        self.edge = edge
        self.state_x = edge[0]
        self.state_y = edge[1]
        self.subset_X = subset_X
        self.esc = esc
        self.exit_id = f'e = {edge}, X = {subset_X}'

    def __str__(self):
        return self.exit_id

    def __repr__(self):
        return self.exit_id


class Exit_Sequence:
    def __init__(self, subset_x, subset_z, esc_x, edge_map):
        self.subset_x = subset_x
        self.subset_z = subset_z
        self.esc_x = esc_x
        self.edge_map = edge_map

        self.state_x = list(edge_map.keys())[-1]
        self.state_y = edge_map[self.state_x]

        self.edge = (self.state_x, self.state_y)

    def get_subset_z(self):
        return self.subset_z.copy()

    def copy(self):
        subset_x = self.subset_x.copy()
        subset_z = self.subset_z.copy()
        esc_x = self.esc_x.copy()
        edge_map = self.edge_map.copy()
        return Exit_Sequence(subset_x, subset_z, esc_x, edge_map)

    def __str__(self):
        return f'{self.edge_map}'

    def __repr__(self):
        return f'{self.edge_map}'

    def __hash__(self):
        return hash(f'{self.edge_map}')


class Subset_Exit_Sequence:
    def __init__(self, subset_x, legitimate_sequences, positive_sequences):
        self.subset_x = subset_x
        self.legitimate_sequences = legitimate_sequences
        self.positive_sequences = positive_sequences


def find_alpha_exit(game, safe_steps):
    X = get_X(game, safe_steps)
    all_exit_sequences = []

    for subset_x in X:
        esc_x = find_ESC(subset_x, safe_steps)
        subset_exits = find_subset_exit_sequences(subset_x, esc_x, safe_steps)

        legitimate_sequences = []
        positive_sequences = []

        for subset_exit in subset_exits:
            sequence = find_legitimate_exit_sequences(subset_exit, esc_x)
            if sequence is not None:
                legitimate_sequences.append(sequence)

            sequence = find_positive_exit_sequence(subset_exit, esc_x)
            if sequence is not None:
                positive_sequences.append(sequence)

        all_exit_sequences.append(Subset_Exit_Sequence(subset_x, legitimate_sequences, positive_sequences))

    return all_exit_sequences


def find_positive_exit_sequence(subset_exit, esc_x):
    for state_x in subset_exit.edge_map.keys():
        if state_x.alpha > 0:
            return subset_exit.copy()


def find_legitimate_exit_sequences(subset_exit, esc_x):
    subset_z = subset_exit.get_subset_z()
    edge_map = subset_exit.edge_map.copy()
    states = list(edge_map.keys())
    states.reverse()

    for state_x in states:

        if state_x in subset_z:
            subset_z.remove(state_x)

        legitimate = True

        for state_z in esc_x.union(subset_exit.subset_z):
            if state_x == state_z:
                continue

            if state_x.same_player(state_z) and state_x.alpha <= state_z.alpha:
                del edge_map[state_x]
                legitimate = False
                break

        if legitimate:
            return subset_exit.copy()

    return None


def is_esc_legitimate(state_x, esc_x):
    legitimate = True
    for state_y in esc_x:
        if state_x == state_y:
            continue

        if state_x.same_player(state_y) and state_x.alpha <= state_y.alpha:
            legitimate = False
            break

    return legitimate


def find_subset_exit_sequences(subset_x, esc_x, safe_steps):
    cycle_map = find_cycle_map(subset_x)
    exit_sequences = []

    for state_x in subset_x:

        subset_z = []
        edge_sequence = {}
        is_exit = False
        edge_sequence[state_x] = []

        for state_y in find_feasible_y(state_x, subset_x, safe_steps):
            if is_exit_sequence(subset_z, esc_x, state_x, state_y):
                is_exit = True
                edge_sequence[state_x].append(state_y)

        if is_exit:
            subset_z.append(state_x)
            edge_sequence = check_descendant(subset_x, esc_x, safe_steps, subset_z, cycle_map, edge_sequence)
            exit_sequences.append(Exit_Sequence(subset_x, subset_z, esc_x, edge_sequence))

    return exit_sequences


def check_descendant(subset_x, esc_x, safe_steps, subset_z, cycle_map, edge_map):
    state_x = cycle_map.get(subset_z[-1])

    if state_x == None:
        print(cycle_map)

    if state_x == subset_z[0]:
        del subset_z[-1]
        return edge_map

    edge_map[state_x] = []
    is_exit = False
    for state_y in find_feasible_y(state_x, subset_x, safe_steps):
        if is_exit_sequence(subset_z, esc_x, state_x, state_y):
            is_exit = True
            edge_map[state_x].append(state_y)

    if is_exit:
        subset_z.append(state_x)
        return check_descendant(subset_x, esc_x, safe_steps, subset_z, cycle_map, edge_map)

    del edge_map[state_x]
    del subset_z[-1]

    return edge_map


def find_cycle_map(subset):
    cycle_map = {}

    for state_x in subset:
        for state_y in subset:
            if state_y in state_x.neighbours:
                cycle_map[state_y] = state_x

    return cycle_map


def find_feasible_y(state_x, subset_x, safe_steps):
    feasible_y = set()

    for state_y in state_x.get_actions():
        # if state_y not in subset_x and state_y not in safe_steps[state_x]:
        if state_y not in subset_x:
            feasible_y.add(state_y)

    return feasible_y


def is_exit_sequence(subset_z, esc_x, state_x, state_y):
    left_implication = True

    for viable_y in state_y.get_viable():
        if alpha_sat(viable_y, esc_x.union(subset_z)):
            continue
        left_implication = False
        break

    is_alpha_exit = True

    if left_implication:
        for viable_y in state_y.get_viable():
            if alpha_sat(viable_y, [state_x]):
                continue
            is_alpha_exit = False
            break

    return is_alpha_exit


def legitimate_alpha_exits(subset_x, esc, safe_steps):
    alpha_exits = []
    feasible_edges = []

    for state_x in subset_x:
        for state_y in state_x.get_actions():
            if state_y not in subset_x and state_y not in safe_steps[state_x]:
                feasible_edges.append((state_x, state_y))

    for feasible_edge in feasible_edges:
        if is_alpha_exit_edge(*feasible_edge, esc):
            alpha_exits.append(Alpha_Exit(feasible_edge, subset_x, esc))

    return alpha_exits


def is_alpha_exit_edge(state_x, state_y, esc):
    left_implication = True

    for viable_y in state_y.get_viable():
        if alpha_sat(viable_y, esc):
            continue
        left_implication = False
        break

    is_alpha_exit = True

    if left_implication:
        for viable_y in state_y.get_viable():
            if alpha_sat(viable_y, [state_x]):
                continue
            is_alpha_exit = False
            break

    legit_alpha_exit = True

    if is_alpha_exit:
        for state_z in esc:
            if state_z == state_x:
                continue

            if state_x.same_player(state_z) and state_z.alpha >= state_x.alpha:
                legit_alpha_exit = False
                break

        return legit_alpha_exit

    return False


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

    for state in subset:
        for step in safe_steps[state]:
            if step not in subset:
                esc.add(state)

    return esc


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
        esc = find_ESC(subset, safe_steps)
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
