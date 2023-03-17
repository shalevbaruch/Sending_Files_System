import socket
import select
import os
import ssl
import threading


def handle(server, ssl_client_soc):  # the server message to the client
    client_msg = ssl_client_soc.recv(1024).decode()
    command_option = client_msg[0]
    match command_option:
        case '1':  # the client wants to upload a file
            case1(server, ssl_client_soc, client_msg)
        case '2':  # the client wants to download a a file
            case2(server, ssl_client_soc, client_msg)
            
        case '3':  # the client requests the list of the available files that the server holds
            fileList = " ".join(server.FILES_LIST)
            ssl_client_soc.sendall(len(fileList).to_bytes(4, byteorder='big'))
            ssl_client_soc.sendall(fileList.encode())
            
        case '4':  # the client wants to close the connection
            raise ValueError("end of conversation")  # creating exception to close the socket
        case _:
            ssl_client_soc.sendall("error - command option not found\n".encode())  # not in the protocol rules, actually can't get here


def case1(server, ssl_client_soc, client_msg): 
        client_msg = client_msg.split(" ")  # splitting between the type of the command, the filename and the file-size 
        filename = client_msg[1]  # the name of the file that the client wants to upload
        ssl_client_soc.send("start uploading".encode())
        with open(os.path.join(server.FILES_DIR_PATH, filename), 'wb') as file_to_write:
            fileSize = int(client_msg[2])
            bytes_written = 0
            while bytes_written != fileSize:
                data = ssl_client_soc.recv(1024)
                file_to_write.write(data)
                bytes_written += len(data)
            server.FILES_LIST.append(filename)


def case2(server, ssl_client_soc, client_msg):
    reqFile = client_msg[1:].strip()  # this is the filename to be downloaded
    if reqFile in server.FILES_LIST:  # if the server has the file
        ssl_client_soc.send("True ".encode())  # Padding with a space so that the message length will be 5 as "False"

        filePath = os.path.join(server.FILES_DIR_PATH, reqFile)
        with open(filePath, 'rb') as file_to_send:
            fileSize = os.path.getsize(filePath)
            ssl_client_soc.sendall(fileSize.to_bytes(4, byteorder='big'))  # this message is 4 bytes long
            fileContent = file_to_send.read()
            ssl_client_soc.sendall(fileContent)
    else:
        ssl_client_soc.sendall("False".encode())  







class My_Server:

    def __init__(self, LISTEN_PORT, SIMULTANEOUS_REQUESTS_LIMIT, TRANSPORT_LAYER_PROTOCOL, FILES_DIR_PATH=None, FILES_LIST=[], HANDLE=handle, RUNS_ONCE=None) -> None:
        self.LISTEN_PORT = LISTEN_PORT
        self.SIMULTANEOUS_REQUESTS_LIMIT = SIMULTANEOUS_REQUESTS_LIMIT
        self.FILES_LIST = FILES_LIST
        self.FILES_DIR_PATH = FILES_DIR_PATH
        self.HANDLE = HANDLE
        self.TRANSPORT_LAYER_PROTOCOL = TRANSPORT_LAYER_PROTOCOL
        self.RUNS_ONCE = RUNS_ONCE

    def start(self):
        isRun = False
        
        if self.TRANSPORT_LAYER_PROTOCOL == "UDP":
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 300000)
        else:
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = ('', self.LISTEN_PORT)
        listen_socket.bind(server_address)
        if self.TRANSPORT_LAYER_PROTOCOL == "TCP":
            listen_socket.listen(self.SIMULTANEOUS_REQUESTS_LIMIT)
        
        connections = {listen_socket}
        to_remove = []  # includes all the sockets that every client closes
        print("Server is listening")
        
        with listen_socket:
            while True:
                # readable contains sockets that received a message (that we haven't read yet) from the client,
                # or the listen_socket for apply new connection
                readable, _, _ = select.select(connections, [], connections)
                for connection in readable:
                    if connection is listen_socket:  # a client sends a message
                        if self.TRANSPORT_LAYER_PROTOCOL == "TCP":
                            client_soc, client_address = listen_socket.accept()
                            ssl_client_soc = ssl.wrap_socket(client_soc, server_side=True, certfile="server.crt", keyfile="server.key")
                            connections.add(ssl_client_soc)
                        else:  # TRANSPORT_LAYER_PROTOCOL == "UDP":
                            try:
                                self.HANDLE(self, connection)
                            except:
                                continue
                    else:  # receive a message from a client - a request ufter the initial connect. can't get here if using UDP
                        try:
                            self.HANDLE(self, connection)
                            if self.RUNS_ONCE is not None:
                                if not isRun:
                                    isRun = True
                                    keyboard_server_ip =  "10.0.0.60"  # when I'm using my laptop as the customer and I'm at home (The IP will probable change if I am at Tel-Aviv)
                                    keyboard_server_port = 9200
                                    Transport_Layer_Protocol = "TCP"
                                    self.RUNS_ONCE(keyboard_server_ip, keyboard_server_port, Transport_Layer_Protocol)
                                    t2 = threading.Thread(target=self.RUNS_ONCE, args=(keyboard_server_ip, keyboard_server_port, Transport_Layer_Protocol))

                        except Exception:  # case 4 (client wants to close the socket) or any other Exception with the socket
                            to_remove.append(connection)

                for s in to_remove:  # remove all the sockets that the clients closed from the current connections list
                    connections.remove(s)
                    s.close()
                to_remove = []





if __name__ == "__main__":
    path = "C:/University/YoungForTech/networks/Sending_Files_System/cloud"
    server = My_Server(9124, 5, "TCP", path, os.listdir(path))
    server.start()