import json
import string
import numpy as np
from game_data.game_utils.state import *


def create_states(num_players, num_states):
    if num_players > num_states:
        raise Exception(f'The number of players ({num_players}) is greater than the number of states ({num_states})')

    players = np.arange(num_players)

    if num_players == num_states:
        states = [State(player, create_payoffs(num_players)) for player in players]
        return states, players

    states = []
    state_cnt = num_players

    letters = list(string.ascii_lowercase)
    player_dict = {player: [] for player in players}

    while state_cnt < num_states:
        player = np.random.choice(players)

        if not player_dict[player]:
            player_dict[player].append('a')

        suffix = letters[len(player_dict[player])]
        player_dict[player].append(suffix)

        state_cnt += 1

    for player in player_dict:

        if not player_dict[player]:
            states.append(State(player, create_payoffs(num_players)))
            continue

        for suffix in player_dict[player]:
            states.append(State(player, create_payoffs(num_players), suffix))

    return states


def create_edges(states, cycle_length):
    edge_map = {state: [] for state in states}
    for state in edge_map:
        edge_map[state].append(state.terminal_state)

    # Shuffle the states
    shuffled_states = states.copy()
    np.random.shuffle(shuffled_states)
    total_edges = 0

    # Create the cycle
    for i in range(cycle_length - 1):
        edge_map[shuffled_states[i]].append(shuffled_states[i + 1])
        total_edges += 1

    # Complete the cycle
    edge_map[shuffled_states[cycle_length]].append(shuffled_states[0])
    total_edges += 1

    # Add extra edges
    while total_edges < len(states) + 1:
        state_x, state_y = np.random.choice(states, 2, replace=False)

        if state_y in edge_map[state_x]:
            continue

        edge_map[state_x].append(state_y)
        total_edges += 1

    return edge_map


def create_payoffs(num_players, min_payoff=-2, max_payoff=2):
    return list(np.random.randint(low=min_payoff, high=max_payoff + 1, size=num_players))


def example_game_1():
    states = [State(0, [-2, 1, -2]),
              State(1, [-2, 0, -2]),
              State(2, [1, -1, -1]),
              State(0, [-2, 0, 0], suffix='a')]

    edge_map = {state: [] for state in states}
    for state in edge_map:
        edge_map[state].append(state.terminal_state)

    edge_map[states[0]].extend([states[3]])
    edge_map[states[1]].extend([states[3], states[2]])
    edge_map[states[2]].extend([states[0]])
    edge_map[states[3]].extend([states[1], states[2]])

    return states, edge_map


def fig_4_game():
    states = [State(0, [-2, 0, 1], suffix='a'), State(1, [-3, 1, 0]),
              State(0, [-1, 2, -2], suffix='b'), State(2, [2, 2, -1])]

    edge_map = {state: [state.terminal_state] for state in states}

    edge_map[states[0]].extend([states[1]])
    edge_map[states[1]].extend([states[2]])
    edge_map[states[2]].extend([states[0], states[3]])
    edge_map[states[3]].extend([states[0]])

    return states, edge_map


def alpha_exit_game_1():
    states = [State(0), State(1), State(2, suffix='a'), State(2, suffix='b'), State(2, suffix='c')]
    payoffs = [[1, 0, 0], [2, -1, 0], [2, -1, -1], [2, -2, -2], [2, -1, -1]]
    neighbours_list = [[states[1]], [states[2]], [states[3]], [states[4]], [states[0]]]

    for state, neighbours, payoff in zip(states, neighbours_list, payoffs):
        state.add_neighbours(neighbours)
        state.add_terminal(payoff)

    for state in states:
        state.create_plans()

    game_dict = {state: state.neighbours for state in states}
    return game_dict


def alpha_exit_game_2():
    states = [State(0), State(1), State(2), State(3), State(4)]
    payoffs = [[-1, -1, -1, -1, 2], [-2, -2, -1, 0, 0], [0, -3, -2, -1, 0], [0, 0, -3, -2, 0], [2, 2, 2, -3, 1]]
    neighbours_list = [[states[1]], [states[2]], [states[3]], [states[4]], [states[0]]]

    for state, neighbours, payoff in zip(states, neighbours_list, payoffs):
        state.add_neighbours(neighbours)
        state.add_terminal(payoff)

    for state in states:
        state.create_plans()

    game_dict = {state: state.neighbours for state in states}
    return game_dict


def save_game(game: dict, game_id):
    states = [(state.player, state.suffix, state.payoffs) for state in game]

    edge_list = []
    for state_t in game:
        edge_list.append([(state.player, state.suffix) for state in game[state_t]])

    data = {
        'states': states,
        'edge_list': edge_list
    }

    filename = f'src/game_saves/{game_id}.json'
    with open(filename, 'w') as file:
        json.dump(data, file)

    print(f"Game saved to {filename}")


def read_game(game_id):
    filename = f'src/game_saves/{game_id}.json'
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


if __name__ == "__main__":
    pass
    # game = fig_4_game()
    # save_game(game, 'fig_4_game')
    #
    # game = read_game('fig_4_game')
