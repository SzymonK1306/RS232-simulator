import socket
import threading


class CommunicatorServer:
    def __init__(self):
        # server socket
        self.server = None
        # list of clients sockets
        self.clients = []

    def start_server(self):
        # create server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # port and host address
        host = "localhost"
        port = 11000

        # server start
        try:
            self.server.bind((host, port))
        except socket.error as e:
            print(str(e))

        self.server.listen()

        print(f"Server is running")
        print(f'Host: {host}')
        print(f'Port: {port}')

        # thread for accept clients
        threading.Thread(target=self.accept_clients).start()

    def accept_clients(self):
        while True:
            client_socket, address = self.server.accept()
            self.clients.append(client_socket)

            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(2020)
                if message:
                    # send to every client (except sender)
                    # broadcast
                    for client in self.clients:
                        if client != client_socket:
                            client.send(message)
                else:
                    self.clients.remove(client_socket)
                    client_socket.close()
                    break
            except:
                continue


