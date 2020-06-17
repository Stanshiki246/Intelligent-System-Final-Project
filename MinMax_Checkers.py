from copy import deepcopy
import time
#Stephanus Jovan - 2201832856
#Stanley Tantysco - 2201814670
#Minimax Checkers



def is_won(board):
    """
        Returns true if the game has been won
    """
    return board.gameWon != board.NOTDONE

#Minimax Algorithm
def minMax2(board):
    """
        Main minmax function, takes a board as input and returns the best possible move in the form
        of a board and the value of that board.
    """
    bestBoard = None
    currentDepth = board.maxDepth + 1
    while not bestBoard and currentDepth > 0:
        currentDepth -= 1
        # Get the best move and it's value from maxMinBoard (minmax handler)
        (bestBoard, bestVal) = maxMove2(board, currentDepth)
        # If we got a NUll board raise an exception
    if not bestBoard:
        raise Exception("Could only return null boards")
    # Otherwise return the board and it's value
    else:
        return (bestBoard, bestVal)

def maxMove2(maxBoard, currentDepth):
    """
        Calculates the best move for BLACK player (computer) (seeks a board with INF value)
    """
    return maxMinBoard(maxBoard, currentDepth-1, float('-inf'))


def minMove2(minBoard, currentDepth):
    """
        Calculates the best move from the perspective of WHITE player (seeks board with -INF value)
    """
    return maxMinBoard(minBoard, currentDepth-1, float('inf'))

def maxMinBoard(board, currentDepth, bestMove):
    """
        Does the actual work of calculating the best move
    """
    # Check if at an end node
    if is_won(board) or currentDepth <= 0:
        return (board, staticEval2(board))

    # if not at an end node, now it is needed to do minmax
    # Set up values for minmax
    best_move = bestMove
    best_board = None

    # consolidate MaxNode and MinNode more by assigning the iterator with a
    # function and doing some trickery with the bestmove == INF
    # MaxNode
    if bestMove == float('-inf'):
        # Create the iterator for the Moves
        moves = board.iterBlackMoves()
        for move in moves:
            maxBoard = deepcopy(board)
            maxBoard.moveSilentBlack(*move)
            value = minMove2(maxBoard, currentDepth-1)[1]
            if value > best_move:
                best_move = value
                best_board = maxBoard

    # MinNode
    elif bestMove == float('inf'):
        moves = board.iterWhiteMoves()
        for move in moves:
            minBoard = deepcopy(board)
            minBoard.moveSilentWhite(*move)
            value = maxMove2(minBoard, currentDepth-1)[1]
            # Take the smallest value we can
            if value < best_move:
                best_move = value
                best_board = minBoard

    # If there is an error in finding bestMove so raise an Exception
    else:
        raise Exception("bestMove is set to something other than inf or -inf")

    # Things appear to be fine, we should have a board with a good value to move to
    return (best_board, best_move)

def staticEval2(evalBoard):
    """
        Evaluates a board for how advantageous it is
        -INF if WHITE player has won
        INF if BLACK player has won
        Otherwise use a particular strategy to evaluate the move
        See Comments above an evaluator for what it's strategy is
    """
    # Has someone won the game? If so return an INFINITE value
    if evalBoard.gameWon == evalBoard.BLACK:
        return float('inf')
    elif evalBoard.gameWon == evalBoard.WHITE:
        return float('-inf')


    # Some setup
    score = 0
    scoremod = 0
    pieces = None
    if evalBoard.turn == evalBoard.WHITE:
        pieces = evalBoard.whitelist
        scoremod = -1
    elif evalBoard.turn == evalBoard.BLACK:
        pieces = evalBoard.blacklist
        scoremod = 1

    # Gigadeath Defense Evaluator
    # This AI will attempt to keep it's pieces as close together as possible until it has a chance
    # to jump the opposing player. It's super effective
    distance = 0
    for piece1 in pieces:
        for piece2 in pieces:
            if piece1 == piece2:
                continue
            dx = abs(piece1[0] - piece2[0])
            dy = abs(piece1[1] - piece2[1])
            distance += dx**2 + dy**2
    distance /= len(pieces)
    score = 1.0/distance * scoremod

    return score

