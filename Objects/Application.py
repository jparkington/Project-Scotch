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

def main():
    parser = Parser(load_pgn_file())
    match  = Matcher(parser)()
    Navigator(parser, match[0], match[1])()

if __name__ == "__main__":
    main()

# Remove "+[CATransaction synchronize] called within transaction"
# Error when attempting to test gms file
# Add about 10,000 games to Storage (maybe from a well-known event across years--use an import if possible)