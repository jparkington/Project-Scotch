'''
Author:        James Parkington
Created Date:  4/15/2023
Modified Date: 4/23/2023

This utility module provides functions for generating data, converting it into a pandas DataFrame, saving it to a CSV file, and constructing file paths.
It also contains a function to load the ipython-sql extension and establish a connection to a SQLite database.
It is meant to be used by other classes or scripts that require similar functionality.

Functions:
    save_path:    Constructs a file path based on the provided subdirectories and an optional parent directory
    open_pgn:     Opens a dialog box to let users choose a .pgn file
    to_dataframe: Converts the generated data to a pandas DataFrame, sorts it, and optionally saves it to a SQLite database table and/or a CSV file
'''

from   IPython            import get_ipython
from   typing             import *
from   tkinter            import Tk
from   tkinter.filedialog import askopenfilename
import pandas             as pd
import sqlite3            as sq
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


# def to_dataframe(data:      Dict[str, Any], 
#                  by:        Optional[List[str]] = None, 
#                  ascending: bool                = True,
#                  add_id:    bool                = True, 
#                  filename:  Optional[str]       = None,
#                  sql_table: Optional[str]       = None) \
#                 -> pd.DataFrame:
#     '''
#     Return a pandas DataFrame representation of the data dictionary object.
#     Optionally save the DataFrame to a CSV file if the filename is provided.

#     Args:
#         data:      The data to be converted to a DataFrame.
#         by:        Column(s) to sort the DataFrame by (optional).
#         ascending: Sort order for the specified columns (optional, default: True).
#         add_id:    Whether to add an id column (optional, default: True).
#         filename:  Name of the CSV file to save the DataFrame to (optional).
#         sql_table: Name of the SQL table to save the DataFrame to (optional).

#     Returns:
#         The sorted DataFrame with an id column added (if specified).
    
#     Considerations:
#         An id column is added with monotonically increasing integers starting from 1 to facilitate record identification and improve query performance.
#         If ascending is skipped, the function will apply the default True to all columns in the by argument
#     '''
#     df = pd.DataFrame(data)
#     if by:
#         df = df.sort_values(by        = by, 
#                             ascending = ascending)

#     if add_id:
#         df.insert(0, 'id', range(1, len(df) + 1))

#     if filename:
#         df.to_csv(filename, index = False)

#     if sql_table:
#         df.to_sql(sql_table, 
#                   sq.connect(),
#                   if_exists = 'replace', 
#                   index     = False)
        
#     return df