import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *
from src import controller


class ChessUI(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.scroll = QScrollArea()
        self.scrollWidget = QWidget()

        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")

        self.thread = Worker()
        self.thread.signal.connect(self.quitApp)

        self.paused = False
        self.initUI()

    def initUI(self):
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
            self.pause_button.setDisabled(False)
            self.thread.start()

        elif sender.text() == 'Pause':
            self.start_button.setDisabled(False)
            self.pause_button.setDisabled(True)
            self.paused = True
            self.thread.quit = True
            self.print_to_user("Application Paused")

        elif sender.text() == 'Stop':
            self.quitApp()

    def quitApp(self):
        self.start_button.setDisabled(True)
        self.pause_button.setDisabled(True)
        self.thread.quit = True
        self.print_to_user("Bye...")
        self.close()
        exit(0)

    def print_to_user(self, message):
        temp = QLabel(message)
        temp.setFixedHeight(20)
        self.scrollWidget.layout().addWidget(temp)
        self.scrollWidget.update()


class Worker(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        QThread.__init__(self)
        self.quit = True

    def run(self):
        color = controller.ask_for_color(interface)
        ChessUI.print_to_user(interface, "Your color: " + color)
        ChessUI.print_to_user(interface, "Listening. What's your move?")
        res = controller.handle_user_command(interface)
        while res != ['exit'] and not self.quit:
            ChessUI.print_to_user(interface, "Your Command: " + str(res))
            res = controller.handle_user_command(interface)
        return




global app
app = QApplication([])

global interface
interface = ChessUI()

if __name__ == "__main__":
    sys.exit(app.exec_())
