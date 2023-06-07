import json
from State import *


def save_game(game: dict, game_id):
    states = [(state.player, state.suffix, state.payoffs) for state in game]

    edge_list = []
    for state_t in game:
        edge_list.append([(state.player, state.suffix) for state in game[state_t]])

    data = {
        'states': states,
        'edge_list': edge_list
    }

    filename = f'game_saves/{game_id}.json'
    with open(filename, 'w') as file:
        json.dump(data, file)

    print(f"Game saved to {filename}")


def read_game(game_id):
    filename = f'game_saves/{game_id}.json'
    with open(filename, 'r') as file:
        loaded_data = json.load(file)

    states_ids = loaded_data['states']
    states = []

    for state_tuple in states_ids:
        state = State(state_tuple[0], suffix=state_tuple[1])
        state.add_terminal(state_tuple[2])
        states.append(state)

    edge_list = loaded_data['edge_list']

    for state, neighbours in zip(states, edge_list):
        state.add_neighbours(get_neighbour_list(neighbours, states))

    for state in states:
        state.create_plans()

    return {state: state.neighbours for state in states}


def get_neighbour_list(neighbours, states):
    neighbour_list = []
    for neighbour in neighbours:
        for state_u in states:
            if state_u.player == neighbour[0] and state_u.suffix == neighbour[1]:
                neighbour_list.append(state_u)
                break

    return neighbour_list
