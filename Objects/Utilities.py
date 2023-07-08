'''
Author:        James Parkington
Created Date:  4/15/2023
Modified Date: 5/9/2023

FIle that provides methods for working with PGN files, generating data, converting it into a pandas DataFrame,
saving and reading data from Parquet files, and constructing file paths. It is meant to be used by other classes or 
scripts that require similar functionality.
'''

from   Parser          import *
from   typing          import *
from   tkinter         import filedialog
import dask.dataframe  as dd
import dask            as dk
import pandas          as pd
import pyarrow.parquet as pa
import os
import sys

class Utility:
    '''
    Utility class that provides methods for working with PGN files, generating data, converting it into a pandas DataFrame,
    saving and reading data from Parquet files, and constructing file paths. Requires creating an instance of the class to use its methods.

    Attributes:
        pgn_path      (str) : The path to the PGN file.
        pq_dir        (str) : The directory to save the Parquet file.
        pq_name       (str) : The name of the Parquet file.
        partition_col (str) : The name of the column used for partitioning the Parquet file. Defaults to 'total_ply'.
    
    Methods:
        get_partition_metadata : Retrieves the id and length of each partition in the Parquet file storage.
        save_path              : Constructs a file path based on the provided subdirectories and an optional parent directory.
        open_pgn               : Opens a dialog box to let users choose a .pgn file.
        load_pgn_file          : Load a PGN file either from a command-line argument or through a file dialog.
        to_parquet             : Save a pandas DataFrame as a Parquet file with a given file name and directory.
        create_dataframe       : Creates a pandas DataFrame from a list of positions and a PGN object.
        archive_multipgn       : Processes a PGN file with multiple games and appends each game to the parquet storage file.
        from_parquet           : Read a Parquet file and return it as a pandas DataFrame.
    '''

    def __init__(self, 
                 pgn_path:      str = None,
                 pq_dir:        str = "Games",
                 pq_name:       str = "Storage",
                 partition_col: str = "total_ply"):
        
        self.pgn_path      = pgn_path or self.get_initial_pgn_path()
        self.pq_path       = self.get_initial_pq_path(pq_dir, pq_name)
        self.partition_col = partition_col


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
    
    def get_partition_col(self):
        return self.partition_col

    
    def get_partition_metadata(self):
        '''
        Retrieves the id and length of each partition in the Parquet file storage.

        This method iterates through the Parquet file storage and collects metadata for each partition, 
        including the partition_id and the total number of rows in that partition. The metadata is 
        stored in a dictionary, with partition_ids as keys and total_rows as values.
        '''

        partitions = [d for d in os.listdir(self.pq_path) if d.startswith(f'{self.partition_col}=')]
        metadata   = {}

        for partition_id in sorted([int(p.split('=')[1]) for p in partitions], reverse = True):
            partition_path = os.path.join(self.pq_path, f'{self.partition_col}={partition_id}')
            parquet_files = [f for f in os.listdir(partition_path) if f.endswith('.parquet')]
            total_rows = 0

            for parquet_file in parquet_files:
                parquet_metadata = pa.read_metadata(os.path.join(partition_path, parquet_file))
                total_rows += parquet_metadata.num_rows

            metadata[partition_id] = total_rows

        return metadata


    def save_path(self,
                  use_parent: bool, 
                  *subdirs:   str) -> str:
        '''
        Construct a file path based on the provided subdirectories.
        Optionally, include the parent directory in the path.

        Arguments:
            use_parent : If True, include the parent directory in the path.
            subdirs    : Subdirectories to include in the path.
        '''

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) \
                   if use_parent else os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(base_dir, *subdirs)

    
    def open_file(self, file_type: str = "PGN"):
        '''
        Opens a file dialog and returns the selected file path as a string. The file type defaults to "PGN".
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
                   target_size: int  = 64 * 1024 * 1024):
        '''
        Save a Dask DataFrame as a Parquet file with a given file name and directory.

        Arguments:
            input       : The Parser object to convert to a DataFrame, or an existing DataFrame, to save as a Parquet file.
            is_parser   : A flag indicating if the input_df is a Parser object. Defaults to True.
            append      : If True, appends the DataFrame to an existing Parquet file, if it exists. Defaults to True.
            write       : If True, proceeds to write the resulting DataFrame to the object's pq_path.
            partitions  : A list of column names to partition the data by.
            target_size : The desired partition size for the output Parquet file in bytes. Defaults to 64 * 1024 * 1024.
        '''

        try:
            df = self.create_dataframe(input) if is_parser else input
            if isinstance(df, dd.DataFrame) and df.npartitions > 0:
                df = df.repartition(npartitions = max(int(df.memory_usage(deep = True).sum().compute() / target_size), 1))

                if write:
                    file_exists = os.path.exists(self.pq_path)
                    if not file_exists and append: append = False

                    df.to_parquet(self.pq_path,
                                  partition_on        = [self.partition_col],
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
        '''
    
        game_id     = parser.generate_id(parser.positions)
        pgn_string  = str(parser.get_game())
        total_ply   = len(parser.positions)

        delayed_data = [dk.delayed(pd.DataFrame({"game_id"   : game_id,
                                                 "pgn"       : pgn_string,
                                                 "total_ply" : total_ply,
                                                 "ply"       : ply,
                                                 "board_sum" : i.bitboard_integers}, 
                                                 index       = [game_id * 100000 + ply]))

                        for ply, i in enumerate(parser.positions)]

        return dd.from_delayed(delayed_data)


    def archive_multipgn(self):
        '''
        Processes a PGN file with multiple games and appends each game to the parquet storage file.

        This method reads a PGN file containing multiple games, and for each game, it creates a Parser
        object, converts the game data into a DataFrame, and appends it to the existing parquet storage
        file using the to_parquet method.
        '''

        path = self.pgn_path
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
                     partitions = None) -> dd.DataFrame:
        '''
        Reads a Parquet directory and returns it as a Dask DataFrame, with optional columm and partition selection
        '''

        pq_path = self.pq_path
        if not os.path.exists(pq_path): 
            print(f"File '{pq_path}' not found. Please select a Parquet file.")
            pq_path = self.open_file("parquet")

        if partitions:
            if not isinstance(partitions, (list, set, tuple)):
                partitions = [partitions]
            filters = [(self.partition_col, 'in', partitions)]
        else:
            filters = None

        return dd.read_parquet(pq_path, 
                               columns = columns, 
                               filters = filters) if pq_path else None
    

    def __call__(self):
        '''
        Allows a Utility() object to more concisely return a pgn_path.
        '''

        return self.pgn_path