import sys
import threading

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *
from src import controller

# class StartThread(threading.Thread):
#     """Thread class with a stop() method. The thread itself has to check
#        regularly for the stopped() condition."""
#
#     def __init__(self, *args, **kwargs):
#         super(StartThread, self).__init__(*args, **kwargs)
#         self._stop_event = threading.Event()
#
#     def stop(self):
#         self._stop_event.set()
#
#     def stopped(self):
#         return self._stop_event.is_set()

class ChessUI(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.messages = ""
        self.label = QLabel(self.messages)
        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.thready = []
        self.thread = Worker()
        self.thread.signal.connect(self.quitApp)
        self.paused = False
        self.initUI()

    def initUI(self):
        self.start_button.clicked.connect(self.buttonClicked)
        self.pause_button.clicked.connect(self.buttonClicked)
        self.stop_button.clicked.connect(self.buttonClicked)

        scroll = QScrollArea()
        scroll.setWidget(self.label)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(400)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.pause_button)
        self.layout.addWidget(self.stop_button)

        self.setWindowTitle("Hands Free Chess")
        self.setLayout(self.layout)
        self.show()

    def buttonClicked(self, e):
        sender = self.sender()
        if sender.text() == 'Start':
            if self.paused:
                self.print_to_user("Restarting application...")
                self.print_to_user("Please wait...")
            else:
                self.print_to_user("Starting application...")
                self.print_to_user("Please wait...")
                controller.setup(self)
            self.paused = False
            self.start_button.setDisabled(True)
            self.start()

        elif sender.text() == 'Pause':
            self.paused = True
            self.start_button.setDisabled(False)
            self.print_to_user("Application Paused")
            self.thread.quit = True
            # self.thready[0].join()

        elif sender.text() == 'Stop':
            self.quitApp()

    def start(self):
        self.thread.start()
        # t = StartThread(target=self.listen, args=())
        # self.thready.append(t)
        # t.start()

    def quitApp(self):
        self.start_button.setDisabled(True)
        self.pause_button.setDisabled(True)
        self.print_to_user("Bye...")
        # self.thready[0].join()
        self.close()
        exit(0)

    def print_to_user(self, message):
        self.messages += ('\n' + message)
        self.label.setText(self.messages)
        self.label.update()
        # print(message)

    # def listen(self):
    #     res = controller.readUserCommand()
    #     while res != ['exit'] and not self.quit:
    #         self.print_to_user("Your Command: " + res.__str__())
    #         res = controller.readUserCommand()
    #     self.quit = True
    #     self.quitApp()


class Worker(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        QThread.__init__(self)
        self.quit = False

    def run(self):
        res = controller.readUserCommand()
        while res != ['exit'] and not self.quit:
            ChessUI.print_to_user(interface, "Your Command: " + res.__str__())
            res = controller.readUserCommand()
        return




global app
app = QApplication([])

global interface
interface = ChessUI()


def print_to_user(message):
    interface.print_to_user(message)


if __name__ == "__main__":
    interface.print_to_user('Click \"Start\" to begin.')

    sys.exit(app.exec_())
