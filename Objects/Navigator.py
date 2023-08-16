from   Parser      import *
from   datetime    import datetime
from   typing      import *
import tkinter     as tk

class Navigator:
    '''
    The Navigator class provides an interactive slideshow for viewing a list of chess positions. 
    It uses the tkinter library for its GUI and works with Parser objects to get the list of positions from PGN files.

    Attributes:
        parsers         (List[Parser]) : A list of Parser objects, each containing a game to be displayed in the slideshow.
        parser_index    (int)          : The index of the currently active Parser object.
        match_indices   (Tuple)        : An optional tuple with the start/end indices of the matching sequence between games from different Parsers.
        ply_index       (int)          : The current index in the list of Position objects from the active Parser.
        square_size     (int)          : The size of each square in the chessboard canvas.
        ts              (datetime)     : Timestamp indicating when the game was uploaded.

    Methods:
        active_indices   : Returns the start and end indices of the matching sequence for the active Parser.
        end_index        : Returns the final index in the list of Position objects for the active Parser.
        create_buttons   : Creates the navigation buttons and binds the appropriate actions to them.
        toggle_parser    : Switches which parser is actively on-screen.
        update_ply_index : Updates the current index based on the button pressed and displays the new position.
        update_states    : Updates the state of navigation buttons based on the current position index.
        draw_canvas      : Draws the chessboard corresponding to the current position.
        update_labels    : Updates the labels to show the current position and metadata.
        pack_components  : Packs the labels, canvas, and buttons into the tkinter window.
        display_position : Updates the display to show the current position and metadata.
        __call__         : Displays the initial position and starts the tkinter main loop.
    '''

    def __init__(self, 
                 parser1       : Parser,
                 parser2       : Optional[Parser] = None,
                 match_indices : Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None):

        self.parsers = [parser1]
        if parser2: self.parsers.append(parser2)

        self.parser_index  = 0
        self.match_indices = match_indices
        self.ply_index     = 0
        self.square_size   = 80
        self.ts            = datetime.now().strftime('%b %d, %Y at %-I:%M %p')
        self.root          = tk.Tk()
        self.frame         = tk.Frame(self.root)
        self.canvas        = tk.Canvas(self.root, width = self.square_size * 8, height = self.square_size * 8)
        self.labels        = [tk.Label(self.root, font = ("Menlo", 20, "bold")),
                              tk.Label(self.root, font = ("Menlo", 14, "italic")),
                              tk.Label(self.root, font = ("Menlo", 12, "bold")),
                              tk.Label(self.root, font = ("Menlo", 12))]

        self.props = {"⇤": {"side": "left",  "key": "<Up>",    "action": lambda: 0,                                       "condition": lambda: self.ply_index    == 0},
                      "←": {"side": "left",  "key": "<Left>",  "action": lambda: max(self.ply_index - 1, 0),              "condition": lambda: self.ply_index    == 0},
                      "↣": {"side": "left",  "key": "c",       "action": lambda: self.active_indices[0],                  "condition": lambda: self.ply_index    == self.active_indices[0]},
                      "↪": {"side": "left",  "key": "<space>", "action": lambda: self.toggle_parser(),                    "condition": lambda: len(self.parsers) == 1},
                      "↛": {"side": "left",  "key": "d",       "action": lambda: self.active_indices[1],                  "condition": lambda: self.ply_index    == self.active_indices[1]},
                      "⇥": {"side": "right", "key": "<Down>",  "action": lambda: self.end_index,                          "condition": lambda: self.ply_index    == self.end_index},
                      "→": {"side": "right", "key": "<Right>", "action": lambda: min(self.ply_index + 1, self.end_index), "condition": lambda: self.ply_index    == self.end_index}}
        self.buttons = self.create_buttons()
    
    @property
    def active_indices(self):
        return self.match_indices[0] if self.parser_index == 0 else self.match_indices[1]

    @property
    def end_index(self):
        return len(self.parsers[self.parser_index].positions) - 1
    
    def create_buttons(self):
        '''
        Creates the navigation buttons and binds the appropriate actions to them. The actions include navigating 
        to the previous or next position and toggling between the loaded games. 
        '''
        
        buttons = []
        for i, (k, v) in enumerate(self.props.items()):
            self.root.bind(v['key'], lambda event, i=i: self.update_ply_index(i))
            buttons.append(tk.Button(self.frame if k in ["↣", "↪", "↛"] else self.root, 
                                text = k, font = ("Menlo", 30), command = lambda i=i: self.update_ply_index(i)))
        return buttons
    
    def toggle_parser(self):
        '''
        Switches between the Parser objects in the parsers list and ensures an invalid ply_index isn't used upon switching.
        
        The parser_index is incremented and wrapped around the length of the parsers list to achieve this. If the current 
        ply_index is beyond the end_index of the new active Parser, it is adjusted to that Parser's final ply.
        '''

        self.parser_index = (self.parser_index + 1) % len(self.parsers)
        if self.ply_index > self.end_index: self.ply_index = self.end_index
        return self.ply_index
    
    def update_ply_index(self, i: int):
        '''
        Updates the current index based on the button pressed and displays the new position.
        '''
        
        self.ply_index = self.props[self.buttons[i].cget('text')]["action"]()
        self.display_position()

    def update_states(self):
        '''
        Updates the state of navigation buttons based on the current position index.
        '''

        for i in self.buttons:
            i.config(state = "disabled" if self.props[i.cget('text')]["condition"]() else "normal")

    def draw_canvas(self, position: Position):
        '''
        Draws the chessboard corresponding to the current position.

        This method creates a rectangle for each square on the chessboard and fills it with a color based on the square's 
        index. It then adds the corresponding chess piece to the center of each square. The chessboard is drawn on the 
        tkinter canvas, which is then packed and visible in the tkinter window.
        '''

        board  = position.get_board()
        colors = ["#E0E0E0", "#B0B0B0" if self.parser_index == 0 else "#A3B9CC"]

        for i, square in enumerate(square for row in board for square in row):
            y, x = divmod(i, 8)
            x *= self.square_size
            y *= self.square_size
            self.canvas.create_rectangle(x, y, x + self.square_size, y + self.square_size, 
                                         fill = colors[(x // self.square_size + y // self.square_size) % 2])
            self.canvas.create_text(x + self.square_size / 2, y + self.square_size / 2 - self.square_size / 20, text = square, 
                                    font = ("Arial Unicode MS", int(self.square_size * 0.8)), fill = 'black')

    def update_labels(self, 
                      parser   : Parser, 
                      position : Position):
        '''
        Updates the labels to show the current position and metadata. This method fetches the metadata and current 
        position from the active Parser and updates the tkinter labels to display this information. 
        
        The labels include the timestamp or game title, the players and date of the game, the current move notation, 
        and the result or current player's turn.
        '''

        metadata = parser.metadata

        self.labels[0].config(text = f"Game Uploaded on {self.ts}" if self.parser_index == 0 else "Matched Game", pady = 10)
        self.labels[1].config(text = f"{metadata.get('White', '')} vs. {metadata.get('Black', '')} ({metadata.get('Date', '').split('.')[0]})", pady = 0)
        self.labels[2].config(text = f"{position.move_number}. {position.move_notation}", pady = 10)
        self.labels[3].config(text = metadata.get('Result', '') if position.final_move else ("White to Move" if position.white_turn else "Black to Move"), pady = 10)

    def pack_components(self):
        '''
        Packs the labels, canvas, and buttons into the tkinter window.
        '''

        for i in self.labels:  i.pack()
        self.canvas.pack()
        for j in self.buttons: j.pack(side = self.props[j.cget('text')]['side'])
        self.frame.pack()

    def display_position(self):
        '''
        Updates the display to show the current position and metadata. 
        
        This method first clears the tkinter canvas and draws the new position. Then it updates the labels to show 
        the correct metadata and position information. Finally, it packs all the GUI components into the tkinter 
        window and updates the state of the navigation buttons. 
        
        This method is called each time a navigation button is pressed to refresh the display.
        '''

        parser   = self.parsers[self.parser_index]
        position = parser.positions[self.ply_index]

        self.canvas.delete("all")
        self.draw_canvas(position)

        self.root.title("Navigator")
        self.update_labels(parser, position)
        self.pack_components()
        self.update_states()

    def __call__(self):

        self.display_position()
        self.root.mainloop()