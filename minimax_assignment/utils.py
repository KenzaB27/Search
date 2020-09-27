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
MAX_ALLOWED_TIME_IN_SECONDS = 0.055
MAX_DEPTH  = 8
MAX_UTILITY = float('inf')
SEARCH_CUT_OFF = False

transposition_table = {}


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

def iterative_deepining_alpha_beta(node, player):
    best_node = None
    start_time = time.time()
    global SEARCH_CUT_OFF
    for depth in  range(1, MAX_DEPTH):
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            # print('TIMEOUT in IDS', file=sys.stderr)
            break
        u, node = negamax(node, depth, float(
            '-inf'), float('inf'), player, start_time)
        if not SEARCH_CUT_OFF:
            utility, best_node = u, node
        # print('depth', depth,  'best_node', best_node, "best_move", best_node.move, file=sys.stderr)
    SEARCH_CUT_OFF = False
    return best_node


def negamax(node, depth, alpha, beta, player, start_time):
    global SEARCH_CUT_OFF
    alphaOrig = alpha
    ttEntry = {}
    if node in transposition_table.keys():
        ttEntry = transposition_table[node]
        if ttEntry['depth'] >= depth:
            if ttEntry['flag'] == EXACT:
                return ttEntry['value'], node
            elif ttEntry['flag'] == LOWERBOUND:
                alpha = max(alpha, ttEntry.value)
            elif ttEntry['flag'] == UPPERBOUND:
                beta = min(beta, ttEntry.value)
            if alpha >= beta:
                return ttEntry['value'], node
    
    # core of negamax
    children = order_children(transition(node), player)
    if depth == 0 or not children:
        color = 1 if player == MAX else -1
        return color * utility(node.state), None
    nega_value, nega_move = float('-inf'), None
    for child in children:
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            # print('TIMEOUT in NEGAMAX', file=sys.stderr)
            SEARCH_CUT_OFF = True
            break
        value, _ = negamax(child, depth - 1, -beta, -alpha, 1-player, start_time)
        value = - value
        if value > nega_value:
            nega_value = value
            nega_move = child
        alpha = max(alpha, nega_value)
        if alpha >= beta:
            break
    # end of negamax 

    ttEntry['value'] = nega_value
    if nega_value <= alphaOrig:
        ttEntry['flag'] = UPPERBOUND
    elif nega_value >= beta:
        ttEntry['flag'] = LOWERBOUND
    else:
        ttEntry['flag'] = EXACT

    ttEntry['depth'] = depth
    transposition_table[node] = ttEntry
    
    return nega_value, nega_move

