'''
Author:        James Parkington
Created Date:  4/15/2023
Modified Date: 4/22/2023

File containing a demonstration of the PGN class usage for parsing a PGN file
and interacting with the Position and Piece classes in a chess game analysis tool.
'''
import time
from Matcher   import *
from Navigator import *
from Parser    import *
from Utilities import *


def main():
    # start = time.time()
    # files  = Utility()
    # parser = Parser(files())
    # match  = Matcher(files, parser)()
    # Navigator(parser, match[0], match[1])()

    # elapsed_time = time.time() - start
    # print(f"Elapsed time: {elapsed_time:.2f} seconds")

    import os
    import gc

    def process_files_in_chunks(file_list, chunk_size):
        for i in range(0, len(file_list), chunk_size):
            yield file_list[i:i + chunk_size]

    utility = Utility('config')
    if __name__ == "__main__":
        dir_path = "/Users/Macington/Documents/Roux/Downloaded"
        all_files = [os.path.join(dir_path, file) for file in os.listdir(dir_path) if file.endswith('.pgn')]
        
        for chunk in process_files_in_chunks(all_files, 50):
            for file_path in chunk:
                files = Utility(file_path)
                files.archive_multipgn()
            
            # Clear any unreferenced objects and run garbage collection
            del chunk
            gc.collect()

    # Before running this, sort out partition strategy

if __name__ == "__main__":
    main()


# Explore a partitioning structure where the first X moves are in progressive sub-directories, instead of partioning on year, which is meaningless for the analysis
# How big should X be? First idea is that it should be at least as long as any legal chess game (e.g. 8 ply). Is there justification for going deeper?
# Any merit to naming the directories with the bitboard sums vs. strings of move notations? What's better/faster for exploration and retrieval? Since the existing logic uses bitboard matches, maybe that can facilitate faster matching inside the Matcher class, since the logic would be crawling through these same directories anyway.
# Notes for Matcher
# Can I get away with matching/writing bitboard sums as I write with ply for the sake of faster sequencing? I think that's worth exploring.
# See if lru_cahching is useful at all in the Matcher class