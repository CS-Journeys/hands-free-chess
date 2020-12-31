import os
import sys
import logging

from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot, QEvent
from PyQt5.QtWidgets import *
from src import controller


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
        self.initUI()

    def initUI(self):
        self.log.info("Initializing UI")
        self.start_button.clicked.connect(self.buttonClicked)
        self.pause_button.setEnabled(False)
        # self.pause_button.clicked.connect(self.buttonClicked)
        self.stop_button.clicked.connect(self.buttonClicked)
        self.help.clicked.connect(self.openHelp)

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

    def buttonClicked(self):
        sender = self.sender()
        if sender.text() == 'Start':
            self.log.info("Start button pressed")
            if self.paused:
                self.print_to_user("Restarting application...")
                self.print_to_user("Please wait...")
                self.log.info("Restarting app")
            else:
                self.print_to_user("Starting application...")
                controller.setup(self)
                self.log.info("First app startup")
            self.paused = False
            self.start_button.setEnabled(False)
            # self.pause_button.setEnabled(True)
            self.log.info("Starting thread")
            self.thread.start()

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
            self.quitApp()

    def quitApp(self):
        self.log.info("Quitting app")
        self.start_button.setEnabled(False)
        # self.pause_button.setEnabled(False)
        self.print_to_user("Bye...")
        self.close()
        exit(0)

    def print_to_user(self, msg):
        self.log.info(f"Print: {msg}")
        temp = QLabel(msg)
        temp.setFixedHeight(20)
        self.scrollWidget.layout().addWidget(temp)
        self.scrollWidget.update()

    def customEvent(self, event):
        if event.type() == 100:
            self.print_to_user(event.data())

    def openHelp(self):
        try:
            if sys.platform == 'linux2' or sys.platform == 'win32':
                os.system("start res/user-manual/user-manual.pdf")
            else:
                os.system("open res/user-manual/user-manual.pdf")
            self.log.info("Opened help document")
        except Exception as e:
            self.log.error(f"Unable to open help document: {str(e)} ", exc_info=True)


class Worker(QThread):
    send_msg = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, recipient):
        QThread.__init__(self)
        self.running = True
        self.name = 'worker'
        self.receiver = recipient
        self.color = False

    def run(self):
        try:
            if not self.color:
                color = controller.ask_for_color(self)
                self.log.emit("Asking for color")
                self.send_msg.emit("Your color: " + color)
                self.color = True
            while self.running:
                self.send_msg.emit("Listening. What's your move?")
                res = controller.handle_user_command(self)
                while res != ['exit']:
                    self.log.emit("Handling move")
                    self.send_msg.emit("Your Command: " + str(res))
                    res = controller.handle_user_command(self)
                self.log.emit("Exiting thread...")
                self.stop()
        except Exception as e:
            self.log.emit(f"Error in thread: {str(e)}")
            self.stop()

    def stop(self):
        self.running = False


def print_to_user(msg):
    interface.print_to_user(msg)


def logger(msg):
    interface.log.info(msg)


if __name__ == "__main__":
    controller.configure_logging()
    app = QApplication([])
    # my_thread = QThread()
    # my_thread.start()

    interface = ChessUI()

    worker = Worker(interface.scroll)
    worker.send_msg.connect(print_to_user)
    worker.log.connect(logger)

    interface.thread = worker

    sys.exit(app.exec_())
