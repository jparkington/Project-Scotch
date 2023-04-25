'''
Author:        James Parkington
Created Date:  4/15/2023
Modified Date: 4/23/2023

This utility module provides functions for generating data, converting it into a pandas DataFrame, saving it to a CSV file, and constructing file paths.
It also contains a function to load the ipython-sql extension and establish a connection to a SQLite database.
It is meant to be used by other classes or scripts that require similar functionality.

Functions:
    save_path:        Constructs a file path based on the provided subdirectories and an optional parent directory
    open_pgn:         Opens a dialog box to let users choose a .pgn file
    create_dataframe: Creates a pandas DataFrame from a list of positions and a PGN object.
    to_parquet:       Save a pandas DataFrame as a Parquet file with a given file name and directory.
    from_parquet:     Read a Parquet file and return it as a pandas DataFrame.
'''

from   typing             import *
from   tkinter            import Tk
from   tkinter.filedialog import askopenfilename
import pandas             as pd
import os

def save_path(use_parent: bool, 
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


def open_pgn():
    '''
    Opens a file dialog and returns the selected file path as a string.

    Returns:
        str: The selected file path.
    '''

    root = Tk()
    root.withdraw()
    file_path = askopenfilename(title="Select a PGN file", filetypes=[("PGN files", "*.pgn")])
    root.destroy()
    return file_path


def create_dataframe(positions, pgn) \
                    -> pd.DataFrame:
    '''
    Creates a pandas DataFrame from a list of positions and a PGN object.

    This function iterates through the given positions and extracts relevant information, such as the
    game hash, PGN string, move number, and bitboard integers. The resulting DataFrame can be used for
    storage, analysis, or matching.

    Args:
        positions (List[Position]): A list of Position objects representing the positions in the game.
        pgn (Parser): The Parser object containing the PGN file and related methods.

    Returns:
        pd.DataFrame: A DataFrame containing the extracted information from the positions and PGN object.
    '''

    game_hash  = pgn.generate_game_hash(positions)
    pgn_string = str(pgn.get_game())
        
    data = [{"id"          : game_hash,
             "pgn"         : pgn_string,
             "move_number" : i.get_move_number(),
             "bitboards"   : i.get_bitboard_integers()

            } for i in positions]

    return pd.DataFrame(data)


def to_parquet(data:         pd.DataFrame, 
               parquet_name: str,
               parquet_dir:  str,
               append:       bool = True):
    '''
    Save a pandas DataFrame as a Parquet file with a given file name and directory.

    Args:
        data:         The pandas DataFrame to save as a Parquet file.
        parquet_name: The name of the Parquet file.
        parquet_dir:  The directory to save the Parquet file.

    For the MVP, this does not actually append data, but a production version would require that.
    '''

    # Create the Parquet directory if it doesn't exist
    if not os.path.exists(parquet_dir):
        os.makedirs(parquet_dir)
    
    parquet_file_path = os.path.join(parquet_dir, parquet_name)
    data.to_parquet(parquet_file_path)


def from_parquet(parquet_name, parquet_dir):
    '''
    Read a Parquet file and return it as a pandas DataFrame.

    Args:
        parquet_name: The name of the Parquet file.
        parquet_dir:  The directory where the Parquet file is located.

    Returns:
        A pandas DataFrame containing the data from the Parquet file.
    '''
    
    parquet_file_path = os.path.join(parquet_dir, parquet_name)

    if not os.path.exists(parquet_file_path):
        raise FileNotFoundError(f"File '{parquet_file_path}' not found.")

    return pd.read_parquet(parquet_file_path)