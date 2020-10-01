from fishing_game_core.shared import *
from fishing_game_core.game_tree import *
import time
import random
import sys

MIN, MAX = 1, 0
LOWERBOUND, EXACT, UPPERBOUND = -1, 0, 1
MAX_ALLOWED_TIME_IN_SECONDS = 0.045

MAX_DEPTH  = 20
INFINITY = float('inf')
SEARCH_CUT_OFF = False

transposition_table = {}

class SearchTimeout(Exception):
    pass


def order_children(children, player, start_time):
    for child in children:
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            raise SearchTimeout('Timeout')
        child.utility = utility(child.state)
    desc = True if player == MAX else False
    if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
        raise SearchTimeout('Timeout')
    sorted_children = sorted(
        children, key=lambda child: child.utility, reverse=desc)
    return sorted_children

def get_utility(child):
    if child.utility:
        return child.utility
    return utility(child.state)

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
    min_distance = INFINITY
    best_fish_id = 0
    for fish_id in fish_positions:
        fish_position = fish_positions[fish_id]
        d = abs(fish_position[0] - hook_position[0]) + \
            abs(fish_position[1] - hook_position[1])
        if best_score - fish_scores[fish_id] <= 5 and min_distance > d:
            min_distance = d
            best_fish_id = fish_id
    # no good fish around
    if min_distance == INFINITY:
        return score_green - score_red
    # take the min distance and weight with the best score
    h = - best_score * min_distance
    # print('heuristic', h)
    return h + score_green - score_red

# https://www.chessprogramming.org/MTD(f)
def mtd(node, first_guess, depth, player, start_time):
    best_guess = first_guess
    best_move = None
    upper_bound = INFINITY
    lower_bound = -INFINITY

    while lower_bound < upper_bound:
        beta = max(best_guess, lower_bound + 1)
        best_guess, best_move = negamax(
            node, depth, beta - 1, beta, player, start_time)

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
            # first_guess, best_move = mtd(root, first_guess, depth, player, start_time)
            # _, best_move = pvs(root, depth, -INFINITY, INFINITY, 1, start_time)
            # _, best_move = negascout(root, depth, -INFINITY, INFINITY, 1, start_time)
            _, best_move = negascout2(root, depth, -INFINITY, INFINITY, 1, start_time)
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
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            raise SearchTimeout('Timeout')
        if not score:
            score = -1 * pvs(node, depth - 1, -beta, -
                             alpha, -color, start_time)[0]
        else:
            score = -1 * pvs(child, depth - 1, -alpha - 1, -
                             alpha, -color, start_time)[0]
            if alpha < score < beta:
                score = -1 * pvs(child, depth - 1, -beta, -
                                 1 * score, -color, start_time)[0]

        if score > alpha:
            alpha = score
            best_child = child

        if alpha >= beta:
            break

    return alpha, best_child

# https://www.chessprogramming.org/NegaScout


def negascout(node, depth, alpha, beta, color, start_time):
    if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
        raise SearchTimeout('Timeout')

    children = order_children(transition(node), MAX if color > 0 else MIN)

    if depth == 0 or not children:
        return color * utility(node.state), None

    b = beta
    best_child = None
    for child in children:
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            raise SearchTimeout('Timeout')
        t, _ = negascout(child, depth - 1, -b, -alpha, -color, start_time)
        t *= -1

        if t > alpha:
            alpha = t
            best_child = child

        if alpha >= beta:
            break
        b = alpha + 1
    return alpha, best_child

# https://www.researchgate.net/figure/NegaScout-Algorithm-Pseudo-Code-Using-the-Minimal-Window-Search-Principle_fig5_262672371


def negascout2(node, depth, alpha, beta, color, start_time):
    if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
        raise SearchTimeout('Timeout')

    children = order_children(transition(node), MAX if color > 0 else MIN)

    if depth == 0 or not children:
        return color * utility(node.state), None

    score = -INFINITY
    n = beta
    best_child = None
    for child in children:
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            raise SearchTimeout('Timeout')
        cur, _ = negascout2(child, depth - 1, -n, -alpha, -color, start_time)
        cur *= -1

        if cur > score:
            if n == beta or depth <= 2:
                score = cur
            else:
                score, _ = negascout2(
                    child, depth - 1, -beta, -cur, -color, start_time)
                score *= -1

        if score > alpha:
            alpha = score
            best_child = child

        if alpha >= beta:
            break
        n = alpha + 1
    return score, best_child


