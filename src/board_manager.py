######################################################################
# PARAMETER DOCUMENTATION
#
# command is an array of strings
#   implicit initial position structure:
#     command[0] is "knight", "bishop", "pawn", things like that.
#     command[1] is the final position letter (lowercase a-h)
#     command[2] is the final position number (1-8)
#   explicit initial position structure:
#     command[0] is the initial position letter (lowercase a-h)
#     command[1] is the initial position number (1-8)
#     command[2] is the piece name ("knight", "bishop", etc.)
#     command[3] is the final position letter (lowercase a-h)
#     command[4] is the final position number (1-8)
#
# board_data is a 8x8 numpy array
#   each element is a ChessPiece object that contains name and color
#
# user_color is a string
#   either "black" or "white"
######################################################################

import numpy as np

UNDETERMINED_POSITION = (-1, -1)
AMBIGUOUS_POSITION = (-2, -2)


######################################################################
# description : Determine if a command is legal given the user's color
#               and the current state of the board
# parameters  : array of strings, string, 8x8 matrix of ChessPieces
# return      : True or False
def is_legal_move(command, user_color, board_data):
    is_legal = False

    # Get the original position before the move is made, the destination position,
    # and the name of the piece to be moved according to the user's command 
    initial_position = get_initial_position(command, user_color, board_data)
    final_position = get_final_position(command, user_color, board_data)
    piece = board_data[initial_position[1], initial_position[0]]

    if (piece.name == extract_piece_name(command)
            and piece.color == user_color
            and piece.can_be_moved(initial_position, final_position, board_data)):
        is_legal = True

    return is_legal


######################################################################
# description : Determine if the initial position is ambiguous (aka multiple initial positions are possible)
# parameters  : array of strings, string, 8x8 matrix of ChessPieces
# return      : If the initial position is ambiguous, return True,
#               else, return False
# example     : The command is ["knight", "d", "6"], the user is Black,
#               there is one black knight at F7 and another at B7.
#               In this situation, it isn't clear which black knight the user wants
#               to move, because either knight could legally be moved to D6.
def is_ambiguous_move(command, user_color, board_data):
    is_ambiguous = False
    initial_position = get_initial_position(command, user_color, board_data)
    if initial_position == AMBIGUOUS_POSITION:
        is_ambiguous = True
    return is_ambiguous


######################################################################
# description : Get the initial or "original" position of the piece
#               to be moved before the move is made.
# parameters  : array of strings, string, 8x8 matrix of ChessPieces
# return      : the initial position's indices (0-7) in the form (column, row)
# example     : The command is ["king", "d", "7"], the user is White,
#               and the white king is currently at D8.
#               => the function returns (4, 7) -- the index equivalent of D8
def get_initial_position(command, user_color, board_data):
    initial_position = UNDETERMINED_POSITION

    # explicit starting position structure
    if (len(command) == 5): 
        initial_position = _alphanum_to_indices(command[0], int(command[1]), user_color)
    
    # implicit starting position structure
    else:
        # set initial position to the position of the only piece of the given type
        # that can be moved to the final position as declared by the command
        num_movable_pieces = 0
        command_piece_name = command[0]
        final_position = get_final_position(command, user_color, board_data)
        for row in range(0, 8):
            for col in range(0, 8):
                board_piece = board_data[row,col]
                if (board_piece.can_be_moved((col, row), final_position, board_data)
                        and board_piece.name == command_piece_name
                        and board_piece.color == user_color):
                    initial_position = (col, row)
                    num_movable_pieces += 1
        # set initial position to unknown in ambiguous
        # situations where multiple pieces could be moved
        if num_movable_pieces > 1:
            initial_position = AMBIGUOUS_POSITION
            
    return (initial_position)


######################################################################
# description : Get the final or "destination" position of the piece to be moved
# parameters  : array of strings, string, 8x8 matrix of ChessPieces
# return      : the final position's indices (0-7) in the form (column, row)
# example     : The command is ["king", "d", "7"], the user is White,
#               and the white king is currently at D8.
#               => the function returns (6, 4)
def get_final_position(command, user_color, board_data):
    final_position = _alphanum_to_indices(command[-2], int(command[-1]), user_color)
    return final_position


######################################################################
# description : Extract the name of the piece to be moved from the user's command
# parameters  : array of strings
# return      : a string
# example     : extract_piece_name(["king", "d", "7"]) returns "king"
#               extract_piece_name(["d", "8", "king", "d", "7"]) returns "king"
def extract_piece_name(command):
    if len(command) == 5:
        name = command[2]
    else:
        name = command[0]
    return name


### Private Functions ###
######################################################################
# description : Convert alphanumeric coordinates to index coordinates
# parameters  : a single character lowercase string (a-h),
#               a single digit number (1-8),
#               and the color of the user's pieces ("black" or "white")
# return      : the index coordinates (0-7) in the form (column, row)
# example     : _alphanum_to_indices("h", 7, "white") returns (0, 6)
def _alphanum_to_indices(alpha, num, user_color):
    if user_color=='black':
        col = 7 - (ord(alpha) - 97)
        row = num - 1
    else:
        col = ord(alpha) - 97
        row = (num - 8)*-1
    return (col, row)
