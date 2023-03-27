'''
File containing the implementation of the PGNParser class for parsing PGN files
and generating Position objects in a chess game analysis tool.

Created on 3/26/2023
James Parkington
'''

class PGNParser:
    """
    Attributes:
        pgn (str): The file path of the PGN file to parse or a string containing the PGN data.

    Methods:
        parse_pgn():           Reads the PGN file or string and generates a list of Position objects for each game in the file.
        parse_metadata(pgn):   Extracts and returns metadata (e.g., event, site, date, players) from a given PGN string.
        pgn_to_positions(pgn): Converts a given PGN string into a sequence of Position objects, each representing a distinct position in the game.
    """

    def __init__(self, pgn):
        self.pgn = pgn

    # Accessors
    def get_pgn(self):
        return self.pgn

    # Mutators
    def set_pgn(self, pgn):
        self.pgn = pgn

    # Other Methods
    def parse_pgn(self):
        """
        Reads the PGN file or string and generates a list of Position objects for each game in the file or string.
        """
        pass

    def parse_metadata(self, pgn):
        """
        Extracts and returns metadata (e.g., event, site, date, players) from a given PGN string.
        """
        pass

    def pgn_to_positions(self, pgn):
        """
        Converts a given PGN string into a sequence of Position objects, each representing a distinct position in the game.
        """
        pass