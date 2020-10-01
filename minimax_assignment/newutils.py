from fishing_game_core.shared import *
from fishing_game_core.game_tree import *
import time
import random
import sys

MIN, MAX = 1, 0
LOWERBOUND, EXACT, UPPERBOUND = -1, 0, 1
MAX_ALLOWED_TIME_IN_SECONDS = 0.050

MAX_DEPTH = 20
INFINITY = float('inf')
SEARCH_CUT_OFF = False

transposition_table = {}


class SearchTimeout(Exception):
    pass


def order_children(children, start_time, initial_score):
    sorted_children = sorted(
        children, key=lambda child: utility(child.state, initial_score), reverse=True)
    return sorted_children


def get_utility(child, initial_score):
    try:
        return child.utility
    except: 
        child.utility = utility(child.state, initial_score)
        return child.utility


def transition(node):
    return node.compute_and_get_children()

def utility(state, initial_score):
    fish_positions = state.fish_positions
    score_green, score_red = state.get_player_scores()
    fish_scores = state.fish_scores
    hook_positions = state.hook_positions
    h = 0
    for fish_id in fish_positions:
        # if fish_scores[fish_id] > 0:
        xmax_dist = abs(fish_positions[fish_id][0] - hook_positions[0][0])
        xmin_dist = abs(fish_positions[fish_id][0] - hook_positions[1][0])
        
        if hook_positions[0][0] < hook_positions[1][0] and hook_positions[1][0] < fish_positions[fish_id][0]:
            xmax_dist = 20 - xmax_dist
        elif fish_positions[fish_id][0] < hook_positions[1][0] and hook_positions[1][0] < hook_positions[0][0] :
            xmax_dist = 20 - xmax_dist
        elif fish_positions[fish_id][0] < hook_positions[0][0] and hook_positions[0][0] < hook_positions[1][0]:
            xmin_dist = 20 - xmin_dist
        elif hook_positions[1][0] < hook_positions[0][0] and hook_positions[0][0] < fish_positions[fish_id][0]:
            xmin_dist = 20 - xmin_dist
        
        d_max = xmax_dist + abs(fish_positions[fish_id][1] - hook_positions[0][1]) + 1
        d_min = xmin_dist + abs(fish_positions[fish_id][1] - hook_positions[1][1]) + 1
        
        h += fish_scores[fish_id] * (1/d_max - 1/d_min)

    return h + score_green - score_red 


def iterative_deepining_new(node, player, zobrist_table):
    best_move = None
    best_val = - INFINITY
    start_time = time.time()
    initial_score = node.state.get_player_scores()
    children = transition(node)
    for depth in range(1, MAX_DEPTH):
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            break
        for child in children: 
            try:
                val = - negamax_zobrist(child, depth, -INFINITY, INFINITY,
                                        1-player, start_time, zobrist_table, initial_score)
                # val = negamax(child, depth, -INFINITY, INFINITY, player, start_time)
                if val > best_val:
                    best_val = val
                    best_move = child.move
            except SearchTimeout:
                break
    return best_move


def negamax_zobrist(node, depth, alpha, beta, player, start_time, zobrist_table, initial_score):
    
    if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
        raise SearchTimeout('Timeout')

    alphaOrig = alpha
    ttEntry = {}
    key = hash(node.state, zobrist_table)
    if key in transposition_table.keys():
        ttEntry = transposition_table[key]
        if ttEntry['depth'] >= depth:
            if ttEntry['flag'] == EXACT:
                return ttEntry['value']
            elif ttEntry['flag'] == LOWERBOUND:
                alpha = max(alpha, ttEntry['value'])
            elif ttEntry['flag'] == UPPERBOUND:
                beta = min(beta, ttEntry['value'])
            if alpha >= beta:
                return ttEntry['value']

    nega_value = -INFINITY
    children = order_children(transition(node), start_time, initial_score)
    
    if depth == 0 or not children:
        color = 1 if player == MAX else -1
        return color * utility(node.state, initial_score)

    for child in children:
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            raise SearchTimeout('Timeout')

        value = - negamax_zobrist(child, depth - 1, -beta, -alpha, 1-player, start_time, zobrist_table, initial_score)

        nega_value = max(value, nega_value)
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

    transposition_table[key] = ttEntry

    return nega_value


def init_zobrist(model):
    nb_fish = len(model) + 2
    size = 400
    table = [[[0 for k in range(nb_fish)]
              for j in range(20)] for i in range(20)]
    for i in range(20):
        for j in range(20):
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