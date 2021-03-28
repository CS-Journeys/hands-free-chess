import sys
import os
import logging

from PyQt5.QtCore import Qt, QTimer
from functools import partial
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

LOGO_FILE = 'res/ui/logo.png'

class ChessUI(QWidget):
    """
    ChessUI is the class that defines and handles the user interface.
    Inherits from QWidget.
    """

    ''' CONSTRUCTOR '''
    def __init__(self):
        super().__init__()  # Invoke base class constructor
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

        self.thread = None  # The thread that will run once 'start' is pressed

        self.paused = False
        self.init_ui()  # Instantiate UI

    ''' PUBLIC '''
    def customEvent(self, event):
        if event.type() == 100:
            self.print_to_user(event.data())

    def init_ui(self):
        """
        This function instantiates all UI widgets.
        """
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
        self.setWindowIcon(QIcon(LOGO_FILE))  # Set window icon
        self.setLayout(self.layout)  # Set layout to layout object

        self.show()  # Display initialized UI

    def button_clicked(self):
        """
        This function handles button clicks.
        """
        sender = self.sender()  # Get current button
        if sender.text() == 'Start':  # Handle start button
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

        elif sender.text() == 'Pause':  # Handle pause button
            self.log.debug("Pause button pressed")
            self.paused = True
            self.thread.paused = True
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.print_to_user("Application Paused")

        elif sender.text() == 'Exit':  # Handle exit button
            self.log.debug("Exit button pressed")
            if self.thread.running:
                self.thread.stop()
            self.quit_app()

    def quit_app(self):
        """
        Cleanly shut down the program.
        """
        self.log.info("Quitting app")
        self.print_to_user("Bye...")
        self.close()  # Close the UI
        sys.exit(0)

    def pause(self):
        """
        This function pauses the program's execution.
        """
        self.print_to_user("Application Paused")
        self.paused = True
        self.thread.paused = True
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)

    # print_to_user
    # Return: Displayed message to user
    def print_to_user(self, msg):
        """
        This function prints messages to the scrollable text frame

        Parameters:
            - msg: the message to be printed to the user
        Output:
            - return: none
            - ui: the message should be displayed to the user
        """
        self.log.debug(f"Print: {msg}")
        temp = QLabel(msg)  # Message label UI element
        temp.setFixedHeight(20)
        self.scrollWidget.layout().addWidget(temp)  # Add element to window frame
        self.scrollWidget.update()  # Update scroll window frame
        QTimer.singleShot(0, partial(self.scroll.ensureWidgetVisible, temp))
        self.show()

    def open_help(self):
        """
        This function uses the operating system's default PDF viewer to open the user manual.
        """
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
