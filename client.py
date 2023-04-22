import socket
import sys
from PySide6 import QtGui
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QDialog, QLineEdit, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, \
    QFileDialog
from PIL import Image


class CommunicatorClient(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Client")
        self.setGeometry(200, 200, 800, 700)

        # Chat box
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QtGui.QFont("Courier", 9))       # font for better ASCII-art displaying
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        # Field for rs232 signals
        self.rs232_edit = QTextEdit()
        self.rs232_edit.setFont(QtGui.QFont("Courier", 9))       # font for better ASCII-art displaying
        self.rs232_edit.setReadOnly(True)
        layout.addWidget(self.rs232_edit)

        # Line to enter messages
        self.edit_line = QLineEdit()
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        upload_button = QPushButton("Upload Image")
        upload_button.clicked.connect(self.convert_image)

        # Layout
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.edit_line)
        bottom_layout.addWidget(send_button)
        bottom_layout.addWidget(upload_button)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        self.socket = None
        self.host = "localhost"
        self.port = 11000

        self.connect_to_server()

    def connect_to_server(self):
        # create self socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connection
        try:
            self.socket.connect((self.host, self.port))
        except socket.error as e:
            print(str(e))
            sys.exit()

        # Receiving messages from others
        self.receive_thread = ReceiveThread(self.socket, self)
        self.receive_thread.start()

    def prepare_data_to_send(self, data):
        # each letter written in ascii
        message_pack = [bin(ord(letter)) for letter in data]

        rs232_pack = ''

        for byte in message_pack:
            single_packet = byte[2::]

            # it should be a full byte
            if len(single_packet) < 8:
                single_packet = '0' * (8 - len(single_packet)) + single_packet

            # add start stop bits
            single_packet = '0' + single_packet + '11'

            # add to packet
            rs232_pack = rs232_pack + single_packet

        return rs232_pack

    def send_message(self):
        # save string
        message = self.edit_line.text()
        # each letter written in ascii
        message_pack = [bin(ord(letter)) for letter in message]

        package = self.prepare_data_to_send(message)

        rs232_package = package.encode()

        self.socket.send(rs232_package)
        # self.text_edit.append(f"Me: {self.edit_line.text()}")
        self.edit_line.clear()

    # upload image and convert to ASCII_art
    def convert_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Image File", ".", "Images (*.png *.jpg *.jpeg *.bmp)")
        if filename:
            image = Image.open(filename)

            # resize the image
            width, height = image.size
            aspect_ratio = height / width
            new_width = 100
            new_height = aspect_ratio * new_width
            image = image.resize((new_width, int(new_height)))

            image = image.convert('L')

            pixels = image.getdata()

            # replace each pixel with a character from array
            chars = ["B", "S", "#", "&", "@", "$", "%", "*", "!", ":", "."]
            new_pixels = [chars[pixel // 25] for pixel in pixels]
            new_pixels = ''.join(new_pixels)

            # split string of chars into multiple strings of length equal to new width and create a list
            new_pixels_count = len(new_pixels)
            ascii_image = [new_pixels[index:index + new_width] for index in range(0, new_pixels_count, new_width)]
            ascii_image = "\n".join(ascii_image)

            message = ascii_image.encode()
            self.socket.sendall(message)
            self.text_edit.append("Me: [Image]")


class ReceiveThread(QThread):
    def __init__(self, socket, parent=None):
        super().__init__(parent)
        self.socket = socket

    def run(self):
        while True:
            try:
                message = self.socket.recv(2020).decode()
                self.parent().text_edit.append(message)
            except socket.error:
                break
