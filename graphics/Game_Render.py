import graphviz


def render_game(game_dict: dict, alpha, name=None):
    if name is None:
        name = 'game'

    graph = graphviz.Digraph(name, engine='circo')

    for state in game_dict:
        # Neighbours
        for neighbour in game_dict[state]:
            graph.edge(state_name(state, alpha), state_name(neighbour, alpha))

        # Terminal state render
        graph.node(state.terminal_state.state_id, label=str(tuple(state.payoffs)), shape='plaintext')
        graph.edge(state_name(state, alpha), state.terminal_state.state_id)

    graph.render(directory='graph-renders', view=False, format='png')

    return f'./graph-renders/{name}.gv.png'


def render_safe_steps(game_dict: dict, alpha, safe_steps, name=None):
    if name is None:
        name = 'game'

    graph = graphviz.Digraph(name, engine='circo')

    for state in game_dict:
        # Neighbours
        for neighbour in game_dict[state]:
            if neighbour in safe_steps[state]:
                graph.edge(state_name(state, alpha), state_name(neighbour, alpha), color='red')
                continue

            graph.edge(state_name(state, alpha), state_name(neighbour, alpha), style='dashed')

        # Terminal state render
        graph.node(state.terminal_state.state_id, label=str(tuple(state.payoffs)), shape='plaintext')

        if state.terminal_state in safe_steps[state]:
            graph.edge(state_name(state, alpha), state.terminal_state.state_id, color='red')
            continue

        graph.edge(state_name(state, alpha), state.terminal_state.state_id, style='dashed')

    graph.render(directory='graph-renders', view=False, format='png')

    return f'./graph-renders/{name}.gv.png'


def state_name(state, alpha):
    return f'{state.state_id},\n\u03B1={alpha[state]}'
