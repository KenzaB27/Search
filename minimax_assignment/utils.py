from fishing_game_core.shared import *
from fishing_game_core.game_tree import *


def transition(player, state):
    return state.compute_and_get_children()

def utility(player, state): 
    # return 1
    return state.state.player_scores[player] - state.state.player_scores[1 - player]

def alpha_beta (state, depth, alpha, beta, player):
    # print(state)
    v = 0
    if depth == 0 or utility(player, state) is None:
        return utility(player, state), state

    elif player == 0: 
        v = float('-inf')
        for child in transition(0, state):
            v = max(v, alpha_beta(child, depth - 1, alpha, beta, 1)[0])
            alpha = max(alpha, v)
            if beta <= alpha: 
                return v, child
    
    else:
        v = float('+inf')
        for child in transition(1, state):
            v = min(v, alpha_beta(child, depth - 1, alpha, beta, 0)[0])
            alpha = min(beta, v)
            if beta <= alpha:
                return v, child

    return v, state
