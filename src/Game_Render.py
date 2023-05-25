import graphviz


def render_game(game_dict: dict):
    graph = graphviz.Digraph('game', engine='circo')

    for state in game_dict:
        # Neighbours
        for neighbour in game_dict[state]:
            graph.edge(state.id, neighbour.id)

        # Terminal state render
        graph.node(state.terminal_state.id, label=str(tuple(state.payoffs)), shape='plaintext')
        graph.edge(state.id, state.terminal_state.id)

    graph.render(directory='graph-renders', view=True, format='png')


class Game_Render:
    def __init__(self):
        self.graph = graphviz.Digraph('game', engine='circo')
        self.test_game()
        self.render_graph()

    def test_game(self):
        graph = self.graph

        graph.edge('2', '1b')
        graph.edge('1b', '1a')
        graph.edge('1b', '3')
        graph.edge('3', '1a')
        graph.edge('1a', '2')

        self.graph_payoff_edge('1a', [-2, 0, 1])
        self.graph_payoff_edge('2', [-3, 1, 0])
        self.graph_payoff_edge('1b', [-1, 2, -2])
        self.graph_payoff_edge('3', [2, 2, -1])

    def graph_payoff_edge(self, parent: str, payoffs: list):
        graph = self.graph

        name = f'{parent}p'
        graph.node(name, label=str(tuple(payoffs)), shape='plaintext')
        graph.edge(parent, name)

    def render_graph(self):
        self.graph.render(directory='graph-renders', view=True, format='png')
