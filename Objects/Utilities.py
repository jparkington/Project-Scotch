'''
Author:        James Parkington
Created Date:  4/15/2023
Modified Date: 4/28/2023

FIle that provides methods for working with PGN files, generating data, converting it into a pandas DataFrame,
saving and reading data from Parquet files, and constructing file paths. It is meant to be used by other classes or 
scripts that require similar functionality.
'''

from   Parser         import *
from   typing         import *
from   tkinter        import filedialog
import dask.dataframe as dd
import dask           as dk
import numpy          as np
import pandas         as pd
import os
import sys

class Utility:
    '''
    Utility class that provides methods for working with PGN files, generating data, converting it into a pandas DataFrame,
    saving and reading data from Parquet files, and constructing file paths. Requires creating an instance of the class to use its methods.

    Attributes:
        pgn_path (str): The path to the PGN file.
        pq_name  (str): The name of the Parquet file.
        pq_dir   (str): The directory to save the Parquet file.
    
    Methods:
        save_path:         Constructs a file path based on the provided subdirectories and an optional parent directory.
        open_pgn:          Opens a dialog box to let users choose a .pgn file.
        load_pgn_file:     Load a PGN file either from a command-line argument or through a file dialog.
        to_parquet:        Save a pandas DataFrame as a Parquet file with a given file name and directory.
        create_dataframe:  Creates a pandas DataFrame from a list of positions and a PGN object.
        archive_multipgn:  Processes a PGN file with multiple games and appends each game to the parquet storage file.
        from_parquet:      Read a Parquet file and return it as a pandas DataFrame.
    '''

    def __init__(self, 
                 pgn_path: str = None,
                 pq_dir:   str = "Games",
                 pq_name:  str = "Storage"):
        
        self.pgn_path = pgn_path or self.get_initial_pgn_path()
        self.pq_path  = self.get_initial_pq_path(pq_dir, pq_name)


    def get_initial_pgn_path(self):
        if len(sys.argv) > 1:
            return sys.argv[1]
        else:
            return self.open_file()
        
    def get_initial_pq_path(self, pq_dir, pq_name):
        dir_loc = self.save_path(True, pq_dir)
        if not os.path.exists(dir_loc): os.makedirs(dir_loc)
        return os.path.join(self.save_path(True, pq_dir, pq_name))
    
    def get_pgn_path(self):
        return self.pgn_path

    def get_pq_path(self):
        return self.pq_path
    
    def set_pgn_path(self, pgn_path):
        self.pgn_path = pgn_path

    def set_pq_path(self, pq_path):
        self.pq_path = pq_path


    def save_path(self,
                  use_parent: bool, 
                  *subdirs:   str) \
                  -> str:
        '''
        Construct a file path based on the provided subdirectories.
        Optionally, include the parent directory in the path.

        Args:
            use_parent: If True, include the parent directory in the path.
            subdirs:    Subdirectories to include in the path.

        Returns:
            str: The constructed file path.'''

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) \
                   if use_parent else os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(base_dir, *subdirs)

    
    def open_file(self, file_type: str = "PGN"):
        '''
        Opens a file dialog and returns the selected file path as a string.

        Args:
            file_type: The file type to open. Defaults to "PGN".
        '''


        file_path = filedialog.askopenfilename(title     = f"Select a {file_type} file",
                                               filetypes = [(f"{file_type} files", f"*.{file_type.lower()}")])
        if not file_path:
            return None

        return file_path

    
    def to_parquet(self,
                   input:       Union[Parser, dd.DataFrame],
                   is_parser:   bool = True,
                   append:      bool = True,
                   write:       bool = True,
                   partitions:  List = ["first_moves"],
                   target_size: int  = 64 * 1024 * 1024):
        '''
        Save a Dask DataFrame as a Parquet file with a given file name and directory.

        Args:
            input:       The Parser object to convert to a DataFrame, or an existing DataFrame, to save as a Parquet file.
            is_parser:   A flag indicating if the input_df is a Parser object. Defaults to True.
            append:      If True, appends the DataFrame to an existing Parquet file, if it exists. Defaults to True.
            write:       If True, proceeds to write the resulting DataFrame to the object's pq_path.
            partitions:  A list of column names to partition the data by.
            target_size: The desired partition size for the output Parquet file in bytes. Defaults to 64 * 1024 * 1024.
        '''

        try:
            df = self.create_dataframe(input).dropna(subset = partitions) if is_parser else input
            if isinstance(df, dd.DataFrame) and df.npartitions > 0:
                df = df.repartition(npartitions = max(int(df.memory_usage(deep = True).sum().compute() / target_size), 1))

                if write:
                    file_exists = os.path.exists(self.get_pq_path())
                    if not file_exists and append: append = False

                    df.to_parquet(self.get_pq_path(),
                                  partition_on        = partitions,
                                  write_metadata_file = True,
                                  engine              = "pyarrow",
                                  compression         = "snappy",
                                  append              = append,
                                  ignore_divisions    = True)
                return df

        except Exception as e:
            print(f"Error while writing Parquet file: {e}")
            if is_parser: print(f"PGN: {input.get_pgn_input()}")
    

    def create_dataframe(self, parser) -> dd.DataFrame:
        '''
        Creates a Dask DataFrame from a list of positions and a PGN object.

        This function iterates through the given Parser object's positions and extracts relevant information, 
        such as the game hash, PGN string, move number, and bitboard integers. The resulting DataFrame can be 
        used for storage, analysis, or matching.

        Args:
            parser (Parser): The Parser object containing the PGN file and related methods.
        '''
    
        positions   = parser.get_positions()
        game_id     = parser.generate_id(positions)
        pgn_string  = str(parser.get_game())
        first_moves = '-'.join([p.get_move_notation() for p in positions[1:4]])
        total_ply   = len(positions)

        delayed_data = [dk.delayed(pd.DataFrame({"id"          : game_id,
                                                 "pgn"         : pgn_string,
                                                 "first_moves" : first_moves,
                                                 "total_ply"   : total_ply,
                                                 "ply"         : ply,
                                                 "move_number" : i.get_move_number(),
                                                 "bitboards"   : i.get_bitboard_integers(),
                                                 "board_sum"   : sum(i.get_bitboard_integers(), np.uint64(0))}))

                        for ply, i in enumerate(positions)]

        return dd.from_delayed(delayed_data)


    def archive_multipgn(self):
        '''
        Processes a PGN file with multiple games and appends each game to the parquet storage file.

        This method reads a PGN file containing multiple games, and for each game, it creates a Parser
        object, converts the game data into a DataFrame, and appends it to the existing parquet storage
        file using the to_parquet method.
        '''

        path = self.get_pgn_path()
        with open(path, 'r') as file:

            dataframes = []
            game       = chess.pgn.read_game(file)

            while game:

                try:
                    dataframes.append(self.to_parquet(Parser(str(game), False), write = False))
                    game = chess.pgn.read_game(file)

                except chess.IllegalMoveError:
                    print("Skipping a game due to IllegalMoveError.")
            
            if dataframes:
                concatenated_df = dd.concat(dataframes)
                self.to_parquet(concatenated_df, is_parser = False)
            
            print(f"Completed processing PGN file: {path}")

        '''
        # This addendum allows for large directories of files to be looped through efficiently when running archive_multipgn
        import os
        import gc

        def process_files_in_chunks(file_list, chunk_size):
            for i in range(0, len(file_list), chunk_size):
                yield file_list[i:i + chunk_size]

        if __name__ == "__main__":
            dir_path = "/Users/Macington/Documents/Roux/Downloaded"
            all_files = [os.path.join(dir_path, file) for file in os.listdir(dir_path) if file.endswith('.pgn')]
            
            for chunk in process_files_in_chunks(all_files, 50):
                for file_path in chunk:
                    Utility(pgn_path = file_path).archive_multipgn()
                
                # Clear any unreferenced objects and run garbage collection
                del chunk
                gc.collect()
        '''

    
    def from_parquet(self, 
                     columns    = None,
                     partitions = None) \
                     -> dd.DataFrame:
        '''
        Reads a Parquet directory and returns it as a Dask DataFrame, with optional columm and partition selection
        '''

        pq_path = self.get_pq_path()
        if not os.path.exists(pq_path): 
            print(f"File '{pq_path}' not found. Please select a Parquet file.")
            pq_path = self.open_file("parquet")

        pq_path = self.get_pq_path()
        if not os.path.exists(pq_path): 
            print(f"File '{pq_path}' not found. Please select a Parquet file.")
            pq_path = self.open_file("parquet")

        filters = [('partitions', 'in', partitions)] if partitions else None
        return dd.read_parquet(pq_path, columns = columns, filters = filters) if pq_path else None
    

    def __call__(self):
        '''
        Allows a Utility() object to more concisely return a pgn_path.
        '''

        return self.get_pgn_path()