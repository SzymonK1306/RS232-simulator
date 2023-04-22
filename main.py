import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QDialog
from server import CommunicatorServer
from client import CommunicatorClient


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My communicator")
        self.setGeometry(100, 100, 200, 200)

        layout = QVBoxLayout()

        # Create button for server
        start_server_button = QPushButton(text="Start Server")
        start_server_button.clicked.connect(self.start_server)
        layout.addWidget(start_server_button)

        # Create button for client
        connect_client_button = QPushButton()
        connect_client_button.setText("Connect Client")
        connect_client_button.clicked.connect(self.connect_client)
        layout.addWidget(connect_client_button)

        widget = QDialog()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.server = CommunicatorServer()

    # start server method
    def start_server(self):
        self.server.start_server()

    # start client method
    def connect_client(self):
        client_window = CommunicatorClient(self)
        client_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
