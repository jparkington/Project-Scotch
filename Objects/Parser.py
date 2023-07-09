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
    '''

    def __init__(self, 
                 pgn_input,
                 is_file  = True):

        self.pgn_input = pgn_input
        self.is_file   = is_file
        self.game      = self.read_game()
        self.positions = self.get_positions()
        self.metadata  = self.get_metadata()

    def read_game(self) -> pgn.Game:
        '''
        Reads the PGN file or PGN string using the python-chess library and returns the game object.

        This method checks whether the pgn_input attribute is a file or a PGN string. If it is a file, it reads the
        file using the python-chess library. Otherwise, it creates a StringIO object, which is used to provide a 
        file-like interface to the PGN string, allowing the python-chess library to read it.
        '''

        if not self.pgn_input:
            print("No PGN file provided. Entering demo mode.")
            self.pgn_input = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Games/demo.pgn')

        if self.is_file:
            with open(self.pgn_input, "r") as pgn_file:
                return pgn.read_game(pgn_file)
        else:
            pgn_string = io.StringIO(self.pgn_input)
            return pgn.read_game(pgn_string)

    def get_metadata(self) -> Dict[str, str]:
        '''
        Returns a dictionary containing the metadata of the PGN file.

        The method extracts the metadata from the game headers and returns a dictionary with key-value pairs.
        '''

        return {k: v for k, v in self.game.headers.items() if v not in ["?", "0", "", " "]}

    def get_positions(self) -> List['Position']:
        '''
        Parses the PGN file and returns a list of Position objects representing each position in the game, and additionally 
        marks if those positions were submitted by the user (optional).

        The method performs the following steps:
            1. Iterate through the game, creating a Position object for each move using the Position.from_chess_board() method.
            2. Set the move number, move notation (in SAN), and user submission status for each Position object.
            3. Return the list of positions.
        '''

        board     = self.game.board()
        positions = [Position()]

        for i, move in enumerate(self.game.mainline_moves()):
            move_notation = board.san(move)
            board.push(move)

            move_number = (i // 2) + 1
            positions.append(Position(move_number   = move_number, 
                                      move_notation = move_notation, 
                                      white_turn    = board.turn,
                                      bitboards     = Position.get_bitboards(board)))

        positions[-1].final_move = True
        return positions