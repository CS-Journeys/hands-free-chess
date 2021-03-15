import sys
import os
import logging

from PyQt5.QtCore import Qt, QTimer
from functools import partial
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon


# ChessUI
# Description: UI class for the hands free application
# Extends the QWidget module
# Parameters: None
class ChessUI(QWidget):
    def __init__(self):
        super().__init__()  # Avoids reference to base class explicitly
        self.layout = QVBoxLayout()  # Vertically aligned window object
        self.log = logging.getLogger(__name__)  # Application log object
        self.scroll = QScrollArea()  # Scroll bar object
        self.scrollWidget = QWidget()  # Scroll widget object
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.scrollWidget.setWindowFlags(Qt.WindowStaysOnTopHint)

        # Make scroll bar lock to bottom
        self.scroll_bar = self.scroll.verticalScrollBar()
        self.scroll_bar.rangeChanged.connect(lambda: self.scroll_bar.setValue(self.scroll_bar.maximum()))

        # UI Buttons
        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.exit_button = QPushButton("Exit")
        self.help = QPushButton("Help")

        self.thread = None # The thread that will run once 'start' is pressed

        self.paused = False
        self.init_ui()  # Instantiate UI

    def customEvent(self, event):
        if event.type() == 100:
            self.print_to_user(event.data())

    # init_ui
    # Description: Instantiates all UI widgets
    # Parameters: None
    # Return: Void
    def init_ui(self):
        self.log.debug("Initializing UI")
        self.start_button.clicked.connect(self.button_clicked)  # Call click function when start is clicked
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(self.button_clicked)
        self.exit_button.clicked.connect(self.button_clicked)
        self.help.clicked.connect(self.open_help)

        self.scrollWidget.setLayout(QVBoxLayout())  # Set scroll alignment to vertical
        self.scroll.setWidget(self.scrollWidget)  # Set scroll widget to the scroll widget object

        temp = QLabel('Click \"Start\" to begin.')  # Click start label
        temp.setFixedHeight(20)  # Set height of label
        self.scrollWidget.layout().addWidget(temp)  # Add click start message to scroll window frame
        self.scrollWidget.layout().setAlignment(Qt.AlignTop)  # Align scroll window frame
        self.scroll.setWidgetResizable(True)  # Allow resizable scroll frame
        self.scroll.setFixedHeight(400)  # Set default scroll frame height
        self.scroll.setFixedWidth(400)  # Set default scroll frame width

        # Add widgets to layout object
        self.layout.addWidget(self.scroll)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.pause_button)
        self.layout.addWidget(self.exit_button)
        self.layout.addWidget(self.help)

        self.setWindowTitle("Hands Free Chess")  # Set window title
        self.setWindowIcon(QIcon('res/logo.png'))  # Set window icon
        self.setLayout(self.layout)  # Set layout to layout object

        self.show()  # Display initialized UI

    # button_clicked
    # Description: Button click function
    # Parameters: Valid button call
    # Return: None
    def button_clicked(self):
        sender = self.sender()  # Get current button
        if sender.text() == 'Start':  # Start button execution
            self.log.debug("Start button pressed")
            if self.paused:
                self.print_to_user("Application Resumed. What's your next move?")
                self.log.debug("Resuming app")
                self.thread.paused = False
            else:
                self.log.debug("First app startup")
                self.log.debug("Starting thread")
                self.thread.start()
                self.thread.finished.connect(self.quit_app)
                self.thread.pause.connect(self.pause)
                self.thread.help.connect(self.open_help)
                self.thread.paused = False
            self.paused = False
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)

        elif sender.text() == 'Pause':
            self.log.debug("Pause button pressed")
            self.paused = True
            self.thread.paused = True
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.print_to_user("Application Paused")

        # Exit button execution
        elif sender.text() == 'Exit':
            self.log.debug("Exit button pressed")
            if self.thread.running:
                self.thread.stop()
            self.quit_app()

    # quit_app
    # Description: Application quit function
    # Parameters: None
    # Return: Application termination
    def quit_app(self):
        self.log.info("Quitting app")
        self.print_to_user("Bye...")
        self.close()  # Close the UI
        sys.exit(0)

    def pause(self):
        self.print_to_user("Application Paused")
        self.paused = True
        self.thread.paused = True
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)

    # print_to_user
    # Description: Print log messages to scroll frame
    # Parameters: valid string message to user (msg)
    # Return: Displayed message to user
    def print_to_user(self, msg):
        self.log.debug(f"Print: {msg}")
        temp = QLabel(msg)  # Message label UI element
        temp.setFixedHeight(20)
        self.scrollWidget.layout().addWidget(temp)  # Add element to window frame
        self.scrollWidget.update()  # Update scroll window frame
        QTimer.singleShot(0, partial(self.scroll.ensureWidgetVisible, temp))
        self.show()

    # open_help
    # Description: Help button functionality
    # Parameters: None
    # Return: Help PDF opened locally
    def open_help(self):
        try:
            if sys.platform == 'win32':
                os.system("start res/user-manual/user-manual.pdf")
            elif sys.platform == 'linux' or sys.platform == 'linux2':
                os.system("xdg-open res/user-manual/user-manual.pdf")
            else:
                os.system("open res/user-manual/user-manual.pdf")
            self.log.info("Opened help document")
        except Exception as e:
            self.log.error(f"Unable to open help document: {str(e)} ", exc_info=True)
