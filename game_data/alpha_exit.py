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
    def __init__(self, state_x, state_y, subset_x, subset_z, esc_x, edge_sequence, legitimate_exits=None):

        self.state_x = state_x
        self.state_y = state_y
        self.subset_x = subset_x
        self.subset_z = subset_z
        self.esc_x = esc_x
        self.edge_sequence = edge_sequence
        self.edge = (self.state_x, self.state_y)

        self.legitimate_exits = legitimate_exits
        self.legitimate_exit = True

        if legitimate_exits is None:
            self.legitimate_exits = []
            self.legitimate_exit = False

        self.is_legitimate_exit_sequences()
        self.positive_exit = self.is_positive_exit()

    def is_legitimate_exit_sequences(self):
        for state_z in self.esc_x.union(self.subset_z):
            if self.state_x.player == state_z.player and self.state_x.alpha <= state_z.alpha:
                self.legitimate_exit = False
                self.legitimate_exits = None
                return

        self.legitimate_exit = True
        if self.edge not in self.legitimate_exits:
            self.legitimate_exits.append(self.edge)

    def is_positive_exit(self):

        if self.state_x.alpha > 0:
            return True

    def get_legitimate_exits_copy(self):
        if not self.legitimate_exit:
            return None
        return self.legitimate_exits.copy()

    def __str__(self):
        return f'{self.edge_sequence}'

    def __repr__(self):
        return f'{self.edge_sequence}'

    def __hash__(self):
        return hash(f'{self.edge_sequence}')


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
        subset_exits = find_subset_exit_sequences(subset_x, esc_x)
        legitimate_exits = [exit_i for exit_i in subset_exits if exit_i.legitimate_exit]
        positive_exits = [exit_i for exit_i in subset_exits if exit_i.positive_exit]
        all_exit_sequences.append(Subset_Exit_Sequence(subset_x, legitimate_exits, positive_exits))

    return all_exit_sequences


def find_subset_exit_sequences(subset_x, esc_x):
    cycle_map = dfs_cycle_paths(list(subset_x)[0], subset_x)
    exit_sequences = []


    for state_x in subset_x:
        for cycle in cycle_map:
            cycle.reverse()
            cycle = cycle_start(cycle, state_x)
            cycle.pop()
            subset_z = []
            edge_sequence = {}
            legitimate_exits = None
            exit_sequences.extend(find_exit_sequence(state_x,
                                                     subset_x,
                                                     esc_x,
                                                     subset_z,
                                                     cycle,
                                                     edge_sequence,
                                                     legitimate_exits))

    return exit_sequences


def cycle_start(lst, start_item):
    try:
        start_index = lst.index(start_item)
    except ValueError:
        return None  # or handle the error however you want

    # Cycle the list
    return lst[start_index:] + lst[:start_index]


def find_exit_sequence(state_x, subset_x, esc_x, subset_z, cycle, edge_sequence, legitimate_exits):
    exit_sequences = []

    for state_y in find_feasible_y(state_x, subset_x):
        if is_exit_sequence(subset_z, esc_x, state_x, state_y):

            next_subset_z = subset_z.copy()
            next_edge_sequence = edge_sequence.copy()
            next_edge_sequence[state_x] = state_y

            sequence = Exit_Sequence(state_x,
                                     state_y,
                                     subset_x,
                                     next_subset_z,
                                     esc_x,
                                     next_edge_sequence,
                                     legitimate_exits)

            exit_sequences.append(sequence)

            if len(cycle) > 0:
                next_subset_z = next_subset_z.copy()
                next_state_x = cycle.pop()
                next_subset_z.append(state_x)
                next_edge_sequence = next_edge_sequence.copy()
                next_legitimate_exits = sequence.get_legitimate_exits_copy()

                exit_sequences.extend(find_exit_sequence(next_state_x,
                                                         subset_x,
                                                         esc_x,
                                                         next_subset_z,
                                                         cycle,
                                                         next_edge_sequence,
                                                         next_legitimate_exits))

    return exit_sequences


def find_cycle_map(subset, cycle_map=None, all_cycles=None):
    if cycle_map is None:
        cycle_map = dict()

    all_cycles = []

    for state_x in subset:
        for state_y in state_x.neighbours:
            next_map = cycle_map.copy()
            if state_y in subset and state_y not in cycle_map.keys():
                next_map[state_y] = state_x
                if len(next_map) == len(subset):
                    all_cycles.append(next_map)
                    continue

                all_cycles.extend(find_cycle_map(subset, next_map, all_cycles))

    return all_cycles


def dfs_cycle_paths(state_t, subset, path=None):

    if path is None:
        path = [state_t]

    deep_paths = []

    for state_u in state_t.neighbours:

        if state_u in path:
            if subset == set(path):
                deep_paths.append(path)
            continue

        next_path = path.copy()
        next_path.append(state_u)
        new_paths = dfs_cycle_paths(state_u, subset, next_path)

        for path_y in new_paths:
            if isinstance(path_y, list):
                deep_paths.append(path_y)
            else:
                deep_paths.append(new_paths)
                break

    return deep_paths




def find_feasible_y(state_x, subset_x):
    feasible_y = set()

    for state_y in state_x.get_actions():
        if state_y not in subset_x:
            feasible_y.add(state_y)

    return feasible_y


def is_exit_sequence(subset_z, esc_x, state_x, state_y):
    left_implication = True

    for viable_y in state_y.get_viable():
        if not alpha_sat(viable_y, esc_x.union(subset_z)):
            left_implication = False
            break

    is_alpha_exit = True

    if left_implication:
        for viable_y in state_y.get_viable():
            if not alpha_sat(viable_y, [state_x]):
                is_alpha_exit = False
                break

    return is_alpha_exit


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



