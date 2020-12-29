import sys
import logging
import threading

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

        self.thread = my_worker

        self.paused = False
        self.initUI()

    def initUI(self):
        self.log.info("Initializing UI")
        self.start_button.clicked.connect(self.buttonClicked)
        self.pause_button.clicked.connect(self.buttonClicked)
        self.stop_button.clicked.connect(self.buttonClicked)

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
                # self.print_to_user("Please wait...")
                controller.setup(self)
                self.log.info("First app startup")
            self.paused = False
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.thread.signal.emit()
            # self.thread.signal.connect(self.print_to_user)
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


class Worker2(QObject):
    signal = pyqtSignal()
    stop = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self.running = False
        self.function = self.threader
        self.signal.connect(self.run)
        self.stop.connect(self.pause)
        self.log = logging.getLogger(__name__)
        self.color = ''

    @pyqtSlot()
    def run(self):
        self.function()

    @pyqtSlot()
    def pause(self):
        self.log.info("Thread halted")
        self.running = False

    def threader(self):
        self.color = controller.ask_for_color(interface)

        try:
            interface.print_to_user("Your color: " + self.color)
            interface.print_to_user("Listening. What's your move?")
            # self.signal.emit("Your color: " + color)
            # self.signal.emit("Listening. What's your move?")
            res = controller.handle_user_command(interface)
            while res != ['exit'] and self.running:
                # print_to_user(interface, "Your Command: " + str(res))
                res = controller.handle_user_command(interface)
                if res == ['exit']:
                    self.running = False
        except Exception as e:
            self.log.debug(f"Error in thread: {str(e)}")
            print(f"Error in thread: {str(e)}")


# class Worker(QThread):
#     signal = pyqtSignal(str)
#
#     def __init__(self):
#         QThread.__init__(self)
#         self.quit = True
#         self.running = False
#         self.log = logging.getLogger(__name__)
#
#     def run(self):
#         try:
#             self.running = True
#             color = controller.ask_for_color(interface)
#
#             self.signal.emit("Your color: " + color)
#             self.signal.emit("Listening. What's your move?")
#             # print_to_user(interface, "Your color: " + color)
#             # print_to_user(interface, "Listening. What's your move?")
#             res = controller.handle_user_command(interface)
#             while res != ['exit'] and self.running:
#                 self.signal.emit("Your Command: " + str(res))
#                 # print_to_user(interface, "Your Command: " + str(res))
#                 res = controller.handle_user_command(interface)
#                 if res == ['exit'] or self.quit == True:
#                     self.exit()
#         except Exception as e:
#             self.log.debug(f"Error in thread: {str(e)}")
#             print(f"Error in thread: {str(e)}")


def print_to_user(ui, msg):
    ui.print_to_user(msg)


if __name__ == "__main__":
    app = QApplication([])
    # thread = Worker()
    my_thread = QThread()
    my_thread.start()

    worker = Worker2()
    worker.moveToThread(my_thread)
    worker.signal.connect(worker.run)

    interface = ChessUI(worker)
    spot = 0

    sys.exit(app.exec_())