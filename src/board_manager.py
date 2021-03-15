import logging

class BoardManager:
    """
    The BoardManager class handles gameplay-related data for the purpose of determining:
        (a) if a move is legal
        (b) if a move is ambiguous (see the definition of "ambiguous" in the comments for 'is_ambiguous_move()')
        (c) the initial coordinates of the piece (before the move is made)
        (d) the final coordinates of the piece (after the move is made)
    More abstractly, the BoardManager is the link between between MoveCommands and the MouseController
    """

    UNDETERMINED_COORDINATES = (-1, -1) # static constant for indicating that no possible coordinate has been found
    AMBIGUOUS_COORDINATES = (-2, -2) # static constant for indicating that multiple possible coordinates were found

    def __init__(self, board_state, color='unknown'):
        """
        Parameters:
            - board_state: a 8x8 numpy array where each element is a ChessPiece object that contains name and color
            - color: a string, either "black", "white", or "unknown"
        """
        self.log = logging.getLogger(__name__)
        self.user_color = color
        self.board_state = board_state

    ''' PUBLIC FUNCTIONS '''
    def is_legal_move(self, command):
        """
        This function determines if a command is legal given the user's color and the current state of the board.

        Parameters:
            - command: a MoveCommand object that represents the move the user wants to make
        Output:
            - return: if the move is legal, return True; else, return False
        """
        self.log.debug(f"Started checking legality of {command.text()}")
        is_legal = False

        # We must know the initial and final coordinates to determine if a move is legal
        initial_coordinates = self.get_initial_coordinates(command)
        final_coordinates = self.get_final_coordinates(command)

        if initial_coordinates == self.UNDETERMINED_COORDINATES:
            self.log.warning("Could not set initial coordinates. No possible starting coordinates were found.")
        elif initial_coordinates == self.AMBIGUOUS_COORDINATES:
            self.log.warning("Could not set initial coordinates. More than one possible coordinate was found.")
        else:
            piece = self.board_state[initial_coordinates[1], initial_coordinates[0]]
            self.log.debug(f"Initial coordinates found. Checking to see if the {piece.color} {piece.name} "
                           f"can be moved from {initial_coordinates} to {final_coordinates}")
            if (piece.name == command.piece_name
                    and piece.color == self.user_color
                    and piece.can_be_moved(initial_coordinates, final_coordinates, self.board_state)):
                is_legal = True

        self.log.debug(f"Legal move: {is_legal}")
        return is_legal

    def is_ambiguous_move(self, command):
        """
        This function determines if a command is ambiguous given the user's color and the current state of the board.
        A command is ambiguous if the user doesn't specify the initial position of the piece they want to move AND
        if more than one piece could legally be moved to their desired final position.

        For example, suppose the command is "Knight to D6," the user is Black, there is one black Knight at F7 and
        another at B7. In this situation, it isn't clear which black knight the user wants to move, because either
        knight could legally be moved to D6. In other words, the move is ambiguous.

        Parameters:
            - command: a MoveCommand object that represents the move the user wants to make
        Output:
            - return: if the initial coordinates are ambiguous, return True; else, return False
        """
        is_ambiguous = False
        initial_coordinates = self.get_initial_coordinates(command)
        if initial_coordinates == self.AMBIGUOUS_COORDINATES:
            is_ambiguous = True
            self.log.warning(f"{command.text()} is ambiguous")
        else:
            self.log.debug(f"{command.text()} is unambiguous. Initial coordinates: {initial_coordinates}")
        return is_ambiguous

    def get_initial_coordinates(self, command):
        """
        This function determines the initial coordinates of the piece the user wants to move. If the user specified
        the piece's position in "File-Rank"* format, simply convert from "File-Rank" format to the 0-7 index
        format (ex: ("h", "3") becomes (7, 5) if White is on the bottom). If the user did NOT specify the piece's
        position, determine if one and only one piece of the specified type can be legally moved to the destination.
        If so, determine the coordinates of said piece.

        *In chess, columns are called "files," and rows are called "ranks."

        Parameters:
            - command: a MoveCommand object that represents the move the user wants to make
        Output:
            - return: a tuple of two 0-7 integers that represent the initial coordinates of the piece to be moved
        """
        initial_coordinates = self.UNDETERMINED_COORDINATES

        if command.get_src() is None:
            num_movable_pieces = 0
            final_coordinates = self.get_final_coordinates(command)

            # Check every row and column to see if the piece at that position can be moved
            for row in range(0, 8):
                for col in range(0, 8):
                    board_piece = self.board_state[row, col]
                    if (board_piece.can_be_moved((col, row), final_coordinates, self.board_state)
                            and board_piece.name == command.piece_name
                            and board_piece.color == self.user_color):
                        initial_coordinates = (col, row)
                        num_movable_pieces += 1
                        self.log.debug(f"{command.piece_name} "
                                       f"@ {initial_coordinates} can be moved")

            if num_movable_pieces > 1:
                initial_coordinates = self.AMBIGUOUS_COORDINATES
                self.log.warning(f"Ambiguous starting coordinates: {num_movable_pieces} "
                                 f"{command.piece_name}s could be moved to {final_coordinates}")
        else:
            initial_coordinates = self._file_rank_to_indices(command.get_src())

        self.log.debug(f"initial_coordinates: {initial_coordinates}")
        return initial_coordinates

    def get_final_coordinates(self, command):
        """
        This function determines the final or "destination" coordinates of the piece to be moved.

        Parameters:
            - command: a MoveCommand object that represents the move the user wants to make
        Output:
            - return: a tuple of two 0-7 integers that represent the final coordinates of the piece to be moved
        """
        final_coordinates = self._file_rank_to_indices(command.get_dest())
        return final_coordinates

    def set_board_state(self, board_state):
        """
        This function sets 'board_state'.
        """
        self.board_state = board_state
        self.log.debug("Board state updated.")

    def set_user_color(self, user_color):
        """
        This function sets 'user_color'.
        """
        self.user_color = user_color
        self.log.debug(f"New user piece color: {user_color}")

    ''' PRIVATE FUNCTIONS '''
    def _file_rank_to_indices(self, coords):
        """
        This function converts from "File-Rank"* format to 0-7 index format. "File-Rank" coordinates are independent of
        the orientation of the board, but our 0-7 index format (useful for image recognition and controlling the mouse)
        switches depending on how the board is oriented.
        For example, if White is on the bottom (ie. the user is White), then ("h", "3") returns (7, 5).

        *In chess, columns are call "files," and rows are called "ranks."

        Parameters:
            - coords: a tuple of two characters that represent coordinates in "File-Rank" format.
                      the first element is a lowercase character (a-h), and
                      the second element is a string representation of a number (1-8)
        Output:
            - return: a tuple of two 0-7 integers that represent the coordinates in "0-7 index" format
        """
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
