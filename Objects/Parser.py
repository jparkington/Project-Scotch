'''
Author:        James Parkington
Created Date:  3/26/2023
Modified Date: 4/25/2023

File containing the implementation of the Parser class for parsing PGN files and generating Position objects
in a chess game analysis tool. The class makes use of the python-chess library for parsing and validating
PGN files.
'''

from Position import *
from typing   import *
from chess    import pgn
import io
import os

class Parser:
    '''
    This class leverages the python-chess library to parse and validate PGN files, allowing the focus to be on
    storing positions as bitboards for Matcher.

    Attributes:
        pgn_input (str)            : The file path of the PGN file to be parsed or an existing PGN string.
        is_file   (bool)           : Whether or not the pgn_input provided is a path to a file or an existing PGN string.
        game      (chess.pgn.Game) : The parsed PGN game object.

    Methods:
        read_game     : Reads the PGN file or PGN string using the python-chess library and returns the game object.
        get_metadata  : Returns a dictionary containing the metadata of the PGN file.
        get_positions : Parses the PGN file and returns a list of Position objects for each position in the game.
        generate_id   : Calculates the bitboard sum of all positions.
    '''

    def __init__(self, 
                 pgn_input,
                 is_file  = True):

        self.pgn_input = pgn_input
        self.is_file   = is_file
        self.game      = self.read_game()

    def read_game(self) -> pgn.Game:
        '''
        Reads the PGN file or PGN string using the python-chess library and returns the game object.

        This method checks whether the pgn_input attribute is a file or a PGN string. If it is a file, it reads the
        file using the python-chess library. Otherwise, it creates a StringIO object, which is used to provide a 
        file-like interface to the PGN string, allowing the python-chess library to read it.
        '''

        def read_first_game(pgn_source) -> pgn.Game:
            first_game  = pgn.read_game(pgn_source)
            second_game = pgn.read_game(pgn_source)
            if second_game: print("Warning: Multiple games detected. The program currently only processes the first game.")
            return first_game

        if not self.pgn_input:
            print("No PGN file provided. Entering demo mode.")
            self.pgn_input = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Games/demo.pgn')

        if self.is_file:
            with open(self.pgn_input, "r") as pgn_file:
                return read_first_game(pgn_file)
        else:
            pgn_string = io.StringIO(self.pgn_input)
            return read_first_game(pgn_string)

    def get_metadata(self) -> Dict[str, str]:
        '''
        Returns a dictionary containing the metadata of the PGN file.

        The method extracts the metadata from the game headers and returns a dictionary with key-value pairs.
        '''

        return {key: self.game.headers[key] for key in self.game.headers.keys() if self.game.headers[key] not in ["?", "0", "", " "]}

    def get_positions(self, user_submitted = True) -> List['Position']:
        '''
        Parses the PGN file and returns a list of Position objects representing each position in the game, and additionally 
        marks if those positions were submitted by the user (optional).

        The method performs the following steps:
            1. Iterate through the game, creating a Position object for each move using the Position.from_chess_board() method.
            2. Set the move number, move notation (in SAN), and user submission status for each Position object.
            3. Return the list of positions.
        '''

        board     = self.game.board()
        positions = [Position.from_chess_board(board)]

        move_number = 1
        for move in self.game.mainline_moves():
            move_notation = board.san(move)
            board.push(move)

            position               = Position.from_chess_board(board)
            position.move_number   = move_number
            position.move_notation = move_notation
            if not user_submitted: position.user_submitted = False
            positions.append(position)

            # Increment move_number after every full move (i.e., a white move and a black move)
            if not board.turn:
                move_number += 1

        positions[-1].final_move = True
        return positions
    
    @staticmethod
    def generate_id(positions: List['Position']) -> int:
        '''
        Calculates a unique identifier for the game based on the positions.

        This method iterates through each position in the game and calculates the sum of the position's 
        bitboards. It then adds the total number of positions to the sum to create an identifier that can 
        be used as a game identifier, allowing for efficient matching and comparison of games.
        '''

        return sum(i.bitboard_integers for i in positions) + len(positions)