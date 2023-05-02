'''
Author:        James Parkington
Created Date:  3/26/2023
Modified Date: 4/24/2023

File containing the implementation of the Matcher class for comparing user-inputted
positions with a database of existing games and returning the best matching games
and relevant information in a chess game analysis tool.
'''

from Parser           import *
from Utilities        import *
from typing           import *
from dask.diagnostics import ProgressBar
import itertools    as it
import dask         as dk
import dask.delayed as delayed

class Matcher:
    '''
    Matcher class for comparing user-inputted positions with a database of existing games and returning the best
    matching games and relevant information in a chess game analysis tool.

    Attributes:
        files       (Utility):   A Utility object containing the pq_dir and pq_name for finding the games for comparison.
        parser      (Parser):    A Parser object containing a game to be compared against a Parquet storage of games.
        positions   (List):      The sequence of Position objects captured within the supplied Parser object.
        match       (Tuple):     A tuple with a Parser object, coordinates, and sequence for the game with the longest matching sequence to parser.
        exact_match (bool):      Whether or not the submitted parser already matches a game in storage.
        storage     (DataFrame): Contains a large DataFrame of all games in Storage.

    Methods:
        find_match(): Finds the best matching game based on the longest sequence of matching moves.
        __str__():    Returns a formatted string describing the best matching game and the longest matching sequence.
        __call__():   Executes find_match and optionally prints the result.
    '''

    def __init__(self,
                 files:  Utility,
                 parser: Parser):
        
        self.parser      = parser
        self.positions   = parser.get_positions()
        self.match       = None
        self.exact_match = False
        self.storage     = files.from_parquet(columns = ['id', 'bitboards', 'pgn'])

    def get_parser(self):
        return self.parser
    
    def get_positions(self):
        return self.positions
    
    def get_match(self):
        return self.match

    def get_exact_match(self):
        return self.exact_match
    
    def set_parser(self, parser):
        self.parser = parser

    def set_positions(self, positions):
        self.positions = positions

    def set_match(self, parser, indices, seq):
        self.match = (parser, indices, seq)

    def set_exact_match(self, exact_match):
        self.exact_match = exact_match
    
    
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

        if self.storage is None:
            print("No storage available. Matching algorithms only work with a storage component. Proceeding to navigate through the submitted game.")
            return self.set_match(None, None, 0)

        positions     = self.get_positions()
        unique_ids    = set(self.storage['id'])
        num_positions = len(positions)

        game_id = self.parser.generate_id(self.positions)
        if game_id in unique_ids:
            game = self.storage[self.storage['id'] == game_id].compute()
            self.handle_exact_match(Parser(game.iloc[0]['pgn'], False))
            return self.set_match(None, None, 0)

        def find_sequence(g, i, j):
            g_filtered = g[g['index'] == j].compute()
            if not g_filtered.empty:
                bb = g_filtered.iloc[0]['bitboards'].tolist()
                seq = sum(1 for _ in it.takewhile(lambda k: positions[i+k].get_bitboard_integers() == bb,
                                                range(min(num_positions - i, len(g) - j))))
                return seq
            return 0

        results = []
        for idx, id in enumerate(unique_ids, start=1):
            print(f"Processing game {idx} out of {len(unique_ids)}")
            g = self.storage[self.storage['id'] == id]
            max_seq = delayed(max)((delayed(find_sequence)(g, i, j) for i in range(num_positions) for j in range(len(g))), default=0)
            pgn = g['pgn'].compute().iloc[0]
            results.append((pgn, max_seq))
        
        with ProgressBar():
            best_seq = dk.compute(*results)

        max_value = max(best_seq, key=lambda x: x[1])
        self.set_match(Parser(max_value[0], False), None, max_value[1])

    
    def handle_exact_match(self, 
                           parser:  Parser):
        '''
        Handles exact matches by printing a message with relevant information about the matching game.
        '''

        metadata = parser.get_metadata()
        self.set_exact_match(True)
        print(f"This game is an exact match of {metadata.get('White', '')} vs. {metadata.get('Black', '')} in {metadata.get('Date', '').split('.')[0]} in our database.")
    

    def __str__(self) -> str:
        '''
        Returns a formatted string describing the best matching game and the longest matching sequence.

        Returns:
            str: A string describing the best matching game and the longest matching sequence. If no matching games
                 are found, returns "No matching games found."
        '''

        match_info = self.get_match()
        if not match_info[0]: return "No matching games found."

        positions   = self.get_positions()
        metadata    = match_info[0].get_metadata()
        start_match = positions[match_info[1][0][0]]
        start_move  = start_match.get_move_number()
        end_match   = positions[match_info[1][0][1]]

        return (f"Your closest game match is {metadata.get('White', '')} vs. {metadata.get('Black', '')} in {metadata.get('Date', '').split('.')[0]}."
                f" The longest matching sequence starts{(' from the beginning' if start_move == 0 else f' with {start_match.get_move_notation()} at move {start_move}')}"
                f" and continues for {match_info[2]} ply to {end_match.get_move_notation()} at move {end_match.get_move_number()}.")
    
    def __call__(self, 
                 print_result: bool = True):
        '''
        Executes find_match and optionally prints the result.

        Args:
            print_result (bool, optional): If True, prints the result to the terminal. Defaults to True.
        '''

        self.find_match()
        if print_result and not self.get_exact_match: print(self)
        return self.get_match()