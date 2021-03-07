"""
Hands-Free Chess allows the user to play chess online using only their voice instead of a keyboard and mouse.
Copyright (C) 2020  CS Journeys

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# TODO: update the comments
######################################################################
# PARAMETER DOCUMENTATION
#
# command is a MoveCommand object
#
# board_data is a 8x8 numpy array
#   each element is a ChessPiece object that contains name and color
#
# user_color is a string
#   either "black" or "white"
######################################################################

import logging

UNDETERMINED_POSITION = (-1, -1)
AMBIGUOUS_POSITION = (-2, -2)

class BoardManager:
    def __init__(self, board_data, color='black'):
        self.log = logging.getLogger(__name__)
        self.user_color = color
        self.board_data = board_data

    """ PUBLIC FUNCTIONS """
    def update_board(self, board_data):
        self.log.debug("Updating board data")
        self.board_data = board_data

    def set_user_color(self, color):
        self.log.info(f"New user piece color: {color}")
        self.user_color = color

    def is_legal_move(self, command):
        # description : Determine if a command is legal given the user's color
        #               and the current state of the board
        # parameters  : array of strings, string, 8x8 matrix of ChessPieces
        # return      : True or False
        ######################################################################

        self.log.info(f"Started checking legality of {command.text()}")

        is_legal = False

        # Get the original position before the move is made, the destination position,
        # and the name of the piece to be moved according to the user's command
        initial_position = self.get_initial_position(command)
        final_position = self.get_final_position(command)

        # Unable to establish initial position
        if initial_position[0] < 0:
            self.log.warning(f"Could not set starting position. Cause: {initial_position[0]}")

        # Initial position is set correctly,
        # so check if piece can move from initial to final position
        else:
            piece = self.board_data[initial_position[1], initial_position[0]]
            self.log.debug(f"Attempting to move piece {piece.color} {piece.name} "
                           f"from {initial_position} to {final_position}")

            if (piece.name == command.piece_name
                    and piece.color == self.user_color
                    and piece.can_be_moved(initial_position, final_position, self.board_data)):
                is_legal = True

        self.log.info(f"Legal move: {is_legal}")
        return is_legal

    def is_ambiguous_move(self, command):
        # description : Determine if the initial position is ambiguous (aka multiple initial positions are possible)
        # parameters  : MoveCommand object, string, 8x8 matrix of ChessPieces
        # return      : If the initial position is ambiguous, return True,
        #               else, return False
        # example     : The command is ["knight", "d", "6"], the user is Black,
        #               there is one black knight at F7 and another at B7.
        #               In this situation, it isn't clear which black knight the user wants
        #               to move, because either knight could legally be moved to D6.
        ######################################################################

        is_ambiguous = False
        initial_position = self.get_initial_position(command)
        if initial_position == AMBIGUOUS_POSITION:
            is_ambiguous = True
            self.log.warning(f"{command.text()} is ambiguous")
        else:
            self.log.debug(f"{command.text()} is unambiguous. Initial position: {initial_position}")
        return is_ambiguous

    def get_initial_position(self, command):
        # description : Get the initial or "original" position of the piece
        #               to be moved before the move is made.
        # parameters  : array of strings, string, 8x8 matrix of ChessPieces
        # return      : the initial position's indices (0-7) in the form (column, row)
        # example     : The command is ["king", "d", "7"], the user is White,
        #               and the white king is currently at D8.
        #               => the function returns (4, 7) -- the index equivalent of D8
        ######################################################################

        initial_position = UNDETERMINED_POSITION

        if command.get_src() is None:
            # set initial position to the position of the only piece of the given type
            # that can be moved to the final position as declared by the command
            num_movable_pieces = 0
            final_position = self.get_final_position(command)
            for row in range(0, 8):
                for col in range(0, 8):
                    board_piece = self.board_data[row, col]
                    if (board_piece.can_be_moved((col, row), final_position, self.board_data)
                            and board_piece.name == command.piece_name
                            and board_piece.color == self.user_color):
                        initial_position = (col, row)
                        num_movable_pieces += 1
                        self.log.debug(f"Implicit command structure, {command.piece_name} "
                                       f"@ {initial_position} can be moved")

            # set initial position to unknown in ambiguous
            # situations where multiple pieces could be moved
            if num_movable_pieces > 1:
                initial_position = AMBIGUOUS_POSITION
                self.log.warning(f"Implicit command structure, ambiguous starting position: {num_movable_pieces} "
                                 f"{command.piece_name}s could be moved to {final_position}")
        else:
            initial_position = self._alphanum_to_indices(command.get_src())

        self.log.debug(f"initial_position: {initial_position}")
        return initial_position

    def get_final_position(self, command):
        # description : Get the final or "destination" position of the piece to be moved
        # parameters  : array of strings, string, 8x8 matrix of ChessPieces
        # return      : the final position's indices (0-7) in the form (column, row)
        # example     : The command is ["king", "d", "7"], the user is White,
        #               and the white king is currently at D8.
        #               => the function returns (6, 4)
        self.log.info("Getting final position")
        final_position = self._alphanum_to_indices(command.get_dest())
        return final_position

    """ PRIVATE FUNCTIONS """
    def _alphanum_to_indices(self, coords):
        # description : Convert alphanumeric coordinates to index coordinates
        # parameters  : a tuple composed of...
        #                   a single character lowercase string (a-h),
        #                   a single digit number (1-8)
        # return      : the index coordinates (0-7) in the form (column, row)
        # example     : _alphanum_to_indices("h", 7) returns (0, 6)
        alpha = coords[0]
        num = int(coords[1])
        if self.user_color == 'black':
            col = 7 - (ord(alpha) - 97)
            row = num - 1
        else:
            col = ord(alpha) - 97
            row = (num - 8) * -1

        self.log.debug(f"Coordinate conversion: {alpha}{num} -> ({col}, {row})")
        return col, row
