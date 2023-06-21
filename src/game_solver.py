from equilibrium import *
from game_data.game_generator import *


def clean_paths(paths):
    if len(paths) == 0:
        return []
    alphas = [paths[0][-1].alpha_vector]
    clean = [paths[0]]

    for path in paths[1:]:
        next_alpha = path[-1].alpha_vector
        if check_alpha(alphas, next_alpha):
            clean.append(path)
            alphas.append(next_alpha)

    return clean


def check_alpha(alphas, check):
    for alpha in alphas:
        if list(alpha.values()) == list(check.values()):
            return False

    return True


class GameTree:
    def __init__(self, root):
        self.root = root

    def find_unique_paths(self):
        paths = []
        current_path = []

        def dfs(current_node):
            current_path.append(current_node)

            if len(current_node.children) == 0:
                paths.append(list(current_path))
            else:
                for child in current_node.children:
                    dfs(child)

            current_path.pop()

        for node in self.root.children:
            dfs(node)

        paths = clean_paths(paths)

        return paths


class RootNode:
    def __init__(self):
        self.children = []

    def add_child(self, child):
        self.children.append(child)


class GameNode:

    def __init__(self, game_start, game_end, itr_num, plateau_u=None, itr_data=None):
        self.game_start = game_start
        self.game_end = game_end

        self.itr_num = itr_num
        self.converged = False
        self.plateau_u = plateau_u
        self.itr_data = itr_data
        self.children = []

        self.alpha_vector = {state: state.alpha for state in self.game_end}
        print(self.alpha_vector)

        if plateau_u is None:
            self.converged = True

    def __str__(self):
        return str(self.alpha_vector)

    def __repr__(self):
        return str(self.alpha_vector)

    def add_child(self, child):
        self.children.append(child)


class Game_Solver:
    def __init__(self):
        self.name = 'new_test'
        # self.game = create_cycle_game(3, 4)
        self.game = fig_4_game()
        self.game_tree = GameTree(RootNode())

        iteration(self.name, self.game, 0, self.game_tree.root)

        print('fini')

    def get_game_paths(self):
        game_paths = self.game_tree.find_unique_paths()

        # while len(game_paths) < 2:
        #     self.game = create_cycle_game(3, 4)
        #     self.game_tree = GameTree(RootNode())
        #     iteration(self.name, self.game, 0, self.game_tree.root)
        #     game_paths = self.game_tree.find_unique_paths()

        return game_paths


def iteration(name, start_itr_game, itr_num, parent_node):
    itr_solver = IterationSolver(start_itr_game, name)
    itr_data = itr_solver.perform_iteration()

    if not itr_data.gamma:
        return

    for plateau_u in itr_data.gamma:
        end_itr_game = copy_game(start_itr_game)
        update_game(plateau_u, end_itr_game, itr_data)

        child_node = GameNode(start_itr_game, end_itr_game, itr_num, plateau_u, itr_data)
        parent_node.add_child(child_node)

        iteration(name, end_itr_game, itr_num + 1, child_node)


def copy_game(game):
    game_copy = {state.copy_state(): [] for state in game}

    for state_o, state_n in zip(game, game_copy):
        new_neighbours = []
        for neighbour_o in game[state_o]:
            for neighbour_n in game_copy:
                if neighbour_o == neighbour_n:
                    new_neighbours.append(neighbour_n)

        game_copy[state_n] = new_neighbours
        state_n.add_neighbours(new_neighbours)

    for state in game_copy:
        state.update_plans(game_copy)

    return game_copy


def update_game(plateau_u, game_map, itr_data):
    gamma = itr_data.gamma
    u_map = plateau_u.u_map
    for state_u in u_map:
        for state_t in game_map:
            if state_u == state_t:
                state_t.update_alpha(gamma[plateau_u].state_payoff)
                break


solver = Game_Solver()
