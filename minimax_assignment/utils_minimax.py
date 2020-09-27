def minimax(node, depth, player, start_time):
    if player == MAX:
        return search_max(node, depth, -MAX_UTILITY, MAX_UTILITY, start_time)
    else:
        return search_min(node, depth, -MAX_UTILITY, MAX_UTILITY, start_time)


def search_max(node, depth, alpha, beta, start_time):
    children = order_children(transition(node), MAX, False)
    # children = transition(node)
    if depth == 0 or not children:
        return utility(MAX, node.state), None

    v = float('-inf')
    best_child = None
    for child in children:
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            search_cut_off = True
            break
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


def search_min(node, depth, alpha, beta, start_time):

    #classic search
    children = order_children(transition(node), MIN, True)
    # children = transition(node)
    if depth == 0 or not children:
        return utility(MIN, node.state), None
    v = float('inf')
    best_child = None
    for child in children:
        if time.time() - start_time > MAX_ALLOWED_TIME_IN_SECONDS:
            search_cut_off = True
            break
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
