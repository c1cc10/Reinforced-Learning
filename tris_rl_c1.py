import random
import copy

# global constants
WINS = 1
LOSES = 0
X = "X"
O = "O"
EMPTY = " "
NUM_SQUARES = 9
TIE = "TIE"
WINNING_STATES = [(0, 1, 2),
                   (3, 4, 5),
                   (6, 7, 8),
                   (0, 3, 6),
                   (1, 4, 7),
                   (2, 5, 8),
                   (0, 4, 8),
                   (2, 4, 6)]
STARTING_BOARD_STATE = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']

def ask_yes_no(question):
    """Ask a yes or no question."""
    response = None
    while response not in ("y", "n"):
        response = input(question).lower()
    return response

def ask_number(question, low, high):
    """Ask for a number within a range."""
    response = None
    while response not in range(low, high):
        response = int(input(question))
    return response

def legal_moves(board):
    """Create list of legal moves."""
    moves = []
    #for square in range(NUM_SQUARES):
    for square in range(len(board)):
        if board[square] == EMPTY:
            moves.append(square)
    return moves

class Player():
    def __init__(self, sign):
       self.sign = sign

class Human(Player):
    def __init__(self, sign):
       super().__init__(sign)

    def move(self, board):
        """Get human move."""  
        legal = legal_moves(board.current_board)
        my_move = None
        while my_move not in legal:
            my_move = ask_number("Where will you move? (0 - 8):", 0, NUM_SQUARES)
            if my_move not in legal:
                print("\nThat square is already occupied, foolish human.  Choose another.\n")
        print("Fine...")
        board.update(my_move, self.sign)
        #return move

class Computer(Player):
    root_state = None
    def __init__(self, sign, learning_rate):
        super().__init__(sign)
        self.lr = learning_rate
        self.step_size = 0.60
        self.load_memory()

    def load_memory(self):
        if self.root_state is None:
            self.root_state = State(STARTING_BOARD_STATE, None)
            self.actual_state = self.root_state
        else: 
            self.actual_state = self.root_state
            print(self.root_state.board)

    def move(self, board):
        #choose if to play greedy or be explorative
        explore = False
        buffer_board = board.copy()
        self.next_state = self.actual_state.has_state(buffer_board)
        r = random.random()
        value = 0.50
        ngue = []
        if self.next_state is None:
            print("\nThis state was NOT found\n")
            self.next_state = self.actual_state.add_state(buffer_board, None)
        if r < self.lr:
            # explore
            print("\n Exploring\n")
            self.next_state.move = random.choice(legal_moves(buffer_board))
            explore = True
        else:
            # be greedy
            if len(self.next_state.children) > 0:
                for move in range(len(self.next_state.value)):
                    if self.next_state.value[move] > value:
                        value = self.next_state.value[move]
                        self.next_state.move = move
                    if self.next_state.value[move] == value:
                        ngue.append(move)
        if value <= 0.50:
            if len(ngue) > 0:
                self.next_state.move = random.choice(ngue)
            else:
                #print("ngue vuoto, vado a caso")
                self.next_state.move = random.choice(legal_moves(buffer_board))
        #self.memorize(board, my_move)
        board.value_display(self.next_state.value)
        board.update(self.next_state.move, self.sign)
        if not explore:
            self.value_function(EMPTY)

    def value_function(self, winner_sign):
        if self.actual_state.move is None:
            self.actual_state.move = self.next_state.move
        if winner_sign == EMPTY: # partita in corso
            #print("valutation: ")
            self.actual_state.value[self.actual_state.move] +=  self.step_size * (self.next_state.value[self.next_state.move] - self.actual_state.value[self.actual_state.move])
            self.actual_state = self.next_state
        elif winner_sign == self.sign: #abbiamo vinto
            #print("gain: ")
            self.actual_state.value[self.actual_state.move] +=  self.step_size * (WINS - self.actual_state.value[self.actual_state.move])
        else: #draw is a loss 
            #print("pain: ")
            self.actual_state.value[self.actual_state.move] +=  self.step_size * (LOSES - self.actual_state.value[self.actual_state.move])
        #print(self.actual_state.value[self.actual_state.move])

