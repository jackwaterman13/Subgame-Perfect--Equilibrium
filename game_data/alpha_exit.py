from itertools import permutations

from game_data.game_graph import GameGraph
from game_data.iteration_solver import alpha_sat


class LegitimateSequence:
    def __init__(self, sequence, edge):
        self.sequence = sequence
        self.edge = edge

    def __str__(self):
        return f'e={self.edge}, z={self.sequence}'

    def __repr__(self):
        return f'e={self.edge}, z={self.sequence}'


def find_legitimate_sequence(sequence, esc_x, alpha):
    while sequence:
        edge = sequence[-1]
        sequence.remove(edge)

        state_x = edge[0]
        subset_z = {edge[0] for edge in sequence}
        z_union_esc_x = esc_x.union(subset_z)

        legitimate = True

        for state_z in z_union_esc_x:
            if state_z.player == state_x.player and alpha[state_z] >= alpha[state_x]:
                legitimate = False
                break

        if legitimate:
            return LegitimateSequence(sequence, edge)


class AlphaExitFinder:
    def __init__(self, game_graph: GameGraph):
        self.states = game_graph.states
        self.action_map = game_graph.action_map

    def find_alpha_exit(self, alpha, threat_pair, safe_steps, viable_plans):
        state_x = threat_pair.state_x
        state_y = threat_pair.state_y
        x_alpha = self.get_X_alpha(alpha, safe_steps, state_x)

        exit_sets = []

        for subset_x in x_alpha:
            esc_x = find_ESC(subset_x, safe_steps)
            plans_v = viable_plans[state_y]

            if is_alpha_exit(esc_x, plans_v, state_x, alpha) and is_legitimate(state_x, esc_x, alpha):
                exit_sets.append(subset_x)

        return exit_sets

    def find_ex_sq(self, alpha, threat_pair, safe_steps, viable_plans):
        self.viable_plans = viable_plans
        x_alpha = self.get_X_alpha(alpha, safe_steps)

        legit_exit_seq = {}
        for subset_x in x_alpha:
            legit_exit_seq[frozenset(subset_x)] = {'sequences': []}

            self.esc_x = find_ESC(subset_x, safe_steps)
            exits = self.find_alpha_exits_from_x(subset_x, self.esc_x, viable_plans, alpha)

            legit_exit_seq[frozenset(subset_x)]['exits'] = exits

            sequences = []
            for state_z in exits:
                for state_y in exits[state_z]:
                    sequence = []
                    subset_z = {state_z}
                    sequence.append((state_z, state_y))
                    self.build_sequence(subset_x, subset_z, sequence, alpha)
                    sequences.append(sequence.copy())

            for sequence in sequences:
                legit_exit = find_legitimate_sequence(sequence, self.esc_x, alpha)
                if legit_exit is not None:
                    legit_exit_seq[frozenset(subset_x)]['sequences'].append(legit_exit)

        return legit_exit_seq

    def build_sequence(self, subset_x, subset_z, sequence, alpha):

        for state_x in subset_x:
            if state_x in subset_z:
                continue

            for state_y in self.get_exit_y(state_x, subset_x):
                z_union_esc = subset_z.union(self.esc_x)
                plans = self.viable_plans[state_y]
                if is_exit_sequence(z_union_esc, plans, state_x, alpha):
                    sequence.append((state_x, state_y))
                    subset_z.add(state_x)
                    break

        return sequence

    def get_X_alpha(self, alpha, safe_steps):
        feasible_X = find_subsets(self.states)

        c = find_C(feasible_X.copy(), self.action_map)
        p = find_P(feasible_X.copy(), alpha)
        e = find_E(feasible_X.copy(), safe_steps, alpha)

        x_alpha = find_all_X(c, p, e)

        return x_alpha

    def find_alpha_exits_from_x(self, subset_x, esc_x, viable_plans, alpha):
        exits_x = dict()

        for state_x in subset_x:
            for state_y in self.get_exit_y(state_x, subset_x):
                plans_v = viable_plans[state_y]
                if is_alpha_exit(esc_x, plans_v, state_x, alpha) and is_legitimate(state_x, esc_x, alpha):
                    # if is_alpha_exit(esc_x, plans_v, state_x, alpha):
                    if exits_x.get(state_x) is None:
                        exits_x[state_x] = {state_y}
                    else:
                        exits_x[state_x].add(state_y)

        return exits_x

    def get_exit_y(self, state_x, subset_x):
        return [state_y for state_y in self.action_map[state_x] if state_y not in subset_x]

    def find_positive_sequences(self, feasible_sequences):
        positive_sequences = []

        for sequence in feasible_sequences:

            subset_z = [state_z[0] for state_z in sequence]

            while subset_z:
                state_x = subset_z.pop()

        return positive_sequences


def alpha_exit_edges(alpha, edges, esc_x, viable_plans):
    exit_edges = set()

    for edge in edges:
        if is_alpha_exit(alpha, esc_x, edge[0], edge[1], viable_plans):
            exit_edges.add(edge)

    return exit_edges


def is_exit_sequence(z_union_esc, plans, state_x, alpha):
    for plan_v in plans:
        alpha_sat_v = alpha_sat_set(plan_v, alpha)

        if not z_union_esc.issubset(alpha_sat_v):
            continue

        if state_x not in alpha_sat_v:
            return False

    return True


def is_alpha_exit(esc_x, plans, state_x, alpha):
    for plan_v in plans:
        alpha_sat_v = alpha_sat_set(plan_v, alpha)
        if not esc_x.issubset(alpha_sat_v):
            continue

        if state_x not in alpha_sat_v:
            return False

    return True


def is_legitimate(state_x, esc_x, alpha):
    for state_z in esc_x:
        if state_z.player == state_x.player and alpha[state_z] >= alpha[state_x]:
            return False
        else:
            continue

    return True


def alpha_sat_set(plan, alpha):
    alpha_set = set()

    for state in alpha:
        if plan.get_payoff(state) >= alpha[state]:
            alpha_set.add(state)

    return alpha_set


def find_subsets(states):
    subsets = [[]]  # Start with an empty set

    # Generate subsets for each element in the original set
    for state in states:
        subsets += [subset + [state] for subset in subsets]

    return [set(subset) for subset in subsets[1:]]


def find_POS(subset, alpha):
    pos = set(state for state in subset if alpha[state] > 0)
    return pos


def find_ESC(subset, safe_steps):
    esc = set()

    for state in subset:
        for step in safe_steps[state]:
            if step not in subset:
                esc.add(state)

    return esc


def find_C(feasible_X, action_map):
    c = []

    for subset in feasible_X:
        c_viable_set = True

        for state_x in subset:
            c_viable_x = False

            for action_x in action_map[state_x]:
                if action_x in subset:
                    c_viable_x = True
                    break

            if not c_viable_x:
                c_viable_set = False
                break

        if c_viable_set:
            c.append(set(subset))

    return c


def find_P(feasible_x, alpha):
    p = []

    for subset in feasible_x:
        if find_POS(subset, alpha) != set():
            p.append(subset)

    return p


def find_E(feasible_x, safe_steps, alpha):
    e = []

    for subset in feasible_x:
        esc = find_ESC(subset, safe_steps)
        pos = find_POS(subset, alpha)
        if esc.intersection(pos) == set():
            e.append(subset)

    return e


def find_all_X(c, p, e):
    x = []

    for subset_c in c:
        if subset_c in p and subset_c in e:
            x.append(subset_c)

    return x
