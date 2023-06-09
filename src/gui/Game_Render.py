import graphviz


def render_game(game_dict: dict, name=None):

    if name is None:
        name = 'game'

    graph = graphviz.Digraph(name, engine='circo')

    for state in game_dict:
        # Neighbours
        for neighbour in game_dict[state]:
            graph.edge(state.id, neighbour.id)

        # Terminal state render
        graph.node(state.terminal_state.id, label=str(tuple(state.payoffs)), shape='plaintext')
        graph.edge(state.id, state.terminal_state.id)

    graph.render(directory='graph-renders', view=False, format='png')


def render_safe_steps(game_dict: dict, U_comp, name=None):

    if name is None:
        name = 'game'

    safe_steps = {}
    for plateau in U_comp:
        for state in U_comp[plateau]:
            safe_steps[state] = U_comp[plateau][state]

    graph = graphviz.Digraph(name, engine='circo')

    for state in game_dict:
        # Neighbours
        for neighbour in game_dict[state]:
            if neighbour in safe_steps[state]:
                graph.edge(state.id, neighbour.id)
                continue

            graph.edge(state.id, neighbour.id, style='dashed')

        # Terminal state render
        graph.node(state.terminal_state.id, label=str(tuple(state.payoffs)), shape='plaintext')

        if state.terminal_state in safe_steps[state]:
            graph.edge(state.id, state.terminal_state.id)
            continue

        graph.edge(state.id, state.terminal_state.id, style='dashed')

    graph.render(directory='graph-renders', view=False, format='png')

