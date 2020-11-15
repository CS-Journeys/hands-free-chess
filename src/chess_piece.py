# Defintion of first and second diagonals of a square matrix:
#      a - - - b
#      - a - b -   The 'a's represent the first diagonal
#      - - * - -   The 'b's represent the second diagonal
#      - b - a -
#      b - - - a
# 

import numpy as np
from PIL import Image

IMG_FILEPATH = 'res/chess-piece-images/'

class ChessPiece:
    def __init__(self, name, color = 'empty'):
        self.name = name
        self.color = color
        if self.name != 'unknown':
            self.img_onblack_fname = name + '-' + color + '-black.png'
            self.img_onwhite_fname = name + '-' + color + '-white.png'
            self.img = [np.array(Image.open(IMG_FILEPATH + self.img_onblack_fname)),
                        np.array(Image.open(IMG_FILEPATH + self.img_onwhite_fname))]

    def can_be_moved(self, currentPos, nextPos, board_data):
        is_legal = True

        # Rules that apply to all types of pieces
        if currentPos == nextPos:
            is_legal = False # can't "move" by not moving
        if board_data[nextPos[1], nextPos[0]].color == self.color:
            is_legal = False # can't move to spot occupied by piece of same color

        # Useful variables for helping to determine if a piece is in the way
        sorted_rows = [currentPos[1], nextPos[1]]
        sorted_rows.sort()
        sorted_columns = [currentPos[0], nextPos[0]]
        sorted_columns.sort()

        # Rules specific to each type of piece
        # KING
        if self.name == 'king':
            # move by more than 1 column
            if abs(currentPos[0] - nextPos[0]) > 1:
                is_legal = False
            # move by more than 1 row
            if abs(currentPos[1] - nextPos[1]) > 1:
                is_legal = False
            # TO-DO: add support for castling

        # QUEEN
        elif self.name == 'queen':
            # vertical move, but a piece is in the way
            if _on_vertical_line(sorted_rows):
                if _vertical_is_blocked(currentPos[0], sorted_rows, board_data):
                    is_legal = False
            # horizontal move, but a piece is in the way
            elif _on_horizontal_line(sorted_columns):
                if _horizontal_is_blocked(currentPos[1], sorted_columns, board_data):
                    is_legal = False
            # diagonal move (first), but a piece is in the way
            elif _on_first_diagonal(currentPos, nextPos):
                if _first_diagonal_is_blocked(sorted_rows, sorted_columns, board_data):
                    is_legal = False
            # diagonal move (second), but a piece is in the way
            elif _on_second_diagonal(currentPos, nextPos):
                if _second_diagonal_is_blocked(sorted_rows, sorted_columns, board_data):
                    is_legal = False
            # neither vertical, horizontal, nor diagonal move
            else:
                is_legal = False

        # PAWN
        elif self.name == 'pawn':
            # not vertical move
            if (not _on_vertical_line(sorted_columns)):
                is_legal = False
            # move forward by 2, but...
            if currentPos[1] - nextPos[1] == 2:
                # pawn not in starting position
                if currentPos[1] != 6:
                    is_legal = False
                # a piece is in the way
                if _vertical_is_blocked(currentPos[0], sorted_rows, board_data):
                    is_legal = False
            # neither a move by 1 nor 2 spots forward
            elif currentPos[1] - nextPos[1] != 1:
                is_legal = False
        # TO-DO: add support for pawn attacks (diagonal move)
        # TO-DO: add support for 'en passant'

        # ROOK
        elif self.name == 'rook':
            # vertical move, but a piece is in the way
            if _on_vertical_line(sorted_rows):
                if _vertical_is_blocked(currentPos[0], sorted_rows, board_data):
                    is_legal = False
            # horizontal move, but a piece is in the way
            elif _on_horizontal_line(sorted_columns):
                if _horizontal_is_blocked(currentPos[1], sorted_columns, board_data):
                    is_legal = False
            # neither vertical nor horizontal move
            else:
                is_legal = False

        # KNIGHT
        elif self.name == 'knight':
            deltaCol = currentPos[0] - nextPos[0]
            deltaRow = currentPos[1] - nextPos[1]
            # not an L-shaped move
            if not ((deltaCol == 2 and deltaRow == 1)
                    or (deltaCol == 2 and deltaRow == -1)
                    or (deltaCol == 1 and deltaRow == 2)
                    or (deltaCol == 1 and deltaRow == -2)
                    or (deltaCol == -1 and deltaRow == 2)
                    or (deltaCol == -1 and deltaRow == -2)
                    or (deltaCol == -2 and deltaRow == 1)
                    or (deltaCol == -2 and deltaRow == -1)):
                is_legal = False

        # BISHOP
        elif self.name == 'bishop':
            # diagonal move (first), but a piece is in the way
            if _on_first_diagonal(currentPos, nextPos):
                if _first_diagonal_is_blocked(sorted_rows, sorted_columns, board_data):
                    is_legal = False
            # diagonal move (second), but a piece is in the way
            elif _on_second_diagonal(currentPos, nextPos):
                if _second_diagonal_is_blocked(sorted_rows, sorted_columns, board_data):
                    is_legal = False
            # not a diagonal move
            else:
                is_legal = False

        return is_legal

# Functions to help with rules for each type of chess piece
def _on_vertical_line(cols):
    return (cols[0] == cols[1])

def _on_horizontal_line(rows):
    return (rows[0] == rows[1])

def _on_first_diagonal(coords1, coords2):
    return (coords1[0] - coords2[0] == coords1[1] - coords2[1])

def _on_second_diagonal(coords1, coords2):
    return (coords1[0] - coords2[0] == coords2[1] - coords1[1])

def _vertical_is_blocked(column, sorted_rows, board_data):
    is_blocked = False
    for i in range(sorted_rows[0] + 1, sorted_rows[1]):
        if board_data[i, column].name != 'empty':
            is_blocked = True
    return is_blocked

def _horizontal_is_blocked(row, sorted_columns, board_data):
    is_blocked = False
    for i in range(sorted_columns[0] + 1, sorted_columns[1]):
        if board_data[row, i].name != 'empty':
            is_blocked = True
    return is_blocked

def _first_diagonal_is_blocked(sorted_rows, sorted_columns, board_data):
    is_blocked = False
    for i in range(1, sorted_rows[1] - sorted_rows[0]):
        if board_data[sorted_rows[0] + i, sorted_columns[0] + i].name != 'empty':
            is_blocked = True
    return is_blocked

def _second_diagonal_is_blocked(sorted_rows, sorted_columns, board_data):
    is_blocked = False
    for i in range(1, sorted_rows[1] - sorted_rows[0]):
        if board_data[sorted_rows[1] - i, sorted_columns[0] + i].name != 'empty':
            is_legal = False
    return is_blocked
