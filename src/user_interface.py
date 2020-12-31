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
import os
from PyQt5.QtWidgets import *
import logging

class ChessUI(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.log = logging.getLogger(__name__)
        self.scroll = QScrollArea()
        self.scrollWidget = QWidget()

        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause (coming soon)")
        self.stop_button = QPushButton("Stop")
        self.help = QPushButton("Help")

        self.thread = None

        self.paused = False
        self.init_ui()

    def customEvent(self, event):
        if event.type() == 100:
            self.print_to_user(event.data())

    def init_ui(self):
        self.log.info("Initializing UI")
        self.start_button.clicked.connect(self.button_clicked)
        self.pause_button.setEnabled(False)
        # self.pause_button.clicked.connect(self.button_clicked)
        self.stop_button.clicked.connect(self.button_clicked)
        self.help.clicked.connect(self.open_help)

        self.scrollWidget.setLayout(QVBoxLayout())
        self.scroll.setWidget(self.scrollWidget)

        temp = QLabel('Click \"Start\" to begin.')
        temp.setFixedHeight(20)
        self.scrollWidget.layout().addWidget(temp)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(400)
        self.scroll.setFixedWidth(400)

        self.layout.addWidget(self.scroll)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.pause_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.help)

        self.setWindowTitle("Hands Free Chess")
        self.setLayout(self.layout)
        self.show()

    def button_clicked(self):
        sender = self.sender()
        if sender.text() == 'Start':
            self.log.info("Start button pressed")
            if self.paused:
                self.print_to_user("Restarting application...")
                self.print_to_user("Please wait...")
                self.log.info("Restarting app")
            else:
                self.print_to_user("Starting application...")
                self.log.info("First app startup")
                self.log.info("Starting thread")
                self.thread.start()
            self.paused = False
            self.start_button.setEnabled(False)
            # self.pause_button.setEnabled(True)


        # elif sender.text() == 'Pause':
        #     self.log.info("Pause button pressed")
        #     self.start_button.setEnabled(not self.paused)
        #     self.pause_button.setEnabled(self.paused)
        #     self.paused = True
        #     self.thread.stop()
        #     self.print_to_user("Application Paused")

        elif sender.text() == 'Stop':
            self.log.info("Stop button pressed")
            self.thread.stop()
            self.quit_app()

    def quit_app(self):
        self.log.info("Quitting app")
        self.start_button.setEnabled(False)
        # self.pause_button.setEnabled(False)
        self.print_to_user("Bye...")
        self.close()
        exit(0)

    def print_to_user(self, msg):
        self.log.debug(f"Print: {msg}")
        temp = QLabel(msg)
        temp.setFixedHeight(20)
        self.scrollWidget.layout().addWidget(temp)
        self.scrollWidget.update()

    def open_help(self):
        try:
            if sys.platform == 'linux2' or sys.platform == 'win32':
                os.system("start res/user-manual/user-manual.pdf")
            else:
                os.system("open res/user-manual/user-manual.pdf")
            self.log.info("Opened help document")
        except Exception as e:
            self.log.error(f"Unable to open help document: {str(e)} ", exc_info=True)
