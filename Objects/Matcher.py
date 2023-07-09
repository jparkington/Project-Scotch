'''
Author:        James Parkington
Created Date:  3/26/2023
Modified Date: 7/8/2023

File containing the implementation of the Matcher class for comparing user-inputted
positions with a database of existing games and returning the best matching games
and relevant information in a chess game analysis tool.
'''

from Parser             import *
from Utilities          import *
from LCS                import lcs_cython as cy
from typing             import *
from alive_progress     import alive_bar

class Matcher:
    '''
    The Matcher class compares a user-inputted game with a database of existing games and returns the best
    matching games and relevant information in a chess game analysis tool. It uses the Longest Common Subsequence algorithm
    to find the longest sequence of moves that the input game and a game in the database have in common.

    Attributes:
        storage        (Utility) : A Utility object containing the pq_dir and pq_name for finding the games for comparison.
        parser         (Parser)  : A Parser object containing a game to be compared against a Parquet storage of games.
        bitboard_sums  (list)    : The sequence of bitboard sums captured within the supplied Parser object.
        partitions     (list)    : A list of dictionaries containing partition information.
        match          (tuple)   : A tuple containing the best matching PGN string, a list of 2 tuples for the start
                                   and end indices of the matching sequence, and the maximum sequence length. If no
                                   matching games are found, the default value is (None, None, 0).

    Methods:
        process_partition : Processes a single partition and computes the LCS for it.
        find_best_lcs     : Finds the best LCS across all partitions.
        __str__           : Returns a formatted string describing the best matching game and the longest matching sequence.
        __call__          : Executes find_best_lcs and optionally prints the result.
    '''


    def __init__(self, 
                 storage: Utility, 
                 parser:  Parser):
        '''
        Instantiates a Matcher object for comparing a Parser game against a database of games for analysis.
        '''

        self.storage       = storage
        self.parser        = parser
        self.bitboard_sums = [position.bitboard_integers for position in parser.positions]
        self.partitions    = storage.get_metadata()
        self.total_records = sum(self.partitions.values())
        self.match         = (None, None, 0, 0)

    def process_partition(self, part_id: int) -> Tuple[int, List[int]]:
        '''
        Processes a single partition and computes the LCS for it.
        '''

        partition = self.storage.from_parquet(partition = part_id, columns = ["board_sum"])
        return cy.lcs_indices(np.array(self.bitboard_sums, dtype = np.uint64), 
                              np.array(partition['board_sum'].tolist(), dtype = np.uint64))


    def find_best_lcs(self) -> Tuple[Optional[str], Optional[List[Tuple[int, int]]], int]:
        '''
        Finds the best Longest Common Subsequence (LCS) across all partitions.

        This method iterates over the partitions in descending order of total_ply. For each partition, it calculates the LCS 
        and updates the best match if the current LCS is longer. The method stops processing partitions as soon as the length 
        of the best LCS is greater than the total_ply of the next partition, as it's impossible for a longer LCS to exist in 
        the remaining partitions.

        A progress bar is displayed using the alive-progress package, showing the progress of the task and the longest 
        sequence of ply found so far.

        Args:
            None

        Returns:
            A tuple containing the Parser object for the best match, the indices of the best match, and the length of the best match.
        '''

        print()
        with alive_bar(self.total_records, bar = 'smooth', dual_line = True) as bar:
            remaining = self.total_records
            for total_ply, num_records in self.partitions.items():
                
                if self.match[2] > total_ply:
                    bar(remaining)
                    break

                bar.text(f'Reviewed all games ≥ {total_ply} ply. Longest sequence ({self.match[2]}): {"".join(["♟︎", "♙"] * (self.match[2] // 2) + ["♟︎"] * (self.match[2] % 2))}')
                bar(num_records)
                remaining -= num_records
                
                lcs_length, lcs_indices = self.process_partition(total_ply)
                if lcs_length > self.match[2]:
                    self.match = (None, lcs_indices, lcs_length, total_ply)

        # Retrieve the best match from storage
        match_row    = self.storage.from_parquet(partition = self.match[3], columns = ['ply', 'pgn'], rows = [self.match[1][1][0]])
        match_pgn    = match_row.iloc[0]['pgn']
        match_parser = Parser(match_pgn, False)
        game_start   = match_row.iloc[0]['ply']
        game_indices = [self.match[1][0], (game_start, game_start + self.match[2] - 1)] # Relate indices to the start of the matched game
        
        self.match = (match_parser, game_indices, self.match[2], self.match[3])

    def __str__(self) -> str:

        match_info = self.match
        if not match_info[0]: return "No matching games found."

        positions   = match_info[0].positions
        metadata    = match_info[0].metadata
        start_match = positions[match_info[1][1][0]]
        end_match   = positions[match_info[1][1][1]]
        start_move  = start_match.move_number
        end_move    = end_match.move_number

        return (f"\nYour closest game match is {metadata.get('White', '')} vs. {metadata.get('Black', '')} in {metadata.get('Date', '').split('.')[0]}."
                f"\nThe longest matching sequence starts{(' from the beginning' if start_move == 0 else f' with {start_match.move_notation} at move {start_move}')}"
                f" and continues for {match_info[2]} ply to {end_match.move_notation} at move {end_move}.")

    def __call__(self):

        self.find_best_lcs()
        print(self)
        return self.match