from Game_Generator import *
from itertools import combinations, product
from collections import namedtuple

display_on = True


class Alpha_Plateau:
    def __init__(self, states, player, alpha):
        self.states = states
        self.player = player
        self.alpha = alpha
        self.plateau_id = f'({alpha}, {self.player})'

    def __hash__(self):
        return hash(self.plateau_id)

    def __str__(self):
        return self.plateau_id

    def __repr__(self):
        return self.plateau_id


class Game:
    def __init__(self, game_id, num_player=3, num_states=5):
        self.game = create_game(num_player, num_states)
        render_game(self.game, game_id)

        self.alpha_plateaus = None
        self.all_U_compatible = {}
        self.viable_compatible = None

    def get_alpha_dict(self):
        return {state: state.alpha for state in self.game}

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

    def get_admissible(self):
        self.admissible_plans = {}

        for plateau in self.alpha_plateaus:
            self.admissible_plans[plateau] = plateau_admissible(self.viable_compatible[key], self.alpha_plateaus[key])

        return self.admissible_plans

    def get_beta(self):
        beta_plans = {}
        for key in self.admissible_plans:
            beta_plans[key] = get_plateau_beta(self.admissible_plans[key])

        return beta_plans


#
# def equilibrium():
#     game = create_game(3, 5)
#
#     converged = False
#
#     print('Alpha initialisation')
#     for state in game:
#         print(f'{state} alpha = {state.alpha}')
#
#     iteration_num = 1
#     while not converged:
#         update_dict = iteration(game)
#
#         if not update_dict:
#             break
#
#         print(f'\nIteration {iteration_num}')
#
#         for state in update_dict:
#             state.update_alpha(update_dict[state])
#
#         for state in game:
#             print(f'{state} alpha = {state.alpha}')
#
#         iteration_num += 1


# def iteration():
#     for state in game:
#         state.update_viable(viable(state))
#
#     alpha_plateaus = find_alpha_plateaus(game)
#
#     display_pause(alpha_plateaus, 'Alpha plateaus')
#
#     viable_compatible = {}
#     admissible_plans = {}
#     U_comp_all = {}
#
#     # key is string with 'player,alpha'
#     for key in alpha_plateaus:
#         U_comp = alpha_safe_combination(alpha_plateaus[key])
#
#         for state in alpha_plateaus[key]:
#             viable_compatible[state] = plateau_viable_compatible(state, U_comp)
#
#         for state in viable_compatible:
#             admissible_plans[state] = plateau_admissible(viable_compatible, state, U_comp)
#
#         U_comp_all.update(U_comp)
#
#     display_pause(U_comp_all, 'U(t)')
#     display_pause(viable_compatible, f'viacomp()')
#     display_pause(admissible_plans, f'admiss()')
#
#     beta_dict = {}
#
#     # TODO: Make sure this takes the whole plateau
#     for state in game:
#         beta_dict[state] = beta(admissible_plans, state)
#
#     gamma_dict = gamma(beta_dict, alpha_plateaus)
#
#     return update_vector(gamma_dict)


def update_vector(gamma_dict):
    update_dict = {}

    for key in gamma_dict:
        alpha = gamma_dict[key][0]
        state = gamma_dict[key][1]

        if alpha > state.alpha:
            update_dict[state] = alpha

    return update_dict


def gamma(beta_dict, alpha_plateau):
    gamma_dict = {}
    for key in alpha_plateau:

        min_beta = float('inf'), None
        for state in alpha_plateau[key]:
            min_beta = min(min_beta[0], beta_dict[state].get_payoff(state)), state

        gamma_dict[key] = min_beta

    return gamma_dict


def get_plateau_beta(admissible_plans):
    plateau_beta = []

    for plateau in admissible_plans:
        plateau_payoffs = {}
        for state in plateau:
            plateau_payoffs[state] = beta(state, plateau)
        plateau_beta.append(plateau_payoffs)

    return plateau_beta


def beta(state_t, admissible_plans):
    plan_payoffs = {plan.get_payoff(state_t): [] for plan in admissible_plans[state_t]}

    for plan in admissible_plans[state_t]:
        plan_payoffs[plan.get_payoff(state_t)].append(plan)

    return plan_payoffs

    # for plan in admissible_plans[state_t]:
    #     if plan.get_payoff(state_t) > state_t.alpha:
    #         alpha_increase_plans.append(plan)
    #
    # if not alpha_increase_plans:
    #     return min(admissible_plans[state_t], key=lambda x: x.get_payoff(state_t))
    # return min(alpha_increase_plans, key=lambda x: x.get_payoff(state_t))


def find_alpha_plateaus(game):
    alpha_map = {}

    for state in game:
        states = alpha_map.get(f'{state.player}{state.alpha}', [])
        states.append(state)
        alpha_map[f'{state.player}{state.alpha}'] = states

    all_plateaus = []
    alpha_plateau = []

    for key in alpha_map:
        for plateau in plateau_combinations(alpha_map[key]):
            alpha_plateau = Alpha_Plateau(plateau, plateau[0].player, plateau[0].alpha)
        all_plateaus.append(alpha_plateau)

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


