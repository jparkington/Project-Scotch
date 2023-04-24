'''
Author:        James Parkington
Created Date:  4/23/2023
Modified Date: 4/23/2023

File containing the implementation of the Navigator class for rendering a list of Position objects
as an interactive slideshow using tkinter.
'''

from   Position  import *
from   typing    import List
from   itertools import *
import tkinter as tk

class Navigator:
    '''
    Attributes:
        positions (List[Position]): The list of Position objects to be displayed in the slideshow.
        index (int):                The current index in the list of Position objects.
        square_size (int):          The size of each square in the chessboard canvas.
        root (tk.Tk):               The tkinter root object.
        move (tk.Label):            The tkinter Label object used to display the move information.
        turn (tk.Label):            The tkinter Label object used to display whose turn it is.
        canvas (tk.Canvas):         The tkinter Canvas object used to display the chessboard.
        l_arrow (tk.Button):        The tkinter Button object used to navigate to the previous position.
        r_arrow (tk.Button):        The tkinter Button object used to navigate to the next position.
        f_arrow (tk.Button):        The tkinter Button object used to navigate to the first position.
        e_arrow (tk.Button):        The tkinter Button object used to navigate to the last position.

    Methods:
        draw_canvas():      Draws the chessboard corresponding to the current position.
        display_position(): Displays the current position on the board_label and move information on the move_label.
        first_position():   Navigates to the next position in the list.
        prev_position():    Navigates to the previous position in the list.
        first_position():   Navigates to the first position in the list.
        end_position():     Navigates to the last position in the list.
        __call__():         Initializes the Navigator and starts the tkinter main loop.

    This class provides a simple way to view a list of Position objects as an interactive slideshow, allowing the
    user to navigate through positions using the left and right arrow keys.
    '''

    def __init__(self, positions: List[Position]):
        self.positions   = positions
        self.index       = 0
        self.square_size = 80

        self.root   = tk.Tk()
        self.move   = tk.Label(self.root, font = ("Menlo", 18, "bold"))
        self.turn   = tk.Label(self.root, font = ("Menlo", 12))
        self.canvas = tk.Canvas(self.root,
                                width  = self.get_square_size() * 8, 
                                height = self.get_square_size() * 8)

        self.l_arrow = tk.Button(self.root, text = "◀",  font = ("Arial Unicode MS", 26), command = self.prev_position)
        self.r_arrow = tk.Button(self.root, text = "▶",  font = ("Arial Unicode MS", 26), command = self.next_position)
        self.f_arrow = tk.Button(self.root, text = "◀◀", font = ("Arial Unicode MS", 26), command = self.first_position)
        self.e_arrow = tk.Button(self.root, text = "▶▶", font = ("Arial Unicode MS", 26), command = self.end_position)


    def get_positions(self):
        return self.positions

    def get_index(self):
        return self.index
    
    def get_square_size(self):
        return self.square_size
    
    def set_positions(self, positions):
        self.positions = positions

    def set_index(self, index):
        self.index = index

    def set_square_size(self, square_size):
        self.square_size = square_size


    def draw_canvas(self):
        '''
        Draws the chessboard corresponding to the current position.
        
        This method creates a rectangle for each square on the chessboard and fills it with a color based on the square's 
        index. It then adds the corresponding chess piece to the center of each square. The chessboard is drawn on the 
        tkinter canvas, which is then packed and visible in the tkinter window.
        '''
        position    = self.get_positions()[self.get_index()]
        board       = position.get_board()
        square_size = self.get_square_size()
        colors      = ["#E0E0E0", "#B0B0B0"] * 4 + ["#B0B0B0", "#E0E0E0"] * 4
        squares     = [square for row in board for square in row]

        for i, (color, square) in enumerate(zip(cycle(colors), squares)):
            j = i % 8
            x = j * square_size
            y = (i // 8) * square_size
            self.canvas.create_rectangle(x, y, x + square_size, y + square_size, fill = color)
            self.canvas.create_text(x + square_size / 2, y + square_size / 2 - square_size / 20, text = square, 
                                     font = ("Arial Unicode MS", int(square_size * 0.8)), fill = 'black')


    def display_position(self):
        '''
        Displays the current position on the board_label and move information on the move_label.
        
        This method updates the text of the move_label with the move information in typical chess parlance (e.g., "1. e4" for the first move) 
        and updates the text of the board_label with the string representation of the current position. It then ensures that both labels are 
        packed and visible in the tkinter window.
        '''

        position = self.get_positions()[self.get_index()]

        self.canvas.delete("all")
        self.draw_canvas()

        self.move.config(text = f"{position.get_move_number()}. {position.get_move_notation()}", pady = 10)
        self.turn.config(text = "Black to Move" if position.white_turn else "White to Move",     pady = 10)

        self.move.pack()
        self.canvas.pack()
        self.turn.pack()

        self.f_arrow.pack(side = "left")
        self.l_arrow.pack(side = "left")
        self.e_arrow.pack(side = "right")
        self.r_arrow.pack(side = "right")


    def next_position(self, event = None):
        self.set_index(min(self.get_index() + 1, len(self.get_positions()) - 1))
        self.display_position()

    def prev_position(self, event = None):
        self.set_index(max(self.get_index() - 1, 0))
        self.display_position()

    def first_position(self, event = None):
        self.set_index(0)
        self.display_position()

    def end_position(self, event = None):
        self.set_index(len(self.get_positions()) - 1)
        self.display_position()


    def __call__(self):
        self.root.title("Navigator")
        self.root.bind("<Right>", self.next_position)
        self.root.bind("<Left>",  self.prev_position)
        self.root.bind("<Up>",    self.first_position)
        self.root.bind("<Down>",  self.end_position)

        self.display_position()
        self.root.mainloop()