'''
Author:        James Parkington
Created Date:  3/26/2023
Modified Date: 4/22/2023

File containing the implementation of the Parser class for parsing PGN files and generating Position objects
in a chess game analysis tool. The class makes use of the python-chess library for parsing and validating
PGN files.
'''

from Position import *
from typing   import *
from chess    import pgn

class Parser:
    '''
    Attributes:
        pgn_path (str):        The file path of the PGN file to be parsed.
        game (chess.pgn.Game): The parsed PGN game object.

    Methods:
        read_game():     Reads the PGN file using the python-chess library and returns the game object.
        get_metadata():  Returns a dictionary containing the metadata of the PGN file.
        get_positions(): Parses the PGN file and returns a list of Position objects for each position in the game.

    This class leverages the python-chess library to parse and validate PGN files, allowing the focus to be on
    storing positions as bitboards for Matcher.
    '''

    def __init__(self, pgn_path):
        self.pgn_path = pgn_path
        self.game     = self.read_game()


    def get_pgn_path(self):
        return self.pgn_path

    def set_pgn_path(self, pgn_path):
        self.pgn_path = pgn_path


    def read_game(self) -> pgn.Game:
        '''
        Reads the PGN file using the python-chess library and returns the game object.
        '''

        with open(self.get_pgn_path(), "r") as pgn_file:
            return pgn.read_game(pgn_file)
        

    def get_metadata(self) -> Dict[str, str]:
        '''
        Returns a dictionary containing the metadata of the PGN file.

        The method extracts the metadata from the game headers and returns a dictionary with key-value pairs.
        '''

        return {key: self.game.headers[key] for key in self.game.headers.keys() if self.game.headers[key] not in ["?", "0", "", " "]}


    def get_positions(self) -> List['Position']:
        '''
        Parses the PGN file and returns a list of Position objects representing each position in the game.

        The method performs the following steps:
            1. Read the PGN file using the python-chess library.
            2. Iterate through the moves of the game, updating the chess.Board object and creating a Position object using the Position.from_chess_board() method.
            3. Set the move number and move notation (in SAN) for each Position object.
            4. Return the list of positions.
        '''

        game      = self.read_game()
        board     = game.board()
        positions = [Position.from_chess_board(board)]

        move_number = 1
        for move in game.mainline_moves():
            move_notation = board.san(move)
            board.push(move)

            position = Position.from_chess_board(board)
            position.set_move_number(move_number)
            position.set_move_notation(move_notation)
            positions.append(position)

            if board.turn:
                move_number += 1

        return positions