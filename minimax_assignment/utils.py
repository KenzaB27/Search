from fishing_game_core.shared import *
from fishing_game_core.game_tree import *
import random

MAX = 0
MIN = 1

def order_children(children, player, desc):
    sorted_children = sorted(children, key=lambda child: child.state.get_player_scores()[player], reverse=desc)
    sorted_children = sorted(sorted_children, key=lambda child: child.move)
    return sorted_children


def transition(node):
    return node.compute_and_get_children()


def utility(player, state):
    hook_position = state.hook_positions[player]
    fish_positions = state.fish_positions
    fish_scores = state.fish_scores
    score_green, score_red = state.get_player_scores()
    distances = []
    best_score = max(fish_scores.values())
    caugh_fish_id = state.player_caught[player]
    if caugh_fish_id != -1 and best_score - fish_scores[caugh_fish_id] <= 2:
        return (100 if player == MAX else -100)
    for fish_id in fish_positions:
        fish_position = fish_positions[fish_id]
        if best_score - fish_scores[fish_id] <= 5:
            distances.append((fish_position[0] - hook_position[0])**2 +
                             (fish_position[1] - hook_position[1])**2)
    if not distances:
        return score_green - score_red
    min_distance = min(distances)
    h = - best_score * min_distance if player == MAX else min_distance/best_score
    # print('heuristic', h)
    return h + score_green - score_red

def minimax(node, depth, player, model, next_moves = None):
    if player == MAX:
        return search_max(node, depth, float('-inf'), float('+inf'), model, next_moves)
    else:
        return search_min(node, depth, float('-inf'), float('+inf'), model)

def search_max(node, depth, alpha, beta, model, next_moves = None):
    next_move = next_moves.pop(0) if next_moves else None
    children = order_children(transition(node), MAX, False)
    # children = transition(node)
    if depth == 0 or not children:
        return utility(MAX, node.state), None

    v = float('-inf')
    best_child = None
    best_max_moves = None
    for child in children:
        if next_move and child.move != next_move:
            continue

        min_v, max_moves = search_min(child, depth - 1, alpha, beta, model, next_moves)
        if min_v > v or best_child is None:
            v = min_v
            best_child = child
            best_max_moves = max_moves

        if beta <= v:
            # print('max pruned')
            break

        alpha = max(alpha, v)

    return v, [best_child] + (best_max_moves or [])

def search_min(node, depth, alpha, beta, model, next_moves = None):
    next_move = next_moves.pop(0) if next_moves else None
    children = order_children(transition(node), MIN, True)
    # children = transition(node)
    if depth == 0 or not children:
        return utility(MIN, node.state), None

    v = float('inf')
    best_child = None
    best_max_moves = None
    for child in children:
        if next_move and child.move != next_move:
            continue

        max_v, max_moves = search_max(child, depth - 1, alpha, beta, model, next_moves)
        if max_v < v:
            v = max_v
            best_child = child
            best_max_moves = max_moves

        if v <= alpha:
            # print('min pruned')
            break

        beta = min(beta, v)

    return v, [best_child] + (best_max_moves or [])
    # return v, best_max_moves