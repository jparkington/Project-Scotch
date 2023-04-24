'''
Author:        James Parkington
Created Date:  3/26/2023
Modified Date: 4/15/2023

File containing the implementation of the Matcher class for comparing user-inputted
positions with a database of existing games and returning the best matching games
and relevant information in a chess game analysis tool.
'''

import pyarrow.parquet as pq
import pandas as pd
from Position import *
from typing import List

class Matcher:
    def __init__(self, parquet_path: str):
        self.parquet_path = parquet_path

    def get_parquet_path(self):
        return self.parquet_path

    def set_parquet_path(self, parquet_path: str):
        self.parquet_path = parquet_path

    def load_games(self) -> pd.DataFrame:
        return pq.read_table(self.get_parquet_path()).to_pandas()

    def find_best_match(self, positions: List[Position]) -> pd.DataFrame:
        games = self.load_games()
        best_match = None
        longest_match = 0

        for index, game in games.iterrows():
            game_positions = game['positions']
            common_positions = 0

            for user_pos, game_pos in zip(positions, game_positions):
                if user_pos == game_pos:
                    common_positions += 1
                else:
                    break

            if common_positions > longest_match:
                longest_match = common_positions
                best_match = game

        return best_match, longest_match