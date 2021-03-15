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

import sys
from PyQt5.QtWidgets import *
from src.log_manager import LogManager
from src.user_interface import ChessUI
from src.game_controller import ControllerThread


'''SLOT FUNCTIONS'''
def print_to_user(msg):
    interface.print_to_user(msg)

def logger(msg):
    interface.log.info(msg)


'''APP ENTRY POINT'''
if __name__ == "__main__":
    log_manager = LogManager()
    app = QApplication([])

    # Initialize the user interface
    interface = ChessUI()

    # Initialize the controller thread
    controller_thread = ControllerThread(interface.scroll)
    controller_thread.send_msg.connect(print_to_user)
    controller_thread.ui_log.connect(logger)

    # Attach the controller thread to the user interface
    interface.thread = controller_thread

    sys.exit(app.exec_())
