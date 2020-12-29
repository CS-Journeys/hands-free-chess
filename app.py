import sys
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import *
from src import controller


class ChessUI(QWidget):
    def __init__(self, worker):
        super().__init__()
        self.layout = QVBoxLayout()
        self.scroll = QScrollArea()
        self.scrollWidget = QWidget()

        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")

        self.thread = worker
        self.thread.signal.connect(self.print_to_user)
        self.thread.finished.connect(self.quitApp)

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

    def buttonClicked(self):
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
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.thread.start()
            self.thread.signal.connect(self.print_to_user)

        elif sender.text() == 'Pause':
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.paused = True
            self.thread.running = False
            self.thread.quit = True
            self.print_to_user("Application Paused")

        elif sender.text() == 'Stop':
            self.quitApp()

    def quitApp(self):
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.thread.running = False
        self.thread.quit = True
        self.print_to_user("Bye...")
        self.close()
        exit(0)

    def print_to_user(self, msg):
        temp = QLabel(msg)
        temp.setFixedHeight(20)
        self.scrollWidget.layout().addWidget(temp)
        self.scrollWidget.update()


class Worker(QThread):
    signal = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.quit = True
        self.running = False

    def run(self):
        try:
            self.running = True
            color = controller.ask_for_color(interface)

            self.signal.emit("Your color: " + color)
            self.signal.emit("Listening. What's your move?")
            # print_to_user(interface, "Your color: " + color)
            # print_to_user(interface, "Listening. What's your move?")
            res = controller.handle_user_command(interface)
            while res != ['exit'] and self.running:
                self.signal.emit("Your Command: " + str(res))
                # print_to_user(interface, "Your Command: " + str(res))
                res = controller.handle_user_command(interface)
                if res == ['exit'] or self.quit == True:
                    self.exit()
        except:
            print("error")


def print_to_user(ui, msg):
    ui.print_to_user(msg)


if __name__ == "__main__":
    app = QApplication([])
    thread = Worker()

    interface = ChessUI(thread)
    spot = 0

    sys.exit(app.exec_())
