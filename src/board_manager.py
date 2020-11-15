######################################################################
# PARAMETER DOCUMENTATION
#
# command is a list of strings
#   implicit starting position structure:
#     command[0] is "knight", "bishop", "pawn", things like that.
#     command[1] is the destination letter (lowercase a-h)
#     command[2] is the destination number (1-8)
#   explicit starting position structure:
#     command[0] is the starting position letter (lowercase a-h)
#     command[1] is the starting position number (1-8)
#     command[2] is the piece name ("knight", "bishop", etc.)
#     command[3] is the destination letter (lowercase a-h)
#     command[4] is the destination number (1-8)
#
# board_data is a 8x8 numpy array
#   each element is a ChessPiece object
#
# user_color is a string
#   either "black" or "white"
#
######################################################################

import numpy as np


UNDETERMINED_POSITION = (-1, -1)
AMBIGUOUS_POSITION = (-2, -2)

def is_legal_move(command, board_data, user_color):
    is_legal = False
    initial_position = get_initial_position(command, board_data, user_color)
    final_position = get_final_position(command, board_data)
    piece = board_data[initial_position[1], initial_position[0]]
    
    if (piece.name == extract_piece_name(command)
            and piece.color == user_color
            and piece.can_be_moved(initial_position, final_position, board_data)):
        is_legal = True

    return is_legal

def is_ambiguous_move(command, board_data, user_color):
    is_ambiguous = False
    initial_position = get_initial_position(command, board_data, user_color)
    if initial_position == AMBIGUOUS_POSITION:
        is_ambiguous = True
    return is_ambiguous

def get_initial_position(command, board_data, user_color):
    initial_position = UNDETERMINED_POSITION

    # explicit starting position structure
    if (len(command) == 5): 
        initial_position = _alphanum_to_indices(command[0], int(command[1]))
        
    # implicit starting position structure
    else:
        # set initial position to the position of the only piece of the given type
        # that can be moved to the final position as declared by the command
        num_movable_pieces = 0
        command_piece_name = command[0]
        final_position = get_final_position(command, board_data)
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

def get_final_position(command, board_data):
    final_position = _alphanum_to_indices(command[-2], int(command[-1]))
    return final_position

def extract_piece_name(command):
    if len(command) == 5:
        name = command[2]
    else:
        name = command[0]
    return name


### Private Functions ###
def _alphanum_to_indices(alpha, num):
    col = 7 - (ord(alpha) - 97) # correct column position if user is black
    row = num - 1               # correct row position if user is black
    return (col, row)
