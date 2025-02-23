from piece import Bishop
from piece import King
from piece import Rook
from piece import Pawn
from piece import Queen
from piece import Knight
from game import WINDOW_MARGIN, WINDOW_SIZE 
from game import DEFAULT_PLAYING_TIME
import time
import pygame

#Board size
BOARD_SIZE = 8

class Board:
    
    #Board circle drawing constants
    MOVE_CIRCLE_RADIUS = 34
    MOVE_CIRCLE_THICKNESS = 4
    CIRCLE_X_OFFSET = 32
    CIRCLE_Y_OFFSET = 30
    
    def __init__(self, rows, cols):
        """
        Initializes the board.
        
        Arguments:
            rows (integer): The number of rows in the board
            cols (integer): The number of columns in the board
        """
        self.rows = rows
        self.cols = cols

        self.ready = False

        self.last = None

        self.copy = True

        self.board = [[0 for x in range(BOARD_SIZE)] for _ in range(rows)]

        piece_types = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        
        #Black and white non-pawn initialization
        for i in range(BOARD_SIZE):
            self.board[0][i] = piece_types[i](0, i, "b")  
            self.board[7][i] = piece_types[i](7, i, "w")  

        #Black and white pawn initialization
        for i in range(BOARD_SIZE):
            self.board[1][i] = Pawn(1, i, "b") 
            self.board[6][i] = Pawn(6, i, "w")

        self.p1_name = "Player 1"
        self.p2_name = "Player 2"

        self.turn = "w"

        self.time1 = DEFAULT_PLAYING_TIME
        self.time2 = DEFAULT_PLAYING_TIME

        self.stored_time_one = 0
        self.stored_time_two = 0

        self.winner = None

        self.start_time = time.time()

    def update_moves(self):
        """
        Updates the valid moves for pieces on the board

        """
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != 0:
                    #Update the move list for each piece on the board
                    self.board[i][j].update_valid_moves(self.board)

    def draw(self, win, color):
        """
        Draws the board and the pieces onto a window

        Arguments:
            win: The pygame window surface to draw on
            color (string): The color of the player whose pieces are being drawn
        """
        if self.last and color == self.turn:
            y, x = self.last[0]
            y1, x1 = self.last[1]

            #Draws move circles for previous move
            xx = (4 - x) +round(WINDOW_MARGIN + (x * WINDOW_SIZE / BOARD_SIZE))
            yy = 3 + round(WINDOW_MARGIN + (y * WINDOW_SIZE / BOARD_SIZE))
            pygame.draw.circle(win, (0,0,255), (xx+self.CIRCLE_X_OFFSET, yy+self.CIRCLE_Y_OFFSET), self.MOVE_CIRCLE_RADIUS, self.MOVE_CIRCLE_THICKNESS)
            xx1 = (4 - x) + round(WINDOW_MARGIN + (x1 * WINDOW_SIZE / BOARD_SIZE))
            yy1 = 3+ round(WINDOW_MARGIN + (y1 * WINDOW_SIZE / BOARD_SIZE))
            pygame.draw.circle(win, (0, 0, 255), (xx1 + self.CIRCLE_X_OFFSET, yy1 + self.CIRCLE_Y_OFFSET), self.MOVE_CIRCLE_RADIUS, self.MOVE_CIRCLE_THICKNESS)

        s = None
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != 0:
                    self.board[i][j].draw(win, color)
                    if self.board[i][j].is_selected:
                        s = (i, j)


    def get_danger_moves(self, color):
        """
        Retrieves all moves that threaten a player of a given color

        Arguments:
            color (string): The color of the player

        Returns:
            list of positions that are threatened by opponent pieces
        """
        danger_moves = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != 0:
                    if self.board[i][j].color != color:
                        for move in self.board[i][j].move_list:
                            danger_moves.append(move)

        return danger_moves

    def is_checked(self, color):
        """
        Checks if the player's king of the given color is in check

        Arguments:
            color (string): The color of the king possibly being check

        Returns:
            True if the player is in check, otherwise False.
        """
        self.update_moves()
        danger_moves = self.get_danger_moves(color)
        king_pos = (-1, -1)
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != 0:
                    if self.board[i][j].king and self.board[i][j].color == color:
                        king_pos = (j, i)

        if king_pos in danger_moves:
            return True

        return False

    def select(self, col, row, color):
        """
        Selects a piece on the board and moves it if valid move is made

        Arguments:
            col (integer): The column of the selected position
            row (integer): The row of the selected position 
            color (string): The color of the player making the move

        Returns:
            True if the move was made successfully, else False.
        """
        changed = False
        prev = (-1, -1)
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != 0:
                    if self.board[i][j].selected:
                        prev = (i, j)

        # if piece is empty and there is a previously selected piece
        if self.board[row][col] == 0 and prev!=(-1,-1):
            moves = self.board[prev[0]][prev[1]].move_list
            if (col, row) in moves:
                changed = self.move(prev, (row, col), color)

        else:
            if prev == (-1,-1):
                self.reset_selected()
                if self.board[row][col] != 0:
                    self.board[row][col].selected = True
            else:
                if self.board[prev[0]][prev[1]].color != self.board[row][col].color:
                    moves = self.board[prev[0]][prev[1]].move_list
                    if (col, row) in moves:
                        changed = self.move(prev, (row, col), color)

                    if self.board[row][col].color == color:
                        self.board[row][col].selected = True
                
                else:
                    if self.board[row][col].color == color:
                        #Logic for castling a rook
                        self.reset_selected()
                        if self.board[prev[0]][prev[1]].moved == False and self.board[prev[0]][prev[1]].rook and self.board[row][col].king and col != prev[1] and prev!=(-1,-1):
                            castle = True
                            #Castle right
                            if prev[1] < col:
                                for j in range(prev[1]+1, col):
                                    if self.board[row][j] != 0:
                                        castle = False

                                if castle:
                                    changed = self.move(prev, (row, 3), color)
                                    changed = self.move((row,col), (row, 2), color)
                                if not changed:
                                    self.board[row][col].selected = True
                            #Castle left
                            else:
                                for j in range(col+1,prev[1]):
                                    if self.board[row][j] != 0:
                                        castle = False

                                if castle:
                                    changed = self.move(prev, (row, 6), color)
                                    changed = self.move((row,col), (row, 5), color)
                                if not changed:
                                    self.board[row][col].selected = True
                            
                        else:
                            self.board[row][col].selected = True

        if changed:
            if self.turn == "w":
                self.turn = "b"
                self.reset_selected()
            else:
                self.turn = "w"
                self.reset_selected()

    def reset_selected(self):
        """
        Deselect all selected pieces on the board
        """
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != 0:
                    self.board[i][j].selected = False

    def check_mate(self, color):
        """
        Checks if the player of the given color is in checkmate.

        Arguments:
            color (string): The color of the player to check

        Returns:
            False temporarily as function is not completed
        """
        '''if self.is_checked(color):
            king = None
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.board[i][j] != 0:
                        if self.board[i][j].king and self.board[i][j].color == color:
                            king = self.board[i][j]
            if king is not None:
                valid_moves = king.valid_moves(self.board)

                danger_moves = self.get_danger_moves(color)

                danger_count = 0

                for move in valid_moves:
                    if move in danger_moves:
                        danger_count += 1
                return danger_count == len(valid_moves)'''

        return False

    def move(self, start, end, color):
        """
        Move piece from start position to end position

        Arguments:
            start (list): The starting position
            end (list): The ending position
            color (string): The color of the player making the move

        Returns:
            True if move was successful, else False
        """
        
        checked_before = self.is_checked(color)
        changed = True
        n_board = self.board[:]
        
        #If the piece is pawn, mark as no longer being the first move so it cannot move two spaces
        if n_board[start[0]][start[1]].pawn:
            n_board[start[0]][start[1]].first = False

        n_board[start[0]][start[1]].change_pos((end[0], end[1]))
        n_board[end[0]][end[1]] = n_board[start[0]][start[1]]
        n_board[start[0]][start[1]] = 0
        self.board = n_board

        #If move made results in check, undo the move
        if self.is_checked(color) or (checked_before and self.is_checked(color)):
            changed = False
            n_board = self.board[:]
            if n_board[end[0]][end[1]].pawn:
                n_board[end[0]][end[1]].first = True

            #switch positions back
            n_board[end[0]][end[1]].change_pos((start[0], start[1]))
            n_board[start[0]][start[1]] = n_board[end[0]][end[1]]
            n_board[end[0]][end[1]] = 0
            self.board = n_board
        else:
            self.reset_selected()

        self.update_moves()
        if changed:
            self.last = [start, end]
            if self.turn == "w":
                self.stored_time_one += (time.time() - self.start_time)
            else:
                self.stored_time_two += (time.time() - self.start_time)
            self.start_time = time.time()

        return changed