def alpha_sat(plan, check_states=None):
    if check_states is None:
        check_states = plan.get_state_set()

    if isinstance(check_states, State):
        check_states = [check_states]

    sat = True

    for state in check_states:
        if plan.get_payoff(state) < state.alpha:
            sat = False

    return sat


def viable(state_t: State):
    viable_plans = []

    for plan in state_t.plans:
        if alpha_sat(plan):
            viable_plans.append(plan)

    return viable_plans


def plateau_admissible(viacomp, alpha_plateaus):
    admissible_plans = []

    for plateau in alpha_plateaus:
        admissible_dict = {}
        for state in plateau:
            plateau_viacomp = match_plateau_viacomp(plateau, viacomp)
            admissible_dict[state] = get_admissible(state, plateau, plateau_viacomp)
        admissible_plans.append(admissible_dict)

    return admissible_plans


def match_plateau_viacomp(plateau, viacomp):
    for viacomp_plateau in viacomp:
        if set(plateau) == viacomp_plateau.keys():
            return viacomp_plateau

    raise Exception(f"No matching viacomp for plateau{plateau}")


def get_admissible(state, plateau, viacomp):
    admissible_plans = []

    for plan in viacomp[state]:
        if is_admissible(plan, state, plateau):
            admissible_plans.append(plan)

    return admissible_plans


def is_admissible(plan_g: Plan, state_t: State, plateau):
    # AD-i
    if state_t.alpha > 0:
        return True

    # AD-ii
    if not plan_g.is_absorbing():
        return True

    visited_dict = {state_u: False for state_u in plateau}
    appeared_once = True

    for state_u in plan_g:

        if visited_dict.get(state_u) is not None:
            if visited_dict[state_u]:
                appeared_once = False

            visited_dict[state_u] = True

        # AD-i: Different payoffs so state_t != state_u
        if appeared_once and state_t.same_player(state_u) and state_u.get_payoff() > state_t.get_payoff():
            return True

        # AD-iv (b)
        if not state_t.same_player(state_u) and appeared_once:
            if is_threat_pair(state_t, state_u, plan_g):
                return True

    return appeared_once


def is_threat_pair(state_t, state_x: State, plan_g):
    # (c)
    for state_v in state_x.neighbours:
        # (d)
        if plan_g[first_occurrence_index(plan_g, state_x) + 1] == state_v:
            continue
        # (e)
        for plan_v in state_v.viable:
            if not alpha_sat(plan_v, [state_x]) and not alpha_sat(plan_v, [state_t]):
                print(f'\n{plan_g}')
                print(f'{state_t} alpha = {state_t.alpha}')
                print(f'{state_x} alpha = {state_x.alpha}')
                print(f'{state_t} Treat pair ({state_x}, {plan_v})')
                return True

    return False


def first_occurrence_index(plan_g, state_t):
    return next((index for index, state in enumerate(plan_g) if state == state_t),
                Exception(f'{state_t} not in plan plan'))


class Viacomp:
    def __init__(self, state, plan, U_map):
        self.state = state
        self.plan = plan
        self.U_map = U_map


def plateau_viable_compatible(plateau, U_compatible):
    plateau_viacomp = []
    for state in plateau.states:
        plateau_viacomp.append(viabel_compatible(state, plateau, U_compatible))

    return plateau_viacomp


def viabel_compatible(state_t, plateau, U_compatible):
    state_viacomp = []

    for plan_g in state_t.viable:

        is_viable_compatible = True
        U_map = {}
        for state_u in plateau.states:
            if state_u not in plan_g:
                continue

            first_action_index = first_occurrence_index(plan_g, state_u) + 1

            if plan_g[first_action_index] in U_compatible[state_u]:
                U_map[state_u] = plan_g[first_action_index]
                continue

            is_viable_compatible = False
            break

        if is_viable_compatible:
            state_viacomp.append(Viacomp(state_t, plan_g, U_map))

    return state_viacomp


def alpha_safe_combination(alpha_plateau):
    return {state: find_safe_steps(state) for state in alpha_plateau}


def display_pause(print_item, title=None):
    if not display_on:
        return

    if title is not None:
        print(title)

    if isinstance(print_item, list):
        for item in print_item:
            print(item)
        input("Press Enter to continue...")
        return

    if isinstance(print_item, dict):
        for item in print_item:
            print(f'{item}: {print_item[item]}')
        input("Press Enter to continue...")
        return

    print(print_item)
    input("Press Enter to continue...")


if __name__ == "__main__":
    equilibrium()

# class U_Compatible:
#     def __init__(self, alpha_plateau, plateau_U):
#         self.alpha_plateau = alpha_plateau
#         self.U_combinations = [list(comb) for comb in list(product(*plateau_U))]
#         self.id = f'({alpha_plateau}, {self.U_combinations}'
#
#     def __str__(self):
#         return self.id
#
#     def __repr__(self):
#         return self.id
