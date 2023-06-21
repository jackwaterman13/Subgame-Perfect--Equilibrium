import graphviz


def render_game(game_dict: dict, name=None):
    if name is None:
        name = 'game'

    graph = graphviz.Digraph(name, engine='circo')

    for state in game_dict:
        # Neighbours
        for neighbour in game_dict[state]:
            graph.edge(state_name(state), state_name(neighbour))

        # Terminal state render
        graph.node(state.terminal_state.id, label=str(tuple(state.payoffs)), shape='plaintext')
        graph.edge(state_name(state), state.terminal_state.id)

    graph.render(directory='graph-renders', view=False, format='png')

    return f'graph-renders/{name}.gv.png'


def render_safe_steps(game_dict: dict, safe_steps, name=None):
    if name is None:
        name = 'game'

    graph = graphviz.Digraph(name, engine='circo')

    for state in game_dict:
        # Neighbours
        for neighbour in game_dict[state]:
            if neighbour in safe_steps[state]:
                graph.edge(state_name(state), state_name(neighbour))
                continue

            graph.edge(state_name(state), state_name(neighbour), style='dashed')

        # Terminal state render
        graph.node(state.terminal_state.id, label=str(tuple(state.payoffs)), shape='plaintext')

        if state.terminal_state in safe_steps[state]:
            graph.edge(state_name(state), state.terminal_state.id)
            continue

        graph.edge(state_name(state), state.terminal_state.id, style='dashed')

    graph.render(directory='graph-renders', view=False, format='png')

    return f'graph-renders/{name}.gv.png'


def state_name(state):
    return f'{state.id},\n\u03B1={state.alpha}'
