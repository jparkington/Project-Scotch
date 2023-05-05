'''
Author:        James Parkington
Created Date:  4/15/2023
Modified Date: 4/22/2023

File containing a demonstration of the PGN class usage for parsing a PGN file
and interacting with the Position and Piece classes in a chess game analysis tool.
'''
import threading
from Matcher   import *
from Navigator import *
from Parser    import *
from Utilities import *

def run_with_timeout(func, timeout):
        def stop_program():
            print(f"Program terminated after {timeout} minutes.")
            sys.exit(0)

        timer = threading.Timer(timeout * 60, stop_program)
        timer.start()
        try:
            func()
        finally:
            timer.cancel()

def main():

    files  = Utility()
    # parser = Parser(files())
    # match  = Matcher(files, parser)()
    # Navigator(parser, match[0], match[1])()

    # df = files.from_parquet()
    # print(df.compute())

    
    # This addendum allows for large directories of files to be looped through efficiently when running archive_multipgn
    import os
    import gc

    def process_files_in_chunks(file_list, chunk_size):
        for i in range(0, len(file_list), chunk_size):
            yield file_list[i:i + chunk_size]

    if __name__ == "__main__":
        dir_path = "/Users/Macington/Documents/Chess PGNs"
        all_files = [os.path.join(dir_path, file) for file in os.listdir(dir_path) if file.endswith('.pgn') and file.startswith('WorldCup')]
        
        for chunk in process_files_in_chunks(all_files, 50):
            for file_path in chunk:
                Utility(pgn_path = file_path).archive_multipgn()
            
            # Clear any unreferenced objects and run garbage collection
            del chunk
            gc.collect()
    
    

if __name__ == "__main__":
    run_with_timeout(main, 200)


# Move unique_ids into an initialized argument, so it can be used in both find_match and the handle_exact_method logic
# After that, move no storage and exact match logic directly into __call__
# Simplify their code structure by making the default for match (None, None 0), instead of just None (if safe to do so)

# Isn't this supposed to use lru caching or something?
# Shouldn't this be using indexed fields and not just matching unindexed?
# It doesn't seem like this is using the partition names at all to help guide and simplify the initial search process
# Ideally, the initial search process grabs at least a sequence number to work with, which then allows us to filter out all games with a ply lower than that sequence, before peforming a second round of lcs
# I don't see memoization hereor pre-processing

# Do we have too many partitions at too small of a file size? Maybe the first two moves should be the partition directory?

'''
Is there any way you can think of to take advantage of Dask to chunk the search itself up to return results more quickly?

Also, are there any packages or modules you're aware of that can be used to speed up the lcd algorithm?
'''