def iterative_deepining_alpha_beta(node, player, zobrist_table):
    best_move = None
    start_time = time.time()

    for depth in range(1, MAX_DEPTH):
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            # print('TIME OUT IDS', file=sys.stderr)
            break
        try:
            # print('BEGINING of NEGAMAX in IDS with depth:' , depth, file=sys.stderr)
            u, n = negamax(
                node, depth, -INFINITY, INFINITY, player, start_time)
            # _, best_node = pvs(node, depth, -INFINITY, INFINITY, 1, start_time)
            # first_guess, n = mtd(node, first_guess, depth, player, start_time)
            # _, best_node = negascout(node, depth, -INFINITY, INFINITY, 1, start_time)
            # print(u,n)
            if n: 
                best_move = n
        except SearchTimeout:
            # print('TIME OUT NEGA', file=sys.stderr)
            break
    print('max depth', depth, file=sys.stderr)
    # print('best_move', best_move, file=sys.stderr)
    return best_move


def negamax_zobrist(node, depth, alpha, beta, player, start_time, zobrist_table):
    if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
        raise SearchTimeout('Timeout')

    alphaOrig = alpha
    ttEntry = {}
    key = hash(node.state, zobrist_table)

    if key in transposition_table.keys():
        ttEntry = transposition_table[key]
        # print('ttEntry', ttEntry,  file=sys.stderr)
        # print('DEPTH is', depth,  file=sys.stderr)
        if ttEntry['depth'] >= depth:
            if ttEntry['flag'] == EXACT:
                # move = node.move
                # print('ttEntry Flag EXACT', file=sys.stderr)
                # if ttEntry['depth'] == depth: 
                #     print('ON EST LA', file = sys.stderr)
                #     move = ttEntry['move']
                return ttEntry['value'], ttEntry['move']
            elif ttEntry['flag'] == LOWERBOUND:
                # print('ttEntry Flag LOWERBOUND', file=sys.stderr)
                alpha = max(alpha, ttEntry['value'])
            elif ttEntry['flag'] == UPPERBOUND:
                # print('ttEntry Flag UPPERBOUND', file=sys.stderr)
                beta = min(beta, ttEntry['value'])
            if alpha >= beta:
                # move = node.move
                # # print('ttEntry Flag EXACT', file=sys.stderr)
                # if ttEntry['depth'] == depth:
                #     move = ttEntry['move']
                return ttEntry['value'], ttEntry['move']

    nega_value, nega_move = -INFINITY, None
    children = order_children(transition(node), player)

    if depth == 0 or not children:
        color = 1 if player == MAX else -1
        u = get_utility(node) 
        u = u if u else utility(node.sate)
        return color * u, None

    for child in children:
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            raise SearchTimeout('Timeout')

        value, _ = negamax_zobrist(
            child, depth - 1, -beta, -alpha, 1-player, start_time, zobrist_table)
        value = - value

        if value > nega_value:
            nega_value = value
            nega_move = child.move

        alpha = max(alpha, nega_value)
        if alpha >= beta:
            break

    ttEntry['value'] = nega_value
    if nega_value <= alphaOrig:
        ttEntry['flag'] = UPPERBOUND
    elif nega_value >= beta:
        ttEntry['flag'] = LOWERBOUND
    else:
        ttEntry['flag'] = EXACT
    ttEntry['depth'] = depth
    ttEntry['move'] = nega_move
    transposition_table[key] = ttEntry

    return nega_value, nega_move


def init_zobrist(model):
    nb_fish = len(model) + 2 
    size = 400
    table = [[[0 for k in range(nb_fish)]
              for j in range(20)] for i in range(20)]
    for i in range(20):
        for j in range (20):
            for k in range(nb_fish):
                table[i][j][k] = random.getrandbits(64)
    return table

def hash(state, table):
    pos_0 = len(table[0][0]) - 2
    pos_1 = len(table[0][0]) - 1
    fish_positions = state.fish_positions
    hook_positions = state.hook_positions

    h = 0 

    for pos in fish_positions:
        h = h ^ table[fish_positions[pos][0]][fish_positions[pos][1]][pos]
    
    h = h ^ table[hook_positions[0][0]][hook_positions[0][1]][pos_0]
    h = h ^ table[hook_positions[1][0]][hook_positions[1][1]][pos_1]

    return h


def negamax(node, depth, alpha, beta, player, start_time):
    children = []
    try:
        children = order_children(transition(node), player, start_time)
    except SearchTimeout:
        raise SearchTimeout('Timeout')
    if depth == 0 or not children:
        color = 1 if player == MAX else -1
        return color * get_utility(node), None
    nega_value, nega_move = float('-inf'), None
    for child in children:
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            raise SearchTimeout('Timeout')
        value, _ = negamax(child, depth - 1, -beta, -
                           alpha, 1-player, start_time)
        value = - value
        if value > nega_value:
            nega_value = value
            nega_move = child
        alpha = max(alpha, nega_value)
        if alpha >= beta:
            break

    return nega_value, nega_move