class board(object):
    BLACK = 1
    WHITE = 0
    NOTDONE = -1
    def __init__(self, height, width, firstPlayer):
        """
            Constructs a board, right now maxDepth is statically assigned
        """
        # Set the height and width of the game board
        self.width = width
        self.height = height
        # Create two lists which will contain the pieces each player posesses
        self.blacklist = []
        self.whitelist = []
        # Set default piece positions
        for i in range(width):
            self.blacklist.append((i, (i+1)%2))
            self.whitelist.append((i, height - (i%2) - 1))
        # boardState contains the current state of the board for printing/eval
        self.boardState = [[' '] * self.width for x in range(self.height)]
        self.gameWon = self.NOTDONE
        self.turn = firstPlayer
        self.maxDepth = 10

    # Generate an iterator for all of the moves
    def iterWhiteMoves(self):
        """
            Main generator for white moves
        """
        for piece in self.whitelist:
            for move in self.iterWhitePiece(piece):
                yield move

    def iterBlackMoves(self):
        """
            Main Generator for black moves
        """
        for piece in self.blacklist:
            for move in self.iterBlackPiece(piece):
                yield move

    def iterWhitePiece(self, piece):
        """
            Generates possible moves for a white piece
        """
        return self.iterBoth(piece, ((-1,-1),(1,-1)))

    def iterBlackPiece(self, piece):
        """
            Generates possible moves for a black piece
        """
        return self.iterBoth(piece, ((-1,1),(1,1)))

    def iterBoth(self, piece, moves):
        """
            Handles the actual generation of moves for either black or white pieces
        """
        for move in moves:
            # Regular Move
            targetx = piece[0] + move[0]
            targety = piece[1] + move[1]
            # If the move is out of bounds don't move
            if targetx < 0 or targetx >= self.width or targety < 0 or targety >= self.height:
                continue
            target = (targetx, targety)
            # Check that there is nothing in the way of moving to the target
            black = target in self.blacklist
            white = target in self.whitelist
            if not black and not white:
                yield (piece, target, self.NOTDONE)
            # There was something in the way, can we jump it?
            else:
                # It has to be of the opposing color to jump
                if self.turn == self.BLACK and black:
                    continue
                elif self.turn == self.WHITE and white:
                    continue
                # Jump proceeds by adding the same movement in order to jump over the opposing
                # piece on the checkerboard
                jumpx = target[0] + move[0]
                jumpy = target[1] + move[1]
                # If the jump is going to be out of bounds don't do it.
                if jumpx < 0 or jumpx >= self.width or jumpy < 0 or jumpy >= self.height:
                    continue
                jump = (jumpx, jumpy)
                # Check that there is nothing in the jumpzone
                black = jump in self.blacklist
                white = jump in self.whitelist
                if not black and not white:
                    yield (piece, jump, self.turn)#AI victory condition

    def updateBoard(self):
        """
            Updates the array containing the board to reflect the current state of the pieces on the
            board
        """
        for i in range(self.width):
            for j in range(self.height):
                self.boardState[i][j] = " "
        for piece in self.blacklist:
            self.boardState[piece[1]][piece[0]] = u'◆'
        for piece in self.whitelist:
            self.boardState[piece[1]][piece[0]] = u'◇'

    # Movement of pieces
    def moveSilentBlack(self, moveFrom, moveTo, winLoss):
        """
            Move black piece without printing
        """
        if moveTo[0] < 0 or moveTo[0] >= self.width or moveTo[1] < 0 or moveTo[1] >= self.height:
            raise Exception("That would move black piece", moveFrom, "out of bounds")
        black = moveTo in self.blacklist
        white = moveTo in self.whitelist
        if not (black or white):
            self.blacklist[self.blacklist.index(moveFrom)] = moveTo
            self.updateBoard()
            self.turn = self.WHITE
            self.gameWon = winLoss
        else:
            raise Exception

    def moveSilentWhite(self, moveFrom, moveTo, winLoss):
        """
            Move white piece without printing
        """
        if moveTo[0] < 0 or moveTo[0] >= self.width or moveTo[1] < 0 or moveTo[1] >= self.height:
            raise Exception("That would move white piece", moveFrom, "out of bounds")
        black = moveTo in self.blacklist
        white = moveTo in self.whitelist
        if not (black or white):
            self.whitelist[self.whitelist.index(moveFrom)] = moveTo
            self.updateBoard()
            self.turn = self.BLACK
            self.gameWon = winLoss
        else:
            raise Exception

    def moveBlack(self, moveFrom, moveTo, winLoss):
        """
            Move a black piece from one spot to another. \n winLoss is passed as either 0(white)
            or 1(black) if the move is a jump
        """
        self.moveSilentBlack(moveFrom, moveTo, winLoss)
        self.printBoard()

    def moveWhite(self, moveFrom, moveTo, winLoss):
        """
            Move a white piece from one spot to another. \n winLoss is passed as either 0(white)
            or 1(black) if the move is a jump
        """
        self.moveSilentWhite(moveFrom, moveTo, winLoss)
        self.printBoard()

    def printBoard(self):
        """
            Prints the game board
        """
        print(self.__unicode__())

    def __unicode__(self):
        """
            Contains the unicode and other BS for printing the board
        """
        # Updates Game board
        self.updateBoard()
        lines = []
        # This prints the numbers at the top of the Game Board
        lines.append('    ' + '   '.join(map(str, range(self.width))))
        # Prints the top of the gameboard in unicode
        lines.append(u'  ╭' + (u'───┬' * (self.width-1)) + u'───╮')

        # Print the boards rows
        for num, row in enumerate(self.boardState[:-1]):
            lines.append(chr(num+65) + u' │ ' + u' │ '.join(row) + u' │')
            lines.append(u'  ├' + (u'───┼' * (self.width-1)) + u'───┤')

        #Print the last row
        lines.append(chr(self.height+64) + u' │ ' + u' │ '.join(self.boardState[-1]) + u' │')

        # Prints the final line in the board
        lines.append(u'  ╰' + (u'───┴' * (self.width-1)) + u'───╯')
        return '\n'.join(lines)

