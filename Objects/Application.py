from Matcher   import *
from Navigator import *
from Parser    import *
from Utilities import *

def main():

    files  = Utility()
    parser = Parser(files())
    match  = Matcher(files, parser)()
    Navigator(parser, match[0], match[1])()

if __name__ == "__main__":
    main()