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
    Attributes:
        parser1       (Parser):    The first Parser object containing a game to be displayed in the slideshow.
        parser2       (Parser):    The optional second Parser object containing another game to be displayed in the slideshow.
        indices       (Tuple):     An optional list with the start and end indices of the matching sequence between parser1 and parser2.
        active_parser (Parser):    The currently active Parser object, used to get positions and metadata for the game.
        index         (int):       The current index in the list of Position objects.
        square_size   (int):       The size of each square in the chessboard canvas.
        ts            (datetime):  Used in the match tk.Label to display the upload time to the user.

        root          (tk.Tk):     The tkinter root object.
        match         (tk.Label):  The tkinter Label object used to display whether or not this was a matching position.
        event         (tk.Label):  The tkinter Label object used to display the players in a matched game.
        move          (tk.Label):  The tkinter Label object used to display the move information.
        turn          (tk.Label):  The tkinter Label object used to display whose turn it is.
        canvas        (tk.Canvas): The tkinter Canvas object used to display the chessboard.

        l_arrow       (tk.Button): The tkinter Button object used to navigate to the previous position.
        r_arrow       (tk.Button): The tkinter Button object used to navigate to the next position.
        f_arrow       (tk.Button): The tkinter Button object used to navigate to the first position.
        e_arrow       (tk.Button): The tkinter Button object used to navigate to the last position.
        toggle        (tk.Button): The tkinter Button object used to switch between two games.
        frame         (tk.Button): The tkinter Frame object that ensures all tk.Button objects are horizontally aligned.

    Methods:
        toggle_game():      Switches to the other Parser object and displays that game's position at the same index.
        draw_canvas():      Draws the chessboard corresponding to the current position.
        display_position(): Displays the current position on the board_label and move information on the move_label.
        __call__():         Initializes the Navigator and starts the tkinter main loop.

    This class provides a simple way to view a list of Position objects as an interactive slideshow, allowing the
    user to navigate through positions using the left and right arrow keys.
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
                                width  = self.get_square_size() * 8, 
                                height = self.get_square_size() * 8)

        self.l_arrow = tk.Button(self.root, text = "←", font = ("Menlo", 30), command = self.set_prev_position)
        self.r_arrow = tk.Button(self.root, text = "→", font = ("Menlo", 30), command = self.set_next_position)
        self.f_arrow = tk.Button(self.root, text = "⇤", font = ("Menlo", 30), command = self.set_first_position)
        self.e_arrow = tk.Button(self.root, text = "⇥", font = ("Menlo", 30), command = self.set_end_position)

        self.frame   = tk.Frame(self.root)
        self.con     = tk.Button(self.frame, text = "↣", font = ("Menlo", 30), command = self.set_convergence_position)
        self.div     = tk.Button(self.frame, text = "↛", font = ("Menlo", 30), command = self.set_divergence_position)
        self.toggle  = tk.Button(self.frame, text = "↪", font = ("Menlo", 30), command = self.toggle_game)

    def get_index(self):
        return self.index
    
    def get_square_size(self):
        return self.square_size
    
    def get_is_parser1(self):
        return self.is_parser1
    
    def get_active_parser(self):
        return self.parser1 if self.get_is_parser1() else self.parser2
    
    def get_end_index(self):
        return len(self.get_active_parser().get_positions()) - 1

    def set_index(self, index):
        self.index = index

    def set_square_size(self, square_size):
        self.square_size = square_size

    def set_is_parser1(self, is_parser1):
        self.is_parser1 = is_parser1

    def set_next_position(self, event = None):
        self.set_index(min(self.get_index() + 1, self.get_end_index()))
        self.display_position()

    def set_prev_position(self, event = None):
        self.set_index(max(self.get_index() - 1, 0))
        self.display_position()

    def set_first_position(self, event = None):
        self.set_index(0)
        self.display_position()

    def set_end_position(self, event = None):
        self.set_index(self.get_end_index())
        self.display_position()

    def set_convergence_position(self, event = None):
        self.index = self.indices[0][0] if self.is_parser1 else self.indices[1][0]
        self.display_position()

    def set_divergence_position(self, event = None):
        self.index = self.indices[0][1] if self.is_parser1 else self.indices[1][1]
        self.display_position()

    def toggle_parser(self):
        self.set_is_parser1(not self.get_is_parser1())

    def toggle_game(self):
        '''
        Switches to the other Parser object and displays that game's position at the same index. 
        
        If out of index, resets to the last position in the current game.
        '''

        self.toggle_parser()
        if self.get_index() > self.get_end_index(): self.set_index(self.get_end_index())
        self.display_position()

    def update_button_states(self):
        """
        Updates the state of navigation buttons based on the current position index.
        
        If at the first position, disable f_arrow and l_arrow buttons.
        If at the last position, disable e_arrow and r_arrow buttons.
        """

        if self.get_index() == 0:
            self.f_arrow.config(state = "disabled")
            self.l_arrow.config(state = "disabled")
        else:
            self.f_arrow.config(state = "normal")
            self.l_arrow.config(state = "normal")

        if self.get_index() == self.get_end_index():
            self.e_arrow.config(state = "disabled")
            self.r_arrow.config(state = "disabled")
        else:
            self.e_arrow.config(state = "normal")
            self.r_arrow.config(state = "normal")

        if self.parser2:
            con_index = self.indices[0][0] if self.is_parser1 else self.indices[1][0]
            div_index = self.indices[0][1] if self.is_parser1 else self.indices[1][1]

            self.con.config(state = "normal" if self.index != con_index else "disabled")
            self.div.config(state = "normal" if self.index != div_index else "disabled")
            self.toggle.config(state = "normal")
            # self.toggle.config(bg = "yellow") if con_index <= self.index <= div_index else self.toggle.config(bg = self.root.cget("bg"))
        else:
            self.con.config(state = "disabled")
            self.div.config(state = "disabled")
            self.toggle.config(state = "disabled")

    def draw_canvas(self, position):
        '''
        Draws the chessboard corresponding to the current position.
        
        This method creates a rectangle for each square on the chessboard and fills it with a color based on the square's 
        index. It then adds the corresponding chess piece to the center of each square. The chessboard is drawn on the 
        tkinter canvas, which is then packed and visible in the tkinter window.
        '''

        board       = position.get_board()
        square_size = self.get_square_size()
        squares     = [square for row in board for square in row]
        colors      = ["#E0E0E0", "#B0B0B0" if self.get_is_parser1() else "#A3B9CC"] * 4

        for i, (color, square) in enumerate(zip(cycle(colors + colors[::-1]), squares)):
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

        parser   = self.get_active_parser()
        position = parser.get_positions()[self.get_index()]
        metadata = parser.get_metadata()

        self.canvas.delete("all")
        self.draw_canvas(position)

        self.match.config(text = f"Game Uploaded on {self.ts}" if self.get_is_parser1() else "Matched Game", pady = 10)
        self.event.config(text = f"{metadata.get('White', '')} vs. {metadata.get('Black', '')} ({metadata.get('Date', '').split('.')[0]})", pady = 0)
        self.move.config(text  = f"{position.move_number}. {position.move_notation}", pady = 10)
        self.turn.config(text  = metadata.get('Result', '') if position.final_move else ("White to Move" if position.white_turn else "Black to Move"), pady = 10)

        self.match.pack()
        self.event.pack()
        self.move.pack()
        self.canvas.pack()
        self.turn.pack()

        self.f_arrow.pack(side = "left")
        self.l_arrow.pack(side = "left")
        self.e_arrow.pack(side = "right")
        self.r_arrow.pack(side = "right")
        self.con.pack(side     = 'left')
        self.toggle.pack(side  = 'left')
        self.div.pack(side     = 'left')
        self.frame.pack()
        self.update_button_states()

    def __call__(self):
        self.root.title("Navigator")
        self.root.bind("<Right>", self.set_next_position)
        self.root.bind("<Left>",  self.set_prev_position)
        self.root.bind("<Up>",    self.set_first_position)
        self.root.bind("<Down>",  self.set_end_position)
        self.root.bind("<space>", self.toggle_game)
        self.root.bind("c",       self.set_convergence_position)
        self.root.bind("d",       self.set_divergence_position)

        self.display_position()
        self.root.mainloop() 