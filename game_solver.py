from game_data.game_graph import GameGraph
from game_data.iteration_solver import IterationSolver
from collections import namedtuple

from game_data.iteration_utils.gamma import Gamma
from game_data.solver_utils.game_tree import GameNode


class GameSolver:
    def __init__(self):
        self.game_graph = GameGraph('Testing')
        self.iteration_solver = IterationSolver(self.game_graph)
        self.game_path = [[]]
        self.perform_iteration(self.game_graph.alpha)
        print()

    def perform_iteration(self, alpha):
        admissible_plans, safe_steps = self.iteration_solver.perform_iteration(alpha)
        beta = beta_plans(admissible_plans)
        gamma = gamma_plans(beta, alpha)

        for key in gamma:
            gamma_u = gamma[key]
            next_alpha = alpha.copy()
            # TODO: Update the full plateau
            for state in gamma_u.u_map:
                next_alpha[state] = gamma_u.state_payoff
            self.game_path[0].append(
                GameNode(self.game_graph, alpha, next_alpha, admissible_plans, safe_steps, gamma_u))
            return self.perform_iteration(next_alpha)


def beta_plans(admissible_plans):
    beta = {}

    for subset in admissible_plans:
        admiss_u = admissible_plans[subset]
        beta_u = {}
        for u_map in admiss_u:
            beta_u[u_map] = min(admiss_u[u_map], key=lambda x: x.state_payoff)

        beta[subset] = beta_u

    return beta


def gamma_plans(beta, alpha):
    gamma = {}

    for subset in beta:
        beta_u = beta[subset]
        for u_map in beta_u:
            admiss = beta_u[u_map]
            if admiss.state_payoff > alpha[admiss.state]:
                gamma[u_map] = admiss

    return gamma


GameSolver()
