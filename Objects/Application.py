'''
Author:        James Parkington
Created Date:  4/15/2023
Modified Date: 4/22/2023

File containing a demonstration of the PGN class usage for parsing a PGN file
and interacting with the Position and Piece classes in a chess game analysis tool.
'''

from Matcher   import *
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

    # Matcher would go here, print the desired outputs about match percentage, and prompt the user about continuing, returning another PGN object
    pgn       = Parser(pgn_path)
    positions = pgn.get_positions()
    metadata  = pgn.get_metadata()
    source    = pgn.get_source()
    navigator = Navigator(positions, metadata, source)
    navigator()

    matched   = Matcher(positions)
    best_game, matched_moves, total_moves = matched.find_best_match()
    print(*matched.find_best_match())

if __name__ == "__main__":
    main()


# Left to Implement
# Maybe something like, "Your closest game match is I vs. J on 1981, in which you had X out of Y of the same moves. Your longest matching sequence was Z moves from A to B. Would you like to take a look at those moves? (Requires Renderer.py class with tkinter)
# Next dialog: "Would you like to see how the I vs. J match continued from your longest sequence?"
# Maybe a prompt at upload that says "We already have this exact game played out: w vs. b in y"
# Check if the game is in the program's history and have a dialog if not (would you like to add this game to the historical record?)


'''
You should also write a report that describes the following:

1) Project description
2) Any changes to the project from Planning document #2
3) Reflection - describe what you learned by implementing this project also what would you do differently if you could go back and start over knowing what you know now.
4) Acknowledgements/Citations - who did you work with, what sources did you use.
'''