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
        file using the python-chess library. Otherwise, it creates a StringIO object, which is used to provide a 
        file-like interface to the PGN string, allowing the python-chess library to read it.
        '''

        def read_first_game(pgn_source) -> pgn.Game:
            first_game  = pgn.read_game(pgn_source)
            second_game = pgn.read_game(pgn_source)
            if second_game: print("Warning: Multiple games detected. The program currently only processes the first game.")
            return first_game

        if not self.get_pgn_input():
            self.set_is_file(False)
            self.set_pgn_input(self.enter_demo_mode())

        if self.is_file:
            with open(self.get_pgn_input(), "r") as pgn_file:
                return read_first_game(pgn_file)
        else:
            pgn_string = io.StringIO(self.get_pgn_input())
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
    

    def enter_demo_mode(self) -> pgn.Game:
        '''
        Enters demo mode when no PGN file is provided.

        In demo mode, the method returns a chess.pgn.Game object representing a predefined PGN string,
        simulating the user providing a PGN file for analysis.
        '''

        print("No PGN file provided. Entering demo mode.")
        demo_pgn = ('[Date "2022.08.21"]\n'
                    '[Round "1"]\n'
                    '[Result "1-0"]\n'
                    '[White "James Parkington"]\n'
                    '[Black "Greg Townsend"]\n'
                    '[PlyCount "57"]\n'
                    '\n'
                    '1.d4 Nf6 2.c4 e6 3.Nf3 d5 4.Nc3 Bb4 5.cxd5 exd5 6.Bg5 h6 7.Bh4\n'
                    'c5 8.e3 g5 9.Bg3 Ne4 10.Bb5+ Kf8 11.dxc5 Nxc3 12.bxc3 Bxc3+\n'
                    '13.Ke2 Bxa1 14.Qxa1 f6 15.h4 g4 16.Nd4 Kf7 17.Bd3 Nd7 18.Qc3\n'
                    'Ne5 19.Nb5 Qe7 20.Nd6+ Kf8 21.Rd1 b6 22.c6 Ba6 23.Bxa6 Qxd6\n'
                    '24.c7 Kf7 25.c8=Q Raxc8 26.Bxc8 Rd8 27.Bf5 Qc6 28.Bxe5 fxe5\n'
                    '29.Qxe5 Qf6 30.Rxd5 Rxd5 31.Qxd5+ Kg7 32.Qd7+ Qf7 33.Qxf7+ Kxf7\n'
                    '34.Bxg4 Kf6 35.f4 b5 36.Kd3 a5 37.Kd4 b4 38.Kc4 Ke7 39.Kb5 Kd6\n'
                    '40.Kxa5 Kc5 41.f5 Kc4 42.f6 Kc3 43.f7 Kb2 44.Be6 Ka1 45.f8=Q b3\n'
                    '46.Bxb3 Kb2 47.Qf6+ Kb1 48.Qf5+ Kb2 49.Qe5+ Kb1 50.Qe4+ Kb2\n'
                    '51.Qd4+ Kb1 52.Qd3+ Kb2 53.Qc2+ Ka3 54.Qc1# 1-0')
        
        return demo_pgn

    
    @staticmethod
    def generate_id(positions: List['Position']) -> int:
        '''
        Calculates a unique identifier for the game based on the positions.

        This method iterates through each position in the game and calculates the sum of the position's 
        bitboards. It then adds the total number of positions to the sum to create an identifier that can 
        be used as a game identifier, allowing for efficient matching and comparison of games.
        '''

        return sum(j for i in positions for j in i.get_bitboard_integers()) + len(positions)