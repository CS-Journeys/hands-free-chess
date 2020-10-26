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
#   each element is a string that represents a piece ("knight", "pawn", "empty", etc.)
#
######################################################################

import numpy as np


def is_legal_move(command, board_data):
    # FIXME
    return True

def get_initial_position(command, board_data):
    initial_position = (-1, -1)
    
    if (len(command) == 5): # explicit starting position structure
        initial_position = _alphanum_to_indices(command[0], int(command[1]))
        
    else:                   # implicit starting position structure
        # TODO: figure out initial position based on which piece can legally
        #       be moved to the position that was declared by the command
        pass
    
    return (initial_position)

def get_final_position(command, board_data):
    final_position = _alphanum_to_indices(command[-2], int(command[-1]))
    return final_position


### Private Functions ###
def _alphanum_to_indices(alpha, num):
    col = ord(alpha) - 97
    row = num - 1
    return (col, row)
