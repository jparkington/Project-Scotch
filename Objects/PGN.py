'''
Author:        James Parkington
Created Date:  3/26/2023
Modified Date: 4/22/2023

File containing the implementation of the PGN class for parsing PGN files and generating Position objects
in a chess game analysis tool. The class makes use of the python-chess library for parsing and validating
PGN files.
'''

from Position import *
from chess    import pgn
from typing   import List

class PGN:
    '''
    Attributes:
        pgn_file_path (str): The file path of the PGN file to be parsed.

    Methods:
        __call__(): Parses the PGN file and returns a list of Position objects representing each position in the game.

    This class leverages the python-chess library to parse and validate PGN files, allowing the focus to be on
    storing positions as bitboards for Matcher.
    '''

    def __init__(self, pgn_file_path):

        self.pgn_file_path = pgn_file_path

    def get_pgn_file_path(self):
        return self.pgn_file_path

    def set_pgn_file_path(self, pgn_file_path):
        self.pgn_file_path = pgn_file_path
        

    def __call__(self) -> List[Position]:
        '''
        Parses the PGN file and returns a list of Position objects representing each position in the game.

        The method performs the following steps:
            1. Read the PGN file using the python-chess library.
            2. Iterate through the moves of the game, updating the chess.Board object and creating a Position object using the Position.from_chess_board() method.
            3. Return the list of positions.
        '''

        with open(self.get_pgn_file_path(), "r") as pgn_file:
            game      = pgn.read_game(pgn_file)
            board     = game.board()
            positions = [Position.from_chess_board(board)]

            for move in game.mainline_moves():
                board.push(move)
                positions.append(Position.from_chess_board(board))

        return positions