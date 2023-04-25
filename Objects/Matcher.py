'''
Author:        James Parkington
Created Date:  3/26/2023
Modified Date: 4/24/2023

File containing the implementation of the Matcher class for comparing user-inputted
positions with a database of existing games and returning the best matching games
and relevant information in a chess game analysis tool.
'''

from Position  import *
from Utilities import *
from typing    import *
import pandas as pd

class Matcher:
    '''
    Matcher class for comparing user-inputted positions with a database of existing games and returning the best
    matching games and relevant information in a chess game analysis tool.

    Attributes:
        parquet_name (str): The name of the Parquet file containing the stored games.
        parquet_dir  (str): The directory in which the Parquet file is stored.

    Methods:
        load_games():       Loads games from the Parquet file into a pandas DataFrame.
        find_best_match():  Finds the best matching game based on the longest sequence of matching moves.
    '''

    def __init__(self,
                 user_submitted: List[str],
                 parquet_name:   Optional[str] = None, 
                 parquet_dir:    Optional[str] = None):
        
        self.user_submitted = user_submitted
        self.parquet_name   = parquet_name
        self.parquet_dir    = parquet_dir


    def get_user_submitted(self):
        return self.user_submitted

    def get_parquet_name(self):
        return self.parquet_name or "Storage"

    def get_parquet_dir(self):
        return self.parquet_dir or save_path(True, "Games")
    
    def set_user_submitted(self, user_submitted):
        self.user_submitted = user_submitted

    def set_parquet_name(self, parquet_name: str):
        self.parquet_name = parquet_name

    def set_parquet_dir(self, parquet_dir: str):
        self.parquet_dir = parquet_dir


    def load_games(self) -> pd.DataFrame:
        '''
        Load games from the Parquet file into a pandas DataFrame.

        Returns:
            A pandas DataFrame containing the game data.
        '''

        return from_parquet(self.get_parquet_name(), self.get_parquet_dir())
    

    def find_best_match(self) -> Tuple[str, int]:
        '''
        Finds the best matching game based on the longest sequence of matching moves.

        Returns:
            A tuple containing the best-matching PGN string and the number of matching moves.
        '''

        games         = self.load_games()
        best_match    = None
        longest_match = 0

        # Get unique game_hashes
        ids = games['id'].unique()

        # Iterate through each unique game_hash
        for id in ids:
            # Filter the games DataFrame to only include rows with the current game_hash
            game_rows = games[games['id'] == id]

            common_moves = 0

            # Iterate through the moves in the current game
            for user_move, game_row in zip(self.get_user_submitted(), game_rows.iterrows()):
                _, game = game_row
                game_move = game['bitboards'].tolist()
                
                if user_move.get_bitboard_integers() == game_move:
                    common_moves += 1
                else:
                    break

            # Update the best match if the current game has more matching moves
            if common_moves > longest_match:
                longest_match = common_moves
                best_match = game['pgn']
                total_moves = len(game_rows)

        return best_match, longest_match, total_moves