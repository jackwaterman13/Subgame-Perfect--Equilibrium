import json
import string
import numpy as np
from .state import *


def create_game(num_players, num_states):
    states = create_states(num_players, num_states)
    create_edges(states, num_states)
    create_terminals(states, num_players)

    for state in states:
        state.create_plans()

    return {state: state.neighbours for state in states}


def create_cycle_game(num_players, num_states, cycle_length=4):
    states = create_states(num_players, num_states)
    create_cycle_edges(states, num_states, cycle_length)
    create_terminals(states, num_players)

    for state in states:
        state.create_plans()

    return {state: state.neighbours for state in states}


def create_states(num_players, num_states):
    if num_players > num_states:
        raise Exception(f'The number of players ({num_players}) is greater than the number of states ({num_states})')

    players = np.arange(num_players)
    states = [State(player) for player in players]

    if num_players == num_states:
        return states

    letters = list(string.ascii_lowercase)
    player_dict = {player: [] for player in players}

    # TODO: Make this work for more than 26 extra suffixes
    while len(states) < num_states:
        player = np.random.choice(players)
        suffix = letters[len(player_dict[player])]

        player_dict[player].append(suffix)
        states.append(State(player, suffix))

    return states


def create_edges(states, num_states):
    max_edges = num_states * (num_states - 1)
    min_edges = num_states - 1

    num_edges = np.random.randint(min_edges, max_edges + 1)

    edge_count = 0

    # Make graph fully connected
    for state in states:
        neighbour = np.random.choice(states)
        while neighbour == state:
            neighbour = np.random.choice(states)

        state.add_neighbour(neighbour)
        edge_count += 1

    # Add missing edges
    while edge_count < num_edges:

        state = np.random.choice(states)
        neighbour = np.random.choice(states)

        # This is very inefficient
        if neighbour == state or neighbour in state.neighbours:
            continue

        state.add_neighbour(neighbour)
        edge_count += 1


def create_cycle_edges(states, num_states, cycle_length):
    max_edges = num_states * (num_states - 1)
    min_edges = num_states + 3

    num_edges = min_edges

    cycle_start = np.random.choice(states)

    cycle_end = np.random.choice(list_less(states, cycle_start))
    cycle_end.add_neighbour(cycle_start)
    edge_count = 1

    cycle = {cycle_start, cycle_end}
    state_x = cycle_start

    while len(cycle) < cycle_length - 1:
        state_y = np.random.choice(states)
        if state_y in cycle:
            continue
        state_x.add_neighbour(state_y)
        cycle.add(state_y)
        state_x = state_y
        edge_count += 1

    state_x.add_neighbour(cycle_end)
    cycle.add(cycle_end)
    edge_count += 1
    state_set = set(states)

    for state in states:
        if not state.neighbours:
            neighbour = np.random.choice(list(state_set.difference([state])))
            state.add_neighbour(neighbour)
            edge_count += 1

    # Add missing edges
    while edge_count < num_edges:

        state = np.random.choice(states)
        neighbour = np.random.choice(states)

        # This is very inefficient
        if neighbour == state or neighbour in state.neighbours:
            continue

        state.add_neighbour(neighbour)
        edge_count += 1


def list_less(items, less):
    items = items.copy()
    items.remove(less)
    return items


def create_terminals(states, num_players, min_payoff=-2, max_payoff=2):
    for state in states:
        payoffs = np.random.randint(low=min_payoff, high=max_payoff + 1, size=num_players)
        state.add_terminal(payoffs)


def fig_4_game():
    states = [State(0, suffix='a'), State(1), State(0, suffix='b'), State(2)]
    payoffs = [[-2, 0, 1], [-3, 1, 0], [-1, 2, -2], [2, 2, -1]]
    neighbours_list = [[states[1]], [states[2]], [states[0], states[3]], [states[0]]]

    for state, neighbours, payoff in zip(states, neighbours_list, payoffs):
        state.add_neighbours(neighbours)
        state.add_terminal(payoff)

    for state in states:
        state.create_plans()

    return {state: state.neighbours for state in states}


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
