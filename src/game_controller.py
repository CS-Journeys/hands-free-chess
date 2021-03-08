"""
Hands-Free Chess allows the user to play chess online using only their voice instead of a keyboard and mouse.
Copyright (C) 2020-2021  CS Journeys

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
import threading
import time

import numpy as np
import logging
from PyQt5.QtCore import QThread, pyqtSignal
import queue

from src.speech_to_text import SpeechRecognizer
from src.text_to_command import TextToCmdBuffer
from src.board_recognition import BoardRecognizer
from src.board_manager import BoardManager
from src.command import Command, MoveCommand
from src import mouse_controller
from src import chess_piece

BOARD_CHECK_PAUSE_TIME = 1.5 # time (in seconds) to wait before rechecking for board

class ControllerThread(QThread):
    send_msg = pyqtSignal(str)
    ui_log = pyqtSignal(str)
    finished = pyqtSignal()
    pause = pyqtSignal()
    help = pyqtSignal()

    """ CONSTRUCTOR """
    def __init__(self, recipient):
        QThread.__init__(self)
        self.controller_log = logging.getLogger(__name__)
        self.controller_log.info("Setting up controller")

        self.running = False
        self.paused = False
        self.name = 'worker'
        self.receiver = recipient

        self.raw_text_queue = queue.Queue(maxsize=10)
        self.cmd_recog = SpeechRecognizer(self.raw_text_queue)
        self.txt_to_cmd_buffer = TextToCmdBuffer()

        self.board_coords = None
        self.board_state = None
        self.board_queue = queue.Queue(maxsize=1)
        self.b_recog = BoardRecognizer()
        self.stop_event = threading.Event()
        self.b_recog_thread = threading.Thread(target=self.b_recog.endlessly_recognize_board,
                                               args=(self.board_queue,0.2,self.stop_event))

        self.color = None
        self.b_manager = BoardManager(np.full((8, 8), chess_piece.ChessPiece('unknown', 'unknown')))

    """ PUBLIC """
    def run(self):
        self.running = True
        try:
            # Start the board recognizer thread
            self.stop_event.clear()
            self.b_recog_thread.start()

            # Start the background listener
            self.cmd_recog.listen_in_background()

            # Ask for user color
            self.send_msg.emit("What's your piece color?")

            # Handle commands as they arrive in the command queue
            while self.running or not self.raw_text_queue.empty():
                if self.paused:
                    self.stop_event.set()
                    self.cmd_recog.stop_listening(wait_for_stop=False)
                    while self.paused:
                        time.sleep(0.1)
                    self.resume()

                self._handle_command(self.raw_text_queue.get())

        except Exception as e:
            self.ui_log.emit(f"Error in thread: {str(e)}")
            self.stop()

        self.finished.emit()

    def resume(self):
        self.controller_log.info("Resuming thread...")
        self.stop_event.clear()
        self.b_recog_thread = threading.Thread(target=self.b_recog.endlessly_recognize_board,
                                               args=(self.board_queue,0.2,self.stop_event))
        self.b_recog_thread.start()
        self.cmd_recog.listen_in_background()

    def stop(self):
        # TODO: fix no-exit bug
        self.ui_log.emit("Exiting thread...")
        self.cmd_recog.stop_listening(wait_for_stop=False)
        self.stop_event.set()
        self.running = False

    """ PRIVATE """
    def _handle_command(self, raw_text):
        if not self.paused:
            if self.color is None:
                self._set_piece_color(raw_text)
            elif raw_text == SpeechRecognizer.NOT_RECOGNIZED:
                self.send_msg.emit("No speech detected")
            else:
                buffer_state = self.txt_to_cmd_buffer.add_text(raw_text)
                command = self.txt_to_cmd_buffer.get_command()
                if isinstance(command, MoveCommand):
                    self.send_msg.emit(f"Your move: {command.text()}")
                    self._update_chessboard()
                    if self.board_state is not None:
                        self._handle_move(command)
                elif isinstance(command, Command):
                    self.send_msg.emit(f"Your command: {command.text()}")
                    if command.text() == 'exit':
                        self.send_msg.emit("Stopping Hands-Free Chess as requested by the user.")
                        self.stop()
                    elif command.text() == 'pause':
                        self.pause.emit()
                    elif command.text() == 'help':
                        self.help.emit()
                else:
                    self.send_msg.emit(f"Your command: {' '.join(buffer_state)}...")

    def _update_chessboard(self):
        if self.board_queue.empty():
            self.controller_log.warning("Chessboard data queue is empty")
            self.send_msg.emit("Warning: Chessboard not detected. Please try again.")
            self.board_coords = None
            self.board_state = None
        else:
            self.board_coords, self.board_state = self.board_queue.get()
            self.b_manager.update_board(self.board_state)

            # Log board state
            formatted_board_state = _format_board_matrix(self.board_state)
            self.controller_log.info(f"Formatted board state:\n{formatted_board_state}")

    def _handle_move(self, move_command):
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
                               + move_command.piece_name
                               + " you want to move.")
        # Notify user if move is illegal
        elif not is_legal:
            self.controller_log.warning(f"{move_command.text()} is illegal")
            self.send_msg.emit("Illegal move! Try again.")
        # If move is unambiguous and legal, move piece with mouse
        else:
            self.controller_log.info(f"OK! Moving {move_command.text()}")
            initial_position = self.b_manager.get_initial_position(move_command)
            final_position = self.b_manager.get_final_position(move_command)
            mouse_controller.move_piece(initial_position, final_position, self.board_coords)

    def _set_piece_color(self, raw_text):
        lower = raw_text.lower()
        if lower == 'black' or lower == 'white':
            self.color = lower
            self.send_msg.emit(f"Your color: {self.color}")
            self.controller_log.debug(f"Piece color: {self.color}")
            self.b_manager.user_color = self.color
            self.send_msg.emit("What's your move?")
        elif lower == SpeechRecognizer.NOT_RECOGNIZED:
            self.send_msg.emit("No speech detected. Please try again. Say \"white\" or \"black.\"")
        elif lower == 'exit':
            self.send_msg.emit("Stopping Hands-Free Chess as requested by the user.")
            self.stop()
        else:
            self.send_msg.emit(f"You said: {lower}. Please try again. Say \"white\" or \"black.\"")


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
