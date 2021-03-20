# Definition of first and second diagonals of a square matrix:
#      a - - - b
#      - a - b -   The 'a's represent the first diagonal
#      - - * - -   The 'b's represent the second diagonal
#      - b - a -   The '*' is an element of both diagonals
#      b - - - a

import logging
import numpy as np
from PIL import Image


IMG_FILEPATH = 'res/chess-piece-images/'

class ChessPiece:
    """
    The ChessPiece class stores all relevant information on chess pieces (except for their position, which is handled
    by the BoardManager).

    Each square on the chessboard is represented by a ChessPiece object. A ChessPiece object has:
        (a) a name (like 'rook', 'pawn', 'king', 'empty', etc.)
        (b) a color ('black', 'white', or 'empty')
        (c) two reference images (one for when the piece is on a black square, the other for when on a white square)
    Note that an empty square has an "empty" ChessPiece object on it.

    The ChessPiece class also stores the rules for each type of piece. We can call 'can_be_moved()' to determine
    if this specific chess piece can be moved from point A to point B given the board's state.
    """

    ''' CONSTRUCTOR '''
    def __init__(self, name, color='empty'):
        self.log = logging.getLogger(__name__)
        self.name = name
        self.color = color
        if self.name != 'unknown':
            self.img_onblack_fname = name + '-' + color + '-black.png'
            self.img_onwhite_fname = name + '-' + color + '-white.png'
            try:
                self.img = [np.array(Image.open(IMG_FILEPATH + self.img_onblack_fname)),
                            np.array(Image.open(IMG_FILEPATH + self.img_onwhite_fname))]
            except FileNotFoundError:
                self.log.error(f"Unable to find the {self.name}'s images.", exc_info=True)

    ''' PUBLIC FUNCTIONS '''
    def can_be_moved(self, current_pos, next_pos, board_state):
        """
        This function determines if this piece can be moved from point A to point B given the current state of the board

        Parameters:
            - current_pos: the piece's current position in the form (column, row)
            - next_pos: the piece's destination position in the form (column, row)
            - board_state: an 8x8 NumPy matrix of ChessPiece objects
        Output:
            - return: if this piece can be moved from its current position to its next position, then return True,
                else, return False
        Example:
            current_pos is (0,0), next_pos is (7,7), and the board looks like this:
                         0  1  2  3  4  5  6  7
                       +-------------------------+
                     0 | wq                      |    wq: white queen
                     1 |                         |    wk: white king
                     2 |                bk       |    bq: black queen
                     3 |                         |    bk: black king
                     4 |                         |    br: black rook
                     5 |                         |
                     6 |                   wk    |
                     7 |    bq                br |
                       +-------------------------+
                       self.name is "queen" and self.color is "white"
                       => the function will return False because the white king is blocking the white queen
                          from moving to (7,7) and capturing the black rook
        """
        # TODO: establish the rules for each piece in a clearer, more elegant way
        self.log.debug(f"Started determining if {self.color} {self.name} @ {current_pos} can move to {next_pos}")

        is_legal = True
        general_rule_failure = False

        # Rules that apply to all types of pieces
        if current_pos == next_pos:
            is_legal = False  # can't "move" by not moving
        if board_state[next_pos[1], next_pos[0]].color == self.color:
            is_legal = False  # can't move to spot occupied by piece of same color
        if not is_legal:
            general_rule_failure = True
            self.log.debug(f"General rule failure")

        # Useful variables for helping to determine if a piece is in the way
        sorted_rows = [current_pos[1], next_pos[1]]
        sorted_rows.sort()
        sorted_columns = [current_pos[0], next_pos[0]]
        sorted_columns.sort()
        self.log.debug(f"Sorted rows: {sorted_rows}")
        self.log.debug(f"Sorted columns: {sorted_columns}")

        # Rules specific to each type of piece
        # KING
        if self.name == 'king':
            # move by more than 1 column
            if abs(current_pos[0] - next_pos[0]) > 1:
                if not ((self.color == 'white' and current_pos == (4, 7)) or
                        (self.color == 'black' and current_pos == (3, 7))):
                    is_legal = False
                else:
                    if self.color == 'black':
                        if (current_pos[0] - next_pos[0]) == 2:
                            if not ((board_state[7, 0].name == 'rook') and (board_state[7, 0].color == 'black')):
                                is_legal = False
                            else:
                                if _horizontal_is_blocked(7, (3, 0), board_state):
                                    is_legal = False
                        elif (current_pos[0] - next_pos[0]) == -2:
                            if not ((board_state[7, 7].name == 'rook') and (board_state[7, 7].color == 'black')):
                                is_legal = False
                            else:
                                if _horizontal_is_blocked(7, (3, 7), board_state):
                                    is_legal = False
                        else:
                            is_legal = False
                    else:
                        if (current_pos[0] - next_pos[0]) == 2:
                            if not ((board_state[7, 0].name == 'rook') and (board_state[7, 0].color == 'white')):
                                is_legal = False
                            else:
                                if _horizontal_is_blocked(7, (4, 0), board_state):
                                    is_legal = False
                        elif (current_pos[0] - next_pos[0]) == -2:
                            if not ((board_state[7, 7].name == 'rook') and (board_state[7, 7].color == 'white')):
                                is_legal = False
                            else:
                                if _horizontal_is_blocked(7, (4, 7), board_state):
                                    is_legal = False
                        else:
                            is_legal = False

            # move by more than 1 row
            if abs(current_pos[1] - next_pos[1]) > 1:
                is_legal = False

        # QUEEN
        elif self.name == 'queen':
            # vertical move, but a piece is in the way
            if _on_vertical_line(sorted_rows):
                if _vertical_is_blocked(current_pos[0], sorted_rows, board_state):
                    is_legal = False
            # horizontal move, but a piece is in the way
            elif _on_horizontal_line(sorted_columns):
                if _horizontal_is_blocked(current_pos[1], sorted_columns, board_state):
                    is_legal = False
            # diagonal move (first), but a piece is in the way
            elif _on_first_diagonal(current_pos, next_pos):
                if _first_diagonal_is_blocked(sorted_rows, sorted_columns, board_state):
                    is_legal = False
            # diagonal move (second), but a piece is in the way
            elif _on_second_diagonal(current_pos, next_pos):
                if _second_diagonal_is_blocked(sorted_rows, sorted_columns, board_state):
                    is_legal = False
            # neither vertical, horizontal, nor diagonal move
            else:
                is_legal = False

        # PAWN
        elif self.name == 'pawn':
            # not vertical move
            if not _on_vertical_line(sorted_columns):
                if (current_pos[1] - next_pos[1]) == 1 and abs(current_pos[0] - next_pos[0]) == 1:
                    if board_state[next_pos[1], next_pos[0]].name == 'empty':
                        if current_pos[1] == 3 and board_state[3, next_pos[0]].name == 'pawn':
                            if self.color == 'black':
                                if not ((board_state[next_pos[1], next_pos[0]].color == 'white') or
                                        (board_state[next_pos[1] + 1, next_pos[0]].color == 'white')):
                                    is_legal = False
                            else:
                                if not ((board_state[next_pos[1], next_pos[0]].color == 'black') or
                                        (board_state[next_pos[1] + 1, next_pos[0]].color == 'black')):
                                    is_legal = False
                        else:
                            is_legal = False
                else:
                    is_legal = False

            # move forward by 2, but...
            if current_pos[1] - next_pos[1] == 2:
                # pawn not in starting position
                if current_pos[1] != 6:
                    is_legal = False
                # a piece is in the way
                if _vertical_is_blocked(current_pos[0], sorted_rows, board_state):
                    is_legal = False
            # neither a move by 1 nor 2 spots forward
            elif current_pos[1] - next_pos[1] != 1:
                is_legal = False

        # ROOK
        elif self.name == 'rook':
            # vertical move, but a piece is in the way
            if _on_vertical_line(sorted_rows):
                if _vertical_is_blocked(current_pos[0], sorted_rows, board_state):
                    is_legal = False
            # horizontal move, but a piece is in the way
            elif _on_horizontal_line(sorted_columns):
                if _horizontal_is_blocked(current_pos[1], sorted_columns, board_state):
                    is_legal = False
            # neither vertical nor horizontal move
            else:
                is_legal = False

        # KNIGHT
        elif self.name == 'knight':
            delta_col = current_pos[0] - next_pos[0]
            delta_row = current_pos[1] - next_pos[1]
            # not an L-shaped move
            if not ((delta_col == 2 and delta_row == 1)
                    or (delta_col == 2 and delta_row == -1)
                    or (delta_col == 1 and delta_row == 2)
                    or (delta_col == 1 and delta_row == -2)
                    or (delta_col == -1 and delta_row == 2)
                    or (delta_col == -1 and delta_row == -2)
                    or (delta_col == -2 and delta_row == 1)
                    or (delta_col == -2 and delta_row == -1)):
                is_legal = False

        # BISHOP
        elif self.name == 'bishop':
            # diagonal move (first), but a piece is in the way
            if _on_first_diagonal(current_pos, next_pos):
                if _first_diagonal_is_blocked(sorted_rows, sorted_columns, board_state):
                    is_legal = False
            # diagonal move (second), but a piece is in the way
            elif _on_second_diagonal(current_pos, next_pos):
                if _second_diagonal_is_blocked(sorted_rows, sorted_columns, board_state):
                    is_legal = False
            # not a diagonal move
            else:
                is_legal = False

        if not general_rule_failure and not is_legal:
            self.log.debug(f"{self.name} rule failure")

        self.log.debug(f"Legal move: {is_legal}")
        return is_legal


