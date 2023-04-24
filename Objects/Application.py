'''
Author:        James Parkington
Created Date:  4/15/2023
Modified Date: 4/22/2023

File containing a demonstration of the PGN class usage for parsing a PGN file
and interacting with the Position and Piece classes in a chess game analysis tool.
'''

from Navigator import *
from Parser    import *
from Utilities import *
import sys

def main():
    if len(sys.argv) > 1:
        pgn_path = sys.argv[1]
    else:
        pgn_path = open_pgn()
        if not pgn_path:
            print("No file selected.")
            return

    pgn       = Parser(pgn_path)
    metadata  = pgn.get_metadata()
    positions = pgn.get_positions()
    navigator = Navigator(positions)

    navigator()

    # Print the board state for the initial position and a few other positions
    print("\nInitial position:")
    print(positions[0])

    print("\nPosition after move 5 (with bitboards):")
    print(positions[5 * 2 - 1].get_bitboard_strings())

    print("\nPosition after move 10 (with full bitstrings):")
    print(positions[10 * 2 - 1].get_bitboard_strings(True))

if __name__ == "__main__":
    main()


# Maybe something like, "Your closest game match is I vs. J on 1981, in which you had X out of Y of the same moves. Your longest matching sequence was Z moves from A to B. Would you like to take a look at those moves? (Requires Renderer.py class with tkinter)
# Next dialog: "Would you like to see how the I vs. J match continued from your longest sequence?"
# Also for the database, design an ID based on a hex of all the PGN moves and see if that ID exists first

'''
Your Final Project is a time to show how you can put everything together.  You should create a project based on your own interests that has the following characteristics:

4) Is thoroughly tested

You should also write a report that describes the following:

1) Project description
2) Any changes to the project from Planning document #2
3) Reflection - describe what you learned by implementing this project also what would you do differently if you could go back and start over knowing what you know now.
4) Acknowledgements/Citations - who did you work with, what sources did you use.
'''