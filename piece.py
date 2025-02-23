import pygame
import os
from board import BOARD_SIZE
from game import WINDOW_MARGIN, WINDOW_SIZE
from game import RED, WHITE

#load images for each piece
b_bishop = pygame.image.load(os.path.join("img", "black_bishop.png"))
b_king = pygame.image.load(os.path.join("img", "black_king.png"))
b_knight = pygame.image.load(os.path.join("img", "black_knight.png"))
b_pawn = pygame.image.load(os.path.join("img", "black_pawn.png"))
b_queen = pygame.image.load(os.path.join("img", "black_queen.png"))
b_rook = pygame.image.load(os.path.join("img", "black_rook.png"))

w_bishop = pygame.image.load(os.path.join("img", "white_bishop.png"))
w_king = pygame.image.load(os.path.join("img", "white_king.png"))
w_knight = pygame.image.load(os.path.join("img", "white_knight.png"))
w_pawn = pygame.image.load(os.path.join("img", "white_pawn.png"))
w_queen = pygame.image.load(os.path.join("img", "white_queen.png"))
w_rook = pygame.image.load(os.path.join("img", "white_rook.png"))

b = [b_bishop, b_king, b_knight, b_pawn, b_queen, b_rook]
w = [w_bishop, w_king, w_knight, w_pawn, w_queen, w_rook]

B = []
W = []

PIECE_SIZE = 55

for img in b:
    B.append(pygame.transform.scale(img, (PIECE_SIZE, PIECE_SIZE)))

for img in w:
    W.append(pygame.transform.scale(img, (PIECE_SIZE, PIECE_SIZE)))

class Piece:
    img = -1
    
    #Piece highlighting constants
    HIGHLIGHT_SIZE = 62
    HIGHLIGHT_THICKNESS = 4

    def __init__(self, row, col, color):
        """
        Initialize a piece object
        Args:
            row (integer): The row the piece is in
            col (integer): The column the piece is in
            color (string): The color of the piece
        """
        self.row = row
        self.col = col
        self.color = color
        self.selected = False
        self.move_list = []
        self.king = False
        self.pawn = False

    def is_selected(self):
        """
        Check if the piece is selected

        Returns:
            Boolean: True if the piece is selected, False otherwise
        """
        return self.selected

    def update_valid_moves(self, board):
        """
        Update the valid moves for the piece
        Args:
            board (list): The current board state
        """
        self.move_list = self.valid_moves(board)

    def draw(self, win, color):
        """
        Draw the piece on the board
        Args:
            win (pygame window): The window to draw the piece on
            color (string): The color of the piece
        """
        if self.color == "w":
            drawThis = W[self.img]
        else:
            drawThis = B[self.img]

        x = (4 - self.col) + round(WINDOW_MARGIN + (self.col * WINDOW_SIZE / BOARD_SIZE))
        y = 3 + round(WINDOW_MARGIN + (self.row * WINDOW_SIZE / BOARD_SIZE))

        if self.selected and self.color == color:
            pygame.draw.rect(win, RED, (x, y, self.HIGHLIGHT_SIZE, self.HIGHLIGHT_SIZE), self.HIGHLIGHT_THICKNESS)

        win.blit(drawThis, (x, y))

        '''if self.selected and self.color == color:  # Remove false to draw dots
            moves = self.move_list

            for move in moves:
                x = 33 + round(WINDOW_MARGIN + (move[0] * WINDOW_SIZE / BOARD_SIZE))
                y = 33 + round(WINDOW_MARGIN + (move[1] * WINDOW_SIZE / BOARD_SIZE))
                pygame.draw.circle(win, RED, (x, y), 10)'''

    def change_pos(self, pos):
        """
        Change the position of the piece

        Args:
            pos (list): The new position of the piece
        """
        self.row = pos[0]
        self.col = pos[1]

    def __str__(self):
        return str(self.col) + " " + str(self.row)

    def generate_moves(self, board, directions):
        """
        Generate valid moves for the piece based on given directions

        Args:
            board (list): The current board state
            directions (list): List of directions to check for valid moves

        Returns:
            list: List of valid moves
        """
        moves = []
        # Check each direction for valid moves
        for direction in directions:
            di, dj = direction
            i, j = self.row, self.col
            
            # Move in the direction until a piece is encountered
            while True:
                i += di
                j += dj
                # Check if the move is within the board
                if 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE:
                    p = board[i][j]
                    if p == 0:
                        moves.append((j, i))
                    elif p.color != self.color:
                        moves.append((j, i))
                        break
                    else:
                        break
                else:
                    break
        return moves



