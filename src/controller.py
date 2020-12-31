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

    '''CONSTRUCTOR'''
    def __init__(self, recipient):
        QThread.__init__(self)
        self.controller_log = logging.getLogger(__name__)
        self.controller_log.info("Setting up controller")

        self.running = True
        self.name = 'worker'
        self.receiver = recipient

        self.color = None
        self.board_data = np.full((8, 8), chess_piece.ChessPiece('unknown', 'unknown'))
        self.b_recog = BoardRecognizer()
        self.b_manager = BoardManager(self.board_data)

    '''PUBLIC FUNCTIONS'''
    def run(self):
        try:
            # Adjust microphone for ambient noise
            self._adjust_for_ambient_noise()

            # Set the user's piece color
            if self.color is None:
                self._ask_for_color()

            # Obey the mighty user's commands
            while self.running:
                res = self._handle_user_command()
                while res != ['exit']:
                    res = self._handle_user_command()
                self.ui_log.emit("Exiting thread...")
                self.stop()

        # Catch errors
        except Exception as e:
            self.ui_log.emit(f"Error in thread: {str(e)}")
            self.stop()

    def stop(self):
        self.running = False

    '''PRIVATE FUNCTIONS'''
    def _adjust_for_ambient_noise(self):
        self.controller_log.info("Adjusting microphone for ambient noise")
        self.send_msg.emit("Please wait...")
        cmd_recog.adjust_for_ambient_noise(2.0)

    def _ask_for_color(self):
        # Listen for color until a valid piece color is provided - black or white
        self.controller_log.info("Listening for piece color")
        self.send_msg.emit("Listening. What's your piece color?")
        user_command = cmd_recog.get_voice_command()
        while user_command != ['white'] and user_command != ['black']:
            self.send_msg.emit('Try again. Say "white" or "black".')
            user_command = cmd_recog.get_voice_command()

        # Set the user's piece color
        self.color = user_command[0]
        self.b_manager.set_user_color(self.color)
        self.controller_log.info(f"Piece color: {self.color}")
        self.send_msg.emit(f"Your color: {self.color}")

    def _handle_user_command(self):
        self.board_data = np.full((8, 8), chess_piece.ChessPiece('unknown', 'unknown'))

        self.controller_log.info("Listening for command")
        self.send_msg.emit("Listening. What's your move?")
        user_command = cmd_recog.get_voice_command()
        self.controller_log.info(f"Command: {user_command}")

        # Proceed if command contains at least 3 parts (minimum num for a valid move cmd)
        if len(user_command) >= 3:
            self.send_msg.emit(f"Your Command: {user_command}")
            self.controller_log.info("Searching for board")
            board_coords = self.b_recog.get_board_coords()

            # If board not detected, loop until board is detected
            while board_coords is None:
                self.controller_log.info("Searching for board again")
                self.send_msg.emit("Board not detected. Searching again.")
                time.sleep(BOARD_CHECK_PAUSE_TIME)
                board_coords = self.b_recog.get_board_coords()

            # Identify each piece on board
            self.controller_log.info("Identifying pieces")
            for row in range(1, 8 + 1):
                for col in range(1, 8 + 1):
                    self.board_data[row - 1][col - 1] = self.b_recog.identify_piece(col, row)

            # Update the board manager's board data
            self.b_manager.update_board(self.board_data)

            # Log board data
            formatted_board_data = _format_board_matrix(self.board_data)
            self.controller_log.info(f"Formatted board data:\n{formatted_board_data}")

            # Notify user if move is ambiguous
            self.controller_log.info("Checking ambiguity")
            if self.b_manager.is_ambiguous_move(user_command):
                self.send_msg.emit("Ambiguous move. Please repeat and specify which "
                                   + str(self.b_manager.extract_piece_name(user_command))
                                   + " you want to move.")

            # If move is legal and unambiguous, move piece with mouse
            else:
                self.controller_log.info("Checking legality")
                if self.b_manager.is_legal_move(user_command):
                    self.controller_log.info(f"OK! Moving {self.b_manager.extract_piece_name(user_command)}"
                                             f" to {user_command[-2]}{user_command[-1]}")
                    initial_position = self.b_manager.get_initial_position(user_command)
                    final_position = self.b_manager.get_final_position(user_command)
                    mouse_controller.move_piece(initial_position, final_position, board_coords)

                # Notify user if move is illegal
                else:
                    self.controller_log.warning(f"{user_command} is illegal")
                    self.send_msg.emit("Illegal move! Try again.")
        elif user_command == ['exit']:
            self.send_msg.emit("Stopping Hands-Free Chess as requested by the user.")
        else:
            self.send_msg.emit("No speech detected")

        return user_command


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
