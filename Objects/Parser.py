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
import hashlib
import io

class Parser:
    '''
    Attributes:
        pgn_input (str):            The file path of the PGN file to be parsed or an existing PGN string.
        source    (str):            The platform or process through which the chess game is being parsed.
        is_file   (bool):           Whether or not the pgn_input provided is a path to a file or an existing PGN string.
        game      (chess.pgn.Game): The parsed PGN game object.

    Methods:
        read_game():            Reads the PGN file or PGN string using the python-chess library and returns the game object.
        get_metadata():         Returns a dictionary containing the metadata of the PGN file.
        get_positions():        Parses the PGN file and returns a list of Position objects for each position in the game.
        generate_game_hash():   Calculates a unique hash for the game based on the positions.

    This class leverages the python-chess library to parse and validate PGN files, allowing the focus to be on
    storing positions as bitboards for Matcher.
    '''

    def __init__(self, 
                 pgn_input,
                 is_file  = True):

        self.pgn_input = pgn_input
        self.is_file   = is_file
        self.game      = self.read_game()


    def get_pgn_input(self):
        return self.pgn_input

    def get_is_file(self):
        return self.is_file

    def get_game(self):
        return self.game

    def set_pgn_input(self, pgn_input):
        self.pgn_input = pgn_input

    def set_is_file(self, is_file):
        self.is_file = is_file

    def set_game(self, game):
        self.game = game


    def read_game(self) -> pgn.Game:
        '''
        Reads the PGN file or PGN string using the python-chess library and returns the game object.

        This method checks whether the pgn_input attribute is a file or a PGN string. If it is a file, it reads the
        file using the python-chess library. Otherwise, it creates a StringIO object, whichis used to provide a 
        file-like interface to the PGN string, allowing the python-chess library to read it.
        '''

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

        game      = self.get_game()
        board     = game.board()
        positions = [Position.from_chess_board(board)]

        move_number = 1
        for move in game.mainline_moves():
            move_notation = board.san(move)
            board.push(move)

            position = Position.from_chess_board(board)
            position.set_move_number(move_number)
            position.set_move_notation(move_notation)
            if not user_submitted: position.set_user_submitted(False)
            positions.append(position)

            if board.turn:
                move_number += 1

        positions[-1].set_final_move(True)
        return positions
    
    
    @staticmethod
    def generate_game_hash(positions: List['Position']) -> str:
        '''
        Calculates a unique hash for the game based on the positions.

        This method iterates through each position in the game, updating the SHA-256 hash with the binary representation of 
        the position's bitboards. The resulting hash can be used as a game identifier, allowing for efficient matching and 
        comparison of games.
        '''

        return hashlib.sha256('|'.join(str(i.get_bitboard_strings()) for i in positions).encode('utf-8')).hexdigest()