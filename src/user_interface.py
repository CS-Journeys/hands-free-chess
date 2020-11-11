import sys
from PyQt5.QtWidgets import *
import main


class ChessUI(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.messages = ""
        self.label = QLabel(self.messages)
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

    def buttonClicked(self, e):
        sender = self.sender()
        if sender.text() == 'Start':
            self.start_button.setDisabled(True)
            self.print_to_user("Starting application...")
            main.main()
        elif sender.text() == 'Stop':
            self.print_to_user("Stopping application...")
            self.close()

    def print_to_user(self, message):
        self.label.setText(self.messages + '\n' + message)
        self.messages += (message + '\n')
        print(message)


global app
app = QApplication([])

global interface
interface = ChessUI()


def getUI():
    global interface
    return interface


def print_to_user(message):
    interface.print_to_user(message)


if __name__ == "__main__":
    interface.print_to_user('Click \"Start\" to begin.')

    sys.exit(app.exec_())
