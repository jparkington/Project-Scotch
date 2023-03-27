'''
File containing the implementation of the Position class for representing 
chess positions in a chess game analysis tool.

Created on 3/26/2023
James Parkington
'''

class Position:
    """
    Attributes:
        board_state (str):   A 64-bit string representing the current state of the chess board.
        move_history (list): A list or stack storing the sequence of moves made in the game.
        player_turn (str):   A string indicating which player's turn it is ('white' or 'black').

    Methods:
        apply_move(move):     Applies a given move to the current position and updates the board state, move history, and player turn accordingly.
        is_valid():           Checks if the current position is valid according to the rules of chess.
        board_to_bitstring(): Converts the board state to a 64-bit string representation.
    """

    def __init__(self, board_state, move_history, player_turn):
            self.board_state  = board_state
            self.move_history = move_history
            self.player_turn  = player_turn

    # Accessors
    def get_board_state(self):
        return self.board_state

    def get_move_history(self):
        return self.move_history

    def get_player_turn(self):
        return self.player_turn
    
    # Mutators
    def set_board_state(self, board_state):
        self.board_state = board_state

    def set_move_history(self, move_history):
        self.move_history = move_history

    def set_player_turn(self, player_turn):
        self.player_turn = player_turn
        
    # Other Methods
    def apply_move(self, move):
        """
        Applies a given move to the current position and updates the board state,
        move history, and player turn accordingly.
        """
        pass

    def is_valid(self):
        """
        Checks if the current position is valid according to the rules of chess.
        """
        pass

    def board_to_bitstring(self):
        """
        Converts the board state to a 64-bit string representation.
        """
        pass