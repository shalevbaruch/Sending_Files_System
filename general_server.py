import socket
import os
import ssl
import threading


class My_Server:

    def __init__(self, listen_port, simultaneous_requests_limit, handle=None) -> None:
        self.listen_port = listen_port
        self.simultaneous_requests_limit = simultaneous_requests_limit
        self.handle = handle
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('', self.listen_port)
        self.listen_socket.bind(self.server_address)


    def start(self):

        self.listen_socket.listen(self.simultaneous_requests_limit)
        
        print("Server is listening")
        
        with self.listen_socket:
            while True:
                client_soc, client_address = self.listen_socket.accept()
                ssl_client_soc = ssl.wrap_socket(client_soc, server_side=True, certfile="server.crt", keyfile="server.key")
                print("received new client")
                t1 = threading.Thread(target=self.handle, args=(ssl_client_soc, client_address))
                t1.start()
                # self.handle(ssl_client_soc, client_address)




