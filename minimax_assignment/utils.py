from fishing_game_core.shared import *
from fishing_game_core.game_tree import *
import random

MAX = 0
MIN = 1

def transition(node):
    return node.compute_and_get_children()


# def utility(player, state, model):
#     hook_position = state.hook_positions[player]
#     all_distance = 0
   
#     for fish_id in model:
#         if fish_id not in state.fish_positions:
#             continue

#         coef = 1 / model[fish_id]['score']# if model[fish_id]['score'] > 0 else -model[fish_id]['score'] + 1000
        
#         fish_position = state.fish_positions[fish_id]
#         d = (fish_position[0] - hook_position[0])**2 + (fish_position[1] - hook_position[1])**2
        
#         d *= coef
#         all_distance += d
     
#     return all_distance

def utility(player, state, model):
    hook_position = state.hook_positions[player]
    min_distance = float('inf')
    min_distance_2 = float('inf')

    max_score = 0
    best_type = None
    second_best_type = None

    type_scores = {}
    for remaining_fish in state.fish_positions.keys():
        if model[remaining_fish]['score'] > 0:
            type_scores[model[remaining_fish]['type']] = model[remaining_fish]['score']

    type_scores = {k: v for k, v in sorted(type_scores.items(), key=lambda  item: item[1])}
    if len(type_scores) > 0:
        best_type = list(type_scores.keys())[0]
    if len(type_scores) > 1:
        second_best_type = list(type_scores.keys())[1]

   
    for fish_id in model:
        if fish_id not in state.fish_positions or (model[fish_id]['type'] != best_type and model[fish_id]['type'] != second_best_type):
            continue

        fish_position = state.fish_positions[fish_id]
        d = abs(fish_position[0] - hook_position[0]) + abs(fish_position[1] - hook_position[1])

        if d == 0:# and state.player_caught[player] == fish_id:
            print(fish_position, hook_position)

        if model[fish_id]['type'] == best_type:
            min_distance = min(min_distance, d)
        elif model[fish_id]['type'] == second_best_type:
            min_distance_2 = min(min_distance_2, d)
     
    total_min = min(min_distance, min_distance_2)
    if total_min == 0:
        return 1
    return 1 / total_min

# def utility(player, state, model):
#     hook_position = state.hook_positions[player]
#     min_distance = float('inf')

#     max_score = 0
#     best_type = None
#     for values in model.values():
#         if values['score'] > max_score:
#             max_score = values['score']
#             best_type = values['type']
   
#     closest_fish = None
#     for fish_id in state.fish_positions:
#         # if model[fish_id]['type'] != best_type:
#         #     continue

#         fish_position = state.fish_positions[fish_id]
#         d = (fish_position[0] - hook_position[0])**2 + (fish_position[1] - hook_position[1])**2

#         if d < min_distance:
#             min_distance = min(min_distance, d)
#             closest_fish = fish_id

#     if closest_fish and model[closest_fish]['score'] < 0:
#         return 0
    
#     if min_distance == 0:
#         return 1

#     return 1 / min_distance

# def utility(player, state, model):
#     hook_position = state.hook_positions[player]
#     min_distance = float('inf')
   
#     for fish_id in model:
#         if fish_id not in state.fish_positions:
#             continue

#         coef = 1 / model[fish_id]['score'] if model[fish_id]['score'] > 0 else -model[fish_id]['score'] + 1000
        
#         fish_position = state.fish_positions[fish_id]
#         d = (fish_position[0] - hook_position[0])**2 + (fish_position[1] - hook_position[1])**2
        
#         d *= coef
#         min_distance = min(min_distance, d)
     
#     return -min_distance

# def utility(player, state, model):
#     opponent_scores = state.player_scores[1 - player]
#     own_scores = state.player_scores[player]

#     fish_id = state.player_caught[player]
#     if fish_id != -1 and model[fish_id]['score'] < 0:
#         opponent_scores -= model[fish_id]['score']
#         own_scores -= model[fish_id]['score']
#     return own_scores - opponent_scores

def minimax(node, depth, alpha, beta, player, model):
    if player == MAX:
        return search_max(node, depth, alpha, beta, model)
    else:
        return search_min(node, depth, alpha, beta, model)

def search_max(node, depth, alpha, beta, model):
    children = transition(node)
    if depth == 0 or not children:
        return utility(MAX, node.state, model), None

    v = float('-inf')
    best_child = None
    for child in children:
        min_v, _ = search_min(child, depth - 1, alpha, beta, model)
        if min_v > v:
            v = min_v
            best_child = child

        if beta <= v:
            break

        alpha = max(alpha, v)

    return v, best_child

def search_min(node, depth, alpha, beta, model):
    children = transition(node)
    if depth == 0 or not children:
        return utility(MIN, node.state, model), None

    v = float('inf')
    best_child = None
    for child in children:
        max_v, _ = search_max(child, depth - 1, alpha, beta, model)
        if max_v < v:
            v = max_v
            best_child = child

        if v <= alpha:
            break

        beta = min(beta, v)

    return v, best_child