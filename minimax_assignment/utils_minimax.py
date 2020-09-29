from fishing_game_core.shared import *
from fishing_game_core.game_tree import *
import time
import random
import sys

MAX = 0
MIN = 1
EXACT = 0
LOWERBOUND = -1
UPPERBOUND = 1
MAX_ALLOWED_TIME_IN_SECONDS = 0.045

MAX_DEPTH = 10
MAX_UTILITY = float('inf')
SEARCH_CUT_OFF = False


def order_children(children, player):
    desc = True if player == MAX else False
    sorted_children = sorted(
        children, key=lambda child: utility(child.state), reverse=desc)
    return sorted_children


def transition(node):
    return node.compute_and_get_children()


def utility(state):
    fish_positions = state.fish_positions
    score_green, score_red = state.get_player_scores()
    # chasing a good fish
    fish_scores = state.fish_scores
    best_score = max(fish_scores.values())
    caugh_fish_id = state.player_caught[0]
    if caugh_fish_id != -1 and best_score - fish_scores[caugh_fish_id] <= 2:
        return 100
    # choose state with min distance to a good fish
    hook_position = state.hook_positions[0]
    min_distance = MAX_UTILITY
    best_fish_id = 0
    for fish_id in fish_positions:
        fish_position = fish_positions[fish_id]
        d = abs(fish_position[0] - hook_position[0]) + \
            abs(fish_position[1] - hook_position[1])
        if best_score - fish_scores[fish_id] <= 5 and min_distance > d:
            min_distance = d
            best_fish_id = fish_id
    # no good fish around
    if min_distance == MAX_UTILITY:
        return score_green - score_red
    # take the min distance and weight with the best score
    h = - best_score * min_distance
    # print('heuristic', h)
    return h + score_green - score_red


def iterative_deepining_alpha_beta_minimax(node, player):
    best_node = None
    start_time = time.time()

    for depth in range(1, MAX_DEPTH):
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            break
        try:
            _, best_node = minimax(node, depth, player, start_time)
        except RuntimeError:
            break

    print('depth', depth,  'best_node', best_node,
          "best_move", best_node.move, file=sys.stderr)
    return best_node

def minimax(node, depth, player, start_time = None):
    if player == MAX:
        return search_max(node, depth, -MAX_UTILITY, MAX_UTILITY, start_time)
    else:
        return search_min(node, depth, -MAX_UTILITY, MAX_UTILITY, start_time)


def search_max(node, depth, alpha, beta, start_time = None):
    children = order_children(transition(node), MAX)
    # children = transition(node)
    if depth == 0 or not children:
        return utility(node.state), None

    v = float('-inf')
    best_child = None
    for child in children:
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            raise RuntimeError('Timeout')
        min_v, max_moves = search_min(
            child, depth - 1, alpha, beta, start_time)
        if min_v > v:
            v = min_v
            best_child = child

        if beta <= v:
            # print('max pruned')
            break

        alpha = max(alpha, v)

    return v, best_child


def search_min(node, depth, alpha, beta, start_time = None):

    #classic search
    children = order_children(transition(node), MIN)
    # children = transition(node)
    if depth == 0 or not children:
        return utility(node.state), None
    v = float('inf')
    best_child = None
    for child in children:
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            raise RuntimeError('Timeout')
        max_v, max_moves = search_max(
            child, depth - 1, alpha, beta, start_time)
        if max_v < v:
            v = max_v
            best_child = child

        if v <= alpha:
            # print('min pruned')
            break

        beta = min(beta, v)

    return v, best_child
