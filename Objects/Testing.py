"""
Author:        James Parkington
Created Date:  4/15/2023
Modified Date: 4/24/2023

Tests for the Parser, Position, Navigator, and Matcher classes

This test suite assumes that you employ the same folder structure as the repo
if you attempt to test any of the Parquet functions in Utilities.py. Note that some of these tests
are going to fail, because I was actively trying to rework methods in each of the classes, based on
results from this unit test.
"""

from Matcher   import Matcher
from Navigator import Navigator
from Parser    import Parser
from Position  import Position
from Utilities import *
from chess     import pgn
from typing    import *
import tkinter as tk
import unittest


class TestParser(unittest.TestCase):

    def setUp(self):
        self.parser = Parser(save_path(True, "Games", "sample.pgn"))

    def test_read_game(self):
        '''Test if the parser can read a game from the PGN file.'''
        game = self.parser.read_game()
        self.assertIsInstance(game, pgn.Game)

    def test_get_metadata(self):
        '''Test if the parser can extract metadata from the PGN file.'''
        metadata = self.parser.get_metadata()
        self.assertIsInstance(metadata, dict)

    def test_get_positions(self):
        '''Test if the parser can extract a list of Position objects.'''
        positions = self.parser.get_positions()
        self.assertIsInstance(positions, List)
        self.assertTrue(all(isinstance(pos, Position) for pos in positions))

    def test_generate_game_hash(self):
        '''Test if the parser can generate a hash string for a list of Position objects.'''
        positions = self.parser.get_positions()
        game_hash = Parser.generate_game_hash(positions)
        self.assertIsInstance(game_hash, str)

    def test_parser_initialization(self):
        '''Test if the parser is initialized with the correct PGN file.'''
        self.assertEqual(self.parser.pgn_path, save_path(True, "Games", "sample.pgn"))


class TestPosition(unittest.TestCase):

    def setUp(self):
        self.parser    = Parser(save_path(True, "Games", "sample.pgn"))
        self.positions = self.parser.get_positions()

    def test_position_from_chess_board(self):
        '''Test if a Position object can be created from a chess.Board object.'''
        board    = self.parser.get_game().board()
        position = Position.from_chess_board(board)
        self.assertIsInstance(position, Position)

    def test_position_get_board(self):
        '''Test if a Position object can return a chess.Board object.'''
        position = self.positions[0]
        board = position.get_board()
        self.assertIsInstance(board, List)
        self.assertTrue(all(isinstance(row, List) for row in board))


class TestNavigator(unittest.TestCase):
    
    def setUp(self):
        self.positions = [Position() for _ in range(5)]
        self.metadata  = {"White": "W_Player", "Black": "B_Player", "Date": "2023.04.24"}
        self.source    = "user"
        self.navigator = Navigator(self.positions, self.metadata, self.source)

    def test_initialization(self):
        '''Test the initialization of the Navigator class and its attributes.'''
        self.assertEqual(self.navigator.positions,   self.positions)
        self.assertEqual(self.navigator.metadata,    self.metadata)
        self.assertEqual(self.navigator.source,      self.source)
        self.assertEqual(self.navigator.index,       0)
        self.assertEqual(self.navigator.square_size, 80)
        self.assertIsInstance(self.navigator.root,   tk.Tk)

    def test_set_and_get_index(self):
        '''Test the set_index and get_index methods of the Navigator class.'''
        self.navigator.set_index(2)
        self.assertEqual(self.navigator.get_index(), 2)

    def test_set_and_get_square_size(self):
        '''Test the set_square_size and get_square_size methods of the Navigator class.'''
        self.navigator.set_square_size(60)
        self.assertEqual(self.navigator.get_square_size(), 60)


class TestMatcher(unittest.TestCase):
    
    def setUp(self):
        self.user_submitted = [Position() for _ in range(3)]
        self.parquet_name   = "Storage"
        self.parquet_dir    = save_path(True, "Games")
        self.matcher        = Matcher(self.user_submitted, self.parquet_name, self.parquet_dir)

    def test_initialization(self):
        '''Test the initialization of the Matcher class and its attributes.'''
        self.assertEqual(self.matcher.user_submitted, self.user_submitted)
        self.assertEqual(self.matcher.parquet_name,   self.parquet_name)
        self.assertEqual(self.matcher.parquet_dir,    self.parquet_dir)

    def test_set_and_get_user_submitted(self):
        '''Test the set_user_submitted and get_user_submitted methods of the Matcher class.'''
        new_user_submitted = [Position() for _ in range(2)]
        self.matcher.set_user_submitted(new_user_submitted)
        self.assertEqual(self.matcher.get_user_submitted(), new_user_submitted)

    def test_set_and_get_parquet_name(self):
        '''Test the set_parquet_name and get_parquet_name methods of the Matcher class.'''
        new_parquet_name = "new_test_storage"
        self.matcher.set_parquet_name(new_parquet_name)
        self.assertEqual(self.matcher.get_parquet_name(), new_parquet_name)

    def test_set_and_get_parquet_dir(self):
        '''Test the set_parquet_dir and get_parquet_dir methods of the Matcher class.'''
        new_parquet_dir = "new_test_dir"
        self.matcher.set_parquet_dir(new_parquet_dir)
        self.assertEqual(self.matcher.get_parquet_dir(), new_parquet_dir)

    def test_load_games(self):
        '''Test the load_games method of the Matcher class.'''
        # Load games using the test parquet file
        loaded_games = self.matcher.load_games()
        self.assertIsInstance(loaded_games, pd.DataFrame)

    def test_find_best_match(self):
        '''Test the find_best_match method of the Matcher class.'''
        best_match, longest_match, total_moves = self.matcher.find_best_match()
        self.assertIsInstance(best_match,    str)
        self.assertIsInstance(longest_match, int)
        self.assertIsInstance(total_moves,   int)


if __name__ == "__main__":
    unittest.main()