''' HELPER FUNCTIONS '''
def _on_vertical_line(cols):
    """
    Determine if given column indices are the same
    """
    return cols[0] == cols[1]

def _on_horizontal_line(rows):
    """
    Determine if given row indices are the same
    """
    return rows[0] == rows[1]

def _on_first_diagonal(coords1, coords2):
    """
    Determine if given coordinates are in a diagonal of type "first"
    Note: see top of file for definition of "first diagonal"
    """
    return coords1[0] - coords2[0] == coords1[1] - coords2[1]

def _on_second_diagonal(coords1, coords2):
    """
    Determine if given coordinates are in a diagonal of type "second"
    Note: see top of file for definition of "second diagonal"
    """
    return coords1[0] - coords2[0] == coords2[1] - coords1[1]

def _vertical_is_blocked(column, sorted_rows, board_data):
    """
    Determine if a piece is between two vertically aligned coordinates
    """
    is_blocked = False
    for i in range(sorted_rows[0] + 1, sorted_rows[1]):
        if board_data[i, column].name != 'empty':
            is_blocked = True
    return is_blocked

def _horizontal_is_blocked(row, sorted_columns, board_data):
    """
    Determine if a piece is between two horizontally aligned coordinates
    """
    is_blocked = False
    for i in range(sorted_columns[0] + 1, sorted_columns[1]):
        if board_data[row, i].name != 'empty':
            is_blocked = True
    return is_blocked

def _first_diagonal_is_blocked(sorted_rows, sorted_columns, board_data):
    """
    Determine if a piece is between two coordinates aligned on a "first" diagonal
    """
    is_blocked = False
    for i in range(1, sorted_rows[1] - sorted_rows[0]):
        if board_data[sorted_rows[0] + i, sorted_columns[0] + i].name != 'empty':
            is_blocked = True
    return is_blocked

def _second_diagonal_is_blocked(sorted_rows, sorted_columns, board_data):
    """
    Determine if a piece is between two coordinates aligned on a "second" diagonal
    """
    is_blocked = False
    for i in range(1, sorted_rows[1] - sorted_rows[0]):
        if board_data[sorted_rows[1] - i, sorted_columns[0] + i].name != 'empty':
            is_blocked = True
    return is_blocked
