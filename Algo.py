from collections import Counter
import random
from typing import Callable, List, Tuple
from copy import deepcopy

Board = List[List[int]]
Pos = Tuple[int, int]
Poss = List[Pos]
Moves = List[Tuple[Pos, Poss]]


class Checkers(object):
    """
    Checkers class
    """
    WHITE_MAN = 1
    WHITE_KING = 3
    
    BLACK_MAN = 2
    BLACK_KING = 4
    
    WHITE = 1
    BLACK = 0

    DX = [1, 1, -1, -1]
    DY = [1, -1, 1, -1]
    
    OO = 10 ** 9

    def __init__(self, size: int = 8):
        """Initial board.
        
        :param: size: size of the checkers board. Defaluts to 8
        :return: None
        """

        self.size = size
        self.board = []
        piece = self.WHITE_MAN
        for i in range(size):
            l = []
            f = i % 2 == 1
            if i == size / 2 - 1:
                piece = 0
            elif i == size / 2 + 1:
                piece = self.BLACK_MAN
            for _ in range(size):
                if f:
                    l.append(piece)
                else:
                    l.append(0)
                f = not f
            self.board.append(l)

        self.stateCounter = Counter()

    def printBoard(self, x: int = None, y: int = None):
        """Print the game board.
        
        :param: x: new x position ; y: new y position
        """
        for i in range(self.size):
            for j in range(self.size):
                if i == x and j == y:
                    print("\033[92m", end="")

                if self.board[i][j] == 0:
                    print("-", end=" ")
                else:
                    print(self.board[i][j], end=" ")

                if i == x and j == y:
                    print("\033[0m", end="")
            print()

    def encodeBoard(self):
        """Encode the game board.

        :return: int: the value of the encoded game board
        """
        value = 0
        for i in range(self.size):
            for j in range(self.size):
                # make the minimum value = 5, 
                # so that it's greater than greatest value of the board (4)
                num = i * self.size + j + 5
                value += num * self.board[i][j]
        return value

    def isValid(self, x: int, y: int):
        """Check if the given position is inside the board

        :param: x: x position y: y position
        :return: bool: the given position is valid
        """
        return x >= 0 and x < self.size and y >= 0 and y < self.size

    def getBoard(self):
        """Get Game board

        :return: Board: game board
        """
        return deepcopy(self.board)

    def setBoard(self, board: Board):
        """Set game board

        :param: board: board to set the game borad to
        """
        self.board = deepcopy(board)

    def nextPoss(self, x: int, y: int):
        """Get the possible next positions for a given position

        :param:x : x position
               y : y position
        :return:(Positions, Positions): next normal positions, next capture positions
        """
        if self.board[x][y] == 0:
            return []

        player = self.board[x][y] % 2
        captureMoves = []
        normalMoves = []
        sign = 1 if player == self.WHITE else -1
        # only forward for men and both forward and backward for Kings
        rng = 2 if self.board[x][y] <= 2 else 4
        for i in range(rng):
            nx = x + sign * self.DX[i]
            ny = y + sign * self.DY[i]
            if self.isValid(nx, ny):
                if self.board[nx][ny] == 0:
                    normalMoves.append((nx, ny))
                elif self.board[nx][ny] % 2 == 1 - player:
                    nx += sign * self.DX[i]
                    ny += sign * self.DY[i]
                    if self.isValid(nx, ny) and self.board[nx][ny] == 0:
                        captureMoves.append((nx, ny))

        return normalMoves, captureMoves

    def nextMoves(self, player: int):
        """Get the next moves of the game board for a certian player

        :param:player (int): the type of player (WHITE, BLACK)
        :return:Moves: valid moves for the player
        """
        captureMoves = []
        normalMoves = []
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] != 0 and self.board[x][y] % 2 == player:
                    normal, capture = self.nextPoss(x, y)
                    if len(normal) != 0:
                        normalMoves.append(((x, y), normal))
                    if len(capture) != 0:
                        captureMoves.append(((x, y), capture))
        if len(captureMoves) != 0:
            return captureMoves
        return normalMoves

    def playMove(self, x: int, y: int, nx: int, ny: int):
        """Change the board by playing a move from (x, y) to (nx, ny)

        :param:x : old x ;y : old y ;nx : new x ;ny :new y
        :return: canCapture (bool): if the player can capture more pieces.  
                 removed (int): the removed piece.  
                 whetherking (bool) if the current piece is king.  
        """
        self.board[nx][ny] = self.board[x][y]
        self.board[x][y] = 0

        removed = 0
        if abs(nx - x) == 2:  # capture move
            dx = nx - x
            dy = ny - y
            removed = self.board[x + dx // 2][y + dy // 2]
            # remove captured piece
            self.board[x + dx // 2][y + dy // 2] = 0
            # if king is removed
            if removed == self.WHITE_KING: 
                return False, removed, False
            if removed == self.BLACK_KING:
                return False, removed, False
            
        # become king
        if self.board[nx][ny] == self.WHITE_MAN and nx == self.size - 1:
            self.board[nx][ny] = self.WHITE_KING
            return False, removed, True
        if self.board[nx][ny] == self.BLACK_MAN and nx == 0:
            self.board[nx][ny] = self.BLACK_KING
            return False, removed, True

        if abs(nx - x) != 2:
            return False, removed, False

        return True, removed, False

    def undoMove(self, x: int, y: int, nx: int, ny: int, removed=0, promoted=False):
        """Undo a move and return the board to its previous state

        """
        if promoted:
            if self.board[nx][ny] == self.WHITE_KING:
                self.board[nx][ny] = self.WHITE_MAN

            if self.board[nx][ny] == self.BLACK_KING:
                self.board[nx][ny] = self.BLACK_MAN

        self.board[x][y] = self.board[nx][ny]
        self.board[nx][ny] = 0

        if abs(nx - x) == 2:
            dx = nx - x
            dy = ny - y
            self.board[x + dx // 2][y + dy // 2] = removed


    def cellContains(self, x: int, y: int, player: int) -> bool:
        """return if cell at (x, y) contains player

        :param:
            x (int): x position of cell
            y (int): y position of cell
            player (int): type of player (WHITE/BLACK)
        :return:
            bool: if cell at (x, y) contains player
        """
        return self.board[x][y] != 0 and self.board[x][y] % 2 == player

    def endGame(self, maximizer: int) -> int:
        """evaluate the current state of the board based on end game strategies
            between maximizer player and the opponent

        :param:maximizer (int): the type of the maximizer player (WHITE, BLACK)
        :return: score of the board
        """
        score1 = 0
        score2 = 0
        maxPieces = 0
        minPieces = 0
        rowScore = 0
        base = 0 if maximizer == self.WHITE else self.size-1
        minimizer = 1 - maximizer
        minimizerPoss = []
        for x in range(self.size):
            for y in range(self.size):
                if self.cellContains(x, y, minimizer):
                    minimizerPoss.append((x, y))

        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != 0:
                    if self.board[i][j] % 2 == maximizer:
                        maxPieces += 1
                        if (self.board[i][j] + 1) // 2 == 1:
                            rowScore += abs(base-i)
                        score1 += (self.board[i][j] + 1) // 2
                        for x,y in minimizerPoss:
                            score2 += (x-i)**2 + (y-j)**2
                    else:
                        minPieces += 1
                        score1 -= (self.board[i][j] + 1) // 2

        # penalize if the minimizer is in the corner to be able to trap him at the end of the game                   
        minimizerCorner = 0
        for x, y in minimizerPoss:
            if (x,y) == (0, 1) or (x,y) == (1, 0) or (x, y) == (self.size-1, self.size-2) \
                or (x,y) == (self.size-2, self.size-1):
                minimizerCorner = 1

        maximizerCorner = 0
        if self.cellContains(0, 1, maximizer) or self.cellContains(1, 0, maximizer) \
            or self.cellContains(self.size-1, self.size-2, maximizer) \
            or self.cellContains(self.size-2, self.size-1, maximizer):
            maximizerCorner = 1

        if maxPieces > minPieces:   #come closer to opponent
            return score1*1000 - score2 - minimizerCorner*5 + rowScore*10
        else:    # run away
            return score1*1000 + score2 + maximizerCorner*5

    def evaluate2(self, maximizer: int):
        """evaluate the current state of the board

        :param:maximizer (int): the type of the maximizer player (WHITE, BLACK)
        :return:int: score of the board
        """
        
        men = 0
        kings = 0
        backRow = 0
        middleBox = 0
        middleRow = 0
        vulnerable = 0
        protected = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != 0:
                    sign = 1 if self.board[i][j] % 2 == maximizer else -1
                    if self.board[i][j] <= 2:
                        men += sign*1
                    else:
                        kings += sign*1
                    if sign == 1 and ((i == 0 and maximizer == self.WHITE) or (i == self.size-1 and maximizer == self.BLACK)):
                        backRow += 1
                    if i == self.size/2-1 or i == self.size/2:
                        if j >= self.size/2-2 and j < self.size/2+2:
                            middleBox += sign*1
                        else:
                            middleRow += sign*1

                    myDir = 1 if maximizer == self.WHITE else -1
                    vul = False
                    for k in range(4):
                        x = i + self.DX[k]
                        y = j + self.DY[k]
                        n = i - self.DX[k]
                        m = j - self.DY[k]
                        opDir = abs(x-n)/(x-n)
                        if self.isValid(x, y) and self.board[x][y] != 0 and self.board[x][y] % 2 != maximizer \
                            and self.isValid(n, m) and self.board[n][m] == 0 and (self.board[x][y] > 2 or myDir != opDir):
                            vul = True
                            break
                    
                    if vul:
                        vulnerable += sign*1
                    else:
                        protected += sign*1
                
        return men*2000 + kings*4000 + backRow*400 + middleBox*250 + middleRow*50 - 300*vulnerable + 300*protected

    def stateValue(self, maximizer):
        """get value of the board state,when the maximizer's pieces is greater than the minimizer's, 
        penalize repeating the same state

        :param: maximizer (int): the type of the maximizer player (WHIET/BLACK)
        :return: int: value of the board state
        """
        maxPieces = 0
        minPieces = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != 0:
                    if self.board[i][j] % 2 == maximizer:
                        maxPieces += 1
                    else:
                        minPieces += 1
        if (maxPieces > minPieces):
            return -self.stateCounter[self.encodeBoard()]
        return 0

    def minimax(self,player: int,maximizer: int,depth: int = 0,alpha: int = -OO,beta: int = OO,
        maxDepth: int = 4,evaluate: Callable[[int],int] = evaluate2,moves: Moves = None,):
        """Get the score of the board using alpha-beta algorithm

        :param:
            player: the type of the current player (WHITE, BLACK)
            maximizer: the type of the maximizer player (WHITE, BLACK)
            depth: the current depth of the algorithm. Defaults to 0.
            alpha: the value of alpha. Defaults to -OO.
            beta: the value of beta of the algorithm. Defaults to OO.
            maxDepth: the higher the max depth, Defaults to 4.
            evaluate: evaluation function. Defaults to evaluate2
            moves: the next capture moves (if any). Defaults to None.
        :return: int|float : score of the baord
        """
        if moves == None:
            moves = self.nextMoves(player)
        if len(moves) == 0 or depth == maxDepth:
            score = evaluate(self, maximizer)
            # if there is no escape from losing, maximize number of moves to lose
            if score < 0:
                score += depth
            return score

        bestValue = -self.OO
        if player != maximizer:
            bestValue = self.OO

        # sort moves by the minimum next positions
        moves.sort(key=lambda move: len(move[1]))
        for pos in moves:
            x, y = pos[0]
            for nx, ny in pos[1]:

                canCapture, removed, promoted = self.playMove(x, y, nx, ny)
                played = False

                if canCapture:
                    _, nextCaptures = self.nextPoss(nx, ny)
                    if len(nextCaptures) != 0:
                        played = True
                        nMoves = [((nx, ny), nextCaptures)]
                        if player == maximizer:
                            bestValue = max(
                                bestValue,
                                self.minimax(player, maximizer, depth + 1, alpha, beta, maxDepth, evaluate, nMoves)
                            )
                            alpha = max(alpha, bestValue)
                        else:
                            bestValue = min(
                                bestValue,
                                self.minimax(player, maximizer, depth + 1, alpha, beta, maxDepth, evaluate, nMoves)
                            )
                            beta = min(beta, bestValue)

                if not played:
                    if player == maximizer:
                        bestValue = max(
                            bestValue,
                            self.minimax(1 - player, maximizer, depth + 1, alpha, beta, maxDepth, evaluate)
                        )
                        alpha = max(alpha, bestValue)
                    else:
                        bestValue = min(
                            bestValue,
                            self.minimax(1 - player, maximizer, depth + 1, alpha, beta, maxDepth, evaluate)
                        )
                        beta = min(beta, bestValue)

                self.undoMove(x, y, nx, ny, removed, promoted)

                if beta <= alpha:
                    break
            if beta <= alpha:
                break

        return bestValue

    def minimaxPlay(self,player: int,moves: Moves = None,maxDepth: int = 4,evaluate: Callable[[int], int] = evaluate2,enablePrint: bool = True):
        """play a move using minimax algorithm
            if the player should continue capturing, it will

        Args:
            player (int): the type of the player (WHITE, BLACK)
            moves (Moves, optional): the next capture moves (if any). Defaults to None.
            maxDepth (int, optional): the max depth of the minimax algorithm
                the higher the max depth, the harder the level of th play 
                and the more time the algorithm will take. Defaults to 4.
            enablePrint (bool, optional): if true it prints the game board 
                to stdout after playing the move. Defaults to True.

        :return:
            continue (bool): false if there is no further plays.  
            reset (bool): true when there is a captured piece, 
                used to reset the counter of the draw condition.
        """

        if moves == None:
            moves = self.nextMoves(player)
        if len(moves) == 0:
            if enablePrint:
                print(("WHITE" if player == self.BLACK else "BLACK") + " Player wins")
            return False, False

        self.stateCounter[self.encodeBoard()] += 1

        random.shuffle(moves)
        bestValue = -self.OO
        bestMove = None

        for pos in moves:
            x, y = pos[0]
            for nx, ny in pos[1]:
                _, removed, promoted = self.playMove(x, y, nx, ny)
                value = self.minimax(1 - player, player, maxDepth=maxDepth, evaluate=evaluate)
                value += 2*self.stateValue(player)  
                self.undoMove(x, y, nx, ny, removed, promoted)
                if value > bestValue:
                    bestValue = value
                    bestMove = (x, y, nx, ny)

        x, y, nx, ny = bestMove
        if enablePrint:
            print(f"Move from ({x}, {y}) to ({nx}, {ny})")
        canCapture, removed, _ = self.playMove(x, y, nx, ny)
        if enablePrint:
            self.printBoard(nx, ny)

        if canCapture:
            _, captures = self.nextPoss(nx, ny)
            if len(captures) != 0:
                self.minimaxPlay(player, [((nx, ny), captures)], maxDepth, evaluate, enablePrint)

        self.stateCounter[self.encodeBoard()] += 1
        reset = removed != 0
        return True, reset
