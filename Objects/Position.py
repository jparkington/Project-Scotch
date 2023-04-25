'''
Author:        James Parkington
Created Date:  3/26/2023
Modified Date: 4/23/2023

File containing the implementation of the Position class for representing 
chess positions in a chess game analysis tool.
'''

from   typing import *
import chess

class Position:
    '''
    Attributes:
        move_history   (list): A list or stack storing the sequence of moves made in the game.
        user_submitted (bool): A boolean indicating whether or not the file came from the user or the program's game storage
        white_turn     (bool): A boolean indicating whether or not it is white's turn to move.
        move_number    (int):  The move number for the current position.
        move_notation  (str):  The move notation in Standard Algebraic Notation (SAN) for the current position.
        final_move     (bool): A boolean indicating whether or not this position was the last one in the PGN file.
        bitboards      (dict): A dictionary containing the bitboards for each piece type and color.

    Methods:
        apply_move():            Applies a given move to the current position and updates the bitboards, move history, and player turn accordingly.
        from_chess_board():      Creates a Position object from a python-chess Board object.
        get_board():             Generates a 2D list representing the board state at a given ply.
        get_bitboard_integers(): Returns a list of the integer resolutions of each bitstring for a given position.
        get_bitboard_strings():  Returns the bitboards for each piece in the position as a multiline string.
        convert_piece_symbol():  Converts a python-chess piece symbol to the corresponding Unicode symbol.
        __str__():               Returns a textual representation of the board state at a given ply for easy visualization.

    Bitboards are an efficient way to represent chess positions using 64-bit integers, with each bit corresponding to a square on the chessboard. 
    They offer several advantages, including memory efficiency, fast bitwise operations on modern CPUs, simplified move generation, and ease of implementation. 
    By using bitboards, our analysis with Matcher will have a relatively small memory footprint and more maintainable code.
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
        
         
    def get_move_history(self):
        return self.move_history
    
    def get_user_submitted(self):
        return self.user_submitted
    
    def get_white_turn(self):
        return self.white_turn
    
    def get_move_number(self):
        return self.move_number
    
    def get_move_notation(self):
        return self.move_notation
    
    def get_final_move(self):
        return self.final_move
    
    def get_bitboards(self):
        return self.bitboards
    
    def set_move_history(self, move_history):
        self.move_history = move_history
        
    def set_user_submitted(self, user_submitted):
        self.move_history = user_submitted

    def set_white_turn(self, white_turn):
        self.white_turn = white_turn

    def set_move_number(self, move_number):
        self.move_number = move_number
    
    def set_move_notation(self, move_notation):
        self.move_notation = move_notation

    def set_final_move(self, final_move):
        self.final_move = final_move

    def set_bitboards(self, bitboards):
        self.bitboards = bitboards
    

    @staticmethod
    def from_chess_board(board: chess.Board) -> 'Position':
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
        '''
        if symbol.islower():
            return {'p': '♟︎', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'}[symbol]
        else:
            return {'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔'}[symbol]
        
        
    def get_board(self) -> List[List[str]]:
        '''
        Generates a 2D list representing the board state at a given ply.

        Returns:
            List[List[str]]: A 2D list representing the board state with piece symbols.
        '''

        board = [[' ' for _ in range(8)] for _ in range(8)]

        for piece, bitboard in self.get_bitboards().items():
            for square in (i for i in range(64) if (bitboard >> i) & 1):
                row, col = 7 - (square // 8), square % 8
                board[row][col] = piece

        return board
    
        
    def get_bitboard_integers(self):
        '''
        Returns a list of the integer resolutions of each bitstring for a given position.

        A production version of this would not convert to strings, but would instead use a performant data type for Parquet storage.
        '''

        return [str(bitboard) for bitboard in self.get_bitboards().values()]
    

    def get_bitboard_strings(self, full_bitstrings: bool = False) -> str:
        '''
        Returns the bitboards for each piece in the position as a multiline string.

        Args:
            full_bitstrings: If True, returns the full integer bitstrings. 
                             If False (default), returns the binary representation of the bitstrings.
        '''

        bitboard_strings = [f"{piece}: {bin(bitboard)[2:].zfill(64)if full_bitstrings else str(bitboard)}"
                            for piece, bitboard in self.get_bitboards().items()]

        return "\n".join(bitboard_strings)
 

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