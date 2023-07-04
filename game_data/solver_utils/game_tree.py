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

    def __init__(self, game_graph, start_alpha, end_alpha, admissible_plans, safe_steps, gamma_u):
        self.game_graph = game_graph
        self.start_alpha = start_alpha
        self.end_alpha = end_alpha
        self.admissible_plans = admissible_plans
        self.safe_steps = safe_steps
        self.gamma_u = gamma_u
        self.children = []

    def __str__(self):
        return str(self.alpha)

    def __repr__(self):
        return str(self.alpha)

    def add_child(self, child):
        self.children.append(child)