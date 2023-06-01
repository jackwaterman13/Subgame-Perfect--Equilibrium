from Game_Generator import *

display_on = False


def equilibrium():
    game = alpha_exit_game()

    converged = False

    print('Alpha initialisation')
    for state in game:
        print(f'{state} alpha = {state.alpha}')

    iteration_num = 1
    while not converged:
        update_dict = iteration(game)

        if not update_dict:
            break

        print(f'\nIteration {iteration_num}')

        for state in update_dict:
            state.update_alpha(update_dict[state])

        for state in game:
            print(f'{state} alpha = {state.alpha}')

        iteration_num += 1


def iteration(game):
    for state in game:
        state.update_viable(viable(state))

    alpha_plateaus = find_alpha_plateaus(game)

    display_pause(alpha_plateaus, 'Alpha plateaus')

    viable_compatible = {}
    admissible_plans = {}
    U_comp_all = {}

    # key is string with 'player,alpha'
    for key in alpha_plateaus:
        U_comp = alpha_safe_combination(alpha_plateaus[key])

        for state in alpha_plateaus[key]:
            viable_compatible[state] = find_viable_compatible(state, U_comp)

        for state in viable_compatible:
            admissible_plans[state] = find_admissible(viable_compatible, state, U_comp)

        U_comp_all.update(U_comp)

    display_pause(U_comp_all, 'U(t)')
    display_pause(viable_compatible, f'viacomp()')
    display_pause(admissible_plans, f'admiss()')

    beta_dict = {}
    for state in game:
        beta_dict[state] = beta(admissible_plans, state)

    gamma_dict = gamma(beta_dict, alpha_plateaus)

    return update_vector(gamma_dict)


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


def beta(admissible_plans, state_t):
    alpha_increase_plans = []
    for plan in admissible_plans[state_t]:
        if plan.get_payoff(state_t) > state_t.alpha:
            alpha_increase_plans.append(plan)

    if not alpha_increase_plans:
        return min(admissible_plans[state_t], key=lambda x: x.get_payoff(state_t))
    return min(alpha_increase_plans, key=lambda x: x.get_payoff(state_t))


def plan_payoff(plan, state_t=None):
    if state_t is None:
        return plan[-1].get_payoff()
    return plan[-1].get_payoff(state_t)


def find_alpha_plateaus(game):
    alpha_map = {f'F({state.player + 1}, {state.alpha})': [] for state in game}

    for state in game:
        alpha_map[f'F({state.player + 1}, {state.alpha})'].append(state)

    return alpha_map


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


def find_admissible(via_comp, state_t, U_comp):
    admissible_plans = []

    for plan in via_comp[state_t]:
        if admissible(plan, state_t, U_comp):
            admissible_plans.append(plan)

    return admissible_plans


def admissible(plan_g, state_t: State, U_comp):

    # AD-i:
    if state_t.alpha > 0:
        return True

    # AD-ii
    if not plan_g.is_absorbing():
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
    return appeared_once_U


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


def find_viable_compatible(state_t, U_compatible):
    viable_compatible_plans = []

    for plan_g in state_t.viable:
        is_viable_compatible = True

        for state_u in U_compatible:

            if state_u not in plan_g:
                continue

            first_action_index = first_occurrence_index(plan_g, state_u) + 1

            if plan_g[first_action_index] in U_compatible[state_u] or first_action_index == len(plan_g):
                continue

            is_viable_compatible = False
            break

        if is_viable_compatible:
            viable_compatible_plans.append(plan_g)

    return viable_compatible_plans


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


equilibrium()
