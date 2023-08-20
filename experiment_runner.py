import itertools
import time

import pandas as pd

from game_data.game_graph import GameGraph
from game_solver import GameSolver
from pdf_output.pdf_builder import create_pdf


class Experiments:
    def __init__(self):
        self.game_graph = GameGraph()
        self.game_solver = GameSolver()

        self.block_results = None
        self.max_iterations = 0

        self.start_time = time.time()
        self.test_payoff()
        end_time = time.time()

        # elapsed_time = end_time - start_time
        # print(f"The function took {elapsed_time/gen} seconds to complete")

    def all_payoffs(self):
        payoff_gen = itertools.product(range(-2, 3), repeat=12)
        payoffs = get_next_block(payoff_gen, 1000)

        block_num = 0
        game_num = 0
        self.block_results = []

        while payoffs:
            for payoff in payoffs:
                self.game_graph.update_payoffs(payoff)
                equilibria = self.game_solver.solve(self.game_graph)
                self.check_equilibria(equilibria, payoff)
                game_num += 1

            self.save_block_results()
            payoffs = get_next_block(payoff_gen, 1000)
            print(f'Time for black number {block_num} = {time.time() - self.start_time}')
            block_num += 1
            self.block_results = []

    def test_payoff(self):
        # # 6 itr
        # # payoff = (-2, -1, 0, -2, -2, -1, -1, -1, 1, 1, -2, -2)
        # payoff = (-2, -1, 0, -2, -2, 0, -1, -1, -1, 1, -2, -2)

        # 3 eq
        # payoff = (-2, -2, 1, 2, 0, 2, 1, 2, 0, 2, 2, -1)

        # Threat pair but no X(alpha)
        payoff = (-2, -2, -2, -2, -2, -2, -1, -2, -2, 0, -2, -1)
        # # payoff = (-2, -2, -2, -2, -2, -2, 1, -1, -2, 2, 0, -1)

        self.game_graph.update_payoffs((-2, -2, -2, -2, -2, -2, 0, 2, -2, 2, 1, 2))
        equilibria = self.game_solver.solve(self.game_graph)

        create_pdf(equilibria, self.game_graph)

    def check_equilibria(self, equilibria, payoff):
        if equilibria.exit_found or equilibria.multi_equilibria:
            result = [payoff, equilibria.equilibria_count, equilibria.max_iterations, equilibria.exit_found]
            self.block_results.append(result)
            return

        if equilibria.max_iterations > self.max_iterations:
            result = [payoff, equilibria.equilibria_count, equilibria.max_iterations, equilibria.exit_found]
            self.block_results.append(result)
            self.max_iterations = equilibria.max_iterations

    def save_block_results(self, output_file='Threat_Pair_Games.csv'):
        df = pd.DataFrame(self.block_results, columns=['payoff', 'num_equilibria', 'max_itr', 'Alpha Critical'])
        df.to_csv(output_file, mode='a', header=False, index=False)


def get_next_block(gen, block_size=10_000_000):
    return list(itertools.islice(gen, block_size))





Experiments()