class Bishop(Piece):
    img = 0

    def valid_moves(self, board):
        """
        Generate valid moves for the bishop piece

        Args:
            board (list): The current board state

        Returns:
            list: List of valid moves
        """
        directions = [(-1, 1), (-1, -1), (1, 1), (1, -1)]
        return self.generate_moves(board, directions)


class King(Piece):
    img = 1

    def __init__(self, row, col, color):
        """
        Initialize a king piece

        Args:
            row (integer): The row the piece is in
            col (integer): The column the piece is in
            color (string): The color of the piece
        """
        super().__init__(row, col, color)
        self.king = True

    def valid_moves(self, board):
        """
        Generate valid moves for the king piece

        Args:
            board (list): The current board state

        Returns:
            list: List of valid moves
        """
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        return self.generate_moves(board, directions)


class Knight(Piece):
    
    img = 2

    def valid_moves(self, board):
        """
        Generate valid moves for the knight piece

        Args:
            board (list): The current board state

        Returns:
            list: List of valid moves
        """
        directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        return self.generate_moves(board, directions)


class Pawn(Piece):
    img = 3

    def __init__(self, row, col, color):
        """
        Initialize a pawn piece

        Args:
            row (integer): The row the piece is in
            col (integer): The column the piece is in
            color (string): The color of the piece
        """
        super().__init__(row, col, color)
        self.first = True
        self.queen = False
        self.pawn = True

    def valid_moves(self, board):
        """
        Generate valid moves for the pawn piece

        Args:
            board (list): The current board state

        Returns:
            list: List of valid moves
        """
        i = self.row
        j = self.col

        moves = []
        # Check for valid moves based on the color of the piece
        try:
            # BLACK
            if self.color == "b":
                if i < 7:
                    p = board[i + 1][j]
                    if p == 0:
                        moves.append((j, i + 1))

                    # DIAGONAL
                    if j < 7:
                        p = board[i + 1][j + 1]
                        if p != 0 and p.color != self.color:
                            moves.append((j + 1, i + 1))

                    if j > 0:
                        p = board[i + 1][j - 1]
                        if p != 0 and p.color != self.color:
                            moves.append((j - 1, i + 1))

                if self.first and i < 6:
                    p = board[i + 2][j]
                    if p == 0 and board[i + 1][j] == 0:
                        moves.append((j, i + 2))
            # WHITE
            else:  
                if i > 0:
                    p = board[i - 1][j]
                    if p == 0:
                        moves.append((j, i - 1))

                    # DIAGONAL
                    if j < 7:
                        p = board[i - 1][j + 1]
                        if p != 0 and p.color != self.color:
                            moves.append((j + 1, i - 1))

                    if j > 0:
                        p = board[i - 1][j - 1]
                        if p != 0 and p.color != self.color:
                            moves.append((j - 1, i - 1))

                if self.first and i > 1:
                    p = board[i - 2][j]
                    if p == 0 and board[i - 1][j] == 0:
                        moves.append((j, i - 2))
        except:
            pass

        return moves


class Queen(Piece):
    img = 4

    def valid_moves(self, board):
        """
        Generate valid moves for the queen piece

        Args:
            board (list): The current board state

        Returns:
            list: List of valid moves
        """
        directions = [(-1, 1), (-1, -1), (1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        return self.generate_moves(board, directions)


class Rook(Piece):
    img = 5

    def valid_moves(self, board):
        """
        Generate valid moves for the rook piece

        Args:
            board (list): The current board state

        Returns:
            list: List of valid moves
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return self.generate_moves(board, directions)