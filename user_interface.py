import sys
import threading

from PyQt5.QtWidgets import *
from src import controller

class StartThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
       regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StartThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

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
            self.start_button.setDisabled(True)
            self.print_to_user("Starting application...")
            self.print_to_user("Please wait...")
            controller.setup()
            self.start()

        elif sender.text() == 'Pause':
            self.start_button.setDisabled(False)
            self.print_to_user("Application Paused")
            self.thready[0].stop()

        elif sender.text() == 'Stop':
            self.quitApp()

    def start(self):
        t = StartThread(target=self.listen, args=())
        self.thready.append(t)
        t.start()

    def quitApp(self):
        self.start_button.setDisabled(True)
        self.pause_button.setDisabled(True)
        self.print_to_user("Bye...")
        self.thready[0].stop()
        self.close()
        exit(0)

    def print_to_user(self, message):
        self.messages += ('\n' + message)
        self.label.setText(self.messages)
        print(message)

    def listen(self):
        res = controller.readUserCommand()
        if res[0]['transcript'] != ['exit']:
            self.print_to_user("Your Command: " + res[0]['transcript'])
            self.listen()
        self.quitApp()


global app
app = QApplication([])

global interface
interface = ChessUI()


def print_to_user(message):
    interface.print_to_user(message)


if __name__ == "__main__":
    interface.print_to_user('Click \"Start\" to begin.')

    sys.exit(app.exec_())
