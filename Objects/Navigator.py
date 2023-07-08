'''
Author:        James Parkington
Created Date:  4/23/2023
Modified Date: 7/8/2023

File containing the implementation of the Navigator class for rendering a list of Position objects
as an interactive slideshow using tkinter.
'''

from   Parser    import *
from   typing    import List
from   itertools import *
from   datetime  import datetime
import tkinter   as tk

class Navigator:
    '''
    This class provides a simple way to view a list of Position objects as an interactive slideshow, allowing the
    user to navigate through positions using the left and right arrow keys.

    Attributes:
        parser1       (Parser)    : The first Parser object containing a game to be displayed in the slideshow.
        parser2       (Parser)    : The optional second Parser object containing another game to be displayed in the slideshow.
        indices       (Tuple)     : An optional list with the start and end indices of the matching sequence between parser1 and parser2.
        active_parser (Parser)    : The currently active Parser object, used to get positions and metadata for the game.
        index         (int)       : The current index in the list of Position objects.
        square_size   (int)       : The size of each square in the chessboard canvas.
        ts            (datetime)  : Used in the match tk.Label to display the upload time to the user.

        root          (tk.Tk)     : The tkinter root object.
        match         (tk.Label)  : The tkinter Label object used to display whether or not this was a matching position.
        event         (tk.Label)  : The tkinter Label object used to display the players in a matched game.
        move          (tk.Label)  : The tkinter Label object used to display the move information.
        turn          (tk.Label)  : The tkinter Label object used to display whose turn it is.
        canvas        (tk.Canvas) : The tkinter Canvas object used to display the chessboard.

        l_arrow       (tk.Button) : The tkinter Button object used to navigate to the previous position.
        r_arrow       (tk.Button) : The tkinter Button object used to navigate to the next position.
        f_arrow       (tk.Button) : The tkinter Button object used to navigate to the first position.
        e_arrow       (tk.Button) : The tkinter Button object used to navigate to the last position.
        toggle        (tk.Button) : The tkinter Button object used to switch between two games.
        frame         (tk.Button) : The tkinter Frame object that ensures all tk.Button objects are horizontally aligned.

    Methods:
        toggle_game      : Switches to the other Parser object and displays that game's position at the same index.
        draw_canvas      : Draws the chessboard corresponding to the current position.
        display_position : Displays the current position on the board_label and move information on the move_label.
        __call__         : Initializes the Navigator and starts the tkinter main loop.
    '''

    def __init__(self, 
                 parser1: Parser,
                 parser2: Optional[Parser] = None,
                 indices: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None):
        
        self.parser1     = parser1
        self.parser2     = parser2
        self.indices     = indices
        self.is_parser1  = True
        self.index       = 0
        self.square_size = 80
        self.ts          = datetime.now().strftime('%b %d, %Y at %-I:%M %p')

        self.root   = tk.Tk()
        self.match  = tk.Label(self.root, font = ("Menlo", 20, "bold"))
        self.event  = tk.Label(self.root, font = ("Menlo", 14, "italic"))
        self.move   = tk.Label(self.root, font = ("Menlo", 12, "bold"))
        self.turn   = tk.Label(self.root, font = ("Menlo", 12))
        self.canvas = tk.Canvas(self.root,
                                width  = self.square_size * 8, 
                                height = self.square_size * 8)

        self.l_arrow = tk.Button(self.root, text = "←", font = ("Menlo", 30), command = self.set_prev_position)
        self.r_arrow = tk.Button(self.root, text = "→", font = ("Menlo", 30), command = self.set_next_position)
        self.f_arrow = tk.Button(self.root, text = "⇤", font = ("Menlo", 30), command = self.set_first_position)
        self.e_arrow = tk.Button(self.root, text = "⇥", font = ("Menlo", 30), command = self.set_end_position)

        self.frame   = tk.Frame(self.root)
        self.con     = tk.Button(self.frame, text = "↣", font = ("Menlo", 30), command = self.set_convergence_position)
        self.div     = tk.Button(self.frame, text = "↛", font = ("Menlo", 30), command = self.set_divergence_position)
        self.toggle  = tk.Button(self.frame, text = "↪", font = ("Menlo", 30), command = self.toggle_game)

    @property
    def active_parser(self):
        return self.parser1 if self.is_parser1 else self.parser2

    @property
    def end_index(self):
        return len(self.active_parser.positions) - 1

    def set_next_position(self, event = None):
        self.index = min(self.index + 1, self.end_index)
        self.display_position()

    def set_prev_position(self, event = None):
        self.index = max(self.index - 1, 0)
        self.display_position()

    def set_first_position(self, event = None):
        self.index = 0
        self.display_position()

    def set_end_position(self, event = None):
        self.index = self.end_index
        self.display_position()

    def set_convergence_position(self, event = None):
        self.index = self.indices[0][0] if self.is_parser1 else self.indices[1][0]
        self.display_position()

    def set_divergence_position(self, event = None):
        self.index = self.indices[0][1] if self.is_parser1 else self.indices[1][1]
        self.display_position()

    def toggle_game(self):
        '''
        Switches to the other Parser object and displays that game's position at the same index. 
        
        If out of index, resets to the last position in the current game.
        '''

        self.is_parser1 = not self.is_parser1
        if self.index > self.end_index:
            self.index = self.end_index
        self.display_position()

    def update_button_states(self):
        '''
        Updates the state of navigation buttons based on the current position index.
        
        If at the first position, disable f_arrow and l_arrow buttons.
        If at the last position, disable e_arrow and r_arrow buttons.
        '''

        if self.index == 0:
            self.f_arrow.config(state = "disabled")
            self.l_arrow.config(state = "disabled")
        else:
            self.f_arrow.config(state = "normal")
            self.l_arrow.config(state = "normal")

        if self.index == self.end_index:
            self.e_arrow.config(state = "disabled")
            self.r_arrow.config(state = "disabled")
        else:
            self.e_arrow.config(state = "normal")
            self.r_arrow.config(state = "normal")

        if self.indices:
            if self.index < self.indices[0][0] or self.index > self.indices[0][1]:
                self.con.config(state = "disabled")
            else:
                self.con.config(state = "normal")

            if self.index < self.indices[0][1] or self.index > self.indices[0][2]:
                self.div.config(state = "disabled")
            else:
                self.div.config(state = "normal")
        else:
            self.con.config(state = "disabled")
            self.div.config(state = "disabled")

        if not self.parser2:
            self.toggle.config(state = "disabled")
        else:
            self.toggle.config(state = "normal")

    def draw_canvas(self):
        '''
        Draws the chessboard corresponding to the current position. The squares are drawn with colors alternating
        between light and dark, and the pieces are drawn as Unicode characters on their respective squares.
        '''

        square_colors = ["#DDB88C", "#A66D4F"]
        pieces = self.active_parser.positions[self.index].get_board()

        for i in range(8):
            for j in range(8):
                x1 = j * self.square_size
                y1 = i * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                color = square_colors[(i+j) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill = color)

                piece = pieces[i][j]
                if piece != " ":
                    if piece.isupper():
                        color = "white"
                    else:
                        color = "black"

                    self.canvas.create_text(x1 + self.square_size/2, y1 + self.square_size/2, text = piece,
                                            font = ("Arial", self.square_size//2), fill = color)

    def display_position(self):
        '''
        Displays the current position on the board_label and move information on the move_label.
        '''

        self.draw_canvas()
        self.update_button_states()

        active_parser_name = "Parser 1" if self.is_parser1 else "Parser 2"
        position = self.active_parser.positions[self.index]

        match_text = active_parser_name + (" (Match)" if self.indices and self.indices[0][0] <= self.index <= self.indices[0][1] else "")
        self.match.config(text = match_text)

        event_text = self.active_parser.get_metadata()['Event'] + " | Uploaded: " + self.ts
        self.event.config(text = event_text)

        move_text = "Move " + str(position.move_number) + ": " + position.move_notation
        self.move.config(text = move_text)

        turn_text = "White's Turn" if position.white_turn else "Black's Turn"
        self.turn.config(text = turn_text)

    def __call__(self):
        '''
        Initializes the Navigator and starts the tkinter main loop.
        '''

        self.root.title("Chess Game Navigator")
        self.root.geometry("800x800")

        self.match.pack()
        self.event.pack()
        self.move.pack()
        self.turn.pack()

        self.canvas.pack()
        self.l_arrow.pack(side = "left")
        self.r_arrow.pack(side = "right")
        self.f_arrow.pack(side = "left")
        self.e_arrow.pack(side = "right")

        self.frame.pack()
        self.con.pack(side = "left")
        self.div.pack(side = "right")
        self.toggle.pack(side = "right")

        self.root.title("Navigator")
        self.root.bind("<Right>", self.set_next_position)
        self.root.bind("<Left>",  self.set_prev_position)
        self.root.bind("<Up>",    self.set_first_position)
        self.root.bind("<Down>",  self.set_end_position)
        self.root.bind("<space>", self.toggle_game)
        self.root.bind("c",       self.set_convergence_position)
        self.root.bind("d",       self.set_divergence_position)

        self.display_position()