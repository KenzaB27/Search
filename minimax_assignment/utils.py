from fishing_game_core.shared import *
from fishing_game_core.game_tree import *
import random

MAX = 0
MIN = 1

# TODO: come up with a better utility function. Maybe straight line distance
# from the hook to the closest positive-score fish?
# hook position - state.hook_positions[player]
# fish positions - state.fish_positions[fish_id]
# fish scores - model[fish_id]['score']



# TODO: utilise the model

def transition(node):
    return node.compute_and_get_children()

def utility(player, state, model):
    print(state.fish_positions)
    print(model)

    hook_position = state.hook_positions[player]
    min_distance = float('inf')

    for fish_id in model:
        if fish_id not in state.fish_positions:
            continue
        if model[fish_id]['score'] > 0:
            fish_position = state.fish_positions[fish_id]
            d = (fish_position[0] - hook_position[0])**2 + (fish_position[1] - hook_position[1])**2
            min_distance = min(min_distance, d)
    
    print('min distance', min_distance)
    return -min_distance
    # return state.player_scores[player] - state.player_scores[1 - player]

def minimax(node, depth, alpha, beta, player, model):
    if player == MAX:
        return search_max(node, depth, alpha, beta, model)
    else:
        return search_min(node, depth, alpha, beta, model)

def search_max(node, depth, alpha, beta, model):
    if depth == 0 or not transition(node):
        return utility(MAX, node.state, model), node

    v = float('-inf')
    best_child = None
    for child in transition(node):
        # v = max(v, search_min(child, depth - 1, alpha, beta, model)[0])
        # alpha = max(alpha, v)

        min_v = search_min(child, depth - 1, alpha, beta, model)[0]
        if min_v > v:
            v = min_v
            best_child = child

        alpha = max(alpha, v)
        if beta <= alpha:
            return v, best_child

    # return v, node
    return v, best_child

def search_min(node, depth, alpha, beta, model):
    if depth == 0 or not transition(node):
        return utility(MIN, node.state, model), node

    v = float('inf')
    best_child = None
    for child in transition(node):
        # v = min(v, search_max(child, depth - 1, alpha, beta)[0])
        # beta = min(beta, v)

        max_v = search_max(child, depth - 1, alpha, beta, model)[0]
        if max_v < v:
            v = max_v
            best_child = child

        beta = min(beta, v)
        if beta <= alpha:
            return v, best_child

    # return v, node
    return v, best_child