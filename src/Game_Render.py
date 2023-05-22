import graphviz


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
        graph.node(name, label=tuple(payoffs).__str__(), shape='plaintext')
        graph.edge(parent, name)

    def render_graph(self):
        self.graph.render(directory='graph-renders', view=True, format='png')