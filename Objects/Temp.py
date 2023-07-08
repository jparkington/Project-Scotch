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

class Parser:
    '''
    Attributes:
        pgn_input (str):            The file path of the PGN file to be parsed or an existing PGN string.
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
            self.is_file = False
            self.pgn_input = self.enter_demo_mode()

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

            position = Position.from_chess_board(board)
            position.move_number = move_number
            position.move_notation = move_notation
            if not user_submitted: position.user_submitted = False
            positions.append(position)

            # Increment move_number after every full move (i.e., a white move and a black move)
            if not board.turn:
                move_number += 1

        positions[-1].final_move = True
        return positions

    def enter_demo_mode(self) -> pgn.Game:
        '''
        Enters demo mode when no PGN file is provided.

        In demo mode, the method returns a chess.pgn.Game object representing a predefined PGN string,
        simulating the user providing a PGN file for analysis.
        '''

        print("No PGN file provided. Entering demo mode.")
        demo_pgn = '[Date "2022.08.21"]\\n' + \
                   '[Round "1"]\\n' + \
                   '[Result "1-0"]\\n' + \
                   '[White "James Parkington"]\\n' + \
                   '[Black "Greg Townsend"]\\n' + \
                   '[PlyCount "57"]\\n' + \
                   '\\n' + \
                   '1.d4 Nf6 2.c4 e6 3.Nf3 d5 4.Nc3 Bb4 5.cxd5 exd5 6.Bg5 h6 7.Bh4 0-0 8.e3 Bf5 9.Qb3 Nc6 10.Bxf6 Qxf6 11.Qxd5 Rad8 12.Qb5 a6 13.Qa4 b5 14.Qd1 Rfe8 15.Be2 bxc4 16.0-0 Bxc3 17.bxc3 Na5 18.Ne5 Rxe5 19.dxe5 Rxd1 20.exf6 Rxf1+ 21.Kxf1 gxf6 22.Rd1 Kf8 23.Rd8+ Ke7 24.Ra8 Nb3 25.axb3 cxb3 26.Rb8 Bc2 27.Bxa6 c5 28.Ke2 Kd6 29.Bd3 Bxd3+ 30.Kxd3 c4+ 31.Kxc4 f5 32.Rxb3 Ke5 33.Rb5+ Kf6 34.Kd5 h5 35.h4 Kg6 36.Ke5 f6+ 37.Ke6 f4 38.exf4 Kh6 39.Kxf6 Kh7 40.Rb8 Kh6 41.Rh8# 1-0'
        
        return self.read_game(demo_pgn)