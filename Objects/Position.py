'''
Author:        James Parkington
Created Date:  3/26/2023
Modified Date: 7/8/2023

File containing the implementation of the Position class for representing 
chess positions in a chess game analysis tool.
'''

from   typing    import *
import numpy     as np
import chess

class Position:
    '''
    Bitboards are an efficient way to represent chess positions using 64-bit integers, with each bit corresponding to a square on the chessboard. 
    They offer several advantages, including memory efficiency, fast bitwise operations on modern CPUs, simplified move generation, and ease of implementation. 
    By using bitboards, our analysis with Matcher will have a relatively small memory footprint and more maintainable code.

    Attributes:
        move_history   (list) : A list or stack storing the sequence of moves made in the game.
        user_submitted (bool) : A boolean indicating whether or not the file came from the user or the program's game storage
        white_turn     (bool) : A boolean indicating whether or not it is white's turn to move.
        move_number    (int)  : The move number for the current position.
        move_notation  (str)  : The move notation in Standard Algebraic Notation (SAN) for the current position.
        final_move     (bool) : A boolean indicating whether or not this position was the last one in the PGN file.
        bitboards      (dict) : A dictionary containing the bitboards for each piece type and color.

    Methods:
        apply_move           : Applies a given move to the current position and updates the bitboards, move history, and player turn accordingly.
        from_chess_board     : Creates a Position object from a python-chess Board object.
        get_board            : Generates a 2D list representing the board state at a given ply.
        convert_piece_symbol : Converts a python-chess piece symbol to the corresponding Unicode symbol.
        __str__              : Returns a textual representation of the board state at a given ply for easy visualization.
    '''

    def __init__(self):

        self.move_history   = []
        self.user_submitted = True
        self.white_turn     = True
        self.move_number    = 0
        self.move_notation  = "Game Start"
        self.final_move     = False
        self.bitboards      = {'♙' : 0b0000000000000000000000000000000000000000000000001111111100000000,
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
        
    @property
    def bitboard_integers(self, board_sum: bool = True) -> Union[List[np.uint64], np.uint64]:
        '''
        Returns either a list of the integer resolutions of each bitstring for a given position or 
        the sum of all bitboards in the list as a single uint64 integer, based on the board_sum argument.
        '''

        bitboard_integers = [np.uint64(bitboard) for bitboard in self.bitboards.values()]

        if board_sum:
            return sum(bitboard_integers, np.uint64(0))

        return bitboard_integers
            
    @staticmethod
    def from_chess_board(board: chess.Board) -> 'Position':
        '''
        Creates a Position object from a python-chess Board object.

        Using a static method allows this conversion to happen without creating an instance of the Position class first.
        '''
        
        position = Position()
        position.bitboards = {piece: 0 for piece in position.bitboards.keys()}
        position.white_turn = board.turn

        for square in chess.SQUARES:
            piece = board.piece_at(square)

            if piece:
                piece_symbol = position.convert_piece_symbol(piece.symbol())
                position.bitboards[piece_symbol] |= 1 << square

        return position

    
    def apply_move(self, move: Tuple[str, int, int]):
        '''
        move (Tuple):
            piece       : a Unicode character representing the moving piece
            origin      : an integer representing the origin square index (0-63)
            destination : an integer representing the destination square index (0-63)

        The method performs the following steps:
            1. Create bitboards with a single bit set at the origin and destination squares.
            2. Update the moving piece's bitboard by clearing the bit at the origin square and setting the bit at the destination square.
            3. Loop over the opponent's pieces and update their bitboards by removing any captured piece from the destination square.
        '''

        piece, origin, destination = move
        origin_bitboard      = 1 << origin
        destination_bitboard = 1 << destination

        self.bitboards[piece] ^= origin_bitboard | destination_bitboard

        # If the loop detects that a capture has occurred, break the loop, since the move must therefore be complete
        for opponent_piece in self.bitboards.keys():
            if opponent_piece != piece:
                if self.bitboards[opponent_piece] & destination_bitboard:
                   self.bitboards[opponent_piece] &= ~destination_bitboard
                   break

        self.move_history.append(move)
        self.white_turn = not self.white_turn


    def convert_piece_symbol(self, symbol: str) -> str:
        '''
        Converts a python-chess piece symbol to the corresponding Unicode symbol.
        '''
        if symbol.islower():
            return {'p': '♟︎', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'}[symbol]
        else:
            return {'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔'}[symbol]
         
    def get_board(self) -> List[List[str]]:
        '''
        Generates a 2D list representing the board state at a given ply.
        '''

        board = [[' ' for _ in range(8)] for _ in range(8)]

        for piece, bitboard in self.bitboards.items():
            for square in (i for i in range(64) if (bitboard >> i) & 1):
                row, col = 7 - (square // 8), square % 8
                board[row][col] = piece

        return board

    def __str__(self) -> str:
        '''
        Returns a textual representation of the board state at a given ply for easy visualization.
        '''

        board = self.get_board()

        dark_square  = "\033[48;5;249m"
        light_square = "\033[48;5;252m"
        reset_ansi   = "\033[0m"

        board_string = '\n'.join(''.join(f"{dark_square if (i + j) % 2 == 0 else light_square} {square} {reset_ansi}" \
                                         for j, square in enumerate(row)) \
                                         for i, row    in enumerate(board))

        return board_string