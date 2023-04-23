'''
Author:        James Parkington
Created Date:  3/26/2023
Modified Date: 4/22/2023

File containing the implementation of the Position class for representing 
chess positions in a chess game analysis tool.
'''

from   typing import Tuple
import chess

class Position:
    '''
    Attributes:
        move_history (list):  A list or stack storing the sequence of moves made in the game.
        white_turn   (str):   A boolean indicating whether or not it is white's turn to move.
        bitboards    (dict):  A dictionary containing the bitboards for each piece type and color.

    Methods:
        apply_move(move):     Applies a given move to the current position and updates the bitboards, move history, and player turn accordingly.
        __str__():            Returns a textual representation of the board state for easy visualization.

    Bitboards are an efficient way to represent chess positions using 64-bit integers, with each bit corresponding to a square on the chessboard. 
    They offer several advantages, including memory efficiency, fast bitwise operations on modern CPUs, simplified move generation, and ease of implementation. 
    By using bitboards, our analysis with Matcher will have a relatively small memory footprint and more maintainable code.
    '''

    def __init__(self):
        self.move_history = []
        self.white_turn   = True
        self.bitboards    = {'♙' : 0b0000000000000000000000000000000000000000000000001111111100000000,
                             '♖' : 0b0000000000000000000000000000000000000000000000000000000010000001,
                             '♘' : 0b0000000000000000000000000000000000000000000000000000000001000010,
                             '♗' : 0b0000000000000000000000000000000000000000000000000000000000100100,
                             '♕' : 0b0000000000000000000000000000000000000000000000000000000000010000,
                             '♔' : 0b0000000000000000000000000000000000000000000000000000000000001000,
                             '♟︎' : 0b0000000011111111000000000000000000000000000000000000000000000000,
                             '♜' : 0b1000000100000000000000000000000000000000000000000000000000000000,
                             '♞' : 0b0100001000000000000000000000000000000000000000000000000000000000,
                             '♝' : 0b0010010000000000000000000000000000000000000000000000000000000000,
                             '♛' : 0b0001000000000000000000000000000000000000000000000000000000000000,
                             '♚' : 0b0000100000000000000000000000000000000000000000000000000000000000}
        
         
    def get_move_history(self):
        return self.move_history
    
    def get_white_turn(self):
        return self.white_turn
    
    def get_bitboards(self):
        return self.bitboards
    
    def set_move_history(self, move_history):
        self.move_history = move_history

    def set_white_turn(self, white_turn):
        self.white_turn = white_turn

    def set_bitboards(self, bitboards):
        self.bitboards = bitboards


    @staticmethod
    def from_chess_board(board: chess.Board) \
        -> 'Position':
        '''
        Creates a Position object from a python-chess Board object.

        Using a static method allows this conversion to happen without creating an instance of the Position class first.

        Args:
            board: A python-chess Board object representing the current position of the chess game.

        Returns:
            position: A Position object with the equivalent bitboard representation of the given chess.Board object.
        '''
        position = Position()
        position.set_bitboards({piece: 0 for piece in position.get_bitboards().keys()})
        position.set_white_turn(board.turn)

        for square in chess.SQUARES:
            piece = board.piece_at(square)

            if piece:
                piece_symbol = position.convert_piece_symbol(piece.symbol())
                position.get_bitboards()[piece_symbol] |= 1 << square

        return position
    

    def apply_move(self, move: Tuple[str, int, int]):
        '''
        move (Tuple):
            piece:       a Unicode character representing the moving piece
            origin:      an integer representing the origin square index (0-63)
            destination: an integer representing the destination square index (0-63)

        The method performs the following steps:
            1. Create bitboards with a single bit set at the origin and destination squares.
            2. Update the moving piece's bitboard by clearing the bit at the origin square and setting the bit at the destination square.
            3. Loop over the opponent's pieces and update their bitboards by removing any captured piece from the destination square.
        '''

        piece, origin, destination = move
        bitboards            = self.get_bitboards()
        origin_bitboard      = 1 << origin
        destination_bitboard = 1 << destination

        bitboards[piece] ^= origin_bitboard | destination_bitboard

        # If the loop detects that a capture has occurred, break the loop, since the move must therefore be complete
        for opponent_piece in self.bitboards.keys():
            if opponent_piece != piece:
                if self.bitboards[opponent_piece] & destination_bitboard:
                   self.bitboards[opponent_piece] &= ~destination_bitboard
                   break

        self.set_move_history(self.get_move_history() + [move])
        self.set_white_turn(not self.get_white_turn())
        self.set_bitboards(bitboards)


    def convert_piece_symbol(self, symbol: str) -> str:
        '''
        Converts a python-chess piece symbol to the corresponding Unicode symbol.

        Args:
            symbol: A single ASCII character representing a chess piece in python-chess.

        Returns:
            The corresponding Unicode character representing the chess piece.
        '''
        if symbol.islower():
            return {'p': '♟︎', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'}[symbol]
        else:
            return {'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔'}[symbol]
        

    def __str__(self) -> str:
        '''
        Returns a textual representation of the board state for easy visualization.
        '''

        board = [[' ' for _ in range(8)] for _ in range(8)]

        bitboards = self.get_bitboards()
        for piece, bitboard in bitboards.items():
            for square in range(64):
                if (bitboard >> square) & 1:
                    row, col = 7 - (square // 8), square % 8
                    board[row][col] = piece

        board_string = ''
        for row in board:
            row_string = ''.join(row)
            board_string += row_string + '\n'

        return board_string