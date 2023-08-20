from game_data.alpha_exit import AlphaExitFinder
from game_data.game_graph import GameGraph
from game_data.iteration_solver import IterationSolver
from game_data.iteration_utils.threat_pair import ThreatPair
from game_data.solver_utils.game_tree import GameTree, GameNode


class GameSolver:
    def __init__(self):

        self.iteration_solver = None
        self.game_tree = None
        self.game_graph = None
        self.alpha_exit_finder = None

    def solve(self, game_graph):
        self.game_graph = game_graph
        self.alpha_exit_finder = AlphaExitFinder(game_graph)

        self.game_tree = GameTree(self.game_graph)
        self.iteration_solver = IterationSolver(self.game_graph)

        self.build_solution(self.game_graph.alpha, self.game_tree.root, 0)
        return self.game_tree.find_equilibria()

    def build_solution(self, alpha, parent, itr_num):
        admissible_plans, safe_steps, viable_plans = self.iteration_solver.perform_iteration(alpha, itr_num)

        beta = beta_plans(admissible_plans)
        gamma = gamma_plans(beta, alpha)
        final_itr = False

        if not gamma:
            final_itr = True

        next_alpha = alpha.copy()
        itr_num += 1

        for u_key in gamma:

            gamma_u = gamma[u_key]
            next_alpha = alpha.copy()
            exit_critical = False

            for state in gamma_u[0].u_map:
                next_alpha[state] = gamma_u[0].state_payoff

            for admiss in gamma_u:
                condition = admiss.condition
                if isinstance(condition, ThreatPair):
                    # all_exits = self.alpha_exit_finder.find_ex_sq(alpha, condition, safe_steps, viable_plans)
                    exit_critical = True

            child = GameNode(alpha, next_alpha, admissible_plans, safe_steps, gamma_u, exit_critical)
            parent.add_child(child)
            self.build_solution(next_alpha, child, itr_num)

        if final_itr:
            child = GameNode(alpha, next_alpha, admissible_plans, safe_steps, final_itr=True)
            parent.add_child(child)


def beta_plans(admissible_plans):
    beta = {}

    for subset in admissible_plans:
        admiss_u = admissible_plans[subset]
        for u_map in admiss_u:
            min_payoff = min(admiss_u[u_map], key=lambda x: x.state_payoff).state_payoff
            for plan in admiss_u[u_map]:
                if plan.state_payoff == min_payoff:
                    if beta.get(u_map) is None:
                        beta[u_map] = [plan]
                    else:
                        beta[u_map].append(plan)

    return beta


def gamma_plans(beta, alpha):
    gamma = {}

    for u_map in beta:
        admiss = beta[u_map]
        for plan in admiss:
            if plan.state_payoff > alpha[plan.state]:
                if gamma.get(u_map) is None:
                    gamma[u_map] = [plan]
                else:
                    gamma[u_map].append(plan)

    return gamma


def is_exit_critical(threat_pair, all_exits):

    is_critical = False
    for subset_x in all_exits:

        exits = all_exits[subset_x]['exits']

        for state_x in exits:
            for state_y in exits[state_x]:
                if (state_x, state_y) == threat_pair.edge:
                    threat_pair.exit_sets.append(subset_x)
                    is_critical = True
                    break

            if is_critical:
                break

        sequences = all_exits[subset_x]['sequences']

        for sequence in sequences:
            if sequence.edge == threat_pair.edge:
                threat_pair.sequences.append(sequence)
                is_critical = True

    return is_critical
