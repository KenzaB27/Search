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
MAX_ALLOWED_TIME_IN_SECONDS = 0.058

MAX_DEPTH  = 19
MAX_UTILITY = float('inf')
SEARCH_CUT_OFF = False

transposition_table = {}

class SearchTimeout(Exception):
    pass

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

# https://www.chessprogramming.org/MTD(f)
def mtd(node, first_guess, depth, player, start_time):
    best_guess = first_guess
    best_move = None
    upper_bound = float('inf')
    lower_bound = float('-inf')

    while lower_bound < upper_bound:
        beta = max(best_guess, lower_bound + 1)
        best_guess, best_move = negamax(node, depth, beta - 1, beta, player, start_time)

        if best_guess < beta:
            upper_bound = best_guess
        else:
            lower_bound = best_guess
    return best_guess, best_move

def iterative_deepening(root, player):
    start_time = time.time()
    first_guess = 0
    best_move = None
    for depth in range(MAX_DEPTH):
        try:
            first_guess, best_move = mtd(root, first_guess, depth, player, start_time)
            # _, best_move = pvs(root, depth, float('-inf'), float('inf'), 1, start_time)
            # _, best_move = negascout(root, depth, float('-inf'), float('inf'), 1, start_time)
        except SearchTimeout:
            break
    # print('max depth', depth)
    return best_move


# https://en.wikipedia.org/wiki/Principal_variation_search
def pvs(node, depth, alpha, beta, color, start_time):
    if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
        raise SearchTimeout('Timeout')

    children = order_children(transition(node), MAX if color > 0 else MIN)

    if depth == 0 or not children:
        return color * utility(node.state), None
    
    score = None
    best_child = None

    for child in children:
        if not score:
            score = -1 * pvs(node, depth - 1, -beta, -alpha, -color, start_time)[0]
        else:
            score = -1 * pvs(child, depth - 1, -alpha - 1, -alpha, -color, start_time)[0]
            if alpha < score < beta:
                score = -1 * pvs(child, depth - 1, -beta, -1 * score, -color, start_time)[0]

        if score > alpha:
            alpha = score
            best_child = child

        if alpha >= beta:
            break

    return alpha, best_child

# https://www.chessprogramming.org/NegaScout
# https://www.researchgate.net/figure/NegaScout-Algorithm-Pseudo-Code-Using-the-Minimal-Window-Search-Principle_fig5_262672371
def negascout(node, depth, alpha, beta, color, start_time):
    if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
        raise SearchTimeout('Timeout')

    children = order_children(transition(node), MAX if color > 0 else MIN)

    if depth == 0 or not children:
        return color * utility(node.state), None

    b = beta
    best_child = None
    for child in children:
        t, _ = negascout(child, depth - 1, -b, -alpha, -color, start_time)
        t *= -1

        if t > alpha:
            alpha = t
            best_child = child

        if alpha >= beta:
            break
        b = alpha + 1
    return alpha, best_child


def iterative_deepining_alpha_beta(node, player):
    best_node = None
    start_time = time.time()

    for depth in range(1, MAX_DEPTH):
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            break
        try: 
            # print('BEGINING of NEGAMAX in IDS with depth:' , depth, file=sys.stderr)
            # _, n = negamax(node, depth, float('-inf'), float('inf'), player, start_time)
            # _, n = pvs(node, depth, float('-inf'), float('inf'), 1, start_time)
            _, n = negascout(node, depth, float('-inf'), float('inf'), 1, start_time)
            if n: 
                best_node = n
        except SearchTimeout:
            break
    # print('max depth', depth)
    return best_node


def negamax(node, depth, alpha, beta, player, start_time = None):
    if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
        raise SearchTimeout('Timeout')

    alphaOrig = alpha
    ttEntry = {}
    state = node.state

    if state in transposition_table.keys():
        ttEntry = transposition_table[state]
        # print('ttEntry', ttEntry,  file=sys.stderr)
        # print('DEPTH is', depth,  file=sys.stderr)
        if ttEntry['depth'] >= depth:
            if ttEntry['flag'] == EXACT:
                # print('ttEntry Flag EXACT', file=sys.stderr)
                return ttEntry['value'], node
            elif ttEntry['flag'] == LOWERBOUND:
                # print('ttEntry Flag LOWERBOUND', file=sys.stderr)
                alpha = max(alpha, ttEntry['value'])
            elif ttEntry['flag'] == UPPERBOUND:
                # print('ttEntry Flag UPPERBOUND', file=sys.stderr)
                beta = min(beta, ttEntry['value'])
            if alpha >= beta:
                return ttEntry['value'], node
                
    nega_value, nega_move = float('-inf'), None
    children = order_children(transition(node), player)

    if depth == 0 or not children:
        color = 1 if player == MAX else -1
        return color * utility(state), None

    for child in children:
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            raise SearchTimeout('Timeout')

        value, _ = negamax(child, depth - 1, -beta, -alpha, 1-player, start_time)
        value = - value

        if value > nega_value:
            nega_value = value
            nega_move = child

        alpha = max(alpha, nega_value)
        if alpha >= beta:
            break

    if node:
        ttEntry['value'] = nega_value
        if nega_value <= alphaOrig:
            ttEntry['flag'] = UPPERBOUND
        elif nega_value >= beta:
            ttEntry['flag'] = LOWERBOUND
        else:
            ttEntry['flag'] = EXACT
        ttEntry['depth'] = depth 
        transposition_table[node.state] = ttEntry

    return nega_value, nega_move


