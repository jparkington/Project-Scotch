'''
Author:        James Parkington
Created Date:  4/15/2023
Modified Date: 4/15/2023

File containing a demonstration of the PGN class usage for parsing a PGN file
and interacting with the Position and Piece classes in a chess game analysis tool.
'''

from PGN       import *
from Utilities import *

def main():
    # Create a PGN object with the path to your sample PGN file
    pgn = PGN(save_path(True, 'Games', 'sample.pgn'))

    # Parse the PGN file, extracting metadata and moves
    pgn.parse_pgn()

    # Print the metadata and moves extracted from the PGN file
    print("Metadata:")
    for key, value in pgn.metadata.items():
        print(f"{key}: {value}")

    print("\nMoves:")
    for i, move in enumerate(pgn.moves, start=1):
        print(f"{i}. {move}")

if __name__ == "__main__":
    main()