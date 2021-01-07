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

import numpy as np
import time
import logging
from PyQt5.QtCore import QThread, pyqtSignal

from src import command_recognition as cmd_recog
from src.board_recognition import BoardRecognizer
from src.board_manager import BoardManager
from src import mouse_controller
from src import chess_piece

BOARD_CHECK_PAUSE_TIME = 1.5  # time (in seconds) to wait before rechecking for board


class ControllerThread(QThread):
    send_msg = pyqtSignal(str)
    ui_log = pyqtSignal(str)

    """ CONSTRUCTOR """
    def __init__(self, recipient):
        QThread.__init__(self)
        self.controller_log = logging.getLogger(__name__)
        self.controller_log.info("Setting up controller")

        self.running = True
        self.name = 'worker'
        self.receiver = recipient

        self.color = None
        self.board_coords = None
        self.b_recog = BoardRecognizer()
        self.b_manager = BoardManager(np.full((8, 8), chess_piece.ChessPiece('unknown', 'unknown')))

    """ PUBLIC FUNCTIONS """
    def run(self):
        # description:
        #   This function is the heart of Hands-Free Chess.
        #   It also catches all errors that come from the "controller" thread.
        # return:
        #   None
        # post-condition:
        #   self.running is False
        try:
            # Adjust microphone for ambient noise
            self._adjust_for_ambient_noise()

            # Set the piece color if it isn't already set
            if self.color is None:
                self._set_piece_color()

            # Repeatedly ask for commands and handle them
            while self.running:
                user_command = self._ask_for_voice_command("Listening. What's your move?")
                self._handle_voice_command(user_command)

        except Exception as e:
            self.ui_log.emit(f"Error in thread: {str(e)}")
            self.stop()

    def stop(self):
        # description: Stop the thread from running
        # return: None
        # post-condition: self.running is False
        self.ui_log.emit("Exiting thread...")
        self.running = False

    """ PRIVATE FUNCTIONS """
    def _ask_for_voice_command(self, msg):
        # description: This function asks for a voice command from the user and gets their command.
        # return: list of strings
        # parameters: 'msg' is a string
        # pre-condition: cmd_recog.get_voice_command() only returns empty lists or formatted valid commands
        # post-condition: a prompt is printed to the UI for the user, and an empty list
        #                 or a formatted valid command is returned
        # example:
        #   1. The message "Listening. What is your command?" is printed to the UI.
        #   2. The user says, "King to E4".
        #   3. ["king", "e", "4"] is returned.
        self.send_msg.emit(msg)
        self.controller_log.info("Listening for command")
        user_command = cmd_recog.get_voice_command()
        self.controller_log.info(f"Command: {user_command}")
        return user_command

    def _adjust_for_ambient_noise(self):
        # description: Adjust the microphone for ambient noise and notify the user about what's going on.
        # return: None
        # post-condition: A "please wait" message is printed to the UI,
        #                 and then the microphone is adjusted for ambient noise.
        self.controller_log.info("Adjusting microphone for ambient noise")
        self.send_msg.emit("Please wait...")
        cmd_recog.adjust_for_ambient_noise(2.0)

    def _set_piece_color(self):
        # description: This function gets the piece color from the user
        # return: None
        # pre-condition: cmd_recog.get_voice_command() can return single-word commands (['white'], ['exit'], etc.)
        # post-condition:
        #   The user is asked via the UI to declare their piece color, then
        #   EITHER self.color is "black" or "white", and the user is notified of their choice via the UI,
        #   OR self.stop() is called (ie. self.running = False)
        self.controller_log.debug("Listening for piece color")
        user_command = self._ask_for_voice_command("Listening. What's your piece color?")
        while user_command != ['white'] and user_command != ['black'] and user_command != ['exit']:
            self.controller_log.debug("Trying to listen again for piece color")
            user_command = self._ask_for_voice_command('Try again. Say "white" or "black".')

        if user_command == ['exit']:
            self.stop()
        else:
            self.color = user_command[0]
            self.b_manager.set_user_color(self.color)
            self.controller_log.debug(f"Piece color: {self.color}")
            self.send_msg.emit(f"Your color: {self.color}")

    def _handle_voice_command(self, user_command):
        # description: Print and act appropriately in response to the user's command
        # return: None
        # pre-condition: cmd_recog.get_voice_command() only returns empty lists or formatted valid commands
        # post-condition:
        #   1. An appropriate response to the user's command is printed to the UI
        #   2. If the user said "exit", self.running is False
        #      If the user said a move, then
        #        a. The board_coords and the board_manager's chessboard data are updated
        #        b. If the move is legal and unambiguous, the move is made
        # TODO: add support for other commands like so: "elif user_command == ['change color']: ...."
        if not user_command:
            self.send_msg.emit("No speech detected")
        elif user_command == ['exit']:
            self.send_msg.emit("Stopping Hands-Free Chess as requested by the user.")
            self.stop()
        else:
            self.send_msg.emit(f"Your move: {user_command}")
            self._update_chessboard()
            self._handle_move(user_command)

    def _update_chessboard(self):
        # description: Update the coordinates of all of the chessboard's vertical and horizontal grid lines, and
        #              update the board_manager to contain the current state of the board (ie. which pieces are where)
        # return: None
        # pre-condition: The user doesn't want to do anything while HFC runs its image recognition
        # post-condition: self.board_coords and the board_manager's chessboard data are updated

        # Repeatedly search for chessboard until it is detected
        self.controller_log.info("Searching for board")
        self.board_coords = self.b_recog.get_board_coords()
        while self.board_coords is None:
            time.sleep(BOARD_CHECK_PAUSE_TIME)
            self.controller_log.info("Searching for board again")
            self.send_msg.emit("Board not detected. Searching again.")
            self.board_coords = self.b_recog.get_board_coords()

        # Identify each piece on board
        self.controller_log.info("Identifying pieces")
        chessboard = np.full((8, 8), chess_piece.ChessPiece('unknown', 'unknown'))
        for row in range(1, 8 + 1):
            for col in range(1, 8 + 1):
                chessboard[row - 1][col - 1] = self.b_recog.identify_piece(col, row)

        # Update the board manager's chessboard data
        self.b_manager.update_board(chessboard)

        # Log board data
        formatted_board_data = _format_board_matrix(chessboard)
        self.controller_log.info(f"Formatted board data:\n{formatted_board_data}")

    def _handle_move(self, move_command):
        # description:
        #   Make the user's move (on condition that the move is legal and unambiguous).
        # return:
        #   None
        # parameters:
        #   move_command: list of strings
        # pre-condition:
        #   'move_command' represents a formatted valid command
        #   self.board_coords represent the CURRENT location of the boards' grid coordinates
        #   the board manager's chessboard data is CURRENT
        # post-condition:
        #   If the move is ambiguous or illegal, an appropriate message is printed to the UI
        #   If the move is unambiguous and legal, the piece is moved with the mouse

        # Get ambiguity and legality of move
        self.controller_log.info("Checking ambiguity")
        is_ambiguous = self.b_manager.is_ambiguous_move(move_command)
        is_legal = False
        if not is_ambiguous:
            self.controller_log.info("Checking legality")
            is_legal = self.b_manager.is_legal_move(move_command)

        # Notify user if move is ambiguous
        if is_ambiguous:
            self.send_msg.emit("Ambiguous move. Please repeat and specify which "
                               + str(self.b_manager.extract_piece_name(move_command))
                               + " you want to move.")
        # Notify user if move is illegal
        elif not is_legal:
            self.controller_log.warning(f"{move_command} is illegal")
            self.send_msg.emit("Illegal move! Try again.")
        # If move is unambiguous and legal, move piece with mouse
        else:
            self.controller_log.info(f"OK! Moving {self.b_manager.extract_piece_name(move_command)}"
                                     f" to {move_command[-2]}{move_command[-1]}")
            initial_position = self.b_manager.get_initial_position(move_command)
            final_position = self.b_manager.get_final_position(move_command)
            mouse_controller.move_piece(initial_position, final_position, self.board_coords)


# Useful helper function for aesthetic debugging <3, delete later
def _format_board_matrix(board_matrix):
    formatted_matrix = board_matrix.copy()
    for i in range(0, formatted_matrix.shape[0]):
        for j in range(0, formatted_matrix.shape[1]):
            if formatted_matrix[i, j].name == "king":
                formatted_matrix[i, j] = "K"
            elif formatted_matrix[i, j].name == "empty":
                formatted_matrix[i, j] = " "
            else:
                formatted_matrix[i, j] = formatted_matrix[i, j].name[0]
    return formatted_matrix
