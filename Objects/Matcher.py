'''
Author:        James Parkington
Created Date:  3/26/2023
Modified Date: 5/9/2023

File containing the implementation of the Matcher class for comparing user-inputted
positions with a database of existing games and returning the best matching games
and relevant information in a chess game analysis tool.
'''

from Parser             import *
from Utilities          import *
from LCS                import lcs_cython as cy
from typing             import *
from concurrent.futures import *
from alive_progress     import alive_bar

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
        self.partitions    = storage.get_partition_metadata()
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


    def process_partition(self, part_id: int) -> Tuple[pd.DataFrame, int, List[int]]:
        '''
        Processes a single partition and computes the LCS for it.
        '''

        partition = self.storage.from_parquet(partitions = part_id).compute()
        return partition, cy.lcs_indices(np.array(self.get_bitboard_sums(),        dtype = np.uint64), 
                                         np.array(partition['board_sum'].tolist(), dtype = np.uint64))


    def find_best_lcs(self) -> Tuple[Optional[str], 
                                     Optional[List[Tuple[int, int]]], 
                                     int]:
        '''
        Finds the best LCS across all partitions.

        This method uses ThreadPoolExecutor to process multiple partitions concurrently, which improves performance
        by taking advantage of multiple CPU cores. It submits futures for each partition and processes them in the order
        they complete using the as_completed function. It cancels any remaining futures with a partition_id less than the
        best match found so far, further improving performance by avoiding unnecessary computations.

        A progress bar is displayed using the alive-progress package, showing the progress of the task and the longest 
        sequence of ply found so far.

        The time complexity of this algorithm depends on the number of partitions, the number of CPU cores, and the time
        required to process each partition. In the worst case, the time complexity is O(n), where n is the number of partitions.
        However, due to concurrency and early stopping, the actual execution time is typically much lower.
        '''

        print()
        with alive_bar(sum(self.partitions.values()), bar = 'smooth', dual_line = True) as bar:

            with ThreadPoolExecutor() as executor:

                futures = {executor.submit(self.process_partition, p): p for p in self.get_partitions()}
                for future in as_completed(futures):
                    seq = self.get_match()[2]
                    bar.text(f'Reviewed all games ≥ {futures[future]} ply. Longest sequence ({seq}): {"".join(["♟︎", "♙"] * (seq // 2) + ["♟︎"] * (seq % 2))}')
                    bar(self.partitions[futures[future]])

                    for cancelled, partition_id in list(futures.items()):
                        if partition_id < seq:
                            cancelled.cancel()

                    try: partition, metadata = future.result()
                    except CancelledError: continue

                    if metadata[0] > self.match[2]:
                        match_parser = Parser(partition.iloc[metadata[1][1][1]]['pgn'], False)
                        metadata[1][1] = (partition.iloc[metadata[1][1][0]]['ply'],
                                          partition.iloc[metadata[1][1][1]]['ply'])
                        self.set_match((match_parser, metadata[1], metadata[0]))

    
    def __str__(self) -> str:
        '''
        Returns a formatted string describing the best matching game and the longest matching sequence.
        '''

        match_info   = self.get_match()
        if not match_info[0]: return "No matching games found."

        positions   = match_info[0].get_positions()
        metadata    = match_info[0].get_metadata()
        start_match = positions[match_info[1][1][0]]
        end_match   = positions[match_info[1][1][1]]
        start_move  = start_match.get_move_number()
        end_move    = end_match.get_move_number()

        return (f"\nYour closest game match is {metadata.get('White', '')} vs. {metadata.get('Black', '')} in {metadata.get('Date', '').split('.')[0]}."
                f"\nThe longest matching sequence starts{(' from the beginning' if start_move == 0 else f' with {start_match.get_move_notation()} at move {start_move}')}"
                f" and continues for {match_info[2]} ply to {end_match.get_move_notation()} at move {end_move}.")
    
    
    def __call__(self, 
                 print_result: bool = True):
        '''
        Executes find_best_lcs and optionally prints the result.
        '''

        self.find_best_lcs()
        if print_result: print(self)
        return self.get_match()