'''
Author:        James Parkington
Created Date:  3/26/2023
Modified Date: 4/24/2023

File containing the implementation of the Matcher class for comparing user-inputted
positions with a database of existing games and returning the best matching games
and relevant information in a chess game analysis tool.
'''

from Parser      import *
from Utilities   import *
from typing      import *
import itertools as it
import pandas    as pd

class Matcher:
    '''
    Matcher class for comparing user-inputted positions with a database of existing games and returning the best
    matching games and relevant information in a chess game analysis tool.

    Attributes:
        parser       (Parser): A Parser object containing a game to be compared against a Parquet storage of games.
        parquet_name (str):    The name of the Parquet file containing the stored games.
        parquet_dir  (str):    The directory in which the Parquet file is stored.
        games        (Dict):   Contains game ids as keys and their corresponding DataFrames as values
        match        (Tuple):  A tuple with a Parser object, coordinates, and sequence for the game with the longest matching sequence to parser.

    Methods:
        load_games(): Loads games from the Parquet file into a pandas DataFrame.
        find_match(): Finds the best matching game based on the longest sequence of matching moves.
        __str__():    Returns a formatted string describing the best matching game and the longest matching sequence.
        __call__():   Executes find_match and optionally prints the result.
    '''

    def __init__(self,
                 parser:         Parser,
                 parquet_name:   Optional[str] = None, 
                 parquet_dir:    Optional[str] = None):
        
        self.parser       = parser
        self.parquet_name = parquet_name
        self.parquet_dir  = parquet_dir
        self.games        = {id: df for id, df in self.load_games().groupby('id')}
        self.match        = None

    def get_parser(self):
        return self.parser

    def get_parquet_name(self):
        return self.parquet_name or "Storage"

    def get_parquet_dir(self):
        return self.parquet_dir or save_path(True, "Games")
    
    def get_match(self):
        return self.match
    
    def set_parser(self, parser):
        self.parser = parser

    def set_parquet_name(self, parquet_name: str):
        self.parquet_name = parquet_name

    def set_parquet_dir(self, parquet_dir: str):
        self.parquet_dir = parquet_dir

    def set_match(self, match):
        self.match = Parser(match[0], False), match[1], match[2]


    def load_games(self) -> pd.DataFrame:
        '''
        Loads games from the Parquet file into a pandas DataFrame, so long as they have at least one matching position.

        Returns:
            A pandas DataFrame containing the game data.
        '''
        
        return from_parquet(self.get_parquet_name(), self.get_parquet_dir())
    
    
    def find_match(self) -> Tuple[Optional[Parser], Optional[List[Tuple[int, int]]], int]:
        '''
        Finds the best matching game based on the longest sequence of matching moves.

        Returns:
            A tuple containing a Parser object of the best-matching PGN string, a list of 2 tuples for the start
            and end indices of the matching sequence, and the maximum sequence length. If no matching games are
            found, returns (None, None, 0).

        Variables:
            i - index of the position in the user's game
            j - index of the position in the loaded game
            g - DataFrame containing rows of the loaded game with a specific id

        Steps:
            1. Create a dictionary 'games' containing game ids as keys and their corresponding DataFrames as values.
            2. Get the positions from the user's game using the parser.
            3. Define the 'find_sequences' generator, which finds the longest matching sequence of positions between the user's game and all loaded games.
            4. Use itertools.product to create a Cartesian product of games' items, positions, and games.
            5. Iterate through the Cartesian product and calculate the longest continuous matching sequence of bitboards using itertools.takewhile.
            6. Yield the PGN string of the game, and the indices of the matching sequence in the user's game and the loaded game.
            7. Find the best match by selecting the game with the longest sequence.
        '''

        positions     = self.parser.get_positions()
        num_positions = len(positions)
        num_games     = len(self.games)

        def find_sequences():
            for g, i, j in it.product(self.games.values(), range(num_positions), range(num_games)):
                if j >= len(g):
                    continue

                seq = sum(1 for _ in it.takewhile(lambda ij: positions[ij[0]].get_bitboard_integers() == g.loc[ij[1]]['bitboards'].tolist(),
                                                 zip(it.count(i), it.count(j))))

                yield g.iloc[0]['pgn'], [(i, i + seq - 1), (j, j + seq - 1)], seq

                if len(positions) - i <= seq:
                    break

        self.set_match(max(find_sequences(), key = lambda x: x[2], default = (None, None, 0)))
    

    def __str__(self) -> str:
        '''
        Returns a formatted string describing the best matching game and the longest matching sequence.

        Returns:
            str: A string describing the best matching game and the longest matching sequence. If no matching games
                 are found, returns "No matching games found."
        '''

        match_info = self.get_match()
        if not match_info[0]: return "No matching games found."

        positions      = self.parser.get_positions()
        metadata       = match_info[0].get_metadata()
        start_match = positions[match_info[1][0][0]]
        start_move  = start_match.get_move_number()
        end_match   = positions[match_info[1][0][1]]
        # position.get_move_notation()
        return (f"Your closest game match is {metadata.get('White', '')} vs. {metadata.get('Black', '')} in {metadata.get('Date', '').split('.')[0]}."
                f" The longest matching sequence starts{(' from the beginning' if start_move == 0 else f' with {start_match.get_move_notation()} at move {start_move}')}"
                f" and continues for {match_info[2]} ply to {end_match.get_move_notation()} at move {end_match.get_move_number()}.")
    
# series of {match_info[2]} ply
    def __call__(self, 
                 print_result: bool = True):
        '''
        Executes find_match and optionally prints the result.

        Args:
            print_result (bool, optional): If True, prints the result to the terminal. Defaults to True.
        '''

        self.find_match()
        if print_result: print(self)
        return self.get_match()