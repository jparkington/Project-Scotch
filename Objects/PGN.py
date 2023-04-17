'''
Author:        James Parkington
Created Date:  3/26/2023
Modified Date: 4/15/2023

File containing the implementation of the PGNParser class for parsing PGN files
and generating Position objects in a chess game analysis tool.
'''

from Position import *
import re

class PGN:
    def __init__(self, pgn):
        self.pgn = pgn

    def get_pgn(self):
        return self.pgn

    def set_pgn(self, pgn):
        self.pgn = pgn

    def read_pgn_file(self):
        with open(self.pgn, "r") as file:
            content = file.read()
        return content

    def parse_pgn(self):
        content = self.read_pgn_file()
        self.parse_metadata(content)
        self.extract_moves(content)
        self.convert_moves()

        # Initialize a starting position
        position = Position()

        # Iterate through moves and interact with the Position and Piece classes
        for move in self.moves:
            # Validate and apply the move using the Piece and Position classes
            pass

    def parse_metadata(self, content):
        metadata = {}
        metadata_regex = re.compile(r'\[(\w+)\s+"([^"]*)"\]')
        matches = metadata_regex.findall(content)
        for match in matches:
            key, value = match
            metadata[key] = value
        self.metadata = metadata

    def extract_moves(self, content):
        moves_regex = re.compile(r'\d+\.(?:\s*\w+){1,2}')
        self.move_text = moves_regex.findall(content)

    def convert_moves(self):
        self.moves = []
        for move_pair in self.move_text:
            moves = move_pair.strip().split()[1:]  # Remove move number and split into white and black moves
            self.moves.extend(moves)