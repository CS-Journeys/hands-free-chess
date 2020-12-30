import os
import subprocess
import sys
import logging
import threading
import webbrowser

from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import *
from src import controller


class ChessUI(QWidget):
    def __init__(self, my_worker):
        super().__init__()
        self.layout = QVBoxLayout()
        self.log = logging.getLogger(__name__)
        self.scroll = QScrollArea()
        self.scrollWidget = QWidget()

        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.help = QPushButton("Help")

        self.thread = my_worker

        self.paused = False
        self.initUI()

    def initUI(self):
        self.log.info("Initializing UI")
        self.start_button.clicked.connect(self.buttonClicked)
        self.pause_button.clicked.connect(self.buttonClicked)
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
            self.pause_button.setEnabled(True)
            self.thread.running = True
            self.log.info("Starting thread")

        elif sender.text() == 'Pause':
            self.log.info("Pause button pressed")
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.paused = True
            self.thread.stop.emit()
            self.print_to_user("Application Paused")

        elif sender.text() == 'Stop':
            self.log.info("Stop button pressed")
            self.quitApp()

    def quitApp(self):
        self.log.info("Quitting app")
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.thread.running = False
        self.print_to_user("Bye...")
        self.close()
        exit(0)

    def print_to_user(self, msg):
        self.log.info(f"Print: {msg}")
        temp = QLabel(msg)
        temp.setFixedHeight(20)
        self.scrollWidget.layout().addWidget(temp)
        self.scrollWidget.update()

    def openHelp(self):
        if sys.platform == 'linux2':
            os.system("start res/user-manual/user-manual.pdf")
        else:
            os.system("open res/user-manual/user-manual.pdf")
        self.log.info("Opened help document")


# class Worker2(QObject):
#     signal = pyqtSignal()
#     stop = pyqtSignal()
#
#     def __init__(self):
#         QThread.__init__(self)
#         self.running = False
#         self.function = self.threader
#         self.signal.connect(self.run)
#         self.stop.connect(self.pause)
#         self.log = logging.getLogger(__name__)
#         self.color = ''
#
#     @pyqtSlot()
#     def run(self):
#         self.function()
#
#     @pyqtSlot()
#     def pause(self):
#         self.log.info("Thread halted")
#         self.running = False
#
#     def threader(self):
#         self.color = controller.ask_for_color(self.interface)
#
#         try:
#             self.win.interface.print_to_user("Your color: " + self.color)
#             self.win.interface.print_to_user("Listening. What's your move?")
#             # self.signal.emit("Your color: " + color)
#             # self.signal.emit("Listening. What's your move?")
#             res = controller.handle_user_command(self.interface)
#             while res != ['exit'] and self.running:
#                 # print_to_user(interface, "Your Command: " + str(res))
#                 res = controller.handle_user_command(self.interface)
#                 if res == ['exit']:
#                     self.running = False
#         except Exception as e:
#             self.log.debug(f"Error in thread: {str(e)}")
#             print(f"Error in thread: {str(e)}")


class Worker(QThread):
    send_msg = pyqtSignal(str)
    stop = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.running = False
        self.log = logging.getLogger(__name__)

    def run(self):
        if self.running:
            self.send_msg.emit("Listening. What's your move?")
            res = controller.handle_user_command(self)
            if res == ['exit']:
                self.running = False
        else:
            self.running = True
            color = controller.ask_for_color(self)
            self.send_msg.emit("Your color: " + color)

        # try:
        #     self.running = True
        #
        #
        #
        #     while res != ['exit'] and self.running:
        #         self.send_msg.emit("Your Command: " + str(res))
        #         # print_to_user(interface, "Your Command: " + str(res))
        #         res = controller.handle_user_command(self)
        #
        # except Exception as e:
        #     self.log.debug(f"Error in thread: {str(e)}")
        #     print(f"Error in thread: {str(e)}")


def print_to_user(msg):
    interface.print_to_user(msg)


if __name__ == "__main__":
    controller.configure_logging()
    app = QApplication([])
    my_thread = QThread()
    my_thread.start()

    worker = Worker()
    worker.moveToThread(my_thread)
    worker.send_msg.connect(print_to_user)
    worker.stop.connect(print_to_user)

    interface = ChessUI(worker)
    spot = 0

    sys.exit(app.exec_())
