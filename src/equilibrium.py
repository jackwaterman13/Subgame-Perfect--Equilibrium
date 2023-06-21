from alpha_exit import *
from game_data.data_structures import *
from game_data.game_generator import *
from itertools import combinations


class IterationSolver:
    def __init__(self, game_map, game_id):
        self.game = game_map
        self.game_id = game_id

        self.alpha_vector = None
        self.alpha_exits = None
        self.alpha_plateaus = None
        self.safe_steps = None
        self.all_U_compatible = None
        self.viable_compatible = None
        self.admissible_plans = None
        self.beta = None
        self.gamma = None
        self.converged = False

    def perform_iteration(self):

        self.alpha_vector = {state: state.alpha for state in self.game}
        self.get_viable_plans()
        self.get_safe_steps()
        self.get_alpha_plateaus()
        self.get_U_compatible()
        self.get_viable_compatible()
        self.get_alpha_exits()
        self.get_admissible()
        self.get_beta()

        return Iteration_Data(self.get_gamma(), self.alpha_vector, self.safe_steps, self.alpha_exits)

    def get_end_game_safe_steps(self):
        self.get_viable_plans()
        self.get_safe_steps()
        return self.safe_steps

    def get_viable_plans(self):
        viable_plans = {}

        for state in self.game:
            viable_plans[state] = viable(state)
            state.update_viable(viable_plans[state])

        return viable_plans

    def get_alpha_plateaus(self):
        self.alpha_plateaus = find_alpha_plateaus(self.game)
        return self.alpha_plateaus

    def get_U_compatible(self):

        self.all_U_compatible = {}
        for plateau in self.alpha_plateaus:
            plateau_U = {}
            for state in plateau.states:
                plateau_U[state] = find_safe_steps(state)

            self.all_U_compatible[plateau] = plateau_U

        return self.all_U_compatible

    def get_viable_compatible(self):
        self.viable_compatible = {}

        for plateau in self.alpha_plateaus:
            self.viable_compatible[plateau] = plateau_viable_compatible(plateau, self.all_U_compatible[plateau])

        return self.viable_compatible

    def get_alpha_exits(self):
        self.alpha_exits = find_alpha_exit(self.game, self.safe_steps)
        return self.alpha_exits

    def get_admissible(self):
        self.admissible_plans = {}

        for plateau in self.alpha_plateaus:
            self.admissible_plans[plateau] = plateau_admissible(self.viable_compatible[plateau])

        return self.admissible_plans

    def get_beta(self):
        self.beta = {}

        for plateau in self.admissible_plans:
            self.beta[plateau] = plateau_beta(self.admissible_plans[plateau])

        return self.beta

    def get_gamma(self):
        self.gamma = find_gamma(self.beta)
        return self.gamma

    def update_delta(self):
        self.converged = self.gamma['Converged']
        if not self.converged:
            admiss_plan = self.gamma['Plan']
            for state in self.gamma['U']:
                state.update_alpha(admiss_plan.state_payoff)

        return self.converged

    def get_safe_steps(self):
        self.safe_steps = {state: find_safe_steps(state) for state in self.game}
        return self.safe_steps


def find_gamma(beta):
    gamma_candidates = {}

    for plateau in beta:
        for beta_plat in beta[plateau]:
            for u_map in beta_plat:
                if beta_plat[u_map].state_payoff > plateau.alpha:
                    gamma_candidates[u_map] = beta_plat[u_map]

    return gamma_candidates


def plateau_beta(admissible_plans):
    beta_plateau = []

    for admiss_t in admissible_plans:
        beta_t = {}
        for u_map in admiss_t:
            beta_t[u_map] = min(admiss_t[u_map], key=lambda x: x.state_payoff)
        beta_plateau.append(beta_t)

    return beta_plateau


def find_alpha_plateaus(game_dict):
    alpha_map = {}

    for state in game_dict:
        states = alpha_map.get(f'{state.player}{state.alpha}', [])
        states.append(state)
        alpha_map[f'{state.player}{state.alpha}'] = states

    all_plateaus = []

    for key in alpha_map:
        if alpha_map[key]:
            all_plateaus.append(AlphaPlateau(alpha_map[key]))

    return all_plateaus


