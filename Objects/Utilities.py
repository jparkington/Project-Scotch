'''
Author:        James Parkington
Created Date:  4/15/2023
Modified Date: 4/15/2023

This utility module provides functions for generating data, converting it into a pandas DataFrame, saving it to a CSV file, and constructing file paths.
It also contains a function to load the ipython-sql extension and establish a connection to a SQLite database.
It is meant to be used by other classes or scripts that require similar functionality.

Functions:
    save_path:    Constructs a file path based on the provided subdirectories and an optional parent directory inclusion
    to_dataframe: Converts the generated data to a pandas DataFrame, sorts it, and optionally saves it to a SQLite database table and/or a CSV file
    load_sql:     Loads the ipython-sql extension and establishes a connection to a SQLite database
'''

from   IPython import get_ipython
import pandas  as pd
import sqlite3 as sq
import os

def save_path(use_parent_directory, *subdirs):
    '''
    Construct a file path based on the provided subdirectories.
    Optionally, include the parent directory in the path.

    Args:
        use_parent_directory (bool): If True, include the parent directory in the path.
        subdirs (str): Subdirectories to include in the path.

    Returns:
        str: The constructed file path.
    '''
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if use_parent_directory else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *subdirs)



def to_dataframe(data, 
                 by        = None, 
                 ascending = True,
                 add_id    = True, 
                 sql_table = None):
    '''
    Return a pandas DataFrame representation of the data dictionary object.
    Optionally save the DataFrame to a CSV file if the filename is provided.

    Args:
        data (dict): The data to be converted to a DataFrame.
        by (str or list of str, optional): Column(s) to sort the DataFrame by.
        ascending (bool, optional): Sort order for the specified columns. Defaults to True.
        sql_table (str, optional): Name of the SQL table to save the DataFrame to.

    Returns:
        pd.DataFrame: The sorted DataFrame with an id column added.
    
    Considerations:
        An id column is added with monotonically increasing integers starting from 1 to facilitate record identification and improve query performance.
        If ascending is skipped, the function will apply the default True to all columns in the by argument
    '''
    df = pd.DataFrame(data)
    if by:
        df = df.sort_values(by        = by, 
                            ascending = ascending)

    if add_id:
        df.insert(0, 'id', range(1, len(df) + 1))

    if sql_table:
        df.to_sql(sql_table, 
                  sq.connect(save_path(True, 'Data', 'jane.db')),
                  if_exists = 'replace', 
                  index     = False)
        
    return df


def load_sql():
    '''
    Load the ipython-sql extension and establish a connection to the SQLite database.
    
    This function is designed to be used in Jupyter Notebooks. It loads the ipython-sql extension and connects to the SQLite database using the provided file path.
    '''
    ipy = get_ipython()
    
    # Check if the 'sql' extension is already loaded
    if not ipy.find_line_magic("sql"):
        ipy.run_line_magic("load_ext", "sql")
        
    ipy.run_line_magic("sql", f"sqlite:///{save_path(True, 'Data', 'jane.db')}")