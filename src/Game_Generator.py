import numpy as np
import string
from State import *
from Game_Render import *


def create_game(num_players, num_states):
    states = create_states(num_players, num_states)
    create_edges(states, num_states)
    create_terminals(states, num_players)

    adjacency_dict = {state: state.neighbours for state in states}
    return adjacency_dict


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


def create_terminals(states, num_players, min_payoff=-3, max_payoff=3):
    for state in states:
        payoffs = np.random.randint(low=min_payoff, high=max_payoff + 1, size=num_players)
        state.add_terminal(payoffs)


game_dict = create_game(4, 5)
render_game(game_dict)

