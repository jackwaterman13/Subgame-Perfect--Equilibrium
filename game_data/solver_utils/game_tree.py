class GameTree:
    def __init__(self, game_graph):
        self.game_graph = game_graph
        self.root = RootNode()

    def find_equilibria(self):
        all_paths = []

        for node in self.root.children:
            self.find_tree_paths(node, [node], all_paths)  # start path with the node itself

        all_paths = sorted(all_paths, key=len)
        exit_found = False
        selected_paths = []
        final_alphas = []

        for path in all_paths:

            alpha = path[-1].end_alpha
            exit_critical = False
            unique_alpha = False

            for node in path:
                if node.exit_critical:
                    exit_critical = True
                    exit_found = True
                    break

            if alpha not in final_alphas:
                final_alphas.append(alpha)
                unique_alpha = True

            if unique_alpha or exit_critical:
                selected_paths.append(Equilibrium(path, exit_critical=exit_critical))

        return Equilibria(selected_paths, exit_found, len(final_alphas))

    def find_tree_paths(self, node, path, all_paths):

        if not node.children:  # if node has no children, it's a leaf
            all_paths.append(path)
            return

        for child in node.children:
            self.find_tree_paths(child, path + [child], all_paths)


class RootNode:
    def __init__(self):
        self.children = []

    def add_child(self, child):
        self.children.append(child)


class GameNode:

    def __init__(self, start_alpha, end_alpha, admissible_plans, safe_steps,
                 gamma_u=None, exit_critical=None, final_itr=False):
        self.start_alpha = start_alpha
        self.end_alpha = end_alpha
        self.admissible_plans = admissible_plans
        self.safe_steps = safe_steps
        self.gamma_u = gamma_u
        self.children = []
        self.exit_critical = exit_critical
        self.final_itr = final_itr

    def __str__(self):
        return str(self.end_alpha)

    def __repr__(self):
        return str(self.end_alpha)

    def add_child(self, child):
        self.children.append(child)


class Equilibrium:
    def __init__(self, iterations, exit_critical=False):
        self.iterations = iterations
        self.exit_critical = exit_critical

    def __getitem__(self, item):
        return self.iterations[item]

    def __len__(self):
        return len(self.iterations)


class Equilibria:
    def __init__(self, paths, exit_found, equilibria_count):
        self.paths = paths
        self.exit_found = exit_found
        self.equilibria_count = equilibria_count
        self.multi_equilibria = True if equilibria_count > 1 else False
        self.max_iterations = len(max(paths, key=len, ))

    def __getitem__(self, item):
        return self.paths[item]
