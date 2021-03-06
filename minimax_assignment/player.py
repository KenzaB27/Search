#!/usr/bin/env python3
import random

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR
from newutils import *
from time import time

class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and send
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):
    start_time = None

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        :return:
        """

        # Generate game tree object
        first_msg = self.receiver()
        # Initialize your minimax model
        model = self.initialize_model(initial_data=first_msg)
        while True:
            msg = self.receiver()

            # Create the root node of the game tree
            node = Node(message=msg, player=0)
            self.start_time = time()
            # Possible next moves: "stay", "left", "right", "up", "down"
            best_move = self.search_best_next_move(
                model=model, initial_tree_node=node)
            end_time = time()

            # print('time', end_time - start_time, file= sys.stderr)
            # Execute next action
            self.sender({"action": best_move, "search_time": end_time - self.start_time})

    def initialize_model(self, initial_data):
        """
        Initialize your minimax model 
        :param initial_data: Game data for initializing minimax model
        :type initial_data: dict
        :return: Minimax model
        :rtype: object

        Sample initial data:
        { 'fish0': {'score': 11, 'type': 3}, 
          'fish1': {'score': 2, 'type': 1}, 
          ...
          'fish5': {'score': -10, 'type': 4},
          'game_over': False }

        Please note that the number of fishes and their types is not fixed between test cases.
        """
        zobrist_table = init_zobrist(initial_data)
        # EDIT THIS METHOD TO RETURN A MINIMAX MODEL ###
        return zobrist_table

    def search_best_next_move(self, model, initial_tree_node):
        """
        Use your minimax model to find best possible next move for player 0 (green boat)
        :param model: Minimax model
        :type model: object
        :param initial_tree_node: Initial game tree node 
        :type initial_tree_node: game_tree.Node 
            (see the Node class in game_tree.py for more information!)
        :return: either "stay", "left", "right", "up" or "down"
        :rtype: str
        """

        # EDIT THIS METHOD TO RETURN BEST NEXT POSSIBLE MODE FROM MINIMAX MODEL ###
        
        # NOTE: Don't forget to initialize the children of the current node 
        #       with its compute_and_get_children() method!

        # initial_tree_node.move
# negamax(node, depth, alpha, beta, player)
        # ut, next_state = negamax(initial_tree_node, 4, float('-inf'), float('inf'), initial_tree_node.state.player)
        # _, next_state = minimax(initial_tree_node, 4,
        #                         initial_tree_node.state.player)
        # next_state = iterative_deepining_alpha_beta(initial_tree_node, initial_tree_node.state.player, model)
        # print('move', next_state, file = sys.stderr)
        # next_state = iterative_deepining_alpha_beta_minimax(initial_tree_node, initial_tree_node.state.player)
        next_state = iterative_deepining_new(
            initial_tree_node, initial_tree_node.state.player, model, self.start_time)
        # next_state = iterative_deepining(initial_tree_node, initial_tree_node.state.player)
        # if not next_state:
        #     return ACTION_TO_STR[random.randint(0, 7)]
        # print("best_move_done", next_state.move, file=sys.stderr)

        return ACTION_TO_STR[next_state]