width = 6
height = 6
firstPlayer = 0

# Gets the move from the User
def getUserMove(b):
    statement1 = "Select one of your tokens eg. " + chr(b.whitelist[0][0]+97) + str(b.whitelist[0][1])
    print(statement1)
    print('in format [a1 b2] or [e5 d4]')
    while True: # Loop until proper input
        move = input().lower().split()
        if not(len(move) == 2):
            print("That is not a valid move, try again.", statement1)
            continue
        moveFromTup = (int(move[0][1]), ord(move[0][0]) - 97)
        moveToTup = (int(move[1][1]), ord(move[1][0]) - 97)
        # Is the piece we want to move one we own?
        if not (moveFromTup in b.whitelist):
            print("You do not own", moveFromTup, "please select one of.", b.whitelist)
            continue
        break
    return (moveFromTup, moveToTup, b.NOTDONE)



#Set the board dan run the game
b = board(width, height, firstPlayer)
b.printBoard()
print("Welcome to checkers.")
print("If enemy captures one of your piece, it is game over")
# Main game loop
step=0
while b.gameWon == -1:
    # Player gets first turn
    userMove = getUserMove(b)
    try:
       b.moveWhite(*userMove)
    except Exception:
        print("Invalid move")
        continue
    # Then it is the computers turn
    # start evaluation
    t1=time.time()
    temp = minMax2(b)
    b = temp[0]
    print("**********COMPUTER MOVE**********")
    b.printBoard()
    step += 1
    t2=time.time()
    #Get time evaluation
    diff=t2-t1
    #SHow step and time evaluation
    print('AI Step: ',step)
    print('AI Speed Time: ', str(diff),' s')
    if b.gameWon == b.WHITE:
        print ("White Wins\nGame Over")
        break
    elif b.gameWon == b.BLACK:
        print ("Black Wins\nGame Over")
        break
