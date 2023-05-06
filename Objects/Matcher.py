'''
Author:        James Parkington
Created Date:  3/26/2023
Modified Date: 5/05/2023

File containing the implementation of the Matcher class for comparing user-inputted
positions with a database of existing games and returning the best matching games
and relevant information in a chess game analysis tool.

To-do: Test a Hirschberg implementation. 
       See if fastlcs is more optimized for these sequences.
'''

from   Parser    import *
from   Utilities import *
from   typing    import *
import dask      as dk

class Matcher:
    '''
    Matcher class for comparing user-inputted positions with a database of existing games and returning the best
    matching games and relevant information in a chess game analysis tool.

    Attributes:
        storage         (Utility): A Utility object containing the pq_dir and pq_name for finding the games for comparison.
        parser          (Parser):  A Parser object containing a game to be compared against a Parquet storage of games.
        bitboard_sums   (List):    The sequence of bitboard sums captured within the supplied Parser object.
        partitions      (List):    A list of dictionaries containing partition information.
        match           (Tuple):   A tuple containing the best matching PGN string, a list of 2 tuples for the start
                                   and end indices of the matching sequence, and the maximum sequence length. If no
                                   matching games are found, the default value is (None, None, 0).

    Methods:
        lcs_indices():        Finds the longest common subsequence (LCS) and its indices for two sequences.
        process_partition():  Processes a single partition and computes the LCS for it.
        sort_partitions():    Sorts the partitions based on their total_ply values.
        find_best_lcs():      Finds the best LCS across all partitions.
        __str__():            Returns a formatted string describing the best matching game and the longest matching sequence.
        __call__():           Executes find_best_lcs and optionally prints the result.
    '''

    def __init__(self,
                 storage: Utility,
                 parser:  Parser):

        self.storage       = storage
        self.parser        = parser
        self.bitboard_sums = [i.get_bitboard_integers() for i in parser.get_positions()]
        self.partitions    = storage.from_parquet(columns = ['total_ply']).compute().to_dict('records')
        self.match         = (None, None, 0)


    def get_storage(self):
        return self.storage
    
    def get_parser(self):
        return self.parser

    def get_bitboard_sums(self):
        return self.bitboard_sums

    def get_partitions(self):
        return self.partitions
    
    def get_match(self):
        return self.match

    def set_storage(self, storage):
        self.utility = storage

    def set_parser(self, parser):
        self.parser = parser

    def set_bitboard_sums(self, bitboard_sums):
        self.bitboard_sums = bitboard_sums

    def set_partitions(self, partitions):
        self.partitions = partitions

    def set_match(self, match):
        self.match = match


    @staticmethod
    def lcs_indices(short_seq: List[int], 
                    long_seq:  List[int]) \
                    -> Tuple[int, List[int]]:
        '''
        Finds the longest common subsequence (LCS) and its indices for two sequences.

        This implementation uses bit-parallelism to compute the LCS. It represents the dynamic programming table using bit vectors, 
        which allows bitwise operations to calculate the table's entries more efficiently. This approach is particularly suitable 
        for cases where the alphabet is small, as in the case of bitboard sums for chess positions.

        While this method is not as memory-efficient as a Hirschberg implementation, the bit-parallel algorithm can be faster in practice, 
        especially for small alphabets and sequences with limited lengths, due to the efficient bitwise operations.

        Args:
            short_seq (List[int]): The shorter sequence for which to find the LCS.
            long_seq  (List[int]): The longer sequence for which to find the LCS.
        '''

        m = len(long_seq)
        w = 64
        b = {x: np.zeros((m + w - 1) // w, dtype = np.uint64) for x in set(short_seq)}

        for i, x in enumerate(long_seq[1:]):
            b[x][(i + 1) // w] |= 1 << ((i + 1) % w)

        dp = np.zeros((m + w - 1) // w, dtype=np.uint64)
        for x in short_seq[1:]:
            dp[:-1], dp[-1] = dp[:-1] | ((dp[:-1] & b[x][:-1]) + (dp[1:] & b[x][1:])) << 1, dp[-1] | (dp[-1] & b[x][-1]) << 1

        length = 0
        indices = []
        for i in range(w):
            current_length = sum(bin(dp[j] >> i).count('1') for j in range(dp.size))
            if current_length > length:
                length  = current_length
                indices = [j * w + i for j in range(dp.size) if (dp[j] >> i) & 1]

        return length, indices
    

    def process_partition(self, partition_id: int) -> Tuple[int, List[int]]:
        '''
        Processes a single partition and computes the LCS for it.
        '''

        partition = self.utility.from_parquet(partitions = partition_id)
        sequences = partition['board_sum'].compute().tolist()
        return self.lcs_indices(self.bitboard_sums, sequences)
    
    
    def sort_partitions(self) -> List[Dict]:
        '''
        Sorts the partitions based on their total_ply values.
        '''

        return sorted(self.partitions, 
                      key     = lambda p: p['total_ply'], 
                      reverse = True)


    def find_best_lcs(self) -> Tuple[Optional[str], 
                                     Optional[List[Tuple[int, int]]], 
                                     int]:
        '''
        Finds the best LCS across all partitions.

        The best_lcs_length variables is a tuple containing the best matching PGN string,
        a list of 2 tuples for the start and end indices of the matching sequence, and the maximum sequence length.
        '''

        for partition in self.sort_partitions():
            lcs_length, indices = dk.delayed(self.process_partition)(partition['id'])
            if lcs_length > self.match[2]:
                self.set_match((partition['pgn'], indices, lcs_length))

            if self.match[2] >= partition['total_ply']:
                break
    
    
    def __str__(self) -> str:
        '''
        Returns a formatted string describing the best matching game and the longest matching sequence.
        '''

        match_info = self.get_match()
        if not match_info[0]: return "No matching games found."

        positions   = self.parser.get_positions()
        metadata    = match_info[0].get_metadata()
        start_match = positions[match_info[1][0][0]]
        end_match   = positions[match_info[1][0][1]]
        start_move  = start_match.get_move_number()
        end_move    = end_match.get_move_number()

        return (f"Your closest game match is {metadata.get('White', '')} vs. {metadata.get('Black', '')} in {metadata.get('Date', '').split('.')[0]}."
                f" The longest matching sequence starts{(' from the beginning' if start_move == 0 else f' with {start_match.get_move_notation()} at move {start_move}')}"
                f" and continues for {match_info[2]} ply to {end_match.get_move_notation()} at move {end_move}.")
    
    
    def __call__(self, 
                 print_result: bool = True):
        '''
        Executes find_best_lcs and optionally prints the result.
        '''

        self.find_best_lcs()
        if print_result: print(self)
        return self.get_match()