class State:
    def __init__(self, board, move):
        self.children = []
        self.value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for square_n in range(len(board)):
            if board[square_n] == EMPTY:
                self.value[square_n] = 0.50
        self.board = board
        self.move = move

    def add_state(self, board, move):
        new_state = State(board.copy(), move)
        self.children.append(new_state)
        return new_state

    def has_state(self, board):
        for state in self.children:
            if board == state.board:
                value = state.value
                board = state.board
                return state
        return None

    def walk(self, node = None):
        """ iterate tree in pre-order depth-first search order """
        if node is None:
            node = self
        print(node.value)
        for child in node.children:
            for n in self.walk(child):
                print(n.value)

class Game():
    def __init__(self, bot_vs_bot = False):
        learning_rate = 0.1
        self.human = Human(O)
        self.computer = Computer(X, learning_rate)
        self.computer2 = Computer(O, learning_rate)
        self.robowar = bot_vs_bot
        self.start()

    def start(self):
        self.computer.load_memory()
        self.computer2.load_memory()
        self.board = Board()
        self.turn = X
        if self.robowar:
            print("\nROBOWAR mode ON")
            self.computer.sign = X
            self.computer2.sign = O
        else:
            if ask_yes_no("Do you require the first move? (y/n): ") == "y":
                print("\nThen take the first move.  You will need it.")
                self.human.sign = X
                self.computer.sign = O
            else:
                self.human.sign = O
                self.computer.sign = X
        
        while not self.is_winner():
            if self.robowar:
                if self.turn == self.computer2.sign:
                    move = self.computer2.move(self.board)
                else:
                    move = self.computer.move(self.board)
            else:
                if self.turn == self.human.sign:
                    move = self.human.move(self.board)
                else:
                    move = self.computer.move(self.board)
            self.board.display()
            self.next_turn()
        self.computer.value_function(self.winner)
        if self.robowar:
            self.computer2.value_function(self.winner)
        self.congrat_winner()

    def congrat_winner(self):
        """Congratulate the winner."""
        if self.winner == self.computer.sign:
            print("As I predicted, human, I am triumphant once more.  \n" \
                  "Proof that computers are superior to humans in all regards.")
    
        elif self.winner == self.human.sign:
            print("No, no!  It cannot be!  Somehow you tricked me, human. \n" \
                  "But never again!  I, the computer, so swear it!")
    
        elif self.winner == TIE:
            print("You were most lucky, human, and somehow managed to tie me.  \n" \
                  "Celebrate today... for this is the best you will ever achieve.")

    def next_turn(self):
        """Switch turns."""
        if self.turn == X:
            self.turn = O
        else:
            self.turn = X

    def is_winner(self):
        """Determine the game winner."""
        for row in WINNING_STATES:
            if self.board.current_board[row[0]] == self.board.current_board[row[1]] == self.board.current_board[row[2]] != EMPTY:
                self.winner = self.board.current_board[row[0]]
                return True
        if not EMPTY in self.board.current_board: 
            self.winner = TIE
            return True
        self.winner = None
        return False

class Board():
    current_board = []
    def __init__(self):
        """Create new game board."""
        self.reset()
        for square in range(NUM_SQUARES):
            self.current_board.append(EMPTY)
        #return self.current_board
        self.display()

    def update(self, square, sign):
        self.current_board[square] = sign

    def reset(self):
        self.current_board = []

    def value_display(self, values):
        """Display game board on screen."""
        print("\n\t", values[0], "|", values[1], "|", values[2])
        print("\t","---------------")
        print("\t",values[3], "|", values[4], "|", values[5])
        print("\t","---------------")
        print("\t",values[6], "|", values[7], "|", values[8])

    def display(self):
        """Display game board on screen."""
        print("\n\t", self.current_board[0], "|", self.current_board[1], "|", self.current_board[2])
        print("\t","---------")
        print("\t",self.current_board[3], "|", self.current_board[4], "|", self.current_board[5])
        print("\t","---------")
        print("\t",self.current_board[6], "|", self.current_board[7], "|", self.current_board[8])

    def copy(self):
        return self.current_board[:]

if __name__ == "__main__":
    mio = Game(True)
    for i in range(0,100000):
       mio.start()
