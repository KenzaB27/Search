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


class SearchTimeout(Exception):
    pass

def order_children(children, initial_score):
    sorted_children = sorted(
        children, key=lambda child: utility(child.state, initial_score), reverse=True)
    return sorted_children


def transition(node):
    return node.compute_and_get_children()


def utility(state, initial_score):
    fish_positions = state.fish_positions
    score_green, score_red = state.get_player_scores()
    fish_scores = state.fish_scores
    hook_positions = state.hook_positions
    h = 0
    for fish_id in fish_positions:
        if fish_scores[fish_id] > 0:
            d_max = (fish_positions[fish_id][0] - hook_positions[0][0])**2 + \
                (fish_positions[fish_id][1] - hook_positions[0][1])**2 + 1
            d_min = (fish_positions[fish_id][0] - hook_positions[1][0])**2 + \
                (fish_positions[fish_id][1] - hook_positions[1][1])**2 + 1
            h += fish_scores[fish_id] * (1/d_max - 1/d_min)

    return h + score_green - initial_score[0] - score_red + initial_score[1]


def iterative_deepining(node, player):
    best_node = None
    start_time = time.time()
    initial_score = node.state.get_player_scores()
    for depth in range(1, MAX_DEPTH):
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            break
        try:
            _, best_node = minimax(node, depth, player,
                                   start_time, initial_score)
        except SearchTimeout:
            break
    print('max depth', depth, file=sys.stderr)
    return best_node


def minimax(node, depth, player, start_time, initial_score):
    if player == MAX:
        return search_max(node, depth, -MAX_UTILITY, MAX_UTILITY, start_time, initial_score)
    else:
        return search_min(node, depth, -MAX_UTILITY, MAX_UTILITY, start_time, initial_score)


def search_max(node, depth, alpha, beta, start_time, initial_score):
    children = order_children(transition(node), initial_score)
    # children = transition(node)
    if depth == 0 or not children:
        return utility(node.state, initial_score), None

    v = float('-inf')
    best_child = None
    for child in children:
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            raise SearchTimeout('Timeout')
        min_v, max_moves = search_min(
            child, depth - 1, alpha, beta, start_time, initial_score)
        if min_v > v:
            v = min_v
            best_child = child

        if beta <= v:
            # print('max pruned')
            break

        alpha = max(alpha, v)

    return v, best_child


def search_min(node, depth, alpha, beta, start_time, initial_score):

    #classic search
    children = order_children(transition(node), initial_score)
    # children = transition(node)
    if depth == 0 or not children:
        return utility(node.state, initial_score), None
    v = float('inf')
    best_child = None
    for child in children:
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            raise SearchTimeout('Timeout')
        max_v, max_moves = search_max(
            child, depth - 1, alpha, beta, start_time, initial_score)
        if max_v < v:
            v = max_v
            best_child = child

        if v <= alpha:
            # print('min pruned')
            break

        beta = min(beta, v)

    return v, best_child
