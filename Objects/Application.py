'''
Author:        James Parkington
Created Date:  4/15/2023
Modified Date: 4/22/2023

File containing a demonstration of the PGN class usage for parsing a PGN file
and interacting with the Position and Piece classes in a chess game analysis tool.
'''

from PGN       import *
from Utilities import *

def main():
    # Create a PGN object
    pgn       = PGN(save_path(True, 'Games', 'sample.pgn'))
    positions = pgn()

    # Print the metadata extracted from the PGN file
    print("Metadata:")
    for key, value in pgn.metadata.items():
        print(f"{key}: {value}")

    # Print the board state for the initial position and a few other positions
    print("\nInitial position:")
    print(positions[0])

    print("\nPosition after move 5:")
    print(positions[5 * 2 - 1])

    print("\nPosition after move 10:")
    print(positions[10 * 2 - 1])

if __name__ == "__main__":
    main()