def plateau_combinations(states):
    state_combinations = []

    for n in range(1, len(states) + 1):
        for comb in combinations(states, n):
            state_combinations.append(list(comb))

    return state_combinations


def find_safe_steps(state_t: State):
    safe = []

    if state_t.get_payoff(state_t) >= state_t.alpha:
        safe.append(state_t.terminal_state)

    for state_u in state_t.neighbours:
        viable_u = state_u.viable

        if all(alpha_sat(plan, [state_t]) for plan in viable_u):
            safe.append(state_u)

    return safe


def viable(state_t: State):
    viable_plans = []

    for plan in state_t.plans:
        if alpha_sat(plan):
            viable_plans.append(plan)

    return viable_plans


def plateau_admissible(viacomp_plateau):
    plat_admissible = []

    for viacomp_t in viacomp_plateau:
        state_admissible = {}
        for plateau_u in viacomp_t:
            state_admissible[plateau_u] = get_admissible_t(viacomp_t[plateau_u], plateau_u)
        plat_admissible.append(state_admissible)

    return plat_admissible


def get_admissible_t(viacomp_list, plateau_u):
    admissible_plans = []

    for viacomp_t in viacomp_list:
        is_admissible, threat_pair = check_admissible(viacomp_t, plateau_u)

        if is_admissible:
            admissible_plans.append(Admissible(viacomp_t, threat_pair))

    return admissible_plans


def check_admissible(viacomp, plateau_u):
    state_t = viacomp.state
    plan_g = viacomp.plan

    # AD-i
    if state_t.alpha > 0:
        return True, None

    # AD-ii
    if not plan_g.is_absorbing():
        return True, None

    visited_dict = {state: False for state in plateau_u.u_map}
    appeared_once = True

    for state_u in plan_g:

        if visited_dict.get(state_u) is not None:
            if visited_dict[state_u]:
                appeared_once = False

            visited_dict[state_u] = True

        # AD-i: Different payoffs so state_t != state_u
        if appeared_once and state_t.same_player(state_u) and state_u.get_payoff() > state_t.get_payoff():
            return True, None

        # AD-iv (b)
        if not state_t.same_player(state_u) and appeared_once:
            is_threat, threat_pair = is_threat_pair(state_t, state_u, plan_g)
            if is_threat:
                return True, threat_pair

    return appeared_once, None


def is_threat_pair(state_t, state_x: State, plan_g):
    # (c)
    for state_v in state_x.get_actions():
        # (d)
        if first_action(plan_g, state_x) == state_v:
            continue
        # (e)
        for plan_v in state_v.get_viable():
            if not alpha_sat(plan_v, [state_x]) and not alpha_sat(plan_v, [state_t]):
                return True, ThreatPair(state_t, state_x, plan_v)

    return False, None


def first_action(plan_g, state_t):
    first_index_t = first_occurrence_index(plan_g, state_t)
    if first_index_t + 1 == len(plan_g):
        return state_t
    return plan_g[first_index_t + 1]


def first_occurrence_index(plan_g, state_t):
    return next((index for index, state in enumerate(plan_g) if state == state_t),
                Exception(f'{state_t} not in plan plan'))


def plateau_viable_compatible(plateau, U_compatible):
    plateau_viacomp = []
    for state in plateau.states:
        plateau_viacomp.append(viabel_compatible(state, plateau, U_compatible))

    return plateau_viacomp


def viabel_compatible(state_t, plateau, U_compatible):
    viacomp_u = {}

    for plan_g in state_t.viable:

        is_viable_compatible = True
        u_t = {}

        for state_u in plateau.states:
            if state_u not in plan_g:
                continue

            # first_action_index = first_occurrence_index(plan_g, state_u) + 1
            action_u = first_action(plan_g, state_u)

            if action_u in U_compatible[state_u]:
                u_t[state_u] = action_u
                continue

            is_viable_compatible = False
            break

        if is_viable_compatible:
            u_map = PlateauU(u_t)
            viabel_plans = viacomp_u.get(u_map, [])
            viabel_plans.append(Viacomp(state_t, plan_g))
            viacomp_u[u_map] = viabel_plans

    return viacomp_u


def get_all_states(game_dict):
    all_states = set()

    for state in game_dict:
        all_states.update({state, state.terminal_state})

    return all_states
