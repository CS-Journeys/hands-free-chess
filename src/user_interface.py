#!/usr/bin/python
# -*- coding: utf-8 -*-
# TODO: amazing UI initialization stuff
# TODO: add start/stop buttons
# import PySimpleGUI as sg
import sys
from PyQt5.QtWidgets import *
import time

import main


class ChessUI(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel(messages)
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.initUI()

    def initUI(self):
        self.start_button.clicked.connect(self.buttonClicked)
        self.stop_button.clicked.connect(self.buttonClicked)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)

        self.setWindowTitle("Hands Free Chess")
        self.setLayout(self.layout)
        self.show()

    def new_data_status(self):
        self.label.setText(messages)

    def buttonClicked(self, e):
        sender = self.sender()
        if sender.text() == 'Start':
            print("START")
            print_to_user("Starting application...")
            main.main
        elif sender.text() == 'Stop':
            print_to_user("Stopping application...")
            self.close()


global messages

if __name__ == "__main__":
    app = QApplication([])

    messages = ""
    ui = ChessUI()

    def print_to_user(message):
        global messages
        messages += (message + '\n')

        print(message)
        ui.new_data_status()

    print_to_user('Click \"Start\" to begin.')
    sys.exit(app.exec_())
