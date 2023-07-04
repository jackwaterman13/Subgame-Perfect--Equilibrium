from collections import namedtuple
from game_data.game_graph import GameGraph
from game_data.game_utils.plans import Plan
from game_data.iteration_utils.admissible import Admissible
from game_data.iteration_utils.threat_pair import ThreatPair


class IterationSolver:
    def __init__(self, game_graph: GameGraph):

        self.game_graph = game_graph
        self.states = game_graph.states
        self.players = game_graph.players
        self.action_map = game_graph.action_map
        self.plans = game_graph.plans

        self.viable_plans = dict()
        self.plateaus = dict()
        self.alpha_safe_combinations = dict()
        self.safe_steps = dict()
        self.viacomp_plans = dict()
        self.admissible_plans = dict()

        self.alpha = None

    def perform_iteration(self, alpha):
        self.alpha = alpha
        self.find_viable_plans()
        self.find_safe_steps()
        self.find_plateaus()
        self.find_viacomp_plans()
        self.find_admissible_plans()

        return self.admissible_plans.copy(), self.safe_steps.copy()

    def find_viable_plans(self):
        for state in self.states:
            self.viable_plans[state] = find_viable(state, self.plans, self.alpha)
            self.viable_plans[state.terminal_state] = [Plan([state.terminal_state])]

    def find_safe_steps(self):
        for state in self.states:
            self.safe_steps[state] = find_state_safe_steps(state,
                                                           self.viable_plans,
                                                           self.action_map,
                                                           self.alpha)

    def find_plateaus(self):

        for state in self.states:
            plateau = Plateau(state.player, self.alpha[state])

            if self.plateaus.get(plateau) is None:
                self.plateaus[plateau] = [state]
                continue

            self.plateaus[plateau].append(state)

    def find_viacomp_plans(self):

        for plateau in self.plateaus:
            plateau_set = self.plateaus[plateau]
            plateau_combinations = find_subsets(plateau_set)
            for subset in plateau_combinations:
                self.viacomp_plans[subset] = find_subset_viacomp_plans(subset, self.viable_plans, self.safe_steps)

    def find_admissible_plans(self):

        for subset_u in self.viacomp_plans:
            self.admissible_plans[subset_u] = find_subset_admissible_plans(self.viacomp_plans[subset_u],
                                                                           self.viable_plans,
                                                                           self.action_map,
                                                                           self.alpha)


def find_viable(state, plans, alpha):
    viable_plans = []

    for plan in plans[state]:
        if alpha_sat(plan, alpha):
            viable_plans.append(plan)

    return viable_plans


def find_state_safe_steps(state_t, viable_plans, action_map, alpha):
    safe = []

    for state_u in action_map[state_t]:
        if all(alpha_sat(plan, alpha, [state_t]) for plan in viable_plans[state_u]):
            safe.append(state_u)

    return safe


def find_subset_viacomp_plans(plateau_set, viabel_plans, safe_steps):
    viacomp_plans = {}

    for state_t in plateau_set:
        for plan in viabel_plans[state_t]:

            if not plateau_set.issubset(plan.plan_set()):
                continue

            u_map = {}
            is_viacomp = True

            for state_u in plateau_set:

                action_u = first_action(plan, state_u)
                if action_u in safe_steps[state_u]:
                    u_map[state_u] = action_u
                    continue

                is_viacomp = False
                break

            if is_viacomp:
                u_map = frozenset(u_map.items())
                if viacomp_plans.get(u_map) is None:
                    viacomp_plans[u_map] = [plan]
                    continue

                viacomp_plans[u_map].append(plan)

    return viacomp_plans


def find_subset_admissible_plans(viacomp_plans, viable_plans, action_map, alpha):
    admissible_plans = {}

    for u_map in viacomp_plans:
        admissible_plans[u_map] = []
        for plan in viacomp_plans[u_map]:
            state_t = plan[0]

            if alpha[state_t] > 0:
                admissible_plans[u_map].append(Admissible(state_t, plan, u_map, 'AD-i: \u03B1 > 0'))
                continue

            if not plan.is_absorbing:
                admissible_plans[u_map].append(Admissible(state_t, plan, u_map, 'AD-ii: non-absorbing'))
                continue

            visited_dict = {state: False for state in u_map}
            appeared_once = True

            for state_u in plan:

                if visited_dict.get(state_u) is not None:
                    if visited_dict[state_u]:
                        appeared_once = False

                    visited_dict[state_u] = True

                if state_u.is_terminal:
                    continue

                # AD-i: Different payoffs so state_t != state_u
                if appeared_once and state_t.player == state_u.player and alpha[state_u] > alpha[state_t]:
                    admissible_plans[u_map].append(Admissible(state_t, plan, u_map,
                                                              f'AD-i: {state_u}.\u03B1 > {state_t}.\u03B1'))

                # AD-iv (b)
                if state_t.player != state_u.player and appeared_once:
                    is_threat, threat_pair = is_threat_pair(state_t, state_u, viable_plans, alpha, action_map, plan)
                    if is_threat:
                        admissible_plans[u_map].append(Admissible(state_t, plan, u_map, threat_pair))

            if appeared_once:
                admissible_plans[u_map].append(Admissible(state_t, plan, u_map,
                                                          'AD-iii: Each state of F(U) appeared once'))

    return admissible_plans


def is_threat_pair(state_t, state_x, viable_plans, alpha, action_map, plan_g):
    # (c)
    for state_v in action_map[state_x]:
        # (d)
        if first_action(plan_g, state_x) == state_v:
            continue
        # (e)
        for plan_v in viable_plans[state_v]:
            if not alpha_sat(plan_v, alpha, [state_x]) and not alpha_sat(plan_v, alpha, [state_t]):
                return True, ThreatPair(state_t, state_x, plan_v)

    return False, None


def alpha_sat(plan, alpha, check_states=None):
    if check_states is None:
        check_states = plan

    for state in check_states:
        if state.is_terminal:
            continue

        if plan.get_payoff(state) < alpha[state]:
            return False

    return True


def first_action(plan_g, state_t):
    if state_t.is_terminal:
        return state_t

    return plan_g[first_occurrence_index(plan_g, state_t) + 1]


def first_occurrence_index(plan_g, state_t):
    return next((index for index, state in enumerate(plan_g) if state == state_t),
                Exception(f'{state_t} not in plan plan'))


def find_subsets(states):
    subsets = [[]]  # Start with an empty set

    # Generate subsets for each element in the original set
    for state in states:
        subsets += [subset + [state] for subset in subsets]

    subsets = {frozenset(subset) for subset in subsets[1:]}
    return subsets


# Named Tuples
Viacomp = namedtuple('Viacomp', ['plan', 'u_map'])
Plateau = namedtuple('Plateau', ['player', 'alpha'])
Alpha_Safe_Combination = namedtuple('Alpha_Safe_Combination', ['state', 'safe_step'])
