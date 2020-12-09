import pickle
import argparse
import random
import copy
#import tris
import logging
import logging.handlers

logger = logging.getLogger('TTT')

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

VERSIONE = "Isolved SrL : UGV station. Version 0.3.0"
PATH_LOG = "./ttt.log"

def getLevelLog(args):
        if args.verbose == 0:
                l = logging.CRITICAL
        elif args.verbose == 1:
                l = logging.ERROR
        elif args.verbose == 2:
                l = logging.WARNING
        elif args.verbose == 3:
                l = logging.INFO
        else:
                l = logging.DEBUG
        return l

def setLogger(level=0):
        logger.setLevel(level)
        logger.propagate = False
        #ch = logging.handlers.WatchedFileHandler(PATH_LOG)
        ch2 = logging.StreamHandler()
        #ch.setLevel(level)
        ch2.setLevel(level)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        #ch.setFormatter(formatter)
        ch2.setFormatter(formatter)
        #logger.addHandler(ch)
        logger.addHandler(ch2)

def readCommandLine():
        readCommandLine = argparse.ArgumentParser(description="Isolved It! UGV Station")
        #readCommandLine.add_argument("-w", "--webcam", action='store_true', help="use webcam instead of drone cam")
        #readCommandLine.add_argument("--path", type=str, help="list of path actions")
        readCommandLine.add_argument("-v", "--verbose", type=int, choices=[0,1,2,3,4], default=1, help="STDOUT log level")
        readCommandLine.add_argument("-x", "--xperience", help="Load experience file")
        args = readCommandLine.parse_args(namespace=Game)
        return args

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
            #logger.info(self.root_state.board)

    def move(self, board):
        #choose if to play greedy or be explorative
        explore = False
        buffer_board = board.copy()
        self.next_state = self.actual_state.has_state(buffer_board)
        r = random.random()
        max_square_value = 0.50
        ngue = []
        if self.next_state is None:
            logger.info("\nThis state was NOT found\n")
            self.next_state = self.actual_state.add_state(buffer_board, None)
        if r < self.lr:
            # explore
            logger.info("\n Exploring\n")
            self.next_state.move = random.choice(legal_moves(buffer_board))
            explore = True
        else:
            # be greedy
            if len(self.next_state.children) > 0:
                max_square_value = max(self.next_state.value)
                self.next_state.move = self.next_state.value.index(max_square_value)
        if max_square_value == 0.50:
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
            #logger.info("valutation: ")
            self.actual_state.value[self.actual_state.move] +=  self.step_size * (self.next_state.value[self.next_state.move] - self.actual_state.value[self.actual_state.move])
            self.actual_state = self.next_state
        elif winner_sign == self.sign: #abbiamo vinto
            #logger.info("gain: ")
            self.actual_state.value[self.actual_state.move] +=  self.step_size * (WINS - self.actual_state.value[self.actual_state.move])
        else: #draw is a loss 
            #logger.info("pain: ")
            self.actual_state.value[self.actual_state.move] +=  self.step_size * (LOSES - self.actual_state.value[self.actual_state.move])
        #logger.info(self.actual_state.value[self.actual_state.move])

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
        logger.info(node.value)
        for child in node.children:
            for n in self.walk(child):
                logger.info(n.value)

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
            logger.info("\nROBOWAR mode ON")
            if self.computer.sign = X:
                self.computer.sign = O
                self.computer2.sign = X
            elif self.computer.sign = O:
                self.computer.sign = X
                self.computer2.sign = O
            if not self.computer.sign:
                self.computer.sign = X
                self.computer2.sign = O
            #self.computer.sign = X
            #self.computer2.sign = O
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
            logger.info("As I predicted, human, I am triumphant once more.  \n" \
                  "Proof that computers are superior to humans in all regards.")
            print("As I predicted, human, I am triumphant once more.  \n" \
                  "Proof that computers are superior to humans in all regards.")
    
        elif self.winner == self.human.sign:
            logger.info("No, no!  It cannot be!  Somehow you tricked me, human. \n" \
                  "But never again!  I, the computer, so swear it!")
            print("No, no!  It cannot be!  Somehow you tricked me, human. \n" \
                  "But never again!  I, the computer, so swear it!")
    
        elif self.winner == TIE:
            logger.info("You were most lucky, human, and somehow managed to tie me.  \n" \
                  "Celebrate today... for this is the best you will ever achieve.")
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

        logger.info("\n\t", values[0], "|", values[1], "|", values[2])
        logger.info("\t","---------------")
        logger.info("\t",values[3], "|", values[4], "|", values[5])
        logger.info("\t","---------------")
        logger.info("\t",values[6], "|", values[7], "|", values[8])

    def display(self):
        """Display game board on screen."""
        print("\n\t", self.current_board[0], "|", self.current_board[1], "|", self.current_board[2])
        print("\t","---------")
        print("\t",self.current_board[3], "|", self.current_board[4], "|", self.current_board[5])
        print("\t","---------")
        print("\t",self.current_board[6], "|", self.current_board[7], "|", self.current_board[8])

    def copy(self):
        return self.current_board[:]

if __name__ == '__main__':
    arguments = readCommandLine()
    l = getLevelLog(arguments)
    setLogger(l)
    logger.info(VERSIONE)
    mio = Game(True)
    if arguments.xperience != '':
        infile = open(arguments.xperience,'rb') 
        mio.computer.root_state = pickle.load(infile)
        infile.close()
    else:
        for i in range(0,100000):
           mio.start()
        with open('tic-tac-toe.pkl', 'wb') as output:
            pickle.dump(mio.computer.root_state, output)
    mio.robowar = False
    wanna_play = True
    while wanna_play:
        mio.start()
        human_answer = input("Another Game?").lower()
        if human_answer == 'n':
            with open(arguments.xperience, 'wb') as output:
                pickle.dump(mio.computer.root_state, output)
            wanna_play = False
