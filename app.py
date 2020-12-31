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

import sys
from PyQt5.QtWidgets import *
from src.user_interface import ChessUI
from src.controller import ControllerThread
import os
import yaml
import logging
import logging.config

LOG_CONF_FILE = 'log_config.yaml'


'''LOGGING'''
def configure_logging():
    # Load logging configuration from file
    if not os.path.exists('log'):
        os.makedirs('log')
    with open(LOG_CONF_FILE, 'r') as conf_file:
        log_cfg = yaml.safe_load(conf_file.read())
    try:
        logging.config.dictConfig(log_cfg)
    except ValueError as e:
        print("Unable to load log configuration\n==> " + str(e))
        exit(1)


'''SLOT FUNCTIONS'''
def print_to_user(msg):
    interface.print_to_user(msg)

def logger(msg):
    interface.log.info(msg)


if __name__ == "__main__":
    configure_logging()
    app = QApplication([])

    interface = ChessUI()

    controller_thread = ControllerThread(interface.scroll)
    controller_thread.send_msg.connect(print_to_user)
    controller_thread.ui_log.connect(logger)

    interface.thread = controller_thread

    sys.exit(app.